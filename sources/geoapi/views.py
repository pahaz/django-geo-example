from rest_framework import viewsets
from rest_framework_gis.pagination import GeoJsonPagination

from .models import ServiceArea, Provider
from .serializers import ServiceAreaSerializer, ProviderSerializer


class ServiceAreaViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceAreaSerializer
    queryset = ServiceArea.objects.all()
    pagination_class = GeoJsonPagination


class ProviderViewSet(viewsets.ModelViewSet):
    serializer_class = ProviderSerializer
    queryset = Provider.objects.all()
