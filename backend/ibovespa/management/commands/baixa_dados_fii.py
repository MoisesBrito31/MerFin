import re
import requests
from datetime import date, datetime

URL = "https://www.fundamentus.com.br/fii_graficos.php?papel=VTLT11&tipo=1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Referer": "https://www.fundamentus.com.br/",
}

resp = requests.get(URL, headers=headers, timeout=20)
resp.raise_for_status()
# usa o encoding aparente para evitar problemas de acentuação
resp.encoding = resp.apparent_encoding or resp.encoding
html = resp.text

# captura pares [Date.UTC(YYYY,MM,DD), VALOR]
# Atenção: no regex abaixo usamos apenas um backslash para escapar o ponto literal e os parênteses, pois r"..." já trata a barra
pattern = re.compile(r"Date\.UTC\(\s*(\d{4})\s*,\s*(\d{1,2})\s*,\s*(\d{1,2})\s*\)\s*,\s*([-?\d.,]+)", re.IGNORECASE)
matches = pattern.findall(html)

if not matches:
    # opcional: salva HTML para inspecionar localmente
    try:
        with open("fundamentus_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Nenhum dado encontrado com o regex. HTML salvo em fundamentus_debug.html para inspeção.")
    except Exception:
        pass

dados = []
for y, m, d, v in matches:
    yyyy, mm, dd = int(y), int(m) + 1, int(d)  # Highcharts usa mês 0-based
    # normaliza número com possível separador de milhar '.' e decimal ','
    valor_str = v.strip()
    if "," in valor_str and "." in valor_str:
        # formato brasileiro: 1.234,56
        valor = float(valor_str.replace(".", "").replace(",", "."))
    elif "," in valor_str and "." not in valor_str:
        # apenas vírgula como decimal
        valor = float(valor_str.replace(",", "."))
    else:
        valor = float(valor_str)
    dados.append((date(yyyy, mm, dd).isoformat(), valor))

print(f"Date.UTC pontos extraídos: {len(dados)}")
for linha in dados:
    print(linha)

# Extração específica da variável JavaScript dataSerieDividendYield (ApexCharts)
pattern_divy_block = re.compile(r"var\s+dataSerieDividendYield\s*=\s*\[(.*?)\];", re.DOTALL | re.IGNORECASE)
m_divy = pattern_divy_block.search(html)

dados_divy = []
if m_divy:
    block = m_divy.group(1)
    # extrai pares [ timestamp_ms , valor_decimal ]
    pair_regex = re.compile(r"\[\s*(\d+)\s*,\s*([-]?\d+(?:\.\d+)?)\s*\]")
    for ts_ms_str, val_str in pair_regex.findall(block):
        ts_ms = int(ts_ms_str)
        dy_val = float(val_str)
        dt = datetime.utcfromtimestamp(ts_ms / 1000).date().isoformat()
        dados_divy.append((dt, dy_val))

    print(f"DividendYield pontos extraídos: {len(dados_divy)}")
    for linha in dados_divy:
        print(linha)
else:
    print("Variável dataSerieDividendYield não encontrada no HTML.")