#!/usr/bin/env python3
"""Arma index.html (sitio público) con la edición curada + la última hora automática.

Usa data/edicion.json (o data/edicion-prueba.json si no existe) y data/candidatos.json.
Uso: python3 scripts/armar_sitio.py
"""
import json, re, html, datetime as dt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AR = dt.timezone(dt.timedelta(hours=-3))
e = lambda s: html.escape(str(s) if s is not None else "")
SEM = {"🟢": ("ok", "Confirmado"), "🟡": ("mid", "Parcial"), "🟠": ("warn", "Sin confirmar"), "🔴": ("bad", "Falso")}
PRE = {"verde?": ("ok", "🟢 verde?"), "amarillo?": ("mid", "🟡 amarillo?"), "naranja?": ("warn", "🟠 naranja?")}
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

CSS = r"""
/* Layout: estética minimalista de los documentos internos de Soda (Estructura de roles), sobre fondo negro mica.
   Fondo blanco, wordmark "soda." en celeste con punto naranja, título en mayúsculas con filete celeste,
   secciones como paneles gris claro con franja de color a la izquierda y chip de área, fichas blancas con borde fino y etiquetas grises. */
:root{--brand:#1A8FE0;--naranja:#F26A35;--rojo:#FF4A33;--amarilloT:#F9B233;--verde:#4CC38A;--violeta:#B48CF2;
--bg:#0E0F11;--panel:#16181B;--surface:#1C1F23;--fg:#ECEEF0;--muted:#9BA3AB;--line:#2B2F35;--tag:#24282D;--accent:#4DAEF0;--soft:#16222E;
--azulbg:#12283B;--naranjabg:#3A2116;--amarillobg:#352B12;--violetabg:#2A2140;
--ok:#4CC38A;--mid:#F2C14E;--warn:#F28A55;--bad:#FF5A45;--okbg:#14291E;--midbg:#352B12;--warnbg:#3A2116;--badbg:#3D1A16;
--display:'Noto Sans',system-ui,sans-serif;--body:'Noto Sans',system-ui,sans-serif;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font:15px/1.55 var(--body);margin:0}
.band-in,main{max-width:900px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.band{padding-top:28px}
.band-in{display:flex;flex-direction:column;gap:6px}
.topline{display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap;border-bottom:3px solid var(--brand);padding-bottom:10px}
.wm{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;text-decoration:none}
.wordmark{font-weight:800;font-size:2.3rem;line-height:1;color:var(--brand);letter-spacing:-.02em}
.wordmark span{color:var(--naranja)}
.band h1{font-size:1.15rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--fg)}
.eyebrow{font-size:.85rem;color:var(--muted)}
.band .lead{color:var(--muted);margin:8px 0 0}
main{display:flex;flex-direction:column;gap:20px;padding-top:20px;padding-bottom:56px}
h1,h2,h3{font-family:var(--display);margin:0;text-wrap:balance}
h3{font-size:1.02rem;line-height:1.3;font-weight:700}
p{margin:0}
a{color:var(--accent)}
.lead{color:var(--muted);margin-top:6px}
.panel{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--stripe,var(--brand));border-radius:10px;padding:14px 16px 16px;display:flex;flex-direction:column;gap:12px;min-width:0}
.s-verde{--stripe:var(--verde)}.s-azul{--stripe:var(--brand)}.s-naranja{--stripe:var(--naranja)}.s-amarillo{--stripe:#F9B233}.s-violeta{--stripe:var(--violeta)}
.phead{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.pside{font-size:.8rem;font-weight:600;color:var(--muted)}
.chip{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:3px 8px;border-radius:4px}
.chip.azul{background:var(--azulbg);color:var(--brand)}.chip.naranja{background:var(--naranjabg);color:var(--warn)}.chip.amarillo{background:var(--amarillobg);color:var(--mid)}.chip.violeta{background:var(--violetabg);color:var(--violeta)}.chip.verde{background:var(--okbg);color:var(--ok)}
.claves{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
.claves li{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px 12px;display:flex;flex-direction:column;gap:6px}
.cf{display:flex;flex-wrap:wrap;gap:4px;font-size:0}
.cf span,.cf a{font-size:.75rem;text-decoration:none;color:var(--muted);background:var(--tag);border:1px solid var(--line);border-radius:4px;padding:1px 7px}
.barra{height:8px;background:var(--tag);border-radius:4px;overflow:hidden}.barra span{display:block;height:100%;background:var(--brand);border-radius:4px}
.temas{display:flex;flex-direction:column;gap:10px}
.tema{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:12px 14px;display:flex;flex-direction:column;gap:8px;min-width:0}
.tema>p:not([class]){color:var(--muted)}
.meta{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.sec{font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:700}
.pill{font-size:.74rem;font-weight:700;padding:2px 8px;border-radius:4px;white-space:nowrap;border:1px solid currentColor}
.pill.ok{background:var(--okbg);color:var(--ok)}.pill.mid{background:var(--midbg);color:var(--mid)}.pill.warn{background:var(--warnbg);color:var(--warn)}.pill.bad{background:var(--badbg);color:var(--bad)}
.lbl{display:block;font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;font-weight:700;color:var(--muted);margin-bottom:2px}
.pq,.prim,.idea{font-size:.9rem}
.idea{background:var(--soft);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
.idea .lbl{color:var(--brand)}
.alert{background:var(--midbg);border-radius:8px;padding:8px 12px;font-size:.86rem}
.alert .lbl{color:var(--mid)}
.alert ul,.fu{margin:0;padding-left:18px;display:flex;flex-direction:column;gap:4px}
.fu{margin-top:6px;font-size:.85rem}
.fu a{text-decoration:none;color:var(--fg)}.fu a b{color:var(--accent)}
.otras{font-size:.8rem;color:var(--muted);margin-top:6px}
details summary{cursor:pointer;font-weight:600;font-size:.84rem;color:var(--accent);min-height:30px;display:flex;align-items:center}
details summary:focus-visible,a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.ley{display:block}
.leyenda{display:flex;flex-wrap:wrap;gap:6px}
.ult{display:flex;flex-direction:column;gap:8px}
.g{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px 12px;display:flex;flex-direction:column;gap:4px;min-width:0}
.g h3{font-size:.95rem;font-weight:600}
.g .sub{font-size:.78rem;color:var(--muted)}
.aviso{background:var(--amarillobg);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:8px 12px;font-size:.86rem}
.ideaobj{display:flex;flex-direction:column;gap:6px}
.ideaobj ol,.ideaobj ul{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:3px}
footer{font-size:.8rem;color:var(--muted);border-top:1px solid var(--line);padding-top:12px;display:flex;flex-direction:column;gap:2px}
"""


