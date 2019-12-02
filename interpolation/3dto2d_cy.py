# coding=utf-8
import os
import SimpleITK as sitk
import matplotlib.pyplot as plt
import csv
import numpy as np
import cv2
import shutil
import random
import pydicom
import pydicom.uid
import sys
import PIL.Image as Image
import gdcm


def get_pixarray(dicom_dataset):
    pixel_array = dicom_dataset.pixel_array
    pixel_array = pixel_array * dicom_dataset.RescaleSlope + dicom_dataset.RescaleIntercept  # 获得图像的CT值
    pixel_array = pixel_array.reshape(dicom_dataset.Rows, dicom_dataset.Columns)
    return pixel_array, dicom_dataset.Rows, dicom_dataset.Columns


# 调整CT图像的窗宽窗位
def setDicomWinWidthWinCenter(img_data, winwidth, wincenter, rows, cols):
    # CT检查肺窗的窗宽和窗位分别是W1350～1500，C - 500～-350。
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


# 加载Dicom图片中的Tag信息
def loadFileInformation(filename):
    information = {}
    ds = pydicom.read_file(filename)
    information['PatientID'] = ds.PatientID
    information['PatientName'] = ds.PatientName
    information['PatientBirthDate'] = ds.PatientBirthDate
    information['PatientSex'] = ds.PatientSex
    information['StudyID'] = ds.StudyID
    information['StudyDate'] = ds.StudyDate
    information['StudyTime'] = ds.StudyTime
    information['InstitutionName'] = ds.InstitutionName
    information['Manufacturer'] = ds.Manufacturer
    print(dir(ds))
    print(type(information))
    return information


def trans2img(img_data, save_path):
    # dcm = pydicom.dcmread(filename)  # 加载Dicom数据
    dcm_img = Image.fromarray(img_data)  # 将Numpy转换为PIL.Image
    dcm_img = dcm_img.convert('L')

    # 保存为jpg文件，用作后面的生成label用
    dcm_img.save(save_path)
    # 显示图像
    # dcm_img.show()


def test_trans():
    workspace_path = "/home/cuiyang/workspace"
    image_root = workspace_path + "/lung_cancer/ct_flow02_new/ct_data/"
    out_path = workspace_path + '/lung_cancer/ct_flow02_new/ct_data_png/'
    pic_folder_list = sorted(os.listdir(image_root))
    print(pic_folder_list)
    folder_num = len(pic_folder_list)
    for name in pic_folder_list:
        if os.path.exists(os.path.join(out_path, name)):
            shutil.rmtree(os.path.join(out_path, name))
        os.makedirs(os.path.join(out_path, name))

    for folder in pic_folder_list:
        file_name_list = os.listdir(image_root + folder)
        file_name_list = sorted(file_name_list)
        for index, file_name in enumerate(file_name_list):
            dcmpath = os.path.join(image_root, folder, file_name)
            img_array, rows, cols = get_pixarray(pydicom.dcmread(dcmpath))
            img_array = setDicomWinWidthWinCenter(img_array, 1400, -400, rows, cols)
            save_path = os.path.join(out_path, folder, "origin_" + str(index).zfill(3) + ".png")
            trans2img(img_array, save_path)

            print("row, col: ", rows, cols)
    print("complete.")


if __name__ == '__main__':
    test_trans()
    # image_root = "D:/lung_cancer/ct_flow02/ct_data/"
    # out_path = 'D:/lung_cancer/ct_flow02/ct_data_png/'
    # if os.path.exists(out_path):
    #     shutil.rmtree(out_path)
    # os.makedirs(out_path)
    #
    # pic_folder_list = sorted(os.listdir(image_root))
    # print(pic_folder_list)
    # folder_num = len(pic_folder_list)
    # for name in pic_folder_list:
    #     os.makedirs(os.path.join(out_path, name))
    #
    # save_num = 0
    #
    # for folder in pic_folder_list:
    #     file_name_list = os.listdir(image_root + folder)
    #     file_name_list = sorted(file_name_list)
    #     for file_name in file_name_list:
    #         if '.mhd' in file_name:
    #             mhd_path = image_root + folder + '/' + file_name
    #             print(save_num, mhd_path)
    #             itkimage = sitk.ReadImage(mhd_path)
    #             numpyImage = sitk.GetArrayFromImage(itkimage)
    #
    #             numpyImage = np.maximum(numpyImage, -1000)
    #             numpyImage = np.minimum(numpyImage, 500)
    #             numpyImage = (numpyImage + 1000) / 1500. * 255.
    #
    #             slice_num = numpyImage.shape[0]
    #
    #             out_folder = out_path + '/' + str(save_num) + '/'
    #             if not os.path.exists(out_folder):
    #                 os.makedirs(out_folder)
    #             save_num += 1
    #
    #             for b in range(slice_num):
    #                 slice_one = numpyImage[b, :, :]
    #                 cv2.imwrite(out_folder + str(b + 1000) + '.jpg', slice_one)
