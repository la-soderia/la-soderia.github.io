#!/usr/bin/env python3
"""Arma index.html (sitio público) con la edición curada + la última hora automática.

Usa data/edicion.json (o data/edicion-prueba.json si no existe) y data/candidatos.json.
Uso: python3 scripts/armar_sitio.py
"""
import json, html, datetime as dt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AR = dt.timezone(dt.timedelta(hours=-3))
e = lambda s: html.escape(str(s) if s is not None else "")
SEM = {"🟢": ("ok", "Confirmado"), "🟡": ("mid", "Parcial"), "🟠": ("warn", "Sin confirmar"), "🔴": ("bad", "Falso")}
PRE = {"verde?": ("ok", "🟢 verde?"), "amarillo?": ("mid", "🟡 amarillo?"), "naranja?": ("warn", "🟠 naranja?")}
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

CSS = r"""
/* Layout: banda celeste de marca con logo y navegación; debajo una columna de lectura con fichas por tema.
   Paleta e identidad: Manual de Identidad de Soda (celeste #0A7DC8, cian #05B2E8, rojo #D8230B, naranja #E65019, amarillo #F9B233, celeste claro #BCE3F9, azul #144488, gris #4D5B59).
   Tipografía de marca: Right Grotesk; en la web se usa Archivo (ancho variable) como reemplazo libre. */
:root{--brand:#097DC8;--cian:#05B2E8;--rojo:#D8230B;--naranja:#E65019;--amarillo:#F9B233;--navy:#144488;--gris:#4D5B59;
--bg:#F2F8FC;--surface:#ffffff;--fg:#0F2440;--muted:#4D5B59;--line:#D4E7F4;--accent:#0A7DC8;--soft:#E3F2FC;
--ok:#1d7f46;--mid:#8a6300;--warn:#b5520f;--bad:#D8230B;--okbg:#e2f3e8;--midbg:#FDF0D3;--warnbg:#fde7d6;--badbg:#fbe1df;
--display:'Archivo',system-ui,sans-serif;--body:'Archivo',system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0B1830;--surface:#12264A;--fg:#EAF4FB;--muted:#A9BCC9;--line:#21406B;--accent:#05B2E8;--soft:#173560;--ok:#5fd08e;--mid:#F9B233;--warn:#f0955a;--bad:#FF6B52;--okbg:#173527;--midbg:#3a3015;--warnbg:#3d2617;--badbg:#45201b;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0B1830;--surface:#12264A;--fg:#EAF4FB;--muted:#A9BCC9;--line:#21406B;--accent:#05B2E8;--soft:#173560;--ok:#5fd08e;--mid:#F9B233;--warn:#f0955a;--bad:#FF6B52;--okbg:#173527;--midbg:#3a3015;--warnbg:#3d2617;--badbg:#45201b;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font:16px/1.55 var(--body);font-variation-settings:"wdth" 100;margin:0}
.band{background:var(--brand);color:#fff;margin-top:calc(-1 * env(safe-area-inset-top,0px));padding-top:calc(env(safe-area-inset-top,0px) + 20px);padding-bottom:26px}
.band-in,main{max-width:720px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.band-in{display:flex;flex-direction:column;gap:10px}
.logo{display:block;width:150px;height:auto}
.band h1{color:#fff;font-size:clamp(1.9rem,6vw,2.7rem);line-height:1;font-weight:900;font-stretch:75%;font-variation-settings:"wdth" 75;text-transform:uppercase;letter-spacing:-.005em}
.band .lead{color:#E3F2FC;margin:0}
.eyebrow{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;font-weight:600;font-variation-settings:"wdth" 125;color:#BCE3F9}
main{display:flex;flex-direction:column;gap:32px;padding-top:26px;padding-bottom:64px}
h1,h2,h3{font-family:var(--display);margin:0;text-wrap:balance}
h2{font-size:1.35rem;margin-bottom:12px;font-weight:900;font-variation-settings:"wdth" 75;text-transform:uppercase;color:var(--accent);letter-spacing:.01em}
h3{font-size:1.22rem;line-height:1.2;font-weight:800;font-variation-settings:"wdth" 85}
p{margin:0}
a{color:var(--accent)}
.lead{color:var(--muted);margin-top:8px}
.stats{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:14px;font-size:.85rem;color:var(--muted);font-variant-numeric:tabular-nums}
.stats b{color:var(--fg)}
.claves{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.claves li{background:var(--surface);border-left:4px solid var(--rojo);border-radius:4px 10px 10px 4px;padding:12px 14px;display:flex;flex-direction:column;gap:4px}
.cf{font-size:.82rem}
.cf a{text-decoration:none;font-weight:600}
.temas{display:flex;flex-direction:column;gap:14px}
.tema{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:10px;min-width:0}
.meta{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.sec{font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--naranja);font-weight:700;font-variation-settings:"wdth" 125}
.pill{font-size:.78rem;font-weight:700;padding:3px 10px;border-radius:99px;white-space:nowrap}
.pill.ok{background:var(--okbg);color:var(--ok)}.pill.mid{background:var(--midbg);color:var(--mid)}.pill.warn{background:var(--warnbg);color:var(--warn)}.pill.bad{background:var(--badbg);color:var(--bad)}
.lbl{display:block;font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;font-weight:700;color:var(--muted);margin-bottom:2px;font-variation-settings:"wdth" 125}
.pq,.prim,.idea{font-size:.94rem}
.idea{background:var(--soft);border-radius:10px;padding:12px 14px}
.idea .lbl{color:var(--accent)}
.alert{background:var(--midbg);border-radius:10px;padding:10px 12px;font-size:.9rem}
.alert .lbl{color:var(--mid)}
.alert ul,.fu{margin:0;padding-left:18px;display:flex;flex-direction:column;gap:6px}
.fu{margin-top:8px;font-size:.88rem}
.fu a{text-decoration:none;color:var(--fg)}.fu a b{color:var(--accent)}
.otras{font-size:.82rem;color:var(--muted);margin-top:6px}
details summary{cursor:pointer;font-weight:700;font-size:.88rem;color:var(--accent);min-height:32px;display:flex;align-items:center}
details summary:focus-visible,a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.nota{font-size:.85rem;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}
.leyenda{display:flex;flex-wrap:wrap;gap:6px}
.ult{display:flex;flex-direction:column;gap:10px}
.g{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:6px;min-width:0}
.g h3{font-size:1.02rem}
.g .sub{font-size:.8rem;color:var(--muted)}
.aviso{background:var(--midbg);color:var(--fg);border-radius:10px;padding:10px 12px;font-size:.88rem}
.ideaobj{display:flex;flex-direction:column;gap:8px}
.ideaobj ol,.ideaobj ul{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:4px}
footer{font-size:.82rem;color:var(--muted);border-top:1px solid var(--line);padding-top:14px;display:flex;flex-direction:column;gap:4px}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
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
    for k, lab in (("enfoque", "Enfoque"), ("portada", "Portada"), ("gancho", "Gancho"), ("copy", "Copy del posteo")):
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


def seccion_edicion(ed):
    aviso = ""
    if ed.get("tipo") == "hipotetica":
        aviso = '<section><p class="aviso"><b>Edición hipotética.</b> ' + e(ed.get("nota") or "Es una prueba: la oficial sale a las 11 h.") + '</p></section>\n'
    return aviso + _seccion_edicion(ed)


def _seccion_edicion(ed):
    claves = "".join(
        f'<li><p>{e(c.get("texto"))}</p><p class="cf">' + " · ".join(link(f.get("url"), e(f.get("medio"))) for f in c.get("fuentes") or []) + "</p></li>"
        for c in ed.get("claves") or [])
    temas = "\n".join(tema(t) for t in ed.get("temas") or [])
    pc = "".join(f'''<article class="tema chk"><div class="meta"><span class="pill mid">🟡 Parcial</span></div><h3>{e(p.get("titulo"))}</h3><p>{e(p.get("resumen"))}</p>{f'<div class="alert"><span class="lbl">Qué falta</span><p>{e(p["falta"])}</p></div>' if p.get("falta") else ""}{f'<details><summary>Fuentes ({len(p["fuentes"])})</summary><ul class="fu">{fuentes(p["fuentes"])}</ul></details>' if p.get("fuentes") else ""}</article>''' for p in ed.get("para_chequear") or [])
    out = ""
    if claves:
        out += f'<section><h2>Lo que tenés que saber</h2><ol class="claves">{claves}</ol></section>\n'
    if temas:
        out += f'<section><h2>Temas del día</h2><div class="temas">{temas}</div></section>\n'
    if pc:
        out += f'<section><h2>Para chequear</h2><div class="temas">{pc}</div></section>\n'
    return out or '<section><p class="lead">Todavía no hay edición curada.</p></section>'


def hora(iso):
    try:
        d = dt.datetime.fromisoformat(iso).astimezone(AR)
        return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}, {d:%H:%M} h", d
    except Exception:
        return iso or "s/d", None


def seccion_ultima(cand):
    if not cand or not cand.get("candidatos"):
        return '<section><h2>Última hora (automático)</h2><p class="lead">Sin datos por ahora.</p></section>'
    lim = (dt.datetime.now(AR) - dt.timedelta(hours=12)).isoformat(timespec="minutes")
    gs = [g for g in cand["candidatos"] if g.get("ultima", "") >= lim] or cand["candidatos"]
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
    return f'''<section><h2>Última hora (automático)</h2>
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&display=swap">
<style>{CSS}
.nav{{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px}}
.btn{{font:inherit;font-weight:700;font-size:.9rem;background:none;cursor:pointer;display:inline-flex;align-items:center;min-height:42px;padding:8px 18px;border-radius:99px;border:2px solid var(--accent);color:var(--accent);text-decoration:none}}
.btn.on{{background:var(--accent);color:var(--surface)}}
.band .btn{{border-color:#fff;color:#fff}}
.band .btn.on{{background:#fff;color:var(--brand)}}
.dia{{font-size:1.6rem;color:var(--fg);border-bottom:3px solid var(--rojo);padding-bottom:6px}}
.rojo{{color:var(--bad);font-weight:800}}
.ed-sep{{font-family:var(--display);font-size:1.05rem;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}}
</style></head><body>
<header class="band"><div class="band-in">
  <a href="{prefijo}index.html" aria-label="Soda, ir a hoy"><img class="logo" src="{prefijo}img/logo-blanco.png" alt="Soda" width="585" height="245"></a>
  <div class="eyebrow">Motor de relevamiento · La Sodería</div>
  <h1>{titulo_h1}</h1>
  <p class="lead">{lead}</p>
  <nav class="nav">{nav}</nav>
</div></header>
<main>
<section><div class="leyenda"><span class="pill ok">🟢 2+ fuentes serias o primaria</span><span class="pill mid">🟡 una sola fuente</span><span class="pill warn">🟠 solo X: no se publica</span><span class="pill bad">🔴 falso</span></div></section>
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
        b += f'<a class="btn{" on" if activo == "archivo" else ""}" href="{prefijo}archivo.html">Archivo</a>'
        return b

    # Hoy: solo ediciones de hoy + última hora automática.
    eds_hoy = por_fecha.get(hoy, [])
    if eds_hoy:
        txt, _ = hora(eds_hoy[0].get("generado"))
        lead = f"Última edición curada: {e(txt)}. Los carruseles los redacta J."
        cuerpo = seccion_edicion(eds_hoy[0])
        if len(eds_hoy) > 1:
            cuerpo += '<details class="ed-sep"><summary>Ver también las ediciones anteriores de hoy</summary>' + bloque_ediciones(eds_hoy[1:]) + "</details>"
    else:
        lead = "La edición curada de hoy sale a las 11 h. Mientras tanto, abajo tenés la última hora automática."
        cuerpo = ""
    cuerpo += seccion_ultima(cand)
    (BASE / "index.html").write_text(pagina("Lo que pasó hoy, chequeado", lead, cuerpo, nav("hoy"), ahora_txt, len(notas), medios))

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
    cuerpo = f'<section><h2>Todas las ediciones</h2><ul class="fu">{items or "<li>Todavía no hay ediciones.</li>"}</ul></section>'
    (BASE / "archivo.html").write_text(pagina("Archivo", "Todas las ediciones curadas, por día.", cuerpo, nav("archivo"), ahora_txt, len(notas), medios))
    print(f"ok | hoy {len(eds_hoy)} | ayer {len(eds_ayer)} | días en archivo {len(por_fecha)}")


if __name__ == "__main__":
    main()
