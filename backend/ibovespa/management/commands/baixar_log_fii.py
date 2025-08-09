import json
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, List, Optional, Tuple, Union, Dict

import requests
from django.core.management.base import BaseCommand, CommandError

from ibovespa.models import FundoImobiliario, FIIHistoricoPreco, FIIRendimento, FIIDividendYield


BASE = "https://www.fundamentus.com.br"


def _build_headers(ticker: str) -> dict:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/139.0.0.0 Safari/537.36"
        ),
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "referer": f"{BASE}/cotacoes.php?papel={ticker}&tela=3",
    }


def _build_html_headers(referer: Optional[str] = None) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/139.0.0.0 Safari/537.36"
        ),
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    if referer:
        headers["referer"] = referer
    return headers


def _parse_js_or_json(content: str) -> Any:
    text = content.strip()
    # Caso já seja JSON puro
    if text.startswith("[") or text.startswith("{"):
        return json.loads(text)
    # Caso venha como JS: var cotacoes = [...];
    m = re.search(r"var\s+cotacoes\s*=\s*(\[.*?\])\s*;", text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return json.loads(m.group(1))
    raise ValueError("Não foi possível identificar JSON ou variável JS 'cotacoes'.")


def _to_date(value: Union[int, str]) -> date:
    # Se inteiro grande: epoch ms
    if isinstance(value, int):
        # assume epoch ms
        return datetime.utcfromtimestamp(value / 1000).date()
    if isinstance(value, str):
        s = value.strip()
        # tenta ISO
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%Y%m%d"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                pass
        # tenta epoch em string
        if s.isdigit():
            iv = int(s)
            # detecta se está em segundos ou ms
            if iv > 10_000_000_000:  # > ~2001 em segundos → provavelmente ms
                return datetime.utcfromtimestamp(iv / 1000).date()
            return datetime.utcfromtimestamp(iv).date()
    raise ValueError(f"Formato de data desconhecido: {value!r}")


def _to_decimal(value: Union[int, float, str]) -> Decimal:
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    s = str(value).strip().replace(" ", "")
    # normaliza vírgula como decimal
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Não foi possível converter para Decimal: {value!r}") from exc


def _normalize_points(parsed: Any) -> List[Tuple[date, Decimal, Optional[int]]]:
    """Retorna lista de tuplas (data, preco, volume_opcional)."""
    points: List[Tuple[date, Decimal, Optional[int]]] = []
    if isinstance(parsed, dict) and "data" in parsed:
        iterable: Iterable = parsed["data"]
    else:
        iterable = parsed  # assume lista

    for item in iterable:
        try:
            if isinstance(item, (list, tuple)):
                # formatos comuns: [timestamp_ms, preco] ou [timestamp_ms, preco, volume]
                ts = item[0]
                price = item[1]
                vol = item[2] if len(item) >= 3 else None
                d = _to_date(ts)
                p = _to_decimal(price)
                v = int(vol) if vol is not None else None
                points.append((d, p, v))
            elif isinstance(item, dict):
                # tenta chaves comuns
                ts = item.get("Data") or item.get("data") or item.get("date") or item.get("x")
                price = item.get("Preco") or item.get("preco") or item.get("close") or item.get("y")
                vol = item.get("Volume") or item.get("volume") or item.get("v")
                if ts is None or price is None:
                    continue
                d = _to_date(ts)
                p = _to_decimal(price)
                v = int(vol) if vol is not None else None
                points.append((d, p, v))
        except Exception:
            # ignora pontos problemáticos
            continue
    return points


class Command(BaseCommand):
    help = (
        "Baixa logs de FIIs do Fundamentus (histórico de preços, rendimentos R$/cota e Dividend Yield). "
        "Uso: python manage.py baixar_log_fii <CODIGO|ALL> [--delay 0.2]"
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument("codigo", type=str, help="Código do FII (quatro letras seguidas de 11), ex.: VTLT11, ou ALL")
        parser.add_argument("--delay", type=float, default=0.2, help="Atraso entre requisições em segundos (padrão 0.2)")

    def handle(self, *args, **options) -> None:
        alvo: str = options["codigo"].upper().strip()
        delay_s: float = options["delay"]

        # resolve lista de tickers
        if alvo == "ALL":
            tickers = self._list_all_fii_codes()
            if not tickers:
                raise CommandError("Não foi possível obter a lista de FIIs do Fundamentus.")
        else:
            if not re.match(r"^[A-Z]{4}11$", alvo):
                raise CommandError("Código inválido. Utilize o formato de 4 letras + 11, ex.: VTLT11, ou ALL.")
            tickers = [alvo]

        total_ok = 0
        for codigo in tickers:
            try:
                fii, _ = FundoImobiliario.objects.get_or_create(codigo=codigo)
                ins_h = self._fetch_and_store_historico(fii)
                if delay_s:
                    self._sleep(delay_s)
                ins_r, ins_dy = self._fetch_and_store_graficos(fii)
                total_ok += 1
                self.stdout.write(self.style.SUCCESS(f"{codigo}: historico+{ins_h}; rend+{ins_r}; dy+{ins_dy}"))
                if delay_s:
                    self._sleep(delay_s)
            except Exception as exc:
                self.stderr.write(self.style.WARNING(f"Falha em {codigo}: {exc}"))
                continue

        self.stdout.write(self.style.SUCCESS(f"Processados {total_ok} FIIs de {len(tickers)}"))

    # utilitários
    def _sleep(self, seconds: float) -> None:
        try:
            import time

            time.sleep(seconds)
        except Exception:
            pass

    def _list_all_fii_codes(self) -> List[str]:
        url = f"{BASE}/script/cmplte.php"
        resp = requests.get(url, headers=_build_html_headers(referer=f"{BASE}/"), timeout=30)
        resp.raise_for_status()
        text = resp.text
        candidates = set(re.findall(r"[A-Z]{4}11", text))
        return sorted(candidates)

    def _fetch_and_store_historico(self, fii: FundoImobiliario) -> int:
        url = f"{BASE}/amline/cot_hist.php?papel={fii.codigo}"
        headers = _build_headers(fii.codigo)

        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or resp.encoding
        raw = resp.text
        parsed = _parse_js_or_json(raw)
        pontos = _normalize_points(parsed)
        inseridos = 0
        for d, preco, volume in pontos:
            _, created = FIIHistoricoPreco.objects.update_or_create(
                fii=fii,
                data=d,
                defaults={"preco_fechamento": preco, "volume": volume},
            )
            if created:
                inseridos += 1
        return inseridos

    def _fetch_and_store_graficos(self, fii: FundoImobiliario) -> Tuple[int, int]:
        url = f"{BASE}/fii_graficos.php?papel={fii.codigo}&tipo=1"
        resp = requests.get(url, headers=_build_html_headers(referer=f"{BASE}/"), timeout=30)
        resp.raise_for_status()
        html = resp.text

        # Rendimento (R$/cota): dataSerieRendimento + labelsRendimento
        labels = [int(x) for x in re.findall(r"labelsRendimento\.push\((\d+)\)\s*;", html)]
        valores = re.findall(r"dataSerieRendimento\.push\(([-]?\d+(?:\.\d+)?)\)\s*;", html)
        rend_pairs: List[Tuple[date, Decimal]] = []
        if labels and valores and len(labels) == len(valores):
            for ts_ms, v in zip(labels, valores):
                dt = datetime.utcfromtimestamp(int(ts_ms) / 1000).date()
                rend_pairs.append((dt, Decimal(v)))

        # Dividend Yield (% em fração): var dataSerieDividendYield = [ [ts, val], ... ]
        m_dy = re.search(r"var\s+dataSerieDividendYield\s*=\s*\[(.*?)\];", html, re.DOTALL | re.IGNORECASE)
        dy_pairs: List[Tuple[date, Decimal]] = []
        if m_dy:
            for ts_ms_str, val_str in re.findall(r"\[\s*(\d+)\s*,\s*([-]?\d+(?:\.\d+)?)\s*\]", m_dy.group(1)):
                dt = datetime.utcfromtimestamp(int(ts_ms_str) / 1000).date()
                dy_pairs.append((dt, Decimal(val_str)))

        # Persistência
        ins_r = 0
        for dt, val in rend_pairs:
            _, created = FIIRendimento.objects.update_or_create(
                fii=fii,
                data=dt,
                defaults={"valor_rendimento": val},
            )
            if created:
                ins_r += 1

        ins_dy = 0
        for dt, val in dy_pairs:
            _, created = FIIDividendYield.objects.update_or_create(
                fii=fii,
                data=dt,
                defaults={"dy": val},
            )
            if created:
                ins_dy += 1

        return ins_r, ins_dy


