#!/usr/bin/env python3
"""Prefiltro gratis del Motor Soda.

Lee data/crudo.json, toma las últimas N horas, descarta ruido (deporte,
espectáculos, ofertas, exterior), agrupa notas parecidas por título y
calcula un pre-semáforo según cuántos medios serios distintos lo cubren.
Salida: data/candidatos.json (insumo para la curaduría de Claude).

Fuentes prioritarias (prioritaria: true en data/fuentes.json, hoy Ecofeminita):
sus notas, y las de otros medios que las nombran en el título, se miran en una
ventana de 72 h, no pasan por los filtros de ruido ni de exterior, cuentan como
fuente primaria (pre-semáforo verde?) y van primeras en candidatos.json.

Uso: python3 scripts/prefiltro.py [horas=24]
"""
import json, re, sys, unicodedata, datetime as dt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
HORAS = int(sys.argv[1]) if len(sys.argv) > 1 else 24
AR = dt.timezone(dt.timedelta(hours=-3))
HORAS_PRIORITARIAS = 72

# Ruido: si el título matchea y no hay una palabra "salvadora", se descarta.
RUIDO = r"""
\bhoroscopo|\bquiniela|\bloteria|\bpronostico del tiempo|\bclima (para|en)\b|black friday|cyber ?monday|\bofertas?\b|descuentos? de hasta|
\bfutbol\b|\bpartido\b|\bgol(es)?\b|\btorneo\b|\bliga\b|\bcopa\b|\bboca\b|\briver\b|\bmessi\b|\bseleccion\b|\bnba\b|\bformula 1\b|\bf1\b|\btenis\b|\bgran hermano\b|
\bnetflix\b|\bserie\b|\bpelicula\b|\breality\b|\bfarandula\b|\bmodelo\b|\bactriz\b|\bactor\b|\bcantante\b|\bwanda\b|\btinelli\b|\breceta\b|\bdieta\b|
duran duran|\bmanchester\b|\bchampions\b|\bpremier league\b|\bpremier\b|\bla liga\b|\breal madrid\b|\bbarcelona fc\b|\bliverpool\b|\barsenal\b|\bchelsea\b|\bjuventus\b|\bbayern\b|
\bbajar (de )?(los )?kilos\b|\bbajo (\d+ )?kilos\b|\bperdio (\d+ )?kilos\b|\bse murio (el|la) (cantante|guitarrista|baterista|vocalista|rockero|musico)\b|\bmurio (el|la) (cantante|guitarrista|baterista|vocalista|rockero|musico)\b
"""
RUIDO = RUIDO.replace("\n", "")  # los espacios dentro de cada término son literales
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


def prioritarias():
    fuentes = json.loads((BASE / "data/fuentes.json").read_text())
    pri = [f for f in fuentes if f.get("prioritaria")]
    dominios = {f["dominio"] for f in pri}
    nombres = "|".join(re.escape(norm(f["nombre"])) for f in pri)
    return dominios, (re.compile(rf"\b({nombres})\b") if nombres else None)


def es_prioritaria(n, dominios, patron):
    return n.get("dominio") in dominios or bool(patron and patron.search(norm(n["titulo"])))


def main():
    crudo = json.loads((BASE / "data/crudo.json").read_text())
    ahora = dt.datetime.now(AR)
    lim = (ahora - dt.timedelta(hours=HORAS)).isoformat(timespec="minutes")
    lim_pri = (ahora - dt.timedelta(hours=max(HORAS, HORAS_PRIORITARIAS))).isoformat(timespec="minutes")
    dom_pri, pat_pri = prioritarias()
    notas = []
    for n in crudo["notas"]:
        f = n.get("fecha", "")
        n["_pri"] = es_prioritaria(n, dom_pri, pat_pri)
        if f >= lim or (n["_pri"] and f >= lim_pri):
            notas.append(n)
    entran, fuera = [], {"ruido": 0, "exterior": 0}
    for n in notas:
        t = norm(n["titulo"])
        if n["_pri"]:
            n["_tok"] = tokens(n["titulo"]) or {"_pri_" + n["id"]}
            entran.append(n); continue
        if re.search(RUIDO, t) and not re.search(SALVA, t):
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
        prioritaria = any(n["_pri"] for n in ns)
        dominios = sorted({n["dominio"] for n in ns})
        if len(serios) >= 2 or oficial or prioritaria:
            pre = "verde?"
        elif len(serios) == 1:
            pre = "amarillo?"
        else:
            pre = "naranja?"
        out.append({
            "id": ns[0]["id"],
            "pre_semaforo": pre,
            "prioritaria": prioritaria,
            "medios_serios": serios,
            "cant_medios": len(dominios),
            "cant_notas": len(ns),
            "ultima": ns[0]["fecha"],
            "notas": [{k: n.get(k) for k in ("titulo", "medio", "dominio", "url", "fecha", "lista_seria", "fuente_tipo")}
                      for n in sorted(ns, key=lambda n: (not n.get("lista_seria"), n["fecha"]))[:8]],
        })
    out.sort(key=lambda g: (g["prioritaria"], len(g["medios_serios"]), g["cant_medios"]), reverse=True)
    res = {"generado": dt.datetime.now(AR).isoformat(timespec="minutes"), "horas": HORAS,
           "notas_ventana": len(notas), "descartadas": fuera, "grupos": len(out), "candidatos": out}
    (BASE / "data/candidatos.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"ventana {len(notas)} | ruido {fuera['ruido']} | exterior {fuera['exterior']} | grupos {len(out)} | "
          f"multi-medio {sum(1 for g in out if g['cant_medios'] >= 2)} | "
          f"prioritarios {sum(1 for g in out if g['prioritaria'])}")


if __name__ == "__main__":
    main()
