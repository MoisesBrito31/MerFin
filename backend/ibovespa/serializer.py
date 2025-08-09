from rest_framework import serializers
from .models import (
    Ativo,
    Setor,
    Segmento,
    HistoricoAtivo,
    FundoImobiliario,
    FIIHistoricoPreco,
    FIIRendimento,
    FIIDividendYield,
)

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
        fields = ['id', 'codigo', 'nome', 'setor', 'segmento', 'preco_atual', 'variacao', 'dividendo_valor', 'dividendo_percentual']

class HistoricoAtivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoAtivo
        fields = '__all__'


# --- FII Serializers ---

class FIISegmentoField(serializers.CharField):
    def to_representation(self, value):
        return value or None


class FIISerializer(serializers.ModelSerializer):
    segmento = serializers.CharField(source='segmento.nome', read_only=True)

    class Meta:
        model = FundoImobiliario
        fields = [
            'id', 'codigo', 'nome', 'segmento',
            'cotacao_atual', 'ffo_yield_percent', 'dividend_yield_percent',
            'valor_mercado', 'quantidade_imoveis', 'preco_m2', 'aluguel_m2',
            'cap_rate_percent', 'vacancia_media_percent',
            'valor_patrimonial_cota', 'p_vp', 'patrimonio_liquido',
            'liquidez_media_diaria', 'taxa_adm', 'taxa_perf', 'data_atualizacao',
        ]


class FIIListSerializer(serializers.ModelSerializer):
    segmento = serializers.CharField(source='segmento.nome', read_only=True)

    class Meta:
        model = FundoImobiliario
        fields = [
            'id', 'codigo', 'nome', 'segmento',
            'cotacao_atual', 'p_vp', 'dividend_yield_percent', 'liquidez_media_diaria',
        ]


class FIIHistoricoPrecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FIIHistoricoPreco
        fields = ['id', 'fii', 'data', 'preco_fechamento', 'volume']


class FIIRendimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FIIRendimento
        fields = ['id', 'fii', 'data', 'valor_rendimento']


class FIIDividendYieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FIIDividendYield
        fields = ['id', 'fii', 'data', 'dy']
