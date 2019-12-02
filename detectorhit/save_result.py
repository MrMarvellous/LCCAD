import os
import shutil
import warnings

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cv2

from config_global import config_global
from full_prep import candidates_list

# import random
# import cv2
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


def get_result(patient):
    result = []
    # pbb_path = './bbox_result/' + patient + '_pbb.npy'
    pbb_path = './new_bbox_result/' + patient['full_name'] + '_pbb.npy'
    if not os.path.exists(pbb_path):
        return -1, result, -1, -1
    pbb = np.load(pbb_path)
    pbb = pbb[pbb[:, 0] > -1]
    pbb = nms(pbb, 0.05)  # 输出的第一个是label表明是否为正样本后面4列数据为bbox的值 z x y radius
    # img_path = './lungSeg/' + patient + '_clean.npy'
    img_path = './new_data/' + patient['full_name'] + '_clean.npy'
    img = np.load(img_path)

    df = pd.read_csv('cls_new.csv')

    cls_result = df[df['id'] == patient]
    prob = list(cls_result['cancer'])
    prob = prob[0]
    if prob < 0.5:
        kind = 'benign'  # '良性'
    else:
        kind = 'malignant'  # 恶性'
    # print('DEBUG kind: ',kind)
    n = len(pbb)
    # print('DEBUG n: ', len(pbb))
    save_result_folder = './static/result_new/'
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
    # patient_folder = save_result_folder + patient['name']+'/'+patient['date']+'/'+patient['window']
    for i in range(n):
        temp = []
        box = pbb[i].astype('int')[1:]
        # print('DEBUG box: ', box)
        # print('DEBUG pbb: ', pbb[i], 'i: ', i)
        ax = plt.subplot(1, 1, 1)
        plt.cla()
        plt.imshow(img[0, box[0]], 'gray')
        # plt.axis('off')
        # fig = plt.gcf()
        # fig.set_size_inches(3.2 / 3, 2.4 / 3)
        # plt.gca().xaxis.set_major_locator(plt.NullLocator())
        # plt.gca().yaxis.set_major_locator(plt.NullLocator())
        # plt.subplots_adjust(top=1, bottom=0, right=1,
        #                     left=0, hspace=0, wspace=0)
        # plt.margins(0, 0)

        plt.savefig(patient_origin_folder + '/origin_' + str(i) + '.png', format='png', transparent=True,
                    dpi=300, pad_inches=0)
        rect = patches.Rectangle((box[2] - box[3], box[1] - box[3]), box[3] * 2, box[3] * 2, linewidth=0.5,
                                 edgecolor='red', facecolor='none')
        ax.add_patch(rect)
        pos = (box[2] + box[3], box[1] + box[3])
        text_pos = (box[2] + box[3] + 40, box[1] + box[3] + 50)
        # plt.annotate('result is {0}\n coord is{1}'.format(kind,(box[2],box[1],box[0])),xy=pos,xytext=text_pos,fontsize=8,arrowprops=dict(facecolor='white',shrink=0.05))
        plt.title(u'patient result is {0}\n coord is{1}'.format(kind, (box[2], box[1], box[0])))
        # fig = plt.gcf()
        # fig.set_size_inches(3.2 / 3, 2.4 / 3)
        # plt.gca().xaxis.set_major_locator(plt.NullLocator())
        # plt.gca().yaxis.set_major_locator(plt.NullLocator())
        # plt.subplots_adjust(top=1, bottom=0, right=1,
        #                     left=0, hspace=0, wspace=0)
        # plt.margins(0, 0)
        plt.savefig(patient_result_folder + '/result_' + str(i) + '.png', format='png', transparent=True,
                    dpi=300, pad_inches=0)
        temp.append(i + 1)
        temp.append((box[2], box[1], box[0]))
        temp.append(box[3])
        result.append(temp)
    return n, result, kind, prob


def get_result_1(patient):  # 需要改路径
    result = []
    pbb_path = './bbox_result/' + patient + '_pbb.npy'
    if not os.path.exists(pbb_path):
        return -1, result, -1, -1
    pbb = np.load(pbb_path)
    pbb = pbb[pbb[:, 0] > -1]
    pbb = nms(pbb, 0.05)  # 输出的第一个是label表明是否为正样本后面4列数据为bbox的值 z x y radius
    img_path = './lungSeg/' + patient + '_clean.npy'
    img = np.load(img_path)
    df = pd.read_csv('cls.csv')
    cls_result = df[df['id'] == int(patient)]
    prob = list(cls_result['cancer'])
    prob = prob[0]
    if prob < 0.5:
        kind = '良性'
    else:
        kind = '恶性'
    n = len(pbb)
    for i in range(n):
        temp = []
        box = pbb[i].astype('int')[1:]
        temp.append(i + 1)
        temp.append("" + str(box[2]) + "," + str(box[1]) + "," + str(box[0]))
        temp.append(box[3])
        result.append(temp)
    return n, result, kind, prob  # n 多少个 result 坐标 半径 kind 良性 prob 概率


