import json

from rest_framework import exceptions
from rest_framework import viewsets
from rest_framework_gis.pagination import GeoJsonPagination

from .models import ServiceArea, Provider
from .serializers import ServiceAreaSerializer, ProviderSerializer


class ServiceAreaViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceAreaSerializer
    queryset = ServiceArea.objects.all()
    pagination_class = GeoJsonPagination

    def get_queryset(self):
        queryset = ServiceArea.objects.all()
        provider_id = self.request.query_params.get('provider_id', None)
        if provider_id is not None:
            if not provider_id.isdigit():
                raise exceptions.ValidationError('invalid provider_id')
            queryset = queryset.filter(provider_id=int(provider_id))
        poly_contains = self.request.query_params.get('poly__contains', None)
        if poly_contains is not None:
            try:
                data = json.loads(poly_contains)
                data_coordinates = [float(x) for x in data['coordinates']]
                data_type = data['type']
                if data_type != "Point":
                    raise ValueError('invalid type! only Point type allowed')
                if len(data_coordinates) != 2:
                    raise ValueError('wrong coordinates length')
                pnt_wkt = 'POINT(%s)' % ' '.join(map(str, data_coordinates))
            except (ValueError, KeyError, TypeError) as e:
                raise exceptions.ValidationError(
                    'invalid poly__contains: %s' % e)
            queryset = queryset.filter(poly__contains=pnt_wkt)
        return queryset


class ProviderViewSet(viewsets.ModelViewSet):
    serializer_class = ProviderSerializer
    queryset = Provider.objects.all()
