from django.contrib.gis import admin

from .models import WorldBorder, Provider, ServiceArea

admin.site.register(WorldBorder, admin.GeoModelAdmin)
admin.site.register(Provider, admin.GeoModelAdmin)
admin.site.register(ServiceArea, admin.GeoModelAdmin)
