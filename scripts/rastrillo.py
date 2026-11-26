#!/usr/bin/env python3
"""Rastrillo de Motor Soda: junta notas de coyuntura argentina.

Lee RSS de portales (data/fuentes.json) y Google Noticias por tema
(data/busquedas.txt). Solo libreria estandar. Escribe data/crudo.json
con los ultimos 7 dias, sin duplicados. Un feed caido no rompe la corrida.

Regla de medios del exterior (simple): una nota que viene de Google Noticias
solo se acepta si su dominio termina en .ar o esta en fuentes.json. Las
busquedas marcadas con "!" en busquedas.txt aceptan cualquier dominio.
Los RSS de fuentes.json se aceptan siempre.
"""
import base64
import email.utils
import hashlib
import json
import re
import ssl
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "data" / "fuentes.json"
BUSQUEDAS = RAIZ / "data" / "busquedas.txt"
PERIODISTAS = RAIZ / "data" / "periodistas.json"
CRUDO = RAIZ / "data" / "crudo.json"
DIAS = 7
MAX_POR_FEED = 150
TIMEOUT = 25
REINTENTOS = 4
UA = "Mozilla/5.0 (compatible; MotorSodaRastrillo/1.0)"
ART = timezone(timedelta(hours=-3))
GNEWS = "https://news.google.com/rss/search?q={q}&hl=es-419&gl=AR&ceid=AR:es-419"


def contexto_ssl():
    """Contexto SSL normal; si Python no trae certificados (Python de python.org en Mac), usa los del sistema."""
    ctx = ssl.create_default_context()
    if not ctx.cert_store_stats().get("x509_ca"):
        for ruta in ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"):
            if Path(ruta).exists():
                return ssl.create_default_context(cafile=ruta)
    return ctx


CTX = contexto_ssl()


def ahora():
    return datetime.now(ART)


def iso(dt):
    return dt.astimezone(ART).strftime("%Y-%m-%dT%H:%M:%S-03:00")


