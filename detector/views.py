import base64
import datetime
import os
import zipfile

import simplejson
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse

import pandas as pd
import sys
sys.path.append('D:/lung_cancer/LCCAD/detector/')

# Create your views here.
from django.utils import timezone

from detect_main import detect_service, plt_raw
from detector.models import CT
from preprocess import preprocess

PATIENT_IMGS_PATH = "D:/workspace/python/LCCAD/detector/patient_imgs/"
local_path = "D:/workspace/python/LCCAD/detector/"


def flush_dir(dirpath):
    for f in os.listdir(dirpath):
        f_path = os.path.join(dirpath, f)
        os.remove(f_path)
    print("flush", dirpath, "complete")


def check_files(file_list):
    ids = []
    for file in file_list:
        id = os.path.splitext(file)[0]
        ids.append(id)
    if ids[0] != ids[1]:
        return "file is incorrect"
    for file in file_list:
        type = os.path.splitext(file)[1]
        if type not in ['.mhd', '.raw', '.zraw']:
            return type + " is not supported"
    return 0


def add_patient_file(request):
    response = {}
    if request.method == 'POST':
        # reqform = simplejson.loads(request.body)
        # 解压缩文件
        file_list = request.FILES.getlist('file')
        if len(file_list) == 1:
            zip = request.FILES.get('file')
            filename = zip.name
            filename_without_type = os.path.splitext(filename)[0]
            type = os.path.splitext(filename)[1]
            if type == '.zip':
                zip_path = 'D:/workspace/python/LCCAD/detector/zipfiles/'
                target_path = 'D:/workspace/python/LCCAD/detector/files/'

                flush_dir(zip_path)

                file = open(zip_path + filename, 'wb+')
                for chunk in zip.chunks():
                    file.write(chunk)
                fs = zipfile.ZipFile(zip_path + filename, 'r')

                result = check_files(fs.namelist())
                if result != 0:
                    response['msg'] = result
                    response['error_num'] = 1
                    return JsonResponse(response)
                for f in fs.namelist():
                    fs.extract(f, target_path)
                file.close()
            else:
                response['msg'] = 'only support zip file now'
                response['error_num'] = 1
                return JsonResponse(response)
        elif len(file_list) == 2:
            filenamelist = []
            for f in file_list:
                filename_without_type = os.path.splitext(f)[0]
                filenamelist.append(f.name)
            result = check_files(filenamelist)
            if result != 0:
                response['msg'] = result
                response['error_num'] = 1
                return JsonResponse(response)
            for file in file_list:
                target_path = 'D:/workspace/python/LCCAD/detector/files/'
                f = open(target_path + file.name, 'wb+')
                for chunk in file.chunks():
                    f.write(chunk)
                f.close()

    return JsonResponse(response)


