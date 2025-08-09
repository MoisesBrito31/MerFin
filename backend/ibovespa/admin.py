from django.contrib import admin
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

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Segmento)
class SegmentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Ativo)
class AtivoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'preco_atual', 'variacao', 'tipo', 'setor', 'segmento')
    search_fields = ('codigo', 'nome')
    list_filter = ('tipo', 'setor', 'segmento')
    ordering = ('codigo',)

admin.site.register(HistoricoAtivo)


@admin.register(FundoImobiliario)
class FundoImobiliarioAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nome',
        'segmento',
        'administrador',
        'gestao',
        'mandato',
        'publico_alvo',
        'p_vp',
        'valor_patrimonial_cota',
        'patrimonio_liquido',
        'liquidez_media_diaria',
        'taxa_adm',
        'taxa_perf',
        'data_atualizacao',
    )
    search_fields = ('codigo', 'nome', 'cnpj')
    list_filter = ('segmento',)
    ordering = ('codigo',)


@admin.register(FIIHistoricoPreco)
class FIIHistoricoPrecoAdmin(admin.ModelAdmin):
    list_display = ('fii', 'data', 'preco_fechamento', 'volume')
    search_fields = ('fii__codigo',)
    list_filter = ('fii',)
    date_hierarchy = 'data'
    ordering = ('-data',)


@admin.register(FIIRendimento)
class FIIRendimentoAdmin(admin.ModelAdmin):
    list_display = ('fii', 'data', 'valor_rendimento')
    search_fields = ('fii__codigo',)
    list_filter = ('fii',)
    date_hierarchy = 'data'
    ordering = ('-data',)


@admin.register(FIIDividendYield)
class FIIDividendYieldAdmin(admin.ModelAdmin):
    list_display = ('fii', 'data', 'dy')
    search_fields = ('fii__codigo',)
    list_filter = ('fii',)
    date_hierarchy = 'data'
    ordering = ('-data',)