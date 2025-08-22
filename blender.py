import os
import torch
import fnmatch
from collections import OrderedDict


def extract(ckpt):
    a = ckpt["model"]
    opt = OrderedDict()
    opt["weight"] = {}
    for key in a.keys():
        if "enc_q" in key:
            continue
        opt["weight"][key] = a[key]
    return opt


def find_matching_layers(layer_keys, pattern):
    """Find all layer keys that match the given pattern using fnmatch."""
    matching = [key for key in layer_keys if fnmatch.fnmatch(key, pattern)]
    print(f"      🔍 Pattern '{pattern}' matched: {matching[:3]}{'...' if len(matching) > 3 else ''}")
    return matching


def blend_models(output_path, model1, model2, blend_rules, default_weight=0.5):
    """
    Blend two models with granular control over individual layers.
    
    Args:
        output_path (str): Relative path including name for the output blended model
        model1 (dict): {"path": "path/to/model1", "sid": 0}
        model2 (dict): {"path": "path/to/model2", "sid": 0} 
        blend_rules (list): [{"layers": "pattern", "weight": 0.3}, ...]
                           weight determines model1's contribution (0.0 = all model2, 1.0 = all model1)
        default_weight (float): Default weight for layers not specified in blend_rules
    Returns:
        str: message on success, error on failure
    """

    # Clamp default weight between 0.0 and 1.0
    clamped_default_weight = max(0.0, min(1.0, default_weight))
    if clamped_default_weight != default_weight:
        print(f"⚠️  default_weight was not in range 0 to 1. Clamped to {clamped_default_weight}")
        default_weight = clamped_default_weight

    try:
        print(f"🔄 Starting blend operation: '{output_path}'")
        print(f"📁 Model 1: {model1['path']} (sid: {model1['sid']})")
        print(f"📁 Model 2: {model2['path']} (sid: {model2['sid']})")
        print(f"⚙️  Blend rules: {len(blend_rules)} rules defined")
        
        # Load models
        print("🔧 Loading model 1...")
        ckpt1 = torch.load(model1["path"], map_location="cpu", weights_only=True)
        print("🔧 Loading model 2...")
        ckpt2 = torch.load(model2["path"], map_location="cpu", weights_only=True)
        print("✅ Both models loaded successfully")

        # Basic compatibility checks
        print("🔍 Checking model compatibility...")
        if ckpt1["sr"] != ckpt2["sr"]:
            print("❌ Sample rate mismatch!")
            return "The sample rates of the two models are not the same."
        print(f"✅ Sample rates match: {ckpt1['sr']} Hz")

        # Extract metadata from first model
        print("📊 Extracting metadata from model 1...")
        cfg = ckpt1["config"]
        cfg_f0 = ckpt1["f0"]
        cfg_version = ckpt1["version"]
        cfg_sr = ckpt1["sr"]
        vocoder = ckpt1.get("vocoder", "HiFi-GAN")
        print(f"   Version: {cfg_version}, F0: {cfg_f0}, Vocoder: {vocoder}")

        # Extract weights
        print("⚖️  Extracting weights from models...")
        if "model" in ckpt1:
            weights1 = extract(ckpt1)["weight"]
        else:
            weights1 = ckpt1["weight"]
            
        if "model" in ckpt2:
            weights2 = extract(ckpt2)["weight"]
        else:
            weights2 = ckpt2["weight"]
        
        print(f"   Model 1 has {len(weights1)} layers")
        print(f"   Model 2 has {len(weights2)} layers")

        # Build layer weight mapping from blend rules
        print("🎛️  Processing blend rules...")
        layer_weights = {}
        for i, rule in enumerate(blend_rules):
            pattern = rule["layers"]
            weight = rule["weight"]
            print(f"   Rule {i+1}:")
            matching_layers = find_matching_layers(weights1.keys(), pattern)
            print(f"       '{pattern}' (weight: {weight}) → {len(matching_layers)} layers")
            for layer in matching_layers:
                layer_weights[layer] = weight
        
        print(f"📋 Total layers with specific weights: {len(layer_weights)}")
        unspecified_layers = len(weights1) - len(layer_weights)
        if unspecified_layers > 0:
            print(f"📋 Layers using default weight ({default_weight}): {unspecified_layers}")

        # Create blended model
        print("🔀 Starting layer blending process...")
        opt = OrderedDict()
        opt["weight"] = {}
        
        processed_layers = 0
        special_layers = 0
        
        for key in weights1.keys():
            # Get blend weight for this layer (default to default_weight if not specified)
            alpha = layer_weights.get(key, default_weight)

            # Handle speaker embedding special case
            if key == "emb_g.weight" and weights1[key].shape != weights2[key].shape:
                print(f"   🔧 Special handling for '{key}': shape mismatch {weights1[key].shape} vs {weights2[key].shape}")
                min_shape0 = min(weights1[key].shape[0], weights2[key].shape[0])
                opt["weight"][key] = (
                    alpha * (weights1[key][:min_shape0].float())
                    + (1 - alpha) * (weights2[key][:min_shape0].float())
                ).half()
                special_layers += 1
            else:
                # Standard layer blending
                opt["weight"][key] = (
                    alpha * (weights1[key].float()) + (1 - alpha) * (weights2[key].float())
                ).half()
            
            processed_layers += 1
            if processed_layers % 50 == 0:  # Progress update every 50 layers
                print(f"   📊 Processed {processed_layers}/{len(weights1)} layers...")
        
        print(f"✅ Blending complete! Processed {processed_layers} layers ({special_layers} with special handling)")

        # Add metadata
        print("📝 Adding metadata to blended model...")
        opt["config"] = cfg
        opt["sr"] = cfg_sr
        opt["f0"] = cfg_f0
        opt["version"] = cfg_version
        opt["vocoder"] = vocoder
        
        # Create blend info message
        blend_info = f"Blended {model1['path']} (sid:{model1['sid']}) and {model2['path']} (sid:{model2['sid']}) with {len(blend_rules)} layer-specific rules"
        opt["info"] = blend_info

        # Save blended model
        print("💾 Saving blended model...")
        torch.save(opt, output_path)
        print(f"🎉 Successfully saved blended model to: {output_path}")
        
        print(blend_info)
        return blend_info
        
    except Exception as error:
        print(f"❌ An error occurred blending the models: {error}")
        print(f"🔍 Error type: {type(error).__name__}")
        return error

  

# main test function
if __name__ == "__main__":
    output_path = "../blends/model.pth"
    model1 = {"path": "../models/Dalitso.pth", "sid": 0}
    model2 = {"path": "../models/Danylo_V02.pth", "sid": 0}
    blend_rules = [
        {"layers": "emb_g.weight", "weight": 0.7},
        {"layers": "dec.cond.*", "weight": 0.2}
        
    ]
    default_weight = 1.0
    blend_info = blend_models(output_path, model1, model2, blend_rules, default_weight=default_weight)
    print(blend_info)