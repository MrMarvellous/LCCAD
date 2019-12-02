import base64

import simplejson
import os
from django.http import JsonResponse
from django.shortcuts import render

from config_tracer import config_tracer
from tracer_func import view_new, view_single


# Create your views here.


def cover(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        patientname = reqform['patientname']
        view_new(patientname, patientname)
        response['error_num'] = 0
        response['msg'] = 'success'
    return JsonResponse(response)


def getCoverResultById(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        patient_name = reqform['patientName']
        img_index = reqform['index']
        img_path = os.path.join(config_tracer['output_path'], patient_name)
        origin_path = os.path.join(img_path, str(img_index) + "_origin.jpg")
        overlay_path = os.path.join(img_path, str(img_index) + "_overlay.jpg")
        response_data = []
        with open(origin_path, 'rb') as f:
            origin_data = f.read()
            origin_data = base64.b64encode(origin_data)
            f.close()
        response_data.append(origin_data)
        with open(overlay_path, 'rb') as f:
            overlay_data = f.read()
            overlay_data = base64.b64encode(overlay_data)
            f.close()
        response_data.append(overlay_data)
        response['data'] = bytes_list_to_str(response_data)
        response['error_num'] = 0
        response['msg'] = 'success'
    return JsonResponse(response)


def bytes_list_to_str(bytesList):
    strList = []
    for index in range(len(bytesList)):
        strList.append(str(bytesList[index], encoding="utf8"))
    return strList
