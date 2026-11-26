#!/usr/bin/env python3
"""Cuenta en cuántos TÍTULOS de data/crudo.json aparece cada término.

Sin distinguir mayúsculas ni tildes. Para los gráficos tipo /dicenlosmedios.
Uso: python3 scripts/menciones.py "Antonio Grimau" "secreto militar" [--dias 7] [--json]
"""
import argparse, json, re, unicodedata, datetime as dt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AR = dt.timezone(dt.timedelta(hours=-3))


def norm(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip()


def contar(terminos, dias=7, crudo=None):
    crudo = crudo or json.loads((BASE / "data/crudo.json").read_text())
    lim = (dt.datetime.now(AR) - dt.timedelta(days=dias)).isoformat(timespec="minutes")
    notas = [n for n in crudo["notas"] if n.get("fecha", "") >= lim]
    res = []
    for t in terminos:
        pat = re.compile(r"(?<![a-z0-9])" + re.escape(norm(t)) + r"(?![a-z0-9])")
        hit = [n for n in notas if pat.search(norm(n["titulo"]))]
        res.append({"termino": t, "titulos": len(hit),
                    "medios": len({n.get("dominio") or n.get("medio") for n in hit})})
    desde = min((n["fecha"] for n in notas), default="")
    return {"dias": dias, "notas_en_ventana": len(notas), "desde": desde,
            "generado": dt.datetime.now(AR).isoformat(timespec="minutes"), "resultados": res}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("terminos", nargs="+")
    ap.add_argument("--dias", type=int, default=7)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = contar(a.terminos, a.dias)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return
    print(f"Ventana: últimos {r['dias']} días, {r['notas_en_ventana']} notas (desde {r['desde'][:16]})")
    for x in r["resultados"]:
        print(f"{x['termino']}: {x['titulos']} títulos, {x['medios']} medios distintos")


if __name__ == "__main__":
    main()
