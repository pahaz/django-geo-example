from django.conf.urls import include, url
from django.contrib.gis import admin
from django.shortcuts import redirect, render

__author__ = 'pahaz'


def index(request):
    if request.method == 'POST':
        return redirect('/')
    return render(request, 'index.html', {})


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('geoapi.urls')),
]
