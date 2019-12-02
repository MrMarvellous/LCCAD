import base64

import simplejson
import os
from django.http import JsonResponse
from django.shortcuts import render
from config_interpolation import config_interpolation
from detectorhit.models import CT_info
from interpolation_func import view_inter


# Create your views here.

def bytes_list_to_str(bytesList):
    strList = []
    for index in range(len(bytesList)):
        strList.append(str(bytesList[index], encoding="utf8"))
    return strList


def queryInterStatus(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        ct_id = reqform['ct_id']
        try:
            ct = CT_info.objects.get(id=ct_id)
            if ct.has_intered == 1:
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

def interpolate(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        dirname=reqform['dirname']
        ct_id=reqform['ct_id']
        try:
            ct = CT_info.objects.get(id=ct_id)
            if ct.has_intered==0:
                view_inter(dirname)
                ct.has_intered=1
                ct.save()
            else:
                print('this ct has intered.')
        except Exception as e:
            response['msg'] = str(e)
            response['error_num'] = 1
            return JsonResponse(response)
        response['error_num'] = 0
        response['msg'] = 'success'
    return JsonResponse(response)


def get_inter_imgs(request):
    response = {}
    if request.method == 'POST':
        reqform = simplejson.loads(request.body)
        filename = reqform['dirname']

        pic_path = os.path.join(config_interpolation['out_path'], filename)
        img_list = []
        for f in sorted(os.listdir(pic_path)):
            print('listdir', f)
            if "flow" in f:
                continue
            img_list.append(os.path.join(pic_path, f))
        if len(img_list) == 0:
            response['msg'] = 'plt inter images error'
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
        print('len inter list', len(responseList))
    return JsonResponse(response)
