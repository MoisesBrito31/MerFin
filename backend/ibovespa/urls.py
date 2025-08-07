from django.urls import path
from .views import AtivoListAPIView, SetorListAPIView, SegmentoListAPIView, AtivoDetailAPIView, HistoricoAtivoListAPIView

urlpatterns = [
    path('ativos/', AtivoListAPIView.as_view(), name='api-ativos-list'),
    path('setor/', SetorListAPIView.as_view(), name='api-setor-list'),
    path('segmento/', SegmentoListAPIView.as_view(), name='api-segmento-list'),
    path('ativos/<str:codigo>/', AtivoDetailAPIView.as_view(), name='api-ativo-detail'),
    path('ativos/<str:codigo>/historico/', HistoricoAtivoListAPIView.as_view(), name='api-ativo-historico'),
]