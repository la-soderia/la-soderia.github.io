#!/usr/bin/env python3
"""Excepción: cobertura de las elecciones generales de España del 29N (hasta el 30/11 inclusive).

Junta notas de los portales de España y Europa (data/espana/fuentes.json), de Google
Noticias España (data/espana/busquedas.txt) y las notas de medios argentinos del crudo
general que hablan de las elecciones. Las agrupa y calcula un pre-semáforo propio:
  verde?    2+ portales serios de España o Europa distintos, o una fuente oficial española
  amarillo? un solo portal serio de España o Europa
  naranja?  solo medios argentinos u otros (no cuenta como chequeo)
Salidas: data/espana/crudo.json y data/espana/candidatos.json.
Pasado FIN no hace nada, así la cobertura se apaga sola.

Uso: python3 scripts/espana.py
"""
import json, re, sys, urllib.parse, datetime as dt
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rastrillo import descargar, items_de, resuelve_google, armar, fusionar, ahora, iso, dominio_coincide  # noqa: E402
from prefiltro import norm, tokens  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
CARPETA = BASE / "data/espana"
AR = dt.timezone(dt.timedelta(hours=-3))
INICIO = dt.datetime(2026, 11, 20, tzinfo=AR)
FIN = dt.datetime(2026, 12, 1, tzinfo=AR)  # hasta el lunes 30/11 inclusive
GNEWS_ES = "https://news.google.com/rss/search?q={q}&hl=es&gl=ES&ceid=ES:es"
MAX_POR_FEED = 150

TEMA = re.compile(r"elecci|electoral|\b29 ?-?n\b|29 de noviembre|campana|sondeo|encuesta|escrutinio|candidat|\burnas?\b|votac|votant|\bvoto|reflexion|investidura|"
                  r"election|scrutin|sondage|\bpoll|\bvote|campaign|campagne")
ACTORES = re.compile(r"feijoo|abascal|pedro sanchez|\bsanchez\b|yolanda diaz|\bsumar\b|podemos|\bvox\b|\bpp\b|\bpsoe\b|\bjunts\b|puigdemont|\berc\b|\bpnv\b|\bbildu\b|moncloa")
ESPANA = re.compile(r"espana|espanol|spain|spanish|espagne|espagnol|madrid|sanchez|feijoo|abascal|\bvox\b|\bpsoe\b")


def activa(ahora_dt=None):
    return (ahora_dt or dt.datetime.now(AR)) < FIN


def es_electoral(titulo, local):
    """local=True para portales de España (alcanza con tema o actores); si no, pide España + tema."""
    t = norm(titulo)
    if local:
        return bool(TEMA.search(t) or ACTORES.search(t))
    return bool(ESPANA.search(t) and (TEMA.search(t) or ACTORES.search(t)))


def nota(it, nombre, dominio, tipo, seria, etiqueta):
    n = armar(it["titulo"], it["link"], resuelve_google(it["link"]), it["fecha"], nombre, dominio, tipo, seria, etiqueta)
    n["origen"] = "espana_europa" if seria else "otros"
    return n


def tarea_rss(f):
    local = f["tipo"] != "europa"
    return [nota(it, f["nombre"], f["dominio"], f["tipo"], True, None)
            for it in items_de(descargar(f["rss"]))[:MAX_POR_FEED]
            if it["titulo"] and it["link"] and es_electoral(it["titulo"], local)]


def tarea_gnews(consulta, fuentes, etiqueta, filtrar):
    q = urllib.parse.quote_plus(consulta + " when:3d")
    out = []
    for it in items_de(descargar(GNEWS_ES.format(q=q))):
        if not it["titulo"] or not it["link"]:
            continue
        medio, dom = it["medio_src"], it["dominio_src"]
        if medio and it["titulo"].endswith(" - " + medio):
            it["titulo"] = it["titulo"][: -len(medio) - 3].strip()
        if filtrar and not es_electoral(it["titulo"], False) and not TEMA.search(norm(it["titulo"])):
            continue
        f = next((x for x in fuentes if dominio_coincide(dom, x["dominio"])), None)
        out.append(nota(it, f["nombre"] if f else (medio or dom), dom, f["tipo"] if f else "medio", bool(f), etiqueta))
    return out


def notas_argentinas():
    crudo = BASE / "data/crudo.json"
    if not crudo.exists():
        return []
    out = []
    for n in json.loads(crudo.read_text()).get("notas", []):
        t = norm(n["titulo"])
        if ESPANA.search(t) and TEMA.search(t):
            m = dict(n, origen="argentina", lista_seria=False)
            out.append(m)
    return out