def get_result_new(patient, use_chinese=True):
    save_result_folder = './static/result_new/'
    save_feature_folder = './new_result_for_feat/'
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
    result = []
    pbb_path = './new_bbox_result/' + patient['full_name'] + '_pbb.npy'
    if not os.path.exists(pbb_path):
        return -1, result, -1, -1
    pbb = np.load(pbb_path)
    pbb = pbb[pbb[:, 0] > -1]
    pbb = nms(pbb, 0.05)  # 输出的第一个是label表明是否为正样本后面4列数据为bbox的值 z x y radius
    img_path = './new_data/' + patient['full_name'] + '_clean.npy'
    img = np.load(img_path)
    df = pd.read_csv('cls_new.csv')
    cls_result = df[df['id'] == patient['full_name']]
    prob = list(cls_result['cancer'])
    prob = prob[0]
    if prob < 0.5:
        if use_chinese:
            kind = '良性'
        else:
            kind = 'benign'
    else:
        if use_chinese:
            kind = '恶性'
        else:
            kind = 'malignant'
    n = len(pbb)
    # write csv files
    if use_chinese:
        patient_window_zh = '错误'
        if patient['window'] == 'feichuang':
            patient_window_zh = '肺窗'
        elif patient['window'] == 'conggechuang':
            patient_window_zh = '纵隔窗'
        pred_result = [
            {'病人姓名': patient['name'], '拍摄CT时间': patient['date'], '窗': patient_window_zh, '预测结果': kind,
             '预测是恶性肿瘤的可能性': prob}]
        pred_df = pd.DataFrame(pred_result, columns=['病人姓名', '拍摄CT时间', '窗', '预测结果', '预测是恶性肿瘤的可能性'])
        pred_df.to_csv(patient_window_folder + '/预测结果.csv', index=False, encoding='utf-8-sig')
    else:
        pred_result = [{'patient name': patient['name'], 'date': patient['date'], 'window': patient['window'],
                        'predict result': kind, 'probability': prob}]
        pred_df = pd.DataFrame(pred_result, columns=['patient name', 'date', 'window', 'predict result', 'probability'])
        pred_df.to_csv(patient_window_folder + '/predict_result.csv', index=False, encoding='utf-8-sig')

    # write imgs only has predicted nodules
    for i in range(n):
        box = pbb[i].astype('int')[1:]
        margin = 32
        nodule_data_np = img[0, box[0], box[1] - margin:box[1] + margin, box[2] - margin:box[2] + margin]  # 64*64 pix
        cv2.imwrite(save_feature_folder + patient['full_name'] + '_' + str(i) + '.png', nodule_data_np)

    single_prob_df = pd.read_csv('cls_single.csv')
    single_prob_df = single_prob_df[single_prob_df['patient_id'] == patient['full_name']]
    for i in range(n):
        print(pbb[i])
        detect_prob = single_prob_df[single_prob_df['pbb_id'] == i]['malignant_probability'].tolist()[0]
        print(detect_prob)
        box = pbb[i].astype('int')[1:]
        ax = plt.subplot(1, 1, 1)
        plt.cla()
        plt.imshow(img[0, box[0]], 'gray')
        rect = patches.Rectangle((box[2] - box[3], box[1] - box[3]), box[3] * 2, box[3] * 2, linewidth=0.5,
                                 edgecolor='red', facecolor='none')
        ax.add_patch(rect)
        plt.title('detect probability:' + str(detect_prob) + '\nsize:' + str(box[3]) + 'mm', loc='right')
        plt.savefig(patient_result_folder + '/result_' + str(i) + '.png', format='png', transparent=True,
                    dpi=300, pad_inches=0)
        detect_result = {}
        if use_chinese:
            detect_result['检测结果图片'] = 'result_' + str(i) + '.png'
            detect_result['坐标（x,y,z）'] = '(' + str(box[2]) + ', ' + str(box[1]) + ', ' + str(box[0]) + ')'
            detect_result['大小(mm)'] = str(box[3])
            detect_result['预测可能性'] = str(detect_prob)
            detect_result['对应原图位置图片'] = 'origin_' + str(box[0]) + '.png'
            result.append(detect_result)
        else:
            detect_result['result picture'] = 'result_' + str(i) + '.png'
            detect_result['coordinate（x,y,z）'] = '(' + str(box[2]) + ', ' + str(box[1]) + ', ' + str(box[0]) + ')'
            detect_result['size(mm)'] = str(box[3])
            detect_result['prob'] = str(detect_prob)
            detect_result['origin picture'] = 'origin_' + str(box[0]) + '.png'
            result.append(detect_result)
    if use_chinese:
        detect_df = pd.DataFrame(result, columns=['检测结果图片', '坐标（x,y,z）', '大小(mm)', '预测可能性', '对应原图位置图片'])
        detect_df.to_csv(patient_window_folder + '/检测结果.csv', index=False, encoding='utf-8-sig')
    else:
        detect_df = pd.DataFrame(result,
                                 columns=['result picture', 'coordinate（x,y,z）', 'size(mm)', 'prob', 'origin picture'])
        detect_df.to_csv(patient_window_folder + '/detect_result.csv', index=False, encoding='utf-8-sig')

    return n, result, kind, prob


