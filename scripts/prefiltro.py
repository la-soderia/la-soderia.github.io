#!/usr/bin/env python3
"""Prefiltro gratis del Motor Soda.

Lee data/crudo.json, toma las últimas N horas, descarta ruido (deporte,
espectáculos, ofertas, exterior), agrupa notas parecidas por título y
calcula un pre-semáforo según cuántos medios serios distintos lo cubren.
Salida: data/candidatos.json (insumo para la curaduría de Claude).

Uso: python3 scripts/prefiltro.py [horas=24]
"""
import json, re, sys, unicodedata, datetime as dt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
HORAS = int(sys.argv[1]) if len(sys.argv) > 1 else 24
AR = dt.timezone(dt.timedelta(hours=-3))

# Ruido: si el título matchea y no hay una palabra "salvadora", se descarta.
RUIDO = r"""
\bhoroscopo|\bquiniela|\bloteria|\bpronostico del tiempo|\bclima (para|en)\b|black friday|cyber ?monday|\bofertas?\b|descuentos? de hasta|
\bfutbol\b|\bpartido\b|\bgol(es)?\b|\btorneo\b|\bliga\b|\bcopa\b|\bboca\b|\briver\b|\bmessi\b|\bseleccion\b|\bnba\b|\bformula 1\b|\bf1\b|\btenis\b|\bgran hermano\b|
\bnetflix\b|\bserie\b|\bpelicula\b|\breality\b|\bfarandula\b|\bmodelo\b|\bactriz\b|\bactor\b|\bcantante\b|\bwanda\b|\btinelli\b|\breceta\b|\bdieta\b
"""
SALVA = r"\bgobierno\b|\bley\b|\bcongreso\b|\bdiputad|\bsenad|\bmilei\b|\bpresupuesto\b|\bsalari|\bdespid|\bviolencia\b|\bfemicid|\buniversi|\bescuela|\bjovenes\b"
EXTERIOR = r"\b(cartagena|colombia|mexico|chile|peru|venezuela|españa|espana|madrid|ucrania|rusia|israel|gaza|iran|china|trump|eeuu|estados unidos|brasil|lula|uruguay|paraguay|bolivia|ecuador)\b"
ARG = r"\b(argentin|milei|caputo|kicillof|bullrich|buenos aires|bonaerense|cordoba|rosario|mendoza|cristina|peronismo|congreso)"

STOP = set("""de la el los las un una y o en a al del por para con sin que se su sus es lo como mas más ya no si sobre tras ante entre hasta desde
hoy este esta estos estas fue son ser ha han hay qué cómo cuál quién dijo dice the y/o vs""".split())


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s)


def tokens(t):
    t = norm(t)
    t = re.sub(r"\s[-|–—]\s[^-|–—]*$", "", t)  # quita " - Medio" al final
    return {w for w in re.findall(r"[a-z0-9]{3,}", t) if w not in STOP}


def main():
    crudo = json.loads((BASE / "data/crudo.json").read_text())
    lim = (dt.datetime.now(AR) - dt.timedelta(hours=HORAS)).isoformat(timespec="minutes")
    notas = [n for n in crudo["notas"] if n.get("fecha", "") >= lim]
    entran, fuera = [], {"ruido": 0, "exterior": 0}
    for n in notas:
        t = norm(n["titulo"])
        if re.search(RUIDO, t, re.X) and not re.search(SALVA, t):
            fuera["ruido"] += 1; continue
        if re.search(EXTERIOR, t) and not re.search(ARG, t):
            fuera["exterior"] += 1; continue
        n["_tok"] = tokens(n["titulo"])
        if len(n["_tok"]) >= 3:
            entran.append(n)

    # Agrupado: greedy por similitud de Jaccard contra el "centro" del grupo.
    entran.sort(key=lambda n: n["fecha"], reverse=True)
    grupos = []
    for n in entran:
        mejor, sim = None, 0.0
        for g in grupos:
            j = len(n["_tok"] & g["tok"]) / len(n["_tok"] | g["tok"])
            if j > sim:
                mejor, sim = g, j
        if mejor and sim >= 0.28:
            mejor["notas"].append(n)
            mejor["tok"] |= n["_tok"] if len(mejor["tok"]) < 25 else set()
        else:
            grupos.append({"tok": set(n["_tok"]), "notas": [n]})

    out = []
    for g in grupos:
        ns = g["notas"]
        serios = sorted({n["dominio"] for n in ns if n.get("lista_seria")})
        oficial = any(n.get("fuente_tipo") == "oficial" for n in ns)
        dominios = sorted({n["dominio"] for n in ns})
        if len(serios) >= 2 or oficial:
            pre = "verde?"
        elif len(serios) == 1:
            pre = "amarillo?"
        else:
            pre = "naranja?"
        out.append({
            "id": ns[0]["id"],
            "pre_semaforo": pre,
            "medios_serios": serios,
            "cant_medios": len(dominios),
            "cant_notas": len(ns),
            "ultima": ns[0]["fecha"],
            "notas": [{k: n.get(k) for k in ("titulo", "medio", "dominio", "url", "fecha", "lista_seria", "fuente_tipo")}
                      for n in sorted(ns, key=lambda n: (not n.get("lista_seria"), n["fecha"]))[:8]],
        })
    out.sort(key=lambda g: (len(g["medios_serios"]), g["cant_medios"]), reverse=True)
    res = {"generado": dt.datetime.now(AR).isoformat(timespec="minutes"), "horas": HORAS,
           "notas_ventana": len(notas), "descartadas": fuera, "grupos": len(out), "candidatos": out}
    (BASE / "data/candidatos.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"ventana {len(notas)} | ruido {fuera['ruido']} | exterior {fuera['exterior']} | grupos {len(out)} | "
          f"multi-medio {sum(1 for g in out if g['cant_medios'] >= 2)}")


if __name__ == "__main__":
    main()
