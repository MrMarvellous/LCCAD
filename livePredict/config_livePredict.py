import os

livePredict_path = "/home/cuiyang/workspace/lung_cancer/LCCAD/livePredict"
config_livePredict={
    'ckpt_path': os.path.join(livePredict_path, 'ckpt_live'),
    'zipfiles':os.path.join(livePredict_path, 'pet_zip_dir'),
    'extractfiles': os.path.join(livePredict_path, 'pet_dir'),
    'flush_zip': False,
}