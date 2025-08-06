import time
import requests
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from ibovespa.models import Ativo, Setor, Segmento

class Command(BaseCommand):
    help = 'Coleta dados da B3 e salva em um arquivo CSV. Pode salvar no banco e usar CSV existente.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--banco',
            action='store_true',
            help='Salva os dados coletados diretamente no banco de dados.'
        )
        parser.add_argument(
            '--nodownload',
            action='store_true',
            help='Usa dados do CSV dados_b3.csv para salvar no banco, sem fazer coleta online.'
        )

    def handle(self, *args, **kwargs):
        salvar_no_banco = kwargs['banco']
        nodownload = kwargs['nodownload']

        if nodownload:
            self.stdout.write(self.style.NOTICE('Carregando dados do CSV existente dados_b3.csv...'))
            try:
                df = pd.read_csv('dados_b3.csv', sep=';')
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR('Arquivo dados_b3.csv não encontrado. Saindo.'))
                return
        else:
            self.stdout.write(self.style.NOTICE('Coletando códigos das ações...'))

            url = 'https://www.fundamentus.com.br/resultado.php'
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            empresas = []
            tabela = soup.find('table', {'class': 'resultado'})
            if tabela:
                linhas = tabela.find_all('tr')
                for linha in linhas[1:]:  # Pula o cabeçalho
                    colunas = linha.find_all('td')
                    if len(colunas) > 1:
                        codigo = colunas[0].a.text.strip()
                        codigo_yahoo = codigo + ".SA"
                        empresas.append({'codigo': codigo_yahoo})

            self.stdout.write(self.style.SUCCESS(f'{len(empresas)} códigos de ações coletados com sucesso!'))

            if not empresas:
                self.stdout.write(self.style.ERROR('Nenhum dado foi coletado.'))
                return

            self.stdout.write(self.style.NOTICE('Coletando dados usando yfinance...'))
            dados = []

            for acao in empresas:
                self.stdout.write(f'Tentando coletar dados para: {acao["codigo"]}')
                try:
                    info = yf.Ticker(acao['codigo']).info
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Erro ao coletar {acao["codigo"]}: {e}'))
                    continue

                info.setdefault('longName', '')
                info.setdefault('shortName', '')
                info.setdefault('currentPrice', None)
                info.setdefault('regularMarketChangePercent', None)
                info.setdefault('industry', '')
                info.setdefault('sector', '')
                info.setdefault('longBusinessSummary', '')
                info.setdefault('fullTimeEmployees', None)
                info.setdefault('auditRisk', '')
                info.setdefault('boardRisk', '')
                info.setdefault('compensationRisk', '')
                info.setdefault('shareHolderRightsRisk', '')
                info.setdefault('overallRisk', '')
                info.setdefault('previousClose', None)
                info.setdefault('dayLow', None)
                info.setdefault('dayHigh', None)
                info.setdefault('volume', None)
                info.setdefault('fiftyTwoWeekLow', None)
                info.setdefault('fiftyTwoWeekHigh', None)
                info.setdefault('dividendRate', None)
                info.setdefault('dividendYield', None)
                info.setdefault('payoutRatio', None)
                info.setdefault('fiveYearAvgDividendYield', None)
                info.setdefault('beta', None)
                info.setdefault('debtToEquity', None)
                info.setdefault('totalDebt', None)
                info.setdefault('targetHighPrice', None)
                info.setdefault('targetMedianPrice', None)
                info.setdefault('targetLowPrice', None)
                info.setdefault('targetMeanPrice', None)

                if not info['longName'] and not info['shortName']:
                    self.stdout.write(self.style.WARNING(f'Ignorando ativo {acao["codigo"]} pois não possui nome válido.'))
                    continue

                dados.append({
                    'Codigo': acao['codigo'],
                    'Nome': info['longName'],
                    'Nick': info['shortName'],
                    'Preco_atual': info['currentPrice'],
                    'Variacao': info['regularMarketChangePercent'],
                    'Setor': info['industry'],
                    'Segmento': info['sector'],
                    'Sobre': info['longBusinessSummary'],
                    'Funcionarios': info['fullTimeEmployees'],
                    'Risco_Auditoria': info['auditRisk'],
                    'Risco_Administrativo': info['boardRisk'],
                    'Risco_Executivos': info['compensationRisk'],
                    'Risco_Acionista': info['shareHolderRightsRisk'],
                    'Risco_Medio': info['overallRisk'],
                    'Fechamento_Anterior': info['previousClose'],
                    'Baixa_do_Dia': info['dayLow'],
                    'Alta_do_Dia': info['dayHigh'],
                    'Volume': info['volume'],
                    'MenorPreco_52S': info['fiftyTwoWeekLow'],
                    'MaiorPreco_52S': info['fiftyTwoWeekHigh'],
                    'DivYeard_Valor': info['dividendRate'],
                    'DivYeard_Percent': info['dividendYield'],
                    'PercLucro_Div': info['payoutRatio'],
                    'MediaDiv_5Anos': info['fiveYearAvgDividendYield'],
                    'Risco_Mercado': info['beta'],
                    'Divida_Sobre_Patrim': info['debtToEquity'],
                    'Divida': info['totalDebt'],
                    'Especialista_Alta': info['targetHighPrice'],
                    'Especialista_Media': info['targetMedianPrice'],
                    'Especialista_Baixa': info['targetLowPrice'],
                    'Especialista_Ideal': info['targetMeanPrice'],
                })
                
                time.sleep(0.5)  # pausa para evitar bloqueios

            df = pd.DataFrame(dados)
            df.to_csv('dados_b3.csv', index=False, encoding='utf-8', sep=';')

        if salvar_no_banco:
            # Criar setores e segmentos únicos primeiro
            setores_unicos = set(df['Setor'].dropna().unique())
            segmentos_unicos = set(df['Segmento'].dropna().unique())

            for nome_setor in setores_unicos:
                if nome_setor:
                    Setor.objects.get_or_create(nome=nome_setor)

            for nome_segmento in segmentos_unicos:
                if nome_segmento:
                    Segmento.objects.get_or_create(nome=nome_segmento)

            registros = df.to_dict(orient='records')

            import math
            def nan_to_none(value):
                if isinstance(value, float) and math.isnan(value):
                    return None
                return value

            for registro in registros:
                setor_obj = None
                if registro.get('Setor'):
                    setor_obj = Setor.objects.filter(nome=registro['Setor']).first()

                segmento_obj = None
                if registro.get('Segmento'):
                    segmento_obj = Segmento.objects.filter(nome=registro['Segmento']).first()

                Ativo.objects.update_or_create(
                    codigo=registro['Codigo'],
                    defaults={
                        'nome': registro.get('Nome', ''),
                        'apelido': registro.get('Nick', ''),
                        'preco_atual': nan_to_none(registro.get('Preco_atual')),
                        'variacao': nan_to_none(registro.get('Variacao')),
                        'setor': setor_obj,
                        'segmento': segmento_obj,
                        'descricao': registro.get('Sobre', ''),
                        'funcionarios': nan_to_none(registro.get('Funcionarios')),
                        'risco_auditoria': registro.get('Risco_Auditoria', ''),
                        'risco_administrativo': registro.get('Risco_Administrativo', ''),
                        'risco_executivos': registro.get('Risco_Executivos', ''),
                        'risco_acionista': registro.get('Risco_Acionista', ''),
                        'risco_medio': registro.get('Risco_Medio', ''),
                        'fechamento_anterior': nan_to_none(registro.get('Fechamento_Anterior')),
                        'baixa_do_dia': nan_to_none(registro.get('Baixa_do_Dia')),
                        'alta_do_dia': nan_to_none(registro.get('Alta_do_Dia')),
                        'volume': nan_to_none(registro.get('Volume')),
                        'menor_preco_52s': nan_to_none(registro.get('MenorPreco_52S')),
                        'maior_preco_52s': nan_to_none(registro.get('MaiorPreco_52S')),
                        'dividendo_valor': nan_to_none(registro.get('DivYeard_Valor')),
                        'dividendo_percentual': nan_to_none(registro.get('DivYeard_Percent')),
                        'percentual_lucro_dividendo': nan_to_none(registro.get('PercLucro_Div')),
                        'media_dividendo_5anos': nan_to_none(registro.get('MediaDiv_5Anos')),
                        'risco_mercado_beta': nan_to_none(registro.get('Risco_Mercado')),
                        'divida_sobre_patrimonio': nan_to_none(registro.get('Divida_Sobre_Patrim')),
                        'divida_total': nan_to_none(registro.get('Divida')),
                        'preco_alvo_alta': nan_to_none(registro.get('Especialista_Alta')),
                        'preco_alvo_media': nan_to_none(registro.get('Especialista_Media')),
                        'preco_alvo_baixa': nan_to_none(registro.get('Especialista_Baixa')),
                        'preco_alvo_ideal': nan_to_none(registro.get('Especialista_Ideal')),
                    }
                )

            self.stdout.write(self.style.SUCCESS('Dados salvos no banco de dados com sucesso!'))
        else:
            self.stdout.write(self.style.SUCCESS('Dados salvos no arquivo CSV com sucesso!'))