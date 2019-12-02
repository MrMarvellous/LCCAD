from django.conf.urls import url, include

from tracer import views

urlpatterns = [
    url(r'^cover/$', views.cover, name='tracerct'),
    url(r'^getCoverResultById/$', views.getCoverResultById, name='getCoverResultById'),

]
