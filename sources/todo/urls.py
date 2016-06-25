from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^incr$', views.async_incr_couter, name='incr'),
]
