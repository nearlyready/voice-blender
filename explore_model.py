import torch

def extract(ckpt):
    a = ckpt["model"]
    opt = OrderedDict()
    opt["weight"] = {}
    for key in a.keys():
        if "enc_q" in key:
            continue
        opt["weight"][key] = a[key]
    return opt


def recursive_key_print(indent_level, data):
    for key, value in data.items():
        print("  " * indent_level + f"{key}: {value.shape if isinstance(value, torch.Tensor) else type(value)}")
        if isinstance(value, dict):
            recursive_key_print(indent_level + 1, value)


def explore(path):
    try:
        ckpt = torch.load(path, map_location="cpu", weights_only=True)
        recursive_key_print(0, ckpt)


    except Exception as error:
        print(f"An error occurred: {error}")
        return error


# Main func
if __name__ == "__main__":
    explore("../models/Dalitso.pth")