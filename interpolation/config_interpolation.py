import os
from detectorhit.config_global import config_global

detector_path = '/home/cuiyang/workspace/lung_cancer/LCCAD/detectorhit/'
interpolation_path = '/home/cuiyang/workspace/lung_cancer/LCCAD/interpolation/'
config_interpolation={
    'detector_path': detector_path,
    'interpolation_path': interpolation_path,

    'flow_model': os.path.join(interpolation_path, 'ckpt_net'),
    'inter_model': os.path.join(interpolation_path, 'ckpt_inter'),

    'data_path': config_global['save_result_no_info_folder'],
    'out_path': os.path.join(interpolation_path, 'inter_sample'),


}