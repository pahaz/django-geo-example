from django.conf.urls import include, url
from django.contrib.gis import admin

__author__ = 'pahaz'


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('geoapi.urls')),
]
