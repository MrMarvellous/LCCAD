from django.conf.urls import url, include

from interpolation import views

urlpatterns = [
    url(r'^interpolate/$', views.interpolate, name='interpolate'),
    url(r'^getInterImgs/$', views.get_inter_imgs, name='getInterImgs'),
    url(r'^queryInterStatus/$', views.queryInterStatus, name='queryInterStatus'),

]