def agrupar(notas):
    for n in notas:
        n["_tok"] = tokens(n["titulo"]) or {"_" + n["id"]}
    notas.sort(key=lambda n: n["fecha"], reverse=True)
    grupos = []
    for n in notas:
        mejor, sim = None, 0.0
        for g in grupos:
            j = len(n["_tok"] & g["tok"]) / len(n["_tok"] | g["tok"])
            if j > sim:
                mejor, sim = g, j
        if mejor and sim >= 0.28:
            mejor["notas"].append(n)
            if len(mejor["tok"]) < 25:
                mejor["tok"] |= n["_tok"]
        else:
            grupos.append({"tok": set(n["_tok"]), "notas": [n]})
    out = []
    for g in grupos:
        ns = g["notas"]
        serios = sorted({n["medio"] for n in ns if n["origen"] == "espana_europa"})
        oficial = any(n.get("fuente_tipo") == "oficial" for n in ns)
        pre = "verde?" if len(serios) >= 2 or oficial else "amarillo?" if serios else "naranja?"
        orden = {"espana_europa": 0, "otros": 1, "argentina": 2}
        out.append({
            "id": ns[0]["id"], "pre_semaforo": pre, "medios_serios": serios,
            "medios_argentinos": sorted({n["medio"] for n in ns if n["origen"] == "argentina"}),
            "cant_medios": len({n["dominio"] for n in ns}), "cant_notas": len(ns), "ultima": ns[0]["fecha"],
            "notas": [{k: n.get(k) for k in ("titulo", "medio", "dominio", "url", "fecha", "fuente_tipo", "origen")}
                      for n in sorted(ns, key=lambda n: (orden[n["origen"]], n["fecha"]))[:10]],
        })
    out.sort(key=lambda g: (len(g["medios_serios"]), g["cant_medios"], g["ultima"]), reverse=True)
    return out


def main():
    inicio = ahora()
    if not activa(inicio):
        print("cobertura España terminada: no se rastrilla")
        return
    fuentes = json.loads((CARPETA / "fuentes.json").read_text())
    busquedas = [l.strip() for l in (CARPETA / "busquedas.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
    trabajos = [("rss " + f["nombre"], lambda f=f: tarea_rss(f)) for f in fuentes if f.get("rss")]
    trabajos += [("site " + f["dominio"], lambda f=f: tarea_gnews(f'site:{f["dominio"]} elecciones', fuentes, "site:" + f["dominio"], False))
                 for f in fuentes if f.get("google_site")]
    trabajos += [("gnews " + q, lambda q=q: tarea_gnews(q, fuentes, q, True)) for q in busquedas]

    def correr(t):
        try:
            return t[0], t[1](), None
        except Exception as ex:
            return t[0], [], str(ex)[:150]

    nuevas, errores = [], []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for nombre, ns, err in ex.map(correr, trabajos):
            if err:
                errores.append({"fuente": nombre, "error": err})
                print("ERROR", nombre, err, file=sys.stderr)
            else:
                nuevas += ns
                print("ok %-45s %3d notas" % (nombre, len(ns)))
    sello = iso(inicio)
    for n in nuevas:
        n["visto"] = sello
    previas = []
    if (CARPETA / "crudo.json").exists():
        previas = [n for n in json.loads((CARPETA / "crudo.json").read_text()).get("notas", []) if n.get("origen") != "argentina"]
    todas = fusionar(previas + nuevas, inicio)
    for n in todas:  # fusionar no conoce "origen": se recalcula
        n["origen"] = "espana_europa" if n.get("lista_seria") else "otros"
    lim = INICIO.isoformat()
    todas = [n for n in todas if n["fecha"] >= lim]
    todas.sort(key=lambda n: n["fecha"], reverse=True)
    (CARPETA / "crudo.json").write_text(json.dumps({"generado": sello, "total": len(todas), "errores": errores, "notas": todas}, ensure_ascii=False, indent=1))

    grupos = agrupar([dict(n) for n in todas] + notas_argentinas())
    (CARPETA / "candidatos.json").write_text(json.dumps({"generado": sello, "fin": FIN.isoformat(), "grupos": len(grupos), "candidatos": grupos}, ensure_ascii=False, indent=1))
    print(f"España | notas {len(todas)} | grupos {len(grupos)} | verdes {sum(g['pre_semaforo'] == 'verde?' for g in grupos)} | errores {len(errores)}")


if __name__ == "__main__":
    main()
