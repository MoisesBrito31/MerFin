from django.db import models
from django.utils import timezone

class Setor(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.nome


class Segmento(models.Model):
    nome = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nome


class Ativo(models.Model):
    TIPO_CHOICES = [
        ('acao', 'Ação'),
        ('fi', 'Fundo Imobiliário'),
    ]

    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=255, blank=True)
    apelido = models.CharField(max_length=255, blank=True)
    preco_atual = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    variacao = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    setor = models.ForeignKey(Setor, null=True, blank=True, on_delete=models.SET_NULL, related_name='ativos')
    segmento = models.ForeignKey(Segmento, null=True, blank=True, on_delete=models.SET_NULL, related_name='ativos')
    descricao = models.TextField(blank=True)
    funcionarios = models.IntegerField(null=True, blank=True)
    risco_auditoria = models.CharField(max_length=50, blank=True)
    risco_administrativo = models.CharField(max_length=50, blank=True)
    risco_executivos = models.CharField(max_length=50, blank=True)
    risco_acionista = models.CharField(max_length=50, blank=True)
    risco_medio = models.CharField(max_length=50, blank=True)
    fechamento_anterior = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    baixa_do_dia = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    alta_do_dia = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    volume = models.BigIntegerField(null=True, blank=True)
    menor_preco_52s = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    maior_preco_52s = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    dividendo_valor = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    dividendo_percentual = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    percentual_lucro_dividendo = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    media_dividendo_5anos = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    risco_mercado_beta = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    divida_sobre_patrimonio = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    divida_total = models.DecimalField(max_digits=25, decimal_places=6, null=True, blank=True)
    preco_alvo_alta = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    preco_alvo_media = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    preco_alvo_baixa = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    preco_alvo_ideal = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='acao')

    def __str__(self):
        return f'{self.codigo} - {self.nome}'


class HistoricoAtivo(models.Model):
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE, related_name='historicos')
    data = models.DateField()
    preco_fechamento = models.DecimalField(max_digits=20, decimal_places=4)
    volume = models.BigIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('ativo', 'data')
        ordering = ['-data']

    def __str__(self):
        return f'{self.ativo.codigo} - {self.data} - {self.preco_fechamento}'

"""
Modelagem específica para Fundos Imobiliários (FIIs), separada de ações.
Baseada nas informações disponíveis no Fundamentus (detalhes de FII e séries históricas).
"""


class FundoImobiliario(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=255, blank=True)
    segmento = models.ForeignKey(Segmento, null=True, blank=True, on_delete=models.SET_NULL, related_name='fiis')

    administrador = models.CharField(max_length=255, blank=True)
    gestao = models.CharField(max_length=255, blank=True)
    mandato = models.CharField(max_length=255, blank=True)
    publico_alvo = models.CharField(max_length=255, blank=True)
    cnpj = models.CharField(max_length=32, blank=True)

    # Indicadores comuns em Fundamentus (opcionais)
    cotacao_atual = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    ffo_yield_percent = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    dividend_yield_percent = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    valor_mercado = models.DecimalField(max_digits=22, decimal_places=2, null=True, blank=True)
    quantidade_imoveis = models.IntegerField(null=True, blank=True)
    preco_m2 = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    aluguel_m2 = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    cap_rate_percent = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    vacancia_media_percent = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    valor_patrimonial_cota = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    p_vp = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    patrimonio_liquido = models.DecimalField(max_digits=22, decimal_places=2, null=True, blank=True)
    liquidez_media_diaria = models.BigIntegerField(null=True, blank=True)
    taxa_adm = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    taxa_perf = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fundo Imobiliário'
        verbose_name_plural = 'Fundos Imobiliários'

    def __str__(self):
        return f'{self.codigo} - {self.nome}'


class FIIHistoricoPreco(models.Model):
    fii = models.ForeignKey(FundoImobiliario, on_delete=models.CASCADE, related_name='historicos_preco')
    data = models.DateField()
    preco_fechamento = models.DecimalField(max_digits=20, decimal_places=4)
    volume = models.BigIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('fii', 'data')
        ordering = ['-data']

    def __str__(self):
        return f'{self.fii.codigo} - {self.data} - {self.preco_fechamento}'


class FIIRendimento(models.Model):
    """Rendimento mensal (R$/cota) do FII."""
    fii = models.ForeignKey(FundoImobiliario, on_delete=models.CASCADE, related_name='rendimentos')
    data = models.DateField()
    valor_rendimento = models.DecimalField(max_digits=20, decimal_places=6)

    class Meta:
        unique_together = ('fii', 'data')
        ordering = ['-data']

    def __str__(self):
        return f'{self.fii.codigo} - {self.data} - R$ {self.valor_rendimento}'


class FIIDividendYield(models.Model):
    """Dividend Yield diário (% em fração, ex.: 0.087 = 8,7%)."""
    fii = models.ForeignKey(FundoImobiliario, on_delete=models.CASCADE, related_name='dividend_yields')
    data = models.DateField()
    dy = models.DecimalField(max_digits=10, decimal_places=6)

    class Meta:
        unique_together = ('fii', 'data')
        ordering = ['-data']

    def __str__(self):
        return f'{self.fii.codigo} - {self.data} - DY {self.dy}'

