import os
from config_global import config_global
from full_prep import full_prep_web
from detect_data import detect_new_data
from cls_data import class_data_web
from save_result import save_result_web
# from save_result_fromDicom import save_result_web


def predict_main(patient, filename, has_info, skip_prep):
    if not skip_prep:
        full_prep_web(patient, has_info)
    detect_new_data(filename, has_info)
    prob_overall, n, pred_list = class_data_web(filename, has_info)
    n, ret_result = save_result_web(prob_overall=float(prob_overall[0]),patient=patient, pred_list=pred_list, has_info=has_info)

    return float(prob_overall[0]), n, ret_result


if __name__ == '__main__':
    # 本地测试文件是否可以成功检测与分类
    skip_prep = True
    filename = 'feichuang'
    has_info = False
    patient_info = {}
    patient_info['path'] = os.path.join(config_global['ROOT_PATH'], 'uploads/extract_files', filename)
    patient_info['path'] = patient_info['path'].replace('\\', '/')
    patient_info['full_name'] = filename
    predict_main(patient_info, filename, has_info, skip_prep=skip_prep)
