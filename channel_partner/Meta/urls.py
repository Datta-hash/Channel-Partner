from django.urls import path, include
from rest_framework.routers import DefaultRouter

from Meta.views import (
    CountryViewSet,
    StateViewSet,
    CityViewSet,
    NatureOfBusinessViewSet
)

router = DefaultRouter()

router.register(r'countries', CountryViewSet, basename='country')
router.register(r'states', StateViewSet, basename='state')
router.register(r'cities', CityViewSet, basename='city')
router.register(r'nature-of-business', NatureOfBusinessViewSet, basename='nature-of-business')

urlpatterns = [
    path('', include(router.urls)),
]
