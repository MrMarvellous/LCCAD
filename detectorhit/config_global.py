import platform
import os

root_path = '/home/cuiyang/workspace/lung_cancer/LCCAD/detectorhit/'
config_global = {
    'ROOT_PATH': root_path,
    'detector_param': os.path.join(root_path, 'ckpts/detector.ckpt'),
    'classifier_param': os.path.join(root_path, 'ckpts/cls.ckpt'),

    'preprocess_result_path': os.path.join(root_path, 'new_data'),
    'preprocess_result_path_no_info': os.path.join(root_path, 'new_data_no_info'),
    'detect_result_path':os.path.join(root_path, 'new_bbox_result'),
    'detect_result_path_no_info': os.path.join(root_path, 'new_bbox_result_no_info'),
    'save_result_folder': os.path.join(root_path, 'new_result'),
    'save_result_no_info_folder': os.path.join(root_path, 'new_result_no_info'),
    'save_feature_folder': os.path.join(root_path, 'new_result_for_feat'),

    'n_gpu': 1,
    'flush_zip': True,
    'zipfiles': os.path.join(root_path, 'zipfiles'),
    'extractfiles': os.path.join(root_path, 'extractfiles'),


}
