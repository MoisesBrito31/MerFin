from django.db.models import Q
from rest_framework import generics
from rest_framework import filters
from .models import (
    Ativo, Setor, Segmento, HistoricoAtivo,
    FundoImobiliario, FIIHistoricoPreco, FIIRendimento, FIIDividendYield,
)
from .serializer import (
    AtivoListSerializer, SetorSerializer, SegmentoSerializer, AtivoSerializer, HistoricoAtivoSerializer,
    FIIListSerializer, FIISerializer, FIIHistoricoPrecoSerializer, FIIRendimentoSerializer, FIIDividendYieldSerializer,
)
from rest_framework.response import Response
from rest_framework.views import APIView

class AtivoListAPIView(generics.ListAPIView):
    serializer_class = AtivoListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['codigo', 'nome', 'preco_atual']
    ordering = ['codigo']

    def get_queryset(self):
        queryset = Ativo.objects.all()
        search = self.request.query_params.get('search', None)
        setor = self.request.query_params.get('setor', None)
        segmento = self.request.query_params.get('segmento', None)

        q_filter = Q()

        if search:
            q_filter &= (
                Q(codigo__icontains=search) |
                Q(nome__icontains=search) |
                Q(setor__nome__icontains=search) |
                Q(segmento__nome__icontains=search) |
                Q(tipo__icontains=search)
            )
        if setor:
            q_filter &= Q(setor__nome__iexact=setor)
        if segmento:
            q_filter &= Q(segmento__nome__iexact=segmento)

        queryset = queryset.filter(q_filter)
        return queryset

class AtivoDetailAPIView(generics.RetrieveAPIView):
    queryset = Ativo.objects.all()
    serializer_class = AtivoSerializer
    lookup_field = 'codigo'

class SetorListAPIView(generics.ListAPIView):
    queryset = Setor.objects.all()
    serializer_class = SetorSerializer

class SegmentoListAPIView(generics.ListAPIView):
    queryset = Segmento.objects.all()
    serializer_class = SegmentoSerializer

class HistoricoAtivoListAPIView(generics.ListAPIView):
    serializer_class = HistoricoAtivoSerializer

    def get_queryset(self):
        codigo = self.kwargs.get('codigo')
        queryset = HistoricoAtivo.objects.filter(ativo__codigo=codigo).order_by('data')
        data_inicio = self.request.query_params.get('data_inicio')
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        return queryset


# --- FII Views ---

class FIIListAPIView(generics.ListAPIView):
    serializer_class = FIIListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['codigo', 'nome', 'cotacao_atual', 'p_vp']
    ordering = ['codigo']

    def get_queryset(self):
        queryset = FundoImobiliario.objects.all()
        search = self.request.query_params.get('search')
        segmento = self.request.query_params.get('segmento')
        q = Q()
        if search:
            q &= (Q(codigo__icontains=search) | Q(nome__icontains=search) | Q(segmento__nome__icontains=search))
        if segmento:
            q &= Q(segmento__nome__iexact=segmento)
        return queryset.filter(q)


class FIIReadonlyAPIView(generics.RetrieveAPIView):
    queryset = FundoImobiliario.objects.all()
    serializer_class = FIISerializer
    lookup_field = 'codigo'


class FIIHistoricoPrecoListAPIView(generics.ListAPIView):
    serializer_class = FIIHistoricoPrecoSerializer

    def get_queryset(self):
        codigo = self.kwargs.get('codigo')
        qs = FIIHistoricoPreco.objects.filter(fii__codigo=codigo).order_by('data')
        data_inicio = self.request.query_params.get('data_inicio')
        if data_inicio:
            qs = qs.filter(data__gte=data_inicio)
        return qs


class FIIRendimentoListAPIView(generics.ListAPIView):
    serializer_class = FIIRendimentoSerializer

    def get_queryset(self):
        codigo = self.kwargs.get('codigo')
        qs = FIIRendimento.objects.filter(fii__codigo=codigo).order_by('data')
        data_inicio = self.request.query_params.get('data_inicio')
        if data_inicio:
            qs = qs.filter(data__gte=data_inicio)
        return qs


class FIIDividendYieldListAPIView(generics.ListAPIView):
    serializer_class = FIIDividendYieldSerializer

    def get_queryset(self):
        codigo = self.kwargs.get('codigo')
        qs = FIIDividendYield.objects.filter(fii__codigo=codigo).order_by('data')
        data_inicio = self.request.query_params.get('data_inicio')
        if data_inicio:
            qs = qs.filter(data__gte=data_inicio)
        return qs

