import os
import shutil
import warnings

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cv2
import pydicom
import gdcm
from PIL import Image

from config_global import config_global
from full_prep import candidates_list

warnings.filterwarnings('ignore')


def iou(box0, box1):
    r0 = box0[3] / 2
    s0 = box0[:3] - r0
    e0 = box0[:3] + r0

    r1 = box1[3] / 2
    s1 = box1[:3] - r1
    e1 = box1[:3] + r1

    overlap = []
    for i in range(len(s0)):
        overlap.append(max(0, min(e0[i], e1[i]) - max(s0[i], s1[i])))

    intersection = overlap[0] * overlap[1] * overlap[2]
    union = box0[3] * box0[3] * box0[3] + \
            box1[3] * box1[3] * box1[3] - intersection
    return intersection / union


def nms(output, nms_th):
    if len(output) == 0:
        return output

    output = output[np.argsort(-output[:, 0])]
    bboxes = [output[0]]
    for i in np.arange(1, len(output)):
        bbox = output[i]
        flag = 1
        for j in range(len(bboxes)):
            temp = iou(bbox[1:5], bboxes[j][1:5])
            if iou(bbox[1:5], bboxes[j][1:5]) >= nms_th:
                flag = -1
                break
        if flag == 1:
            bboxes.append(bbox)
    bboxes = np.asarray(bboxes, np.float32)
    bboxes = bboxes[np.argsort(-bboxes[:, 0])]
    return bboxes


def flush_dir(dirpath):
    for f in os.listdir(dirpath):
        f_path = os.path.join(dirpath, f)
        os.remove(f_path)
    print("flush", dirpath, "complete")


def get_pixarray(dicom_dataset):
    pixel_array = dicom_dataset.pixel_array
    pixel_array = pixel_array * dicom_dataset.RescaleSlope + dicom_dataset.RescaleIntercept  # 获得图像的CT值
    pixel_array = pixel_array.reshape(dicom_dataset.Rows, dicom_dataset.Columns)
    return pixel_array, dicom_dataset.Rows, dicom_dataset.Columns


# 调整CT图像的窗宽窗位
def setDicomWinWidthWinCenter(img_data, winwidth, wincenter, rows, cols):
    # CT检查肺窗的窗宽和窗位分别是W: 1350～1500，C: -500～-350。
    img_temp = img_data
    img_temp.flags.writeable = True
    min = (2 * wincenter - winwidth) / 2.0 + 0.5
    max = (2 * wincenter + winwidth) / 2.0 + 0.5
    dFactor = 255.0 / (max - min)

    for i in np.arange(rows):
        for j in np.arange(cols):
            img_temp[i, j] = int((img_temp[i, j] - min) * dFactor)

    min_index = img_temp < 0
    img_temp[min_index] = 0
    max_index = img_temp > 255
    img_temp[max_index] = 255

    return img_temp


def trans2img(img_data, save_path):
    # dcm = pydicom.dcmread(filename)  # 加载Dicom数据
    dcm_img = Image.fromarray(img_data)  # 将Numpy转换为PIL.Image
    dcm_img = dcm_img.convert('L')

    # 保存为jpg文件，用作后面的生成label用
    dcm_img.save(save_path)
    # 显示图像
    # dcm_img.show()


def save_origin_web(patient):
    patient_window_folder = os.path.join(config_global['save_result_no_info_folder'], patient['full_name'])
    if not os.path.exists(patient_window_folder):
        os.makedirs(patient_window_folder)
    patient_origin_folder = os.path.join(patient_window_folder, 'origin')
    if not os.path.exists(patient_origin_folder):
        os.mkdir(patient_origin_folder)
    patient_result_folder = os.path.join(patient_window_folder, 'result')
    if not os.path.exists(patient_result_folder):
        os.mkdir(patient_result_folder)

    dicom_path = os.path.join(config_global['extractfiles'],patient['full_name'])
    file_list = sorted(os.listdir(dicom_path))
    for index, file_name in enumerate(file_list):
        dcmpath = os.path.join(dicom_path, file_name)
        img_array, rows, cols = get_pixarray(pydicom.dcmread(dcmpath))
        img_array = setDicomWinWidthWinCenter(img_array, 1400, -400, rows, cols)
        save_path = os.path.join(patient_origin_folder, "origin_" + str(index).zfill(3) + ".png")
        trans2img(img_array, save_path)
        if index%100==0:
            print("trans "+str(index)+"ok")

    return 0


