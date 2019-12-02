import os
import random
import string
import zipfile

import simplejson
from django.db import transaction
from django.forms import model_to_dict
from django.http import JsonResponse
from django.utils import timezone

from config_livePredict import config_livePredict
from detectorhit.views import check_files
from doctorModule.models import Doctor
from livePredict_func import view_single

# Create your views here.
from detectorhit.models import CT_info
from livePredict.models import pet_result

def objects_to_json(objs):
    json_list = []
    for obj in objs:
        json_dict = model_to_dict(obj)
        json_list.append(json_dict)
    return json_list

def flush_dir(dirpath):
    for f in os.listdir(dirpath):
        f_path = os.path.join(dirpath, f)
        os.remove(f_path)
    print("flush", dirpath, "complete")

def check_files_pet(file_list):
    ids = []
    for file in file_list:
        type = os.path.splitext(file)[1]
        if type not in ['']:
            return type + " type file is not supported currently"

    return 0

def upload_pet(request):
    response = {}
    if request.method == 'POST':
        file_list = request.FILES.getlist('file')
        if len(file_list) != 1:  # TODO: 检验是否是压缩包文件
            response['msg'] = 'should upload a zip file'
            response['error_num'] = 1
            return JsonResponse(response)
        zip = request.FILES.get('file')
        filename = zip.name
        filename_without_type = os.path.splitext(filename)[0]
        type = os.path.splitext(filename)[1]
        if type == '.zip':
            zip_path = config_livePredict['zipfiles']
            target_path = config_livePredict['extractfiles']

            if config_livePredict['flush_zip']:
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


def extract_pet(request):

    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        patient_name = ""
        if 'patient_name' in reqform.keys():
            patient_name = reqform['patient_name']
        filename = reqform['filename']
        doctor_id = reqform['doctorId']
        specify_id = None
        if 'specify_id' in reqform.keys():
            specify_id = reqform['specify_id']
        docname = Doctor.objects.filter(id=doctor_id).values('doc_name').first()['doc_name']
        # uploadtime = datetime.datetime.now()
        uploadtime = timezone.now()
        try:
            if not patient_name:
                ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 5))
                dirname = ran_str + "_" + str(uploadtime.strftime('%Y%m%d-%H%M%S')) + "_" + docname
            else:
                dirname = patient_name + "_" + str(uploadtime.strftime('%Y%m%d-%H%M%S')) + "_" + docname
            if os.path.exists(os.path.join(config_livePredict['extractfiles'], dirname)):
                response['msg'] = 'please wait a moment and try again'
                response['error_num'] = 1
                return JsonResponse(response)
            os.mkdir(os.path.join(config_livePredict['extractfiles'], dirname))
            fs = zipfile.ZipFile(os.path.join(config_livePredict['zipfiles'], filename), 'r')
            result = check_files_pet(fs.namelist())
            # print('result is:', result)
            if result != 0:
                response['msg'] = result
                response['error_num'] = 1
                return JsonResponse(response)
            for f in fs.namelist():
                fs.extract(f, os.path.join(config_livePredict['extractfiles'], dirname))
            with transaction.atomic():
                # pet_path = os.path.join(config_livePredict['extractfiles'], dirname)
                if not patient_name:
                    info = CT_info.objects.create(file_name=filename, upload_time=uploadtime, doctor_id=doctor_id,
                                           dirname=dirname, is_pet=True)
                else:
                    info = CT_info.objects.create(file_name=filename, upload_time=uploadtime, patient_name=patient_name,
                                           doctor_id=doctor_id, dirname=dirname,is_pet=True)
                if specify_id:
                    info.specify_id = specify_id
                    info.save()

        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 1
            return JsonResponse(response)
        response['msg'] = 'success'
        response['error_num'] = 0
    return JsonResponse(response)


def predict(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        pet_id = reqform['pet_id']
        if 'specify_id' in reqform.keys():
            specify_id = reqform['specify_id']
        else:
            specify_id = CT_info.objects.get(id=pet_id).specify_id
        file_path = CT_info.objects.get(id=pet_id).dirname
        date_out, live_out = view_single(file_path, specify_id)
        # print("DEBUG date, live:",date_out, live_out)
        response['data'] = [float('%.2f' % date_out), float('%.2f' % live_out)]
        response['error_num'] = 0
        response['msg'] = 'success'
        # todo: save pet info into database
        with transaction.atomic():
            pet_result.objects.create(pet_id=pet_id, date=date_out, live=live_out)
            info = CT_info.objects.get(id=pet_id)
            info.has_detected=1
            info.save()
    return JsonResponse(response)


def get_predict_result_by_PID(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        pet_id = reqform['pet_id']
        result = pet_result.objects.get(pet_id=pet_id)
        if result:
            date_res = result.date
            live_res = result.live
            response['data'] = [float('%.2f' % date_res), float('%.2f' % live_res)]
        response['error_num'] = 0
        response['msg'] = 'success'
    return JsonResponse(response)