def save_ct_info(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        # 存储CT信息
        patient_id = reqform['patient_id']
        filename_without_type = reqform['filename']
        target_path = 'D:/workspace/python/LCCAD/detector/files/'
        try:
            newCT = CT(patient_id=patient_id, ct_name=filename_without_type,
                       ct_path=target_path + filename_without_type + '.mhd', upload_time=timezone.now())
            newCT.save()
            response['msg'] = 'success'
            response['data'] = objects_to_json([newCT,])[0]
            response['error_num'] = 0
            return JsonResponse(response)
        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 1
            return JsonResponse(response)
    return JsonResponse(response)


def delete_ct_info(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        ct_id = reqform['ct_id']
        try:
            CT.objects.filter(id=ct_id).delete()
            response['msg'] = 'success'
            response['error_num'] = 0
            return JsonResponse(response)
        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 1
            return JsonResponse(response)

    return JsonResponse(response)


def get_cts_by_patient(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        patient_id = reqform['patient_id']
        ctName = reqform['ct_name']
        cts = CT.objects.filter(patient_id=patient_id, ct_name=ctName).order_by('-upload_time')
        response['msg'] = 'success'
        response['error_num'] = 0
        if len(cts) >= 1:
            response['total'] = 1
            response['data'] = objects_to_json([cts[0],])
        else:
            response['total'] = 0
            response['data'] = objects_to_json(cts)

    return JsonResponse(response)


def get_img_response(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)

        if 'name' not in reqform.keys():
            response['msg'] = 'blank'
            response['error_num'] = 0
            return JsonResponse(response)

        # try:
        img_name = reqform['name']
        img_path = os.path.join(PATIENT_IMGS_PATH, img_name) + "/"
        if not os.path.exists(img_path):
            os.makedirs(img_path)
        img_list = os.listdir(img_path)
        if len(img_list) == 0:
            islabel = False
            if 'islabel' in reqform.keys():
                islabel = reqform['islabel']
            try:
                preprocess(img_name, islabel)
                plt_raw(img_name)
                img_list = os.listdir(img_path)
            except Exception as e:
                response['msg'] = str(e)
                response['error_num'] = 1
                return JsonResponse(response)
        for id in range(len(img_list)):
            img_list[id] = img_path + img_list[id]
        responseList = []
        for img_path in img_list:
            with open(img_path, 'rb') as f:
                img_data = f.read()
                img_data = base64.b64encode(img_data)
                f.close()
            responseList.append(img_data)
        response['msg'] = 'success'
        response['error_num'] = 0
        response['data'] = bytes_list_to_str(responseList)
    return JsonResponse(response, safe=False)
    # except Exception as e:
    #     response['msg']=str(e)
    #     response['error_num']=1
    #     return JsonResponse(response, safe=False)

def get_img_by_index_list(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        ct_name = reqform['ct_name']
        img_list = reqform['img_list']
        # img_list = img_str.strip('[').strip(']').split(',')
        # new_list = []
        # for index in img_list:
        #     index = index.strip()
        #     new_list.append(index)
        try:
            img_data_list = get_index_img(ct_name=ct_name,index_list=img_list)
        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 1
            return JsonResponse(response)
        response['msg']='success'
        response['error_num']=0
        response['data']=bytes_list_to_str(img_data_list)

    return JsonResponse(response)



def get_predict_result(request):  # replace detect_ct function
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        patient_name = reqform['name']
        islabel = False
        if 'islabel' in reqform.keys():
            islabel = reqform['islabel']

        # now has detected images
        result_patient_path = local_path + "result_imgs/" + patient_name + "/"
        if not os.path.exists(result_patient_path):
            os.makedirs(result_patient_path)
        result_img_path = local_path + "result_imgs/" + patient_name + "/predicts/"
        if not os.path.exists(result_img_path):
            os.makedirs(result_img_path)
        result_img_list = os.listdir(result_img_path)
        print("len predict list: ", len(result_img_list))
        if len(result_img_list) == 0:
            try:
                detect_service(patient_name, islabel)
            except Exception as e:
                response['msg'] = str(e)
                response['error_num'] = 1
                return JsonResponse(response, safe=False)
        result_img_list = os.listdir(result_img_path)
        for id in range(len(result_img_list)):
            result_img_list[id] = result_img_path + result_img_list[id]
        responseList = []
        for img_path in result_img_list:
            with open(img_path, 'rb') as f:
                img_data = f.read()
                img_data = base64.b64encode(img_data)
            responseList.append(img_data)
        response['msg'] = 'success'
        response['error_num'] = 0
        # data [imgs,pos,z,x,y,size]
        resultcsv = pd.read_csv(result_patient_path+"predictResult.csv")
        pos_list = resultcsv['possibility'].values.tolist()
        z_list = resultcsv['z'].values.tolist()
        x_list = resultcsv['x'].values.tolist()
        y_list = resultcsv['y'].values.tolist()
        size_list = resultcsv['size'].values.tolist()
        response['data'] = [bytes_list_to_str(responseList),pos_list,z_list,x_list,y_list,size_list]
    return JsonResponse(response, safe=False)





def splite_raw_img(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        patient_name = reqform['name']
        islabel = False
        if 'islabel' in reqform.keys():
            islabel = reqform['islabel']
        try:
            preprocess(patient_name, islabel)
            plt_raw(patient_name)
        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 1
            return JsonResponse(response)
        response['msg'] = 'success'
        response['error_num'] = 0
    return JsonResponse(response)


def detect_CT(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        patient_name = reqform['name']
        islabel = False
        if 'islabel' in reqform.keys():
            islabel = reqform['islabel']
        try:
            detect_service(patient_name, islabel)
        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 1
            return JsonResponse(response)
        response['msg'] = 'success'
        response['error_num'] = 0
    return JsonResponse(response, safe=False)


def get_index_img(ct_name,index_list):
    img_path = os.path.join(PATIENT_IMGS_PATH, ct_name) + "/"
    img_list = os.listdir(img_path)
    ret_list = []
    for index in index_list:
        if index == '':
            break
        index_str = 'img'+str(index).zfill(3)+'.jpg'
        if index_str in img_list:
            index_path = img_path+index_str
            with open(index_path, 'rb') as f:
                img_data = f.read()
                img_data = base64.b64encode(img_data)
                f.close()
                ret_list.append(img_data)
    return ret_list



def objects_to_json(objs):
    json_list = []
    for obj in objs:
        json_dict = model_to_dict(obj)
        json_list.append(json_dict)
    return json_list


def bytes_list_to_str(bytesList):
    strList = []
    for index in range(len(bytesList)):
        strList.append(str(bytesList[index], encoding="utf8"))
    return strList