def get_origin_new(patient):
    save_result_folder = './static/result_new/'
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

    img_path = './new_data/' + patient['full_name'] + '_clean.npy'
    img = np.load(img_path)
    n = img.shape[1]
    for i in range(n):
        plt.cla()
        plt.imshow(img[0, i], 'gray')
        plt.savefig(patient_origin_folder + '/origin_' + str(i) + '.png', format='png', transparent=True,
                    dpi=300, pad_inches=0)

    return n


def save_result_main():
    all_data_path = '/home/guanzhilin/app/hit_lung_data'
    patient_list = candidates_list(all_data_path)
    for patient in patient_list:
        get_result_new(patient)
        # get_origin_new(patient)

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


def save_origin_web(patient, has_info):
    patient_window_folder = os.path.join(config_global['save_result_no_info_folder'], patient['full_name'])
    if not os.path.exists(patient_window_folder):
        os.makedirs(patient_window_folder)
    patient_origin_folder = os.path.join(patient_window_folder, 'origin')
    if not os.path.exists(patient_origin_folder):
        os.mkdir(patient_origin_folder)
    patient_result_folder = os.path.join(patient_window_folder, 'result')
    if not os.path.exists(patient_result_folder):
        os.mkdir(patient_result_folder)

    img_path = os.path.join(config_global['preprocess_result_path'], patient['full_name'] + '_clean.npy')
    if not has_info:
        img_path = os.path.join(config_global['preprocess_result_path_no_info'], patient['full_name'] + '_clean.npy')
    img = np.load(img_path)
    n = img.shape[1]
    img_list = os.listdir(patient_origin_folder)
    if len(img_list) == n:
        return 0
    for i in range(n):
        ax = plt.subplot(1, 1, 1)
        plt.cla()
        img_data = img[0,i]
        img_data = setDicomWinWidthWinCenter(img_data, 1400, -400, img_data.shape[0], img_data.shape[1])
        plt.imshow(img_data, 'gray')
        plt.axis('off')
        fig = plt.gcf()
        fig.set_size_inches(3.2 / 3, 2.4 / 3)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1, bottom=0, right=1,
                            left=0, hspace=0, wspace=0)
        plt.margins(0, 0)

        plt.savefig(patient_origin_folder + '/origin_' + str(i).zfill(3) + '.png', format='png',
                    transparent=True,
                    dpi=300, pad_inches=0)
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
        ax = plt.subplot(1, 1, 1)
        plt.cla()
        plt.imshow(img[0, box[0]], 'gray')
        rect = patches.Rectangle((box[2] - box[3], box[1] - box[3]), box[3] * 2, box[3] * 2, linewidth=0.5,
                                 edgecolor='red', facecolor='none')
        ax.add_patch(rect)
        plt.axis('off')
        # fig = plt.gcf()
        # fig.set_size_inches(3.2 / 3, 2.4 / 3)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1, bottom=0, right=1,
                            left=0, hspace=0, wspace=0)
        plt.margins(0, 0)

        plt.savefig(patient_result_folder + '/result_' + str(i).zfill(zfill_length) + '.png', format='png',
                    transparent=True,
                    dpi=300, pad_inches=0)

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


def save_result_web(prob_overall, patient, pred_list, has_info=True, save_origin=True, save_feat=True):
    if save_origin:
        save_origin_web(patient, has_info)
    n, result = get_result_web(prob_overall=prob_overall, patient=patient, pred_list=pred_list, save_feat=save_feat,
                               has_info=has_info, use_chinese=False)

    return n, result


if __name__ == '__main__':
    save_result_main()
