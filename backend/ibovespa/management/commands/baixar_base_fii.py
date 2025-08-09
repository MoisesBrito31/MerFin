import re
import unicodedata
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable, List, Optional

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError

from ibovespa.models import (FundoImobiliario, Segmento)


BASE = "https://www.fundamentus.com.br"


def normalize_text(value: str) -> str:
    if value is None:
        return ""
    # remove acentos e pontuação leve
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text).strip().lower()


def build_headers(ref: Optional[str] = None) -> Dict[str, str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/139.0.0.0 Safari/537.36"
        ),
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-mobile": "?0",
    }
    if ref:
        headers["referer"] = ref
    return headers


## removido: headers XHR e qualquer coleta de séries


def parse_number(text: str) -> Optional[Decimal]:
    if text is None:
        return None
    s = text.strip()
    if not s:
        return None
    # normaliza formatos tipo 1.234,56
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    s = re.sub(r"[^0-9\.-]", "", s)
    if s in ("", "-", "."):
        return None
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def list_all_fii_codes() -> List[str]:
    # Estratégia preferida: tabela consolidada de FIIs (fii_resultado.php)
    try:
        rows = fetch_fii_resultado_rows()
        codes = [r["codigo"] for r in rows if r.get("codigo")]
        if codes:
            return sorted(set(codes))
    except Exception:
        pass
    # Fallback: script de autocomplete
    try:
        url = f"{BASE}/script/cmplte.php"
        resp = requests.get(url, headers=build_headers(ref=f"{BASE}/"), timeout=30)
        resp.raise_for_status()
        text = resp.text
        candidates = set(re.findall(r"[A-Z]{4}11", text))
        return sorted(candidates)
    except Exception:
        return []


