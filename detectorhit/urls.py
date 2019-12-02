from django.conf.urls import url, include

from detectorhit import views

urlpatterns = [
    url(r'^uploadCT/$', views.upload_ct, name='uploadCT'),
    url(r'^extractCT/$', views.extract_ct, name='addPatientFile'),
    url(r'^getCTList/$', views.get_ct_info, name='getCTInfoList'),
    url(r'^predCT/$', views.predict_ct, name='predCT'),
    url(r'^getOriginImg/$', views.get_origin_imgs, name='getOriginImg'),
    url(r'^getResultImg/$', views.get_result_imgs, name='getResultImg'),

]
