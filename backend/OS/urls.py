from django.urls import path
from .views import OsList, OsDetail
from .views import EstadoList, EstadoDetail

urlpatterns = [
    path('', OsList.as_view()),
    path('<int:pk>/',OsDetail.as_view()),
    path('estado/', EstadoList.as_view()),
    path('estado/<int:pk>/',EstadoDetail.as_view()),
]