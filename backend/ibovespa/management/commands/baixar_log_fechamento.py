import yfinance as yf
from django.core.management.base import BaseCommand
from ibovespa.models import Ativo, HistoricoAtivo
from django.utils import timezone
from datetime import datetime

class Command(BaseCommand):
    help = 'Baixa o histórico de fechamento dos ativos usando yfinance.'

    def add_arguments(self, parser):
        parser.add_argument('codigo', type=str, help="Código do ativo (ex: PETR4) ou 'ALL' para todos")
        parser.add_argument('--anos', type=int, default=5, help="Quantidade de anos de histórico a baixar (ex: --anos 10 para 10 anos, padrão 5 anos)")

    def handle(self, *args, **options):
        codigo = options['codigo']
        anos = options['anos']
        periodo = f'{anos}y'
        if codigo == 'ALL':
            ativos = Ativo.objects.all()
            total = ativos.count()
            self.stdout.write(f'Baixando histórico de {total} ativos ({anos} anos)...')
            for idx, ativo in enumerate(ativos, 1):
                self.stdout.write(f'[{idx}/{total}] {ativo.codigo}...')
                self.baixar_e_salvar(ativo.codigo, periodo)
            self.stdout.write(self.style.SUCCESS('Processo finalizado!'))
        else:
            self.baixar_e_salvar(codigo + ".SA", periodo)
            self.stdout.write(self.style.SUCCESS(f'Histórico de {codigo} baixado e salvo!'))

    def baixar_e_salvar(self, codigo_com_sufixo, periodo):
        try:
            ticker = yf.Ticker(codigo_com_sufixo)
            hist = ticker.history(period=periodo)
            if hist.empty:
                self.stdout.write(self.style.WARNING(f'Nenhum dado encontrado para {codigo_com_sufixo}'))
                return
            #codigo = codigo_com_sufixo.replace('.SA', '')
            ativo = Ativo.objects.get(codigo=codigo_com_sufixo)
            count = 0
            for data, row in hist.iterrows():
                data_date = data.date() if hasattr(data, 'date') else datetime.strptime(str(data), '%Y-%m-%d').date()
                preco_fechamento = row['Close']
                volume = row['Volume']
                obj, created = HistoricoAtivo.objects.update_or_create(
                    ativo=ativo,
                    data=data_date,
                    defaults={
                        'preco_fechamento': preco_fechamento,
                        'volume': volume
                    }
                )
                count += 1
            self.stdout.write(self.style.SUCCESS(f'{codigo_com_sufixo}: {count} registros atualizados.'))
        except Ativo.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Ativo {codigo_com_sufixo} não encontrado no banco.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao baixar {codigo_com_sufixo}: {e}'))