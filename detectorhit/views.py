import base64
import os
import random
import shutil
import string
import zipfile
import pandas as pd

import simplejson
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.forms import model_to_dict
from django.core.paginator import Paginator

from config_global import config_global
# Create your views here.
from detectorhit.models import CT_info
from doctorModule.models import Doctor
from main_local import predict_main


def flush_dir(dirpath):
    for f in os.listdir(dirpath):
        f_path = os.path.join(dirpath, f)
        os.remove(f_path)
    print("flush", dirpath, "complete")


def check_files(file_list):
    ids = []
    is_dcm = False
    for file in file_list:
        if file[-1] == '/':
            continue  # 判断是不是文件夹
        type = os.path.splitext(file)[1]
        if type not in ['', '.dcm']:
            return type + " type file is not supported"
        if type == '.dcm':
            is_dcm = True
        if is_dcm and type != '.dcm':
            return 'DCM file is not correct!'
    return 0

def arrange_dir(dir_path):
    filelist=[]
    subdirlist=[]
    for root, dirs, files in os.walk(dir_path):
        if root==dir_path:
            for dir in dirs:
                subdirlist.append(os.path.join(root, dir))
        for file in files:
            filelist.append(os.path.join(root, file))
    try:
        for file in filelist:
            shutil.move(file, dir_path)
        for dir in subdirlist:
            shutil.rmtree(dir)
    except:
        print("ERROR! arrange dir failed.")
        return -1
    return 0

def object_to_jsob(obj):
    json_dict = model_to_dict(obj)
    return json_dict


def objects_to_json(objs):
    json_list = []
    for obj in objs:
        json_dict = model_to_dict(obj)
        json_list.append(json_dict)
    return json_list


def list_to_json(objs):
    json_list = []
    for obj in objs:
        json_dict = obj
        json_list.append(json_dict)
    return json_list


def bytes_list_to_str(bytesList):
    strList = []
    for index in range(len(bytesList)):
        strList.append(str(bytesList[index], encoding="utf8"))
    return strList


def upload_ct(request):
    response = {}
    if request.method == 'POST':
        file_list = request.FILES.getlist('file')
        if len(file_list) != 1:
            response['msg'] = 'should upload a zip file'
            response['error_num'] = 1
            return JsonResponse(response)
        zip = request.FILES.get('file')
        filename = zip.name
        filename_without_type = os.path.splitext(filename)[0]
        type = os.path.splitext(filename)[1]
        if type == '.zip':
            zip_path = config_global['zipfiles']
            target_path = config_global['extractfiles']

            if config_global['flush_zip']:
                flush_dir(zip_path)
            try:
                file = open(os.path.join(zip_path, filename), 'wb+')
                for chunk in zip.chunks():
                    file.write(chunk)
                file.close()
                print(' write zip file complete')
            except Exception as e:
                response['msg'] = str(e)
                response['error_num'] = 1
                return JsonResponse(response)
            response['data'] = str(filename)
            response['msg'] = 'success'
            response['error_num'] = 0

    return JsonResponse(response)


def extract_ct(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        patient_name = ""
        if 'patient_name' in reqform.keys():
            patient_name = reqform['patient_name']
        filename = reqform['filename']
        doctor_id = reqform['doctorId']
        docname = Doctor.objects.filter(id=doctor_id).values('doc_name').first()['doc_name']
        # uploadtime = datetime.datetime.now()
        uploadtime = timezone.now()
        try:
            if not patient_name:
                ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 5))
                dirname = ran_str + "_" + str(uploadtime.strftime('%Y%m%d-%H%M%S')) + "_" + docname
            else:
                dirname = patient_name + "_" + str(uploadtime.strftime('%Y%m%d-%H%M%S')) + "_" + docname
            if os.path.exists(os.path.join(config_global['extractfiles'], dirname)):
                response['msg'] = 'please wait a moment'
                response['error_num'] = 1
                return JsonResponse(response)
            os.mkdir(os.path.join(config_global['extractfiles'], dirname))
            EXTRACT_DIR = os.path.join(config_global['extractfiles'], dirname)
            fs = zipfile.ZipFile(os.path.join(config_global['zipfiles'], filename), 'r')
            result = check_files(fs.namelist())
            # print('result is:', result)
            if result != 0:
                response['msg'] = result
                response['error_num'] = 1
                return JsonResponse(response)
            for f in fs.namelist():
                fs.extract(f, EXTRACT_DIR)
            arrange_dir(EXTRACT_DIR)
            with transaction.atomic():
                if not patient_name:
                    CT_info.objects.create(file_name=filename, upload_time=uploadtime, doctor_id=doctor_id,
                                           dirname=dirname)
                else:
                    CT_info.objects.create(file_name=filename, upload_time=uploadtime, patient_name=patient_name,
                                           doctor_id=doctor_id, dirname=dirname)
        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 1
            return JsonResponse(response)
        response['msg'] = 'success'
        response['error_num'] = 0
    return JsonResponse(response)