def get_result_web(prob_overall, patient, pred_list, save_feat, use_chinese=True, has_info=True):
    save_result_folder = config_global['save_result_folder']
    save_feature_folder = config_global['save_feature_folder']
    if has_info:
        patient_name_folder = os.path.join(save_result_folder, patient['name'])
        if not os.path.exists(patient_name_folder):
            os.mkdir(patient_name_folder)
        patient_date_folder = os.path.join(patient_name_folder, patient['date'])
        if not os.path.exists(patient_date_folder):
            os.mkdir(patient_date_folder)
        patient_window_folder = os.path.join(patient_date_folder, patient['window'])
        if not os.path.exists(patient_window_folder):
            os.mkdir(patient_window_folder)
        patient_origin_folder = os.path.join(patient_window_folder, 'origin')
        if not os.path.exists(patient_origin_folder):
            os.mkdir(patient_origin_folder)
        patient_result_folder = os.path.join(patient_window_folder, 'result')
        if not os.path.exists(patient_result_folder):
            os.mkdir(patient_result_folder)
    else:
        patient_window_folder = os.path.join(config_global['save_result_no_info_folder'], patient['full_name'])
        if not os.path.exists(patient_window_folder):
            os.makedirs(patient_window_folder)
        patient_origin_folder = os.path.join(patient_window_folder, 'origin')
        if not os.path.exists(patient_origin_folder):
            os.mkdir(patient_origin_folder)
        patient_result_folder = os.path.join(patient_window_folder, 'result')
        if not os.path.exists(patient_result_folder):
            os.mkdir(patient_result_folder)

    result = []
    pbb_path = os.path.join(config_global['detect_result_path'], patient['full_name'] + '_pbb.npy')

    if not has_info:
        pbb_path = os.path.join(config_global['detect_result_path_no_info'], patient['full_name'] + '_pbb.npy')
    print('pbb_path:', pbb_path)
    if not os.path.exists(pbb_path):
        return -1, result
    pbb = np.load(pbb_path)
    pbb = pbb[pbb[:, 0] > -1]
    pbb = nms(pbb, 0.05)  # 输出的第一个是label表明是否为正样本后面4列数据为bbox的值 z x y radius
    img_path = os.path.join(config_global['preprocess_result_path'], patient['full_name'] + '_clean.npy')
    if not has_info:
        img_path = os.path.join(config_global['preprocess_result_path_no_info'], patient['full_name'] + '_clean.npy')
    img = np.load(img_path)

    n = len(pbb)

    zfill_length = 0
    temp_n = n
    while temp_n / 10 > 0:
        zfill_length = zfill_length + 1
        temp_n = int(temp_n / 10)

    if save_feat:
        if os.path.exists(os.path.join(save_feature_folder, patient['full_name'])):
            flush_dir(os.path.join(save_feature_folder, patient['full_name']))
            # shutil.rmtree(os.path.join(save_feature_folder, patient['full_name']))
        else:
            os.mkdir(os.path.join(save_feature_folder, patient['full_name']))
        for i in range(n):
            box = pbb[i].astype('int')[1:]
            margin = 32
            nodule_data_np = img[0, box[0], box[1] - margin:box[1] + margin,
                             box[2] - margin:box[2] + margin]  # 64*64 pix
            cv2.imencode('.png', nodule_data_np)[1].tofile(
                os.path.join(save_feature_folder, patient['full_name'], 'feat_' + str(i) + '.png'))
            # cv2.imwrite(os.path.join(save_feature_folder, patient['full_name'] + '_' + str(i) + '.png'), nodule_data_np)

    ret_result = []
    for i in range(n):
        # print(pbb[i])
        detect_prob = pred_list[i]
        # print(detect_prob)
        box = pbb[i].astype('int')[1:]
        # ax = plt.subplot(1, 1, 1)
        # plt.cla()
        img_data = img[0, box[0]]
        # img_data = setDicomWinWidthWinCenter(img_data, 1400, -400, img_data.shape[0], img_data.shape[1] )
        trans2img(img_data, patient_result_folder + '/result_' + str(i).zfill(zfill_length) + '.png')
        # plt.imshow(img_data, 'gray')
        # rect = patches.Rectangle((box[2] - box[3], box[1] - box[3]), box[3] * 2, box[3] * 2, linewidth=0.5,
        #                          edgecolor='red', facecolor='none')
        # ax.add_patch(rect)
        # plt.axis('off')
        # # fig = plt.gcf()
        # # fig.set_size_inches(3.2 / 3, 2.4 / 3)
        # plt.gca().xaxis.set_major_locator(plt.NullLocator())
        # plt.gca().yaxis.set_major_locator(plt.NullLocator())
        # plt.subplots_adjust(top=1, bottom=0, right=1,
        #                     left=0, hspace=0, wspace=0)
        # plt.margins(0, 0)
        #
        # plt.savefig(patient_result_folder + '/result_' + str(i).zfill(zfill_length) + '.png', format='png',
        #             transparent=True,
        #             dpi=300, pad_inches=0)

        detect_result = {}
        temp = []
        if use_chinese:
            detect_result['检测结果图片'] = 'result_' + str(i) + '.png'
            detect_result['坐标(x,y,z)'] = str(box[2]) + ', ' + str(box[1]) + ', ' + str(box[0])
            detect_result['大小(mm)'] = str(box[3])
            detect_result['预测可能性'] = str(detect_prob)
            detect_result['病人总体概率'] = str(prob_overall)
            detect_result['对应原图位置图片'] = 'origin_' + str(box[0]) + '.png'
            result.append(detect_result)
            temp.append(i + 1)
            temp.append("" + str(box[2]) + "," + str(box[1]) + "," + str(box[0]))
            temp.append(str(box[3]))
            temp.append(str('%.4f' % detect_prob))
            ret_result.append(temp)
        else:
            detect_result['result_picture'] = 'result_' + str(i) + '.png'
            detect_result['coordinate(x,y,z)'] = str(box[2]) + ', ' + str(box[1]) + ', ' + str(box[0])
            detect_result['size(mm)'] = str(box[3])
            detect_result['prob'] = str(detect_prob)
            detect_result['prob_overall'] = str(prob_overall)

            detect_result['origin_picture'] = 'origin_' + str(box[0]) + '.png'
            result.append(detect_result)
            temp.append(i + 1)
            temp.append("" + str(box[2]) + "," + str(box[1]) + "," + str(box[0]))
            temp.append(str(box[3]))
            temp.append(str('%.4f' % detect_prob))
            ret_result.append(temp)
    if use_chinese:
        detect_df = pd.DataFrame(result, columns=['检测结果图片', '坐标(x,y,z)', '大小(mm)', '预测可能性', '病人总体概率', '对应原图位置图片'])
        detect_df.to_csv(patient_window_folder + '/检测结果.csv', index=False, encoding='utf-8-sig')
    else:
        detect_df = pd.DataFrame(result,
                                 columns=['result_picture', 'coordinate(x,y,z)', 'size(mm)', 'prob', 'prob_overall',
                                          'origin_picture'])
        detect_df.to_csv(patient_window_folder + '/detect_result.csv', index=False)

    return n, ret_result


def save_result_web(prob_overall, patient, pred_list, has_info=True, save_origin=False, save_feat=True):
    if save_origin:
        save_origin_web(patient)
    n, result = get_result_web(prob_overall=prob_overall, patient=patient, pred_list=pred_list, save_feat=save_feat,
                               has_info=has_info, use_chinese=False)

    return n, result

