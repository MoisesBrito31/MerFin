from django.db.models import Q
from rest_framework import generics
from rest_framework import filters
from .models import Ativo, Setor, Segmento
from .serializer import AtivoListSerializer, SetorSerializer, SegmentoSerializer

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

class SetorListAPIView(generics.ListAPIView):
    queryset = Setor.objects.all()
    serializer_class = SetorSerializer

class SegmentoListAPIView(generics.ListAPIView):
    queryset = Segmento.objects.all()
    serializer_class = SegmentoSerializer

