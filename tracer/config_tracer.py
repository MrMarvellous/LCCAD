import os

detector_path = '/home/cuiyang/workspace/lung_cancer/LCCAD/detectorhit/'
tracer_path = '/home/cuiyang/workspace/lung_cancer/LCCAD/tracer/'
config_tracer={
    'detector_path': detector_path,
    'feat_save_path': os.path.join(detector_path, 'new_result_for_feat'),
    'tracer_path': tracer_path,

    'cover_model': os.path.join(tracer_path, 'ckpt_cover'),
    'class_model': os.path.join(tracer_path, 'ckpt_class'),
    'optimizer_model': os.path.join(tracer_path, 'optimizer_ckpt'),

    'input_path': os.path.join(detector_path, 'new_result_for_feat'),
    'output_path': os.path.join(tracer_path, 'cover_2d_out'),

}