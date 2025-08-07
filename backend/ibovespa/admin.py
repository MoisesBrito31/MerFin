from django.contrib import admin
from .models import Ativo, Setor, Segmento, HistoricoAtivo

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