def normaliza(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def hash_corto(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


def dominio_de(url):
    d = urllib.parse.urlparse(url).netloc.lower()
    return d[4:] if d.startswith("www.") else d


def descargar(url):
    """GET con reintentos y backoff ante 429/5xx/errores de red. Devuelve bytes."""
    espera = 3
    ultimo = None
    for i in range(REINTENTOS):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            ultimo = "HTTP %d" % e.code
            if e.code != 429 and e.code < 500:
                break
        except Exception as e:  # timeout, DNS, SSL...
            ultimo = type(e).__name__ + ": " + str(e)[:80]
            if "CERTIFICATE" in str(e):
                break
        if i < REINTENTOS - 1:
            time.sleep(espera)
            espera *= 2
    raise RuntimeError(ultimo or "error")


def texto(el, *nombres):
    for n in nombres:
        x = el.find(n)
        if x is not None and (x.text or "").strip():
            return x.text.strip()
    return ""


def parsea_fecha(s):
    if not s:
        return None
    try:
        dt = email.utils.parsedate_to_datetime(s)
    except Exception:
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def items_de(xml_bytes):
    """Devuelve lista de dicts crudos (titulo, link, fecha, medio_src, dominio_src) de RSS o Atom."""
    raiz = ET.fromstring(xml_bytes)
    salida = []
    for it in raiz.iter("item"):
        src = it.find("source")
        salida.append({
            "titulo": re.sub(r"\s+", " ", texto(it, "title")),
            "link": texto(it, "link") or texto(it, "guid"),
            "fecha": parsea_fecha(texto(it, "pubDate", "{http://purl.org/dc/elements/1.1/}date")),
            "medio_src": (src.text or "").strip() if src is not None else "",
            "dominio_src": dominio_de(src.get("url", "")) if src is not None else "",
        })
    for it in raiz.iter("{http://www.w3.org/2005/Atom}entry"):
        ns = "{http://www.w3.org/2005/Atom}"
        l = it.find(ns + "link")
        salida.append({
            "titulo": re.sub(r"\s+", " ", texto(it, ns + "title")),
            "link": (l.get("href") if l is not None else "") or "",
            "fecha": parsea_fecha(texto(it, ns + "published", ns + "updated")),
            "medio_src": "", "dominio_src": "",
        })
    return salida


def resuelve_google(link):
    """Intenta sacar la URL real de un link de Google Noticias (formato viejo). Si no, None."""
    m = re.search(r"/articles/([A-Za-z0-9_-]+)", link)
    if not m:
        return None
    b = m.group(1)
    try:
        raw = base64.urlsafe_b64decode(b + "=" * (-len(b) % 4))
    except Exception:
        return None
    u = re.search(rb"https?://[\x21-\x7e]+", raw)
    return u.group(0).decode("ascii", "ignore") if u else None


def cargar_fuentes():
    return json.loads(FUENTES.read_text(encoding="utf-8"))


def cargar_busquedas():
    res = []
    for linea in BUSQUEDAS.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        abierta = linea.startswith("!")
        res.append((linea.lstrip("!").strip(), abierta))
    return res


def cargar_periodistas():
    try:
        return json.loads(PERIODISTAS.read_text(encoding="utf-8"))
    except Exception:
        return []


def dominio_coincide(dom, pdom):
    return bool(pdom) and (dom == pdom or dom.endswith("." + pdom))


def apellido_en(titulo, nombre):
    """True si el titulo contiene algun apellido (palabras del nombre salvo la primera, de 4+ letras)."""
    t = " " + normaliza(titulo) + " "
    toks = [normaliza(x) for x in nombre.split()[1:]]
    return any(len(x) >= 4 and " " + x + " " in t for x in toks)


def etiqueta_per(p):
    return "periodista:" + p["nombre"]


def tarea_periodista(p, fuentes_por_dom):
    """Busqueda en Google Noticias por el nombre entre comillas, ultimas 48 h.
    No se descarta por la regla del exterior si el dominio es el del periodista."""
    q = urllib.parse.quote_plus('"' + p["nombre"] + '" when:2d')
    notas = []
    for it in items_de(descargar(GNEWS.format(q=q))):
        if not it["titulo"] or not it["link"]:
            continue
        medio, dom = it["medio_src"], it["dominio_src"]
        titulo = it["titulo"]
        if medio and titulo.endswith(" - " + medio):
            titulo = titulo[: -len(medio) - 3].strip()
        f = fuentes_por_dom.get(dom)
        if not (dom.endswith(".ar") or f or dominio_coincide(dom, p.get("dominio"))):
            continue
        notas.append(armar(titulo, it["link"], resuelve_google(it["link"]), it["fecha"],
                           (f["nombre"] if f else medio) or dom, dom,
                           f["tipo"] if f else "medio", bool(f and f["lista_seria"]), etiqueta_per(p)))
    return notas, 0


def marcar_periodistas(notas, periodistas):
    """Recalcula el campo 'periodistas' de cada nota."""
    for n in notas:
        marcados = []
        for p in periodistas:
            dom_ok = dominio_coincide(n.get("dominio", ""), p.get("dominio"))
            ape = apellido_en(n["titulo"], p["nombre"])
            de_busqueda = etiqueta_per(p) in n.get("busquedas", [])
            if (de_busqueda and (dom_ok or ape)) or (dom_ok and ape):
                marcados.append(p["nombre"])
        n["periodistas"] = marcados


def tarea_rss(f):
    """Un feed RSS directo de fuentes.json."""
    notas = []
    for it in items_de(descargar(f["rss"]))[:MAX_POR_FEED]:
        if not it["titulo"] or not it["link"]:
            continue
        notas.append(armar(it["titulo"], it["link"], None, it["fecha"], f["nombre"], f["dominio"],
                           f["tipo"], f["lista_seria"], None))
    return notas


def tarea_gnews(consulta, abierta, ventana, fuentes_por_dom, etiqueta):
    q = urllib.parse.quote_plus(consulta + " when:" + ventana)
    notas, descartadas = [], 0
    for it in items_de(descargar(GNEWS.format(q=q))):
        if not it["titulo"] or not it["link"]:
            continue
        medio, dom = it["medio_src"], it["dominio_src"]
        titulo = it["titulo"]
        if medio and titulo.endswith(" - " + medio):
            titulo = titulo[: -len(medio) - 3].strip()
        f = fuentes_por_dom.get(dom)
        if not abierta and not (dom.endswith(".ar") or f):
            descartadas += 1
            continue
        notas.append(armar(titulo, it["link"], resuelve_google(it["link"]), it["fecha"],
                           (f["nombre"] if f else medio) or dom, dom,
                           f["tipo"] if f else "medio", bool(f and f["lista_seria"]), etiqueta))
    return notas, descartadas


def armar(titulo, url, url_original, fecha, medio, dominio, tipo, seria, busqueda):
    return {
        "id": hash_corto(url), "titulo": titulo, "medio": medio, "dominio": dominio, "url": url,
        "url_original": url_original, "fecha": iso(fecha) if fecha else None,
        "fuente_tipo": tipo, "lista_seria": seria,
        "busquedas": [busqueda] if busqueda else [], "visto": None,
    }


def prefiere(a, b):
    """Entre dos duplicados, conserva el que tiene URL directa (no de Google)."""
    ga = "news.google.com" in a["url"]
    gb = "news.google.com" in b["url"]
    if ga != gb:
        return b if ga else a
    return a


def fusionar(lotes, inicio):
    """Une notas, deduplicando por URL y por titulo normalizado."""
    por_url, por_titulo, orden = {}, {}, []
    for n in lotes:
        if not n.get("fecha"):
            n["fecha"] = iso(inicio)
        clave_t = normaliza(n["titulo"])
        previo = por_url.get(n["url"]) or por_titulo.get(clave_t)
        if previo is None:
            por_url[n["url"]] = n
            por_titulo[clave_t] = n
            orden.append(n)
            continue
        ganador = prefiere(previo, n)
        otro = n if ganador is previo else previo
        ganador["busquedas"] = sorted(set(ganador["busquedas"]) | set(otro["busquedas"]))
        ganador["lista_seria"] = ganador["lista_seria"] or otro["lista_seria"]
        ganador["visto"] = min(filter(None, [ganador.get("visto"), otro.get("visto")]), default=None)
        if not ganador.get("url_original"):
            ganador["url_original"] = otro.get("url_original")
        if ganador is not previo:
            orden[orden.index(previo)] = ganador
        por_url[ganador["url"]] = ganador
        por_url[otro["url"]] = ganador
        por_titulo[clave_t] = ganador
    return orden


def main():
    inicio = ahora()
    sello = iso(inicio)
    fuentes = cargar_fuentes()
    por_dom = {}
    for f in fuentes:
        por_dom.setdefault(f["dominio"], f)
    errores, nuevas_lotes = [], []
    descartadas = 0

    trabajos = []
    for f in fuentes:
        if f.get("rss"):
            trabajos.append(("rss " + f["nombre"], lambda f=f: (tarea_rss(f), 0)))
        if f.get("google_site"):
            trabajos.append(("gnews site:" + f["dominio"],
                             lambda f=f: tarea_gnews("site:" + f["dominio"], True, "7d", por_dom, "site:" + f["dominio"])))
    for q, abierta in cargar_busquedas():
        trabajos.append(("gnews " + q, lambda q=q, a=abierta: tarea_gnews(q, a, "1d", por_dom, q)))

    periodistas = cargar_periodistas()
    for p in periodistas:
        trabajos.append(("periodista " + p["nombre"], lambda p=p: tarea_periodista(p, por_dom)))

    def correr(t):
        nombre, fn = t
        try:
            return nombre, fn(), None
        except Exception as e:
            return nombre, ([], 0), str(e)[:150]

    with ThreadPoolExecutor(max_workers=4) as ex:
        for nombre, (notas, desc), err in ex.map(correr, trabajos):
            if err:
                errores.append({"fuente": nombre, "error": err})
                print("ERROR", nombre, err, file=sys.stderr)
            else:
                nuevas_lotes.extend(notas)
                descartadas += desc
                print("ok %-45s %3d notas" % (nombre, len(notas)))

    for n in nuevas_lotes:
        n["visto"] = sello

    previas = []
    if CRUDO.exists():
        try:
            previas = json.loads(CRUDO.read_text(encoding="utf-8")).get("notas", [])
        except Exception as e:
            errores.append({"fuente": "crudo previo", "error": str(e)[:100]})
    ids_previos = {n["id"] for n in previas}
    titulos_previos = {normaliza(n["titulo"]) for n in previas}

    # Las previas van primero: conservan su "visto" original.
    todas = fusionar(previas + nuevas_lotes, inicio)
    limite = inicio - timedelta(days=DIAS)
    todas = [n for n in todas if datetime.fromisoformat(n["fecha"]) >= limite]
    marcar_periodistas(todas, periodistas)
    todas.sort(key=lambda n: n["fecha"], reverse=True)
    nuevas = sum(1 for n in todas if n["id"] not in ids_previos and normaliza(n["titulo"]) not in titulos_previos)

    salida = {"generado": sello, "total": len(todas), "nuevas_ultima_corrida": nuevas,
              "errores": errores, "notas": todas}
    CRUDO.parent.mkdir(exist_ok=True)
    tmp = CRUDO.with_suffix(".tmp")
    tmp.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(CRUDO)
    print("total %d | nuevas %d | errores %d | descartadas por dominio %d" % (len(todas), nuevas, len(errores), descartadas))


if __name__ == "__main__":
    main()
