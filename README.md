# Voice Blender 

Clone from this repo: https://github.com/nearlyready/voice-blender
- No PAT needed if cloning into VSCode SSH remote session


## Andrii

Running three training cells at the same time (select all, run). Can this be combined into a single function?
Identifying the best training run visually, labelling the checkpoint "_best.pth"
Selecting and copying all of the "_best" files and place in one folder (removes name), three-way blending (two double blends in sequence), make audio for each blend.
- He created his own script for inferencing when there are multiple models, and multiple files. The prompt files for inferencing are selected from validation files drawn from validation folders nested according to gender > (singing | language | emotions)
Tools needed for sisters to evaluate and rate multiple audio files (1 - 5?), export ratings to excel.
Based on sister evaluations select which checkpoint should be saved.
Kim uses tools to assess fundamental frequency of synthetic voice and source data (Joshko tool), generates picture.
- RVC is slower than WebUI for _inference_.

Typical training cell which is called multiple times in sequence:
- The folder and batch_size is the only thing that changes
- Batch size is related to total file size and limited by GPU VRAM
- CPU cores depends on the pod (!nproc -- gives a wrong value, )
```
import training
training.run_pipeline(
    "Dutch_F_Old_CorrieMulder",  # folder with audios | real path: /workspace/rvc-cli/datasets/model_name
    32,                 # CPU cores
    25,                  # save every x epoch
    250,                  # total epochs
    12,                 # batch size
    "/workspace/base/macsi1",     # real path: /workspace/rvc-cli/g_pretrained.pth
    save_only_latest=True,
    overtraining_detector=True, overtraining_threshold=50,
    skip_preprocessing=False, skip_extraction=False, skip_training=False
)
```