def leer(ruta):
    p = BASE / ruta
    return json.loads(p.read_text()) if p.exists() else None


def link(url, txt):
    return f'<a href="{e(url)}" target="_blank" rel="noopener">{txt}</a>' if url else txt


def fuentes(fs):
    return "".join(f'<li>{link(f.get("url"), "<b>" + e(f.get("medio")) + "</b> · " + e(f.get("titulo")))}</li>' for f in fs or [])


def rojo(s):
    """Escapa el texto y pasa *así* a destacado en rojo, como en las placas de Soda."""
    import re as _re
    return _re.sub(r"\*(.+?)\*", r'<span class="rojo">\1</span>', e(s))


def idea(i):
    if not i:
        return ""
    if isinstance(i, str):
        return f'<p class="idea"><span class="lbl">Idea de carrusel</span> {e(i)}</p>'
    partes = []
    for k, lab in (("formato", "Formato"), ("enfoque", "Enfoque"), ("portada", "Portada"), ("gancho", "Gancho"), ("copy", "Copy del posteo")):
        if i.get(k):
            partes.append(f'<p><b>{lab}.</b> {rojo(i[k])}</p>')
    if i.get("placas"):
        partes.append("<div><b>Placas</b><ol>" + "".join(f"<li>{rojo(p)}</li>" for p in i["placas"]) + "</ol></div>")
    if i.get("audiovisual"):
        av = i["audiovisual"]
        av = "".join(f"<li>{e(x)}</li>" for x in av) if isinstance(av, list) else f"<li>{e(av)}</li>"
        partes.append(f"<div><b>Audiovisual y fotos</b><ul>{av}</ul></div>")
    if i.get("a_chequear"):
        ac = i["a_chequear"]
        ac = "".join(f"<li>{e(x)}</li>" for x in ac) if isinstance(ac, list) else f"<li>{e(ac)}</li>"
        partes.append(f"<div><b>A chequear antes de publicar</b><ul>{ac}</ul></div>")
    return f'<div class="idea ideaobj"><span class="lbl">Idea de carrusel</span>{"".join(partes)}</div>'