def fetch_fii_resultado_rows() -> List[Dict[str, Any]]:
    """Lê a tabela base de FIIs em fii_resultado.php e retorna linhas normalizadas.

    Campos possíveis retornados (quando presentes):
    - codigo (Papel)
    - nome (Nome/Fundo)
    - segmento (Segmento)
    - p_vp (P/VP)
    - cotacao_atual (Cotação)
    - ffo_yield_percent (FFO Yield)
    - dividend_yield_percent (Dividend Yield)
    - valor_mercado (Valor de mercado)
    - quantidade_imoveis (Quantidade de imóveis)
    - preco_m2 (Preço/m²)
    - aluguel_m2 (Aluguel/m²)
    - cap_rate_percent (Cap rate)
    - vacancia_media_percent (Vacância média)
    - liquidez_media_diaria (Liquidez diária)
    - outros campos ignorados (DY, FFO yield, etc.)
    """
    url = f"{BASE}/fii_resultado.php"
    resp = requests.get(url, headers=build_headers(ref=f"{BASE}/"), timeout=30)
    resp.raise_for_status()
    html = resp.text
    try:
        with open("backend/ibovespa/management/commands/fii_resultado_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
    except Exception:
        pass

    soup = BeautifulSoup(html, "html.parser")
    # seleciona a tabela correta procurando por cabeçalhos que contenham colunas típicas
    candidate_tables = soup.find_all("table")
    table = None
    headers_norm: List[str] = []
    for tb in candidate_tables:
        first_tr = tb.find("tr")
        if not first_tr:
            continue
        header_cells = first_tr.find_all(["th", "td"])
        tmp_headers = [normalize_text(th.get_text(" ")) for th in header_cells]
        hset = "|".join(tmp_headers)
        if ("papel" in hset) and ("p/vp" in hset or "p vp" in hset) and ("segmento" in hset or "setor" in hset):
            table = tb
            headers_norm = tmp_headers
            break
    if table is None:
        # fallback: primeira tabela
        table = soup.find("table")
        if not table:
            raise CommandError("Tabela de FIIs não encontrada em fii_resultado.php")
        header_cells = table.find("tr").find_all(["th", "td"]) if table.find("tr") else []
        headers_norm = [normalize_text(th.get_text(" ")) for th in header_cells]

    # cabeçalhos
    header_cells = table.find("tr").find_all(["th", "td"]) if table.find("tr") else []
    headers_norm: List[str] = []
    for th in header_cells:
        h = normalize_text(th.get_text(" "))
        headers_norm.append(h)

    # mapeia índices de colunas
    idx_codigo = next((i for i, h in enumerate(headers_norm) if "papel" in h or h == "codigo"), None)
    idx_nome = next((i for i, h in enumerate(headers_norm) if "nome" in h or "fundo" in h), None)
    idx_segmento = next((i for i, h in enumerate(headers_norm) if "segmento" in h), None)
    idx_pvp = next((i for i, h in enumerate(headers_norm) if "p/vp" in h or h == "p vp" or "p vp" in h), None)
    idx_cot = next((i for i, h in enumerate(headers_norm) if "cotacao" in h or "cotação" in h), None)
    idx_ffo = next((i for i, h in enumerate(headers_norm) if "ffo" in h), None)
    idx_dy = next((i for i, h in enumerate(headers_norm) if "dividend" in h or "dy" in h), None)
    idx_vm = next((i for i, h in enumerate(headers_norm) if "valor de mercado" in h or "v. mercado" in h), None)
    idx_qtdimv = next((i for i, h in enumerate(headers_norm) if ("qtd" in h and ("imoveis" in h or "imóveis" in h))), None)
    if idx_qtdimv is None:
        idx_qtdimv = next((i for i, h in enumerate(headers_norm) if "imoveis" in h or "imóveis" in h), None)
    idx_preco_m2 = next((i for i, h in enumerate(headers_norm) if ("preco/m2" in h or "preco m2" in h or "preco por m2" in h or "preco por m" in h)), None)
    if idx_preco_m2 is None:
        idx_preco_m2 = next((i for i, h in enumerate(headers_norm) if ("preco" in h and "m2" in h)), None)
    idx_aluguel_m2 = next((i for i, h in enumerate(headers_norm) if ("aluguel/m2" in h or "aluguel m2" in h or "aluguel por m2" in h or ("aluguel" in h and "m2" in h))), None)
    idx_cap = next((i for i, h in enumerate(headers_norm) if "cap" in h and "rate" in h), None)
    idx_vac = next((i for i, h in enumerate(headers_norm) if "vacancia" in h or "vacância" in h), None)
    # "Liquidez diária" pode aparecer abreviado como "Liq. diária"; cobrimos ambos (headers_norm já normalizado em lower)
    idx_liq = next((
        i for i, h in enumerate(headers_norm)
        if ("liquidez" in h) or ("liq" in h and "diaria" in h)
    ), None)

    rows: List[Dict[str, Any]] = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if not tds:
            continue
        def val(i: Optional[int]) -> str:
            if i is None or i >= len(tds):
                return ""
            return tds[i].get_text(" ").strip()

        codigo = val(idx_codigo).upper()
        if not re.match(r"^[A-Z]{4}11$", codigo):
            # ignora linhas que não são FIIs
            continue

        row: Dict[str, Any] = {"codigo": codigo}
        nome = val(idx_nome)
        if not nome and len(tds) > 0:
            # tenta extrair do atributo title do primeiro td/anchor
            first_td = tds[0]
            title_attr = first_td.get("title")
            if not title_attr:
                a_tag = first_td.find("a")
                if a_tag and a_tag.has_attr("title"):
                    title_attr = a_tag.get("title")
            if title_attr:
                nome = title_attr.strip()
        if not nome:
            # varredura por qualquer atributo title na linha
            any_title = None
            for el in tr.find_all(True):
                if el.has_attr("title") and el.get("title"):
                    any_title = el.get("title").strip()
                    if any_title:
                        break
            if any_title:
                nome = any_title
        if nome:
            row["nome"] = nome
        segmento_txt = val(idx_segmento)
        if segmento_txt:
            row["segmento"] = segmento_txt
        pvp_txt = val(idx_pvp)
        if pvp_txt:
            row["p_vp"] = parse_number(pvp_txt)
        cot_txt = val(idx_cot)
        if cot_txt:
            row["cotacao_atual"] = parse_number(cot_txt)
        ffo_txt = val(idx_ffo)
        if ffo_txt:
            row["ffo_yield_percent"] = parse_number(ffo_txt)
        dy_txt = val(idx_dy)
        if dy_txt:
            row["dividend_yield_percent"] = parse_number(dy_txt)
        liq_txt = val(idx_liq)
        # fallback: 8ª coluna (0-based 7) costuma ser a Liquidez diária na tabela
        if (not liq_txt) and len(tds) >= 8:
            liq_txt = tds[7].get_text(" ").strip()
        if (not liq_txt) and len(tds) >= 7:
            liq_txt = tds[6].get_text(" ").strip()
        if not liq_txt:
            # última tentativa: procurar por célula cujo header, data-th ou title indique liquidez
            cand = None
            for td in tds:
                data_th = td.get("data-th") or td.get("aria-label") or ""
                text_header = normalize_text(data_th)
                if "liquidez" in text_header:
                    cand = td.get_text(" ").strip()
                    break
            if cand:
                liq_txt = cand
        if liq_txt:
            # Liquidez pode vir com: R$ 1,2M | 850 K | 3,4 mi | 2,1 bi | 123.456
            s = liq_txt.strip().lower().replace("r$", "").strip()
            # extrai número e sufixo final
            import re as _re
            m = _re.search(r"([0-9\.,]+)\s*([a-z]{1,3})?$", s)
            mult = Decimal("1")
            num_str = s
            if m:
                num_str = m.group(1)
                suf = (m.group(2) or "").lower()
                if suf in ("k", "mil"):
                    mult = Decimal("1000")
                elif suf in ("m", "mi", "mm"):
                    mult = Decimal("1000000")
                elif suf in ("b", "bi"):
                    mult = Decimal("1000000000")
            # normaliza padrão como 1.355.850 -> 1355850
            if "," not in num_str and "." in num_str:
                num_str = num_str.replace(".", "")
            n = parse_number(num_str)
            if n is not None:
                total = n * mult
                try:
                    row["liquidez_media_diaria"] = int(total)
                except Exception:
                    row["liquidez_media_diaria"] = int(total.to_integral_value())
        vm_txt = val(idx_vm)
        if vm_txt:
            row["valor_mercado"] = parse_number(vm_txt)
        qtd_txt = val(idx_qtdimv)
        if qtd_txt:
            n = parse_number(qtd_txt)
            row["quantidade_imoveis"] = int(n) if n is not None else None
        pm2_txt = val(idx_preco_m2)
        if pm2_txt:
            row["preco_m2"] = parse_number(pm2_txt)
        am2_txt = val(idx_aluguel_m2)
        if am2_txt:
            row["aluguel_m2"] = parse_number(am2_txt)
        cap_txt = val(idx_cap)
        if cap_txt:
            row["cap_rate_percent"] = parse_number(cap_txt)
        vac_txt = val(idx_vac)
        if vac_txt:
            row["vacancia_media_percent"] = parse_number(vac_txt)

        rows.append(row)

    return rows


def fetch_details_page(ticker: str) -> BeautifulSoup:
    # Tenta página específica de FII; se não, usa a genérica
    candidates = (
        f"/fii_detalhes.php?papel={ticker}",
        f"/fii_detalhes.php?papel={ticker}&interface=mobile",
        f"/detalhes.php?papel={ticker}",
        f"/detalhes.php?papel={ticker}&interface=mobile",
    )
    for idx, path in enumerate(candidates, start=1):
        url = f"{BASE}{path}"
        resp = requests.get(url, headers=build_headers(ref=f"{BASE}/"), timeout=30)
        if resp.status_code == 200 and resp.text:
            # salva para depuração
            try:
                debug_path = f"backend/ibovespa/management/commands/fii_details_debug_{ticker}_{idx}.html"
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(resp.text)
            except Exception:
                pass
            return BeautifulSoup(resp.text, "html.parser")
    raise CommandError(f"Não foi possível obter página de detalhes para {ticker}")


def extract_fii_attributes(soup: BeautifulSoup) -> Dict[str, Any]:
    # Procura por tabelas de chave/valor, mapeando rótulos conhecidos para campos do modelo
    mapping = {
        # instituição/gestão
        "administrador": "administrador",
        "gestao": "gestao",
        "gestor": "gestao",
        # caracterização
        "mandato": "mandato",
        "publico alvo": "publico_alvo",
        "publico-alvo": "publico_alvo",
        # identificação
        "cnpj": "cnpj",
        "nome": "nome",
        "fundo": "nome",
        # indicadores
        "valor patrimonial por cota": "valor_patrimonial_cota",
        "valor patrimonial r$/cota": "valor_patrimonial_cota",
        "vpa": "valor_patrimonial_cota",
        "p/vp": "p_vp",
        "patrimonio liquido": "patrimonio_liquido",
        "liquidez media diaria": "liquidez_media_diaria",
        "taxa de administracao": "taxa_adm",
        "taxa de performance": "taxa_perf",
        # classificação
        "segmento": "segmento",
    }
    data: Dict[str, Any] = {}

    # analisa todas as células de tabelas, pares label -> valor
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = row.find_all(["td", "th"])  # alguns rótulos ficam em th
            if len(cols) < 2:
                continue
            # percorre aos pares: (label, valor), (label2, valor2), ...
            for i in range(0, len(cols) - 1, 2):
                raw_label = cols[i].get_text(" ")
                raw_value = cols[i + 1].get_text(" ").strip()
                label = normalize_text(raw_label)
                if not label:
                    continue
                for key, field in mapping.items():
                    if key in label:
                        if field in ("valor_patrimonial_cota", "p_vp", "patrimonio_liquido", "taxa_adm", "taxa_perf"):
                            data[field] = parse_number(raw_value)
                        elif field == "liquidez_media_diaria":
                            n = parse_number(raw_value)
                            data[field] = int(n) if n is not None else None
                        elif field == "segmento":
                            data[field] = raw_value.strip()
                        else:
                            data[field] = raw_value.strip()
                        break

    return data


def upsert_fii_record(ticker: str, attrs: Dict[str, Any]) -> FundoImobiliario:
    segmento_nome = attrs.pop("segmento", None)
    segmento_obj = None
    if segmento_nome:
        nome_limpo = segmento_nome.strip()
        if nome_limpo:
            segmento_obj, _ = Segmento.objects.get_or_create(nome=nome_limpo)

    defaults: Dict[str, Any] = {
        "nome": (attrs.get("nome") or "").strip(),
        "administrador": attrs.get("administrador") or "",
        "gestao": attrs.get("gestao") or "",
        "mandato": attrs.get("mandato") or "",
        "publico_alvo": attrs.get("publico_alvo") or "",
        "cnpj": (attrs.get("cnpj") or "").strip(),
    }

    # Copia campos numéricos se presentes
    for field in (
        "valor_patrimonial_cota",
        "p_vp",
        "patrimonio_liquido",
        "liquidez_media_diaria",
        "taxa_adm",
        "taxa_perf",
        "cotacao_atual",
        "ffo_yield_percent",
        "dividend_yield_percent",
        "valor_mercado",
        "quantidade_imoveis",
        "preco_m2",
        "aluguel_m2",
        "cap_rate_percent",
        "vacancia_media_percent",
    ):
        if field in attrs:
            defaults[field] = attrs[field]
    if segmento_obj:
        defaults["segmento"] = segmento_obj

    fii, created = FundoImobiliario.objects.update_or_create(
        codigo=ticker,
        defaults=defaults,
    )
    return fii


## removido: qualquer parsing/persistência de gráficos ou DY


## removido: utilitários para histórico


## removido: coleta/persistência de histórico de preços


def process_one_fii(ticker: str) -> None:
    # Preferimos a tabela consolidada para atributos básicos
    try:
        all_rows = fetch_fii_resultado_rows()
        row = next((r for r in all_rows if r.get("codigo") == ticker), None)
        base_attrs: Dict[str, Any] = {}
        if row:
            base_attrs = {k: v for k, v in row.items() if k != "codigo"}
            fii = upsert_fii_record(ticker, base_attrs)
            preenchidos = sorted([k for k, v in base_attrs.items() if v not in (None, "")])
            print(f"{ticker}: base atualizada via tabela (campos: {', '.join(preenchidos) if preenchidos else 'nenhum'})")
            return
    except Exception:
        pass

    # Fallback: página de detalhes
    soup = fetch_details_page(ticker)
    attrs = extract_fii_attributes(soup)
    fii = upsert_fii_record(ticker, attrs)
    preenchidos = sorted([k for k, v in attrs.items() if v not in (None, "")])
    print(f"{ticker}: base atualizada via detalhes (campos: {', '.join(preenchidos) if preenchidos else 'nenhum'})")


class Command(BaseCommand):
    help = (
        "Baixa e popula APENAS metadados de FIIs a partir do Fundamentus (sem logs). "
        "Uso: python manage.py baixar_base_fii <CODIGO|ALL>"
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "alvo",
            type=str,
            help="Código do FII (ex.: VTLT11) ou ALL para processar todos",
        )
        # sem delay; não há múltiplas chamadas por FII aqui

    def handle(self, *args, **options) -> None:
        alvo: str = options["alvo"].strip().upper()

        tickers: List[str]
        if alvo in ("ALL", "TUDO"):
            tickers = list_all_fii_codes()
            if not tickers:
                raise CommandError("Não foi possível obter a lista de FIIs do Fundamentus.")
        else:
            if not re.match(r"^[A-Z]{4}11$", alvo):
                raise CommandError("Código inválido. Use o formato 4 letras + 11, ex.: VTLT11, ou ALL.")
            tickers = [alvo]

        ok = 0
        # Quando ALL, podemos usar a tabela diretamente para performance
        table_rows: List[Dict[str, Any]] = []
        if alvo in ("ALL", "TUDO"):
            try:
                table_rows = fetch_fii_resultado_rows()
            except Exception as exc:
                self.stderr.write(self.style.WARNING(f"Falha ao ler tabela base: {exc}. Usando fallback por código."))

        for code in tickers:
            try:
                if table_rows:
                    row = next((r for r in table_rows if r.get("codigo") == code), None)
                    if row:
                        base_attrs = {k: v for k, v in row.items() if k != "codigo"}
                        upsert_fii_record(code, base_attrs)
                        ok += 1
                        self.stdout.write(self.style.SUCCESS(f"{code}: base atualizada (tabela)"))
                        continue
                process_one_fii(code)
                ok += 1
            except Exception as exc:
                self.stderr.write(self.style.WARNING(f"Falha em {code}: {exc}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"Processados {ok} FIIs de {len(tickers)}"))


