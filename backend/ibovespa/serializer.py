from rest_framework import serializers
from .models import Ativo, Setor, Segmento

class SetorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setor
        fields = ['id', 'nome']

class SegmentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segmento
        fields = ['id', 'nome']

class AtivoSerializer(serializers.ModelSerializer):
    setor = SetorSerializer(read_only=True)
    segmento = SegmentoSerializer(read_only=True)

    class Meta:
        model = Ativo
        fields = '__all__'

class AtivoListSerializer(serializers.ModelSerializer):
    setor = serializers.CharField(source='setor.nome', read_only=True)
    segmento = serializers.CharField(source='segmento.nome', read_only=True)

    class Meta:
        model = Ativo
        fields = ['id', 'codigo', 'nome', 'setor', 'segmento', 'preco_atual', 'variacao']