def tema(t):
    cls, lab = SEM.get(t.get("semaforo"), ("mid", ""))
    prim = t.get("primaria")
    prim_html = ""
    if prim:
        nom = prim.get("nombre") or f'{prim.get("medio", "")} · {prim.get("titulo", "")}'
        prim_html = '<p class="prim"><span class="lbl">Fuente primaria</span> ' + link(prim.get("url"), e(nom)) + "</p>"
    al = "".join(f"<li>{e(a)}</li>" for a in t.get("alertas") or [])
    otras = ", ".join(e(o) if isinstance(o, str) else e(o.get("medio", "")) for o in t.get("otras") or [])
    fs = t.get("fuentes") or []
    mas = f' + {len(t["otras"])} más' if t.get("otras") else ""
    return f'''<article class="tema" id="{e(t.get("id"))}">
  <div class="meta"><span class="sec">{e(t.get("seccion", ""))}</span><span class="pill {cls}">{e(t.get("semaforo", ""))} {lab}</span></div>
  <h3>{e(t.get("titulo"))}</h3>
  <p>{e(t.get("resumen"))}</p>
  {f'<p class="pq"><span class="lbl">Por qué importa</span> {e(t["por_que_importa"])}</p>' if t.get("por_que_importa") else ""}
  {prim_html}
  {f'<details><summary>Fuentes ({len(fs)}{mas})</summary><ul class="fu">{fuentes(fs)}</ul>' + (f'<p class="otras">También: {otras}</p>' if otras else "") + "</details>" if fs else ""}
  {f'<div class="alert"><span class="lbl">Ojo antes de publicar</span><ul>{al}</ul></div>' if al else ""}
  {idea(t.get("idea_carrusel"))}
</article>'''


SECCIONES = [
    ("Política", "politica", "naranja"),
    ("Juventud y educación", "juventud", "violeta"),
    ("Sociedad y cultura", "sociedad", "verde"),
    ("Economía", "economia", "amarillo"),
]
MAPA_SECCION = {"politica": 0, "juventud y educacion": 1, "juventud": 1, "educacion": 1,
                "sociedad y cultura": 2, "sociedad": 2, "cultura": 2, "economia": 3}


