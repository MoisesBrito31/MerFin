from django.urls import path
from .views import (
    AtivoListAPIView, SetorListAPIView, SegmentoListAPIView, AtivoDetailAPIView, HistoricoAtivoListAPIView,
    FIIListAPIView, FIIReadonlyAPIView, FIIHistoricoPrecoListAPIView, FIIRendimentoListAPIView, FIIDividendYieldListAPIView,
)

urlpatterns = [
    path('ativos/', AtivoListAPIView.as_view(), name='api-ativos-list'),
    path('setor/', SetorListAPIView.as_view(), name='api-setor-list'),
    path('segmento/', SegmentoListAPIView.as_view(), name='api-segmento-list'),
    path('ativos/<str:codigo>/', AtivoDetailAPIView.as_view(), name='api-ativo-detail'),
    path('ativos/<str:codigo>/historico/', HistoricoAtivoListAPIView.as_view(), name='api-ativo-historico'),
    # FII endpoints
    path('fiis/', FIIListAPIView.as_view(), name='api-fii-list'),
    path('fiis/<str:codigo>/', FIIReadonlyAPIView.as_view(), name='api-fii-detail'),
    path('fiis/<str:codigo>/historico/', FIIHistoricoPrecoListAPIView.as_view(), name='api-fii-historico'),
    path('fiis/<str:codigo>/rendimentos/', FIIRendimentoListAPIView.as_view(), name='api-fii-rendimentos'),
    path('fiis/<str:codigo>/dy/', FIIDividendYieldListAPIView.as_view(), name='api-fii-dy'),
]