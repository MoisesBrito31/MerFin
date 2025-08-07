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