def sin_tildes(t):
    import unicodedata
    t = unicodedata.normalize("NFD", (t or "").lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn").strip()


def indice_seccion(t):
    return MAPA_SECCION.get(sin_tildes(t.get("seccion")), 2)


RUIDO_AGENDA = re.compile(r"\bdolar|riesgo pais|\bbonos?\b|\bacciones\b|\badrs?\b|merval|wall street|mercados?\b|cotiza|brecha cambiaria|plazo fijo|a cuanto (cerro|cotiza|se vende|esta)|cotiza(n)? (hoy|este)|(dolar|euro|real) (blue|oficial|hoy).{0,25}(hoy|lunes|martes|miercoles|jueves|viernes|sabado|domingo)|euro blue|cuando cobro|que jubilados cobran|cronograma de pago|fecha de cobro|horoscopo|clima (para|en)")
COMUNES = {"Milei", "Javier", "Gobierno", "Argentina", "Presidente", "Senado", "Congreso", "Nación", "Estado", "Buenos", "Aires", "Hoy", "Cómo", "Qué", "Quién", "Toto", "Luis"}


def _propios(g):
    """Nombres propios de los títulos del grupo, sin los muy comunes."""
    out = set()
    for n in g.get("notas", [])[:8]:
        out |= {w for w in re.findall(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{3,}", n.get("titulo", "")) if w not in COMUNES}
    return out


def _palabras(g):
    out = set()
    for n in g.get("notas", [])[:8]:
        out |= {w for w in re.findall(r"[a-z0-9]{4,}", sin_tildes(n.get("titulo", "")))}
    return out


def _argentino(g):
    """Al menos una nota de un medio serio o de un dominio .ar."""
    return any(n.get("lista_seria") or str(n.get("dominio", "")).endswith(".ar") for n in g.get("notas", []))


def fusionar_agenda(gs):
    """Junta grupos del mismo tema (nombre propio en común y vocabulario parecido) para que la agenda no repita."""
    res = []
    for g in gs:
        pg, wg = _propios(g), _palabras(g)
        destino = None
        for r in res:
            if pg & r["_prop"] and len(wg & r["_pal"]) / max(1, len(wg | r["_pal"])) >= 0.12:
                destino = r
                break
        if destino:
            urls = {x.get("url") for x in destino["notas"]}
            destino["notas"] = destino["notas"] + [n for n in g["notas"] if n.get("url") not in urls]
            destino["cant_notas"] += g["cant_notas"]
            destino["cant_medios"] = max(destino["cant_medios"], g["cant_medios"], len({n.get("dominio") for n in destino["notas"]}))
        else:
            res.append({**g, "notas": list(g["notas"]), "_prop": pg, "_pal": wg})
    return sorted(res, key=lambda g: (g["cant_medios"], g["cant_notas"]), reverse=True)


def panel_agenda(cand):
    """Los 10 grupos de las últimas 24 h cubiertos por más medios distintos."""
    gs = []
    if cand and cand.get("candidatos"):
        lim = (dt.datetime.now(AR) - dt.timedelta(hours=24)).isoformat(timespec="minutes")
        gs = [g for g in cand["candidatos"] if g.get("ultima", "") >= lim and g.get("notas")
              and not RUIDO_AGENDA.search(sin_tildes(g["notas"][0].get("titulo", ""))) and _argentino(g)]
        gs = fusionar_agenda(sorted(gs, key=lambda g: (g["cant_medios"], g["cant_notas"]), reverse=True))[:10]
    if not gs:
        cuerpo = '<p class="lead">Sin datos por ahora.</p>'
    else:
        tope = max(g["cant_medios"] for g in gs) or 1
        cuerpo = '<div class="ult">'
        for k, g in enumerate(gs):
            if k == 5:
                cuerpo += '</div><details class="mas"><summary>Ver 5 temas más</summary><div class="ult">'
            ns = g["notas"][:5]
            lis = "".join(f'<li>{link(n.get("url"), "<b>" + e(n.get("medio")) + "</b> · " + e(n.get("titulo")))}</li>' for n in ns)
            pct = max(4, round(100 * g["cant_medios"] / tope))
            cuerpo += f'''<article class="g"><h3>{e(g["notas"][0]["titulo"])}</h3>
<div class="barra" aria-hidden="true"><span style="width:{pct}%"></span></div>
<span class="sub">{g["cant_medios"]} medios · {g["cant_notas"]} notas</span>
<details><summary>Links ({len(ns)})</summary><ul class="fu">{lis}</ul></details></article>'''
        cuerpo += "</div></details>" if len(gs) > 5 else "</div>"
    return f'<section class="panel s-azul" id="agenda"><div class="phead"><h2 class="chip azul">Agenda general</h2><span class="pside">Lo que cubren todos los medios</span></div>{cuerpo}</section>\n'


def ficha_periodista(p, auto=False):
    notas = "".join(f'<li>{link(n.get("url"), e(n.get("titulo")) + (" · " + e(n.get("medio")) if n.get("medio") else ""))}</li>' for n in p.get("notas") or [])
    temas = "".join(f"<span>{e(t)}</span>" for t in p.get("temas") or [])
    return f'''<article class="tema">
  <div class="meta"><span class="sec">{e(p.get("rol", ""))}</span>{'<span class="sub">Automático, sin curar</span>' if auto else ""}</div>
  <h3>{e(p.get("nombre"))}</h3>
  {f'<p class="cf">{temas}</p>' if temas else ""}
  {f'<p>{e(p["posicion"])}</p>' if p.get("posicion") else ""}
  {f'<ul class="fu">{notas}</ul>' if notas else '<p class="lead">Sin publicaciones en las últimas 48 h</p>'}
</article>'''


def panel_periodistas(ed_pers, auto_pers, ident=True):
    """ed_pers: periodistas curados de la edición; auto_pers: lista (ya armada) de los que faltan, automáticos."""
    fichas = "".join(ficha_periodista(p) for p in ed_pers) + "".join(ficha_periodista(p, True) for p in auto_pers)
    if not fichas:
        return ""
    return f'<section class="panel s-azul"{" id=periodistas" if ident else ""}><div class="phead"><h2 class="chip azul">Periodistas</h2><span class="pside">Qué publican y cómo se posicionan</span></div><div class="temas">{fichas}</div></section>\n'


def auto_periodistas(excluir, crudo_notas):
    lista = leer("data/periodistas.json") or []
    lim = (dt.datetime.now(AR) - dt.timedelta(hours=48)).isoformat(timespec="minutes")
    out = []
    for p in lista:
        if p["nombre"] in excluir:
            continue
        ns = [n for n in crudo_notas if p["nombre"] in (n.get("periodistas") or []) and (n.get("fecha") or "") >= lim]
        ns.sort(key=lambda n: n["fecha"], reverse=True)
        if ns:  # los que no publicaron en 48 h no aparecen
            out.append({"nombre": p["nombre"], "rol": p.get("rol", ""), "notas": ns[:5]})
    return out


def seccion_edicion(ed, home=False, cand=None, crudo_notas=None):
    aviso = ""
    if ed.get("tipo") == "hipotetica":
        aviso = '<section><p class="aviso"><b>Edición hipotética.</b> ' + e(ed.get("nota") or "Es una prueba: la oficial sale a las 11 h.") + '</p></section>\n'
    return aviso + _seccion_edicion(ed, home, crudo_notas or [], panel_agenda(cand) if home else "")


def _seccion_edicion(ed, home=False, crudo_notas=None, agenda_html=""):
    claves = "".join(
        f'<li><p>{e(c.get("texto"))}</p><p class="cf">' + " · ".join(link(f.get("url"), e(f.get("medio"))) for f in c.get("fuentes") or []) + "</p></li>"
        for c in ed.get("claves") or [])
    pc = "".join(f'''<article class="tema chk"><div class="meta"><span class="pill mid">🟡 Parcial</span></div><h3>{e(p.get("titulo"))}</h3><p>{e(p.get("resumen"))}</p>{f'<div class="alert"><span class="lbl">Qué falta</span><p>{e(p["falta"])}</p></div>' if p.get("falta") else ""}{f'<details><summary>Fuentes ({len(p["fuentes"])})</summary><ul class="fu">{fuentes(p["fuentes"])}</ul></details>' if p.get("fuentes") else ""}</article>''' for p in ed.get("para_chequear") or [])
    out = ""
    if claves:
        out += f'<section class="panel s-azul"><div class="phead"><h2 class="chip azul">Lo que tenés que saber</h2><span class="pside">Claves de la edición</span></div><ol class="claves">{claves}</ol></section>\n'
    temas = ed.get("temas") or []
    if temas:
        if home:
            out += '<section><nav class="nav secciones">' + "".join(f'<a class="btn" href="#{i}">{e(n)}</a>' for n, i, _ in SECCIONES) + "</nav></section>\n"
        grupos = [[] for _ in SECCIONES]
        for t in temas:
            grupos[indice_seccion(t)].append(t)
        for (nombre, ident, color), ts in zip(SECCIONES, grupos):
            if not ts and not home:
                continue
            cont = "\n".join(tema(t) for t in ts) if ts else '<p class="lead">Sin temas curados en esta edición</p>'
            out += f'<section class="panel s-{color}"{f" id={ident}" if home else ""}><div class="phead"><h2 class="chip {color}">{e(nombre)}</h2><span class="pside">Chequeados con semáforo</span></div><div class="temas">{cont}</div></section>\n'
    out += agenda_html
    ed_pers = ed.get("periodistas") or []
    auto = auto_periodistas({p.get("nombre") for p in ed_pers}, crudo_notas or []) if home else []
    out += panel_periodistas(ed_pers, auto, home)
    if pc:
        out += f'<section class="panel s-amarillo"><div class="phead"><h2 class="chip amarillo">Para chequear</h2><span class="pside">Una sola fuente</span></div><div class="temas">{pc}</div></section>\n'
    return out or '<section><p class="lead">Todavía no hay edición curada.</p></section>'


def hora(iso):
    try:
        d = dt.datetime.fromisoformat(iso).astimezone(AR)
        return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}, {d:%H:%M} h", d
    except Exception:
        return iso or "s/d", None


def seccion_ultima(cand):
    if not cand or not cand.get("candidatos"):
        return '<section class="panel s-violeta"><div class="phead"><h2 class="chip violeta">Última hora</h2><span class="pside">Automático, sin curar</span></div><p class="lead">Sin datos por ahora.</p></section>'
    lim = (dt.datetime.now(AR) - dt.timedelta(hours=12)).isoformat(timespec="minutes")
    gs = [g for g in cand["candidatos"] if g.get("ultima", "") >= lim] or cand["candidatos"]
    gs = [g for g in gs if g.get("notas") and not RUIDO_AGENDA.search(sin_tildes(g["notas"][0].get("titulo", "")))]
    gs = sorted(gs, key=lambda g: (g["cant_medios"], len(g.get("medios_serios") or [])), reverse=True)[:15]
    items = ""
    for g in gs:
        cls, lab = PRE.get(g["pre_semaforo"], ("warn", g["pre_semaforo"]))
        ns = g.get("notas") or []
        titulo = ns[0]["titulo"] if ns else ""
        lis = "".join(f'<li>{link(n.get("url"), "<b>" + e(n.get("medio")) + "</b> · " + e(n.get("titulo")))}</li>' for n in ns[:5])
        items += f'''<article class="g"><div class="meta"><span class="pill {cls}">{e(lab)}</span><span class="sub">{g["cant_medios"]} medios · {g["cant_notas"]} notas</span></div>
<h3>{e(titulo)}</h3><span class="sub">Pre-chequeo automático, sin revisar</span>
<details><summary>Links ({len(ns[:5])})</summary><ul class="fu">{lis}</ul></details></article>'''
    return f'''<section class="panel s-violeta"><div class="phead"><h2 class="chip violeta">Última hora</h2><span class="pside">Automático, sin curar</span></div>
<p class="aviso">Esto no está curado: lo arma un script con los temas más cubiertos de las últimas 12 horas. El semáforo es un pre-chequeo automático, sin revisar por una persona.</p>
<div class="ult" style="margin-top:12px">{items}</div></section>'''


def ediciones_por_fecha():
    """Lee data/ediciones/*.json y las agrupa por fecha (AAAA-MM-DD), de la más nueva a la más vieja."""
    out = {}
    carpeta = BASE / "data/ediciones"
    for f in sorted(carpeta.glob("*.json")) if carpeta.exists() else []:
        ed = leer(f"data/ediciones/{f.name}")
        if not ed or ed.get("tipo") == "prueba":
            continue
        fecha = (ed.get("id") or f.stem)[:10]
        out.setdefault(fecha, []).append(ed)
    for v in out.values():
        v.sort(key=lambda x: x.get("id", ""), reverse=True)
    return dict(sorted(out.items(), reverse=True))


def fecha_larga(fecha):
    d = dt.date.fromisoformat(fecha)
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]}"


