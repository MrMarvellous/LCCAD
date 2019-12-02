from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
# from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPICodec
# schema_view = get_schema_view(title='API', renderer_classes=[SwaggerUIRenderer, OpenAPICodec])
import doctorModule.urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('doctorModule.urls')),
    url(r'^detecthit/', include('detectorhit.urls')),
    url(r'^tracer/', include('tracer.urls')),
    url(r'^interpolation/', include('interpolation.urls')),
    url(r'^livePredict/', include('livePredict.urls')),

]