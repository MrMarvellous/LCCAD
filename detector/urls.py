from django.conf.urls import url, include

from detector import views

urlpatterns = [
    url(r'^addPatientFile/$', views.add_patient_file, name='addPatientFile'),
    url(r'^splitPatientRawFile/$', views.splite_raw_img, name='splitPatientRawFile'),
    url(r'^detectPatientNodule/$', views.detect_CT, name='detectPatientNodule'),  # not used too
    url(r'^addCTInfo/$', views.save_ct_info, name='addCTInfo'),
    url(r'^deleteCTInfo/$', views.delete_ct_info, name='addCTInfo'),
    url(r'^getCTByPatient/$', views.get_cts_by_patient, name='getCTByPatient'),
    url(r'^image/getAllImage/$', views.get_img_response, name='getAllImage'),
    url(r'^image/getAIPredict/$', views.get_predict_result, name='getAIPredict'),
    url(r'^image/getImageByIndexList/$', views.get_img_by_index_list, name='getImageByIndexList'),


]