def pagina(titulo_h1, lead, cuerpo, nav, ahora_txt, notas, medios, prefijo=""):
    titulo = "La Sodería · Motor Soda"
    desc = "Lo que pasó, chequeado: temas del día con semáforo de fuentes y última hora automática."
    return f'''<!doctype html>
<html lang="es-AR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<title>{titulo}</title>
<meta property="og:title" content="{titulo}"><meta property="og:description" content="{desc}"><meta property="og:type" content="website"><meta property="og:image" content="https://la-soderia.github.io/img/og.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="description" content="{desc}">
<link rel="icon" href="{prefijo}img/logo-color.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600;700;800&display=swap">
<style>{CSS}
.nav{{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}}
.btn{{font:inherit;font-weight:600;font-size:.85rem;background:var(--surface);cursor:pointer;display:inline-flex;align-items:center;min-height:38px;padding:6px 14px;border-radius:6px;border:1px solid var(--line);color:var(--fg);text-decoration:none}}
.btn:hover{{border-color:var(--brand)}}
.btn.on{{background:var(--brand);border-color:var(--brand);color:#fff}}
.dia{{font-size:1.05rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;border-bottom:2px solid var(--brand);padding-bottom:6px}}
.rojo{{color:var(--bad);font-weight:800}}
.ed-sep{{font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);border-top:1px solid var(--line);padding-top:12px}}
</style></head><body>
<header class="band"><div class="band-in">
  <div class="topline"><a class="wm" href="{prefijo}index.html" aria-label="Soda, ir a hoy"><span class="wordmark">soda<span>.</span></span>{f"<h1>{titulo_h1}</h1>" if titulo_h1 else ""}</a><span class="eyebrow">Motor de relevamiento • La Sodería</span></div>
  <p class="lead">{lead}</p>
  <nav class="nav">{nav}</nav>
</div></header>
<main>
<section class="ley"><div class="leyenda"><span class="pill ok">🟢 2+ fuentes serias o primaria</span><span class="pill mid">🟡 una sola fuente</span><span class="pill warn">🟠 solo X: no se publica</span><span class="pill bad">🔴 falso</span></div></section>
{cuerpo}
<footer><span><b>Actualizado:</b> {e(ahora_txt)}</span><span>{notas} notas leídas de {medios} medios.</span><span>Los links de Google Noticias redirigen a la nota original.</span></footer>
</main></body></html>
'''


