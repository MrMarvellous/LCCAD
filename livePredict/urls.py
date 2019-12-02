from django.conf.urls import url, include

from livePredict import views

urlpatterns = [
    url(r'^predictPET/$', views.predict, name='predictPET'),
    url(r'^extractPET/$', views.extract_pet, name='predictPET'),
    url(r'^uploadPET/$', views.upload_pet, name='uploadPET'),
    url(r'^getPETResultByPID/$', views.get_predict_result_by_PID, name='getPETResultByPID'),

]
