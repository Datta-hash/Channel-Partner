from rest_framework.viewsets import ModelViewSet

from Meta.models import (
    Country,
    State,
    City,
    NatureOfBusiness
)

from Meta.serializers import (
    CountrySerializer,
    StateSerializer,
    CitySerializer,
    NatureOfBusinessSerializer
)

class CountryViewSet(ModelViewSet):
    queryset = Country.objects.filter(status=True)
    serializer_class = CountrySerializer

class StateViewSet(ModelViewSet):
    serializer_class = StateSerializer

    def get_queryset(self):
        return State.objects.filter(status=True)


class CityViewSet(ModelViewSet):
    serializer_class = CitySerializer

    def get_queryset(self):
        return City.objects.select_related("state")\
                           .filter(status=True)

class NatureOfBusinessViewSet(ModelViewSet):
    serializer_class = NatureOfBusinessSerializer

    def get_queryset(self):
        return NatureOfBusiness.objects.filter(status=True)