def bloque_ediciones(eds):
    """Una o más ediciones del mismo día: la más nueva arriba."""
    out = ""
    for k, ed in enumerate(eds):
        txt, _ = hora(ed.get("generado"))
        hh = (ed.get("id") or "")[11:13]
        if len(eds) > 1:
            out += f'<p class="ed-sep">Edición de las {e(hh)} h</p>\n'
        out += seccion_edicion(ed)
    return out


def main():
    cand = leer("data/candidatos.json")
    crudo = leer("data/crudo.json") or {}
    notas = crudo.get("notas") or []
    medios = len({n.get("dominio") for n in notas})
    ahora = dt.datetime.now(AR)
    ahora_txt, _ = hora(ahora.isoformat())
    hoy = ahora.date().isoformat()
    ayer = (ahora.date() - dt.timedelta(days=1)).isoformat()
    por_fecha = ediciones_por_fecha()

    def nav(activo, prefijo=""):
        b = f'<a class="btn{" on" if activo == "hoy" else ""}" href="{prefijo}index.html">Hoy</a>'
        b += f'<a class="btn{" on" if activo == "ayer" else ""}" href="{prefijo}ayer.html">Noticias de ayer</a>'
        b += f'<a class="btn" href="{prefijo}index.html#periodistas">Periodistas</a>'
        b += f'<a class="btn{" on" if activo == "archivo" else ""}" href="{prefijo}archivo.html">Archivo</a>'
        return b

    # Hoy: solo ediciones de hoy + última hora automática.
    eds_hoy = por_fecha.get(hoy, [])
    if eds_hoy:
        txt, _ = hora(eds_hoy[0].get("generado"))
        lead = f"Última edición curada: {e(txt)}."
        cuerpo = seccion_edicion(eds_hoy[0], True, cand, notas)
        if len(eds_hoy) > 1:
            cuerpo += '<details class="ed-sep"><summary>Ver también las ediciones anteriores de hoy</summary>' + bloque_ediciones(eds_hoy[1:]) + "</details>"
    else:
        lead = "La edición curada de hoy sale a las 11 h. Mientras tanto, abajo tenés la última hora automática."
        cuerpo = panel_agenda(cand) + panel_periodistas([], auto_periodistas(set(), notas))
    cuerpo += seccion_ultima(cand)
    (BASE / "index.html").write_text(pagina("", lead, cuerpo, nav("hoy"), ahora_txt, len(notas), medios))

    # Ayer y anteayer (para el lunes: sábado y domingo relevados).
    eds_ayer = por_fecha.get(ayer, [])
    anteayer = (ahora.date() - dt.timedelta(days=2)).isoformat()
    def boton_dia(fecha):
        d = dt.date.fromisoformat(fecha)
        return f"{DIAS[d.weekday()].capitalize()} {d.day:02d}/{d.month:02d}"

    botones, paneles = "", ""
    for k, fecha in enumerate((ayer, anteayer)):
        eds = por_fecha.get(fecha, [])
        botones += f'<button type="button" class="btn{" on" if k == 0 else ""}" data-dia="d{fecha}" id="b{fecha}">{e(boton_dia(fecha))}</button>'
        contenido = bloque_ediciones(eds) if eds else '<section><p class="lead">No hay ediciones curadas de ese día.</p></section>\n'
        paneles += f'<div class="panel-dia" id="d{fecha}"{"" if k == 0 else " hidden"}><h2 class="dia">{e(boton_dia(fecha))}</h2>{contenido}</div>\n'
    cuerpo = f'''<section><nav class="nav dias">{botones}</nav></section>
{paneles}
<script>
document.querySelectorAll('.dias .btn').forEach(function(b){{
  b.addEventListener('click',function(){{
    document.querySelectorAll('.dias .btn').forEach(function(x){{x.classList.toggle('on',x===b)}});
    document.querySelectorAll('.panel-dia').forEach(function(p){{p.hidden=(p.id!==b.dataset.dia)}});
  }});
}});
</script>'''
    lead = "Elegí el día: las ediciones curadas de los dos días anteriores."
    (BASE / "ayer.html").write_text(pagina("Noticias de ayer", lead, cuerpo, nav("ayer"), ahora_txt, len(notas), medios))

    # Archivo: una página por día + índice.
    (BASE / "archivo").mkdir(exist_ok=True)
    items = ""
    for fecha, eds in por_fecha.items():
        (BASE / f"archivo/{fecha}.html").write_text(pagina(f"Edición del {fecha_larga(fecha)}", f"{len(eds)} edición(es) curada(s).", bloque_ediciones(eds), nav("archivo", "../"), ahora_txt, len(notas), medios, prefijo="../"))
        temas = sum(len(x.get("temas") or []) for x in eds)
        items += f'<li><a href="archivo/{fecha}.html"><b>{e(fecha_larga(fecha).capitalize())}</b></a> · {len(eds)} edición(es), {temas} temas</li>'
    cuerpo = f'<section class="panel s-azul"><div class="phead"><h2 class="chip azul">Todas las ediciones</h2></div><ul class="fu">{items or "<li>Todavía no hay ediciones.</li>"}</ul></section>'
    (BASE / "archivo.html").write_text(pagina("Archivo", "Todas las ediciones curadas, por día.", cuerpo, nav("archivo"), ahora_txt, len(notas), medios))
    print(f"ok | hoy {len(eds_hoy)} | ayer {len(eds_ayer)} | días en archivo {len(por_fecha)}")


if __name__ == "__main__":
    main()