def queryDetectStatus(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        ct_id = reqform['ct_id']
        try:
            ct = CT_info.objects.get(id=ct_id)
            if ct.has_detected == 1:
                response['data'] = 1
                response['error_num'] = 0
                response['msg'] = 'success'
            else:
                response['data'] = 0
                response['error_num'] = 0
                response['msg'] = 'success'
            # return JsonResponse(response)
        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 1
            return JsonResponse(response)
    return JsonResponse(response)


def get_ct_info(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        docId = reqform['doctorId']
        nowPage = reqform['page']
        pageSize = reqform['pageSize'] if reqform['pageSize'] is not None else 8
        cts = CT_info.objects.filter(doctor_id=docId).order_by("-upload_time")
        p = Paginator(cts, pageSize)
        ct_page = p.page(nowPage)
        response['data'] = objects_to_json(ct_page)
        response['total'] = p.count
        response['msg'] = 'success'
        response['error_num'] = 0
    return JsonResponse(response)


def predict_ct(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        skip_prep = False
        ct_id = reqform['ctId']
        filename = reqform['dirname']
        has_info = False
        patient_info = {}
        patient_info['path'] = os.path.join(config_global['extractfiles'], filename)
        # patient_info['path'] = patient_info['path'].replace('\\', '/')
        patient_info['full_name'] = filename
        prob_overall, nod_num, nod_info = predict_main(patient_info, filename, has_info, skip_prep=skip_prep)
        # response_dict = {}
        # response_dict['prob_overall'] = prob_overall
        # response_dict['nod_num'] = nod_num
        # response_dict['nod_info'] = nod_info
        # response['data'] = response_dict
        response['msg'] = 'success'
        response['error_num'] = 0
        CT_info.objects.filter(id=ct_id).update(has_detected=1)
    return JsonResponse(response)


def get_origin_imgs(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        filename = reqform['dirname']

        origin_path = os.path.join(config_global['save_result_no_info_folder'], filename, 'origin')
        img_list = []
        for f in sorted(os.listdir(origin_path)):
            img_list.append(os.path.join(origin_path, f))
        if len(img_list) == 0:
            response['msg'] = 'plt raw images error'
            response['error_num'] = 1
            return JsonResponse(response)
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
    return JsonResponse(response)


def get_result_imgs(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        filename = reqform['dirname']

        result_path = os.path.join(config_global['save_result_no_info_folder'], filename, 'result')
        img_list = []
        for f in os.listdir(result_path):
            img_list.append(os.path.join(result_path, f))
        if len(img_list) == 0:
            response['msg'] = 'get result images error'
            response['error_num'] = 1
            return JsonResponse(response)
        responseList = []
        for img_path in img_list:
            with open(img_path, 'rb') as f:
                img_data = f.read()
                img_data = base64.b64encode(img_data)
                f.close()
            responseList.append(img_data)
        response['msg'] = 'success'
        response['error_num'] = 0

        resultcsv = pd.read_csv(
            os.path.join(config_global['save_result_no_info_folder'], filename, "detect_result.csv"))
        pos_list = resultcsv['prob'].values.tolist()
        coord_list = resultcsv['coordinate(x,y,z)'].values.tolist()
        size_list = resultcsv['size(mm)'].values.tolist()
        prob_overall = resultcsv['prob_overall'].values.tolist()[0]
        response['data'] = [bytes_list_to_str(responseList), pos_list, coord_list, size_list, prob_overall]
    return JsonResponse(response, safe=False)
