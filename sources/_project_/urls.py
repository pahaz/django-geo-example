from django.conf.urls import include, url
from django.contrib import admin

from utils.gridfs import prepare_mongodb_settings
from utils.media import serve_from_storage

__author__ = 'pahaz'

prepare_mongodb_settings()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.+)', serve_from_storage),
    url(r'^', include('todo.urls')),
]
