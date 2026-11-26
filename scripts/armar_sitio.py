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
/* Layout: una columna de lectura; claves arriba, temas como fichas con semáforo, "para chequear" al final */
:root{--bg:#f3f6f7;--surface:#fff;--fg:#132026;--muted:#56666d;--line:#d9e2e5;--accent:#0b6f8c;--soft:#e3f0f3;
--ok:#1d7f46;--mid:#9a6f00;--warn:#b5520f;--bad:#b3261e;--okbg:#e2f3e8;--midbg:#fbf1d6;--warnbg:#fde7d6;--badbg:#fbe1df;
--display:'Bricolage Grotesque',system-ui,sans-serif;--body:'Inter',system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0e1619;--surface:#162227;--fg:#e4eef1;--muted:#97a9b0;--line:#2a3a40;--accent:#5cc3df;--soft:#1b2f36;--ok:#5fd08e;--mid:#e5bf4f;--warn:#f0955a;--bad:#f2837b;--okbg:#173527;--midbg:#3a3015;--warnbg:#3d2617;--badbg:#3f1e1c;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0e1619;--surface:#162227;--fg:#e4eef1;--muted:#97a9b0;--line:#2a3a40;--accent:#5cc3df;--soft:#1b2f36;--ok:#5fd08e;--mid:#e5bf4f;--warn:#f0955a;--bad:#f2837b;--okbg:#173527;--midbg:#3a3015;--warnbg:#3d2617;--badbg:#3f1e1c;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font:15.5px/1.55 var(--body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 64px}
main{max-width:700px;margin:0 auto;display:flex;flex-direction:column;gap:32px}
h1,h2,h3{font-family:var(--display);margin:0;text-wrap:balance}
h1{font-size:2.1rem;line-height:1.05;font-weight:800}
h2{font-size:1.2rem;margin-bottom:12px}
h3{font-size:1.18rem;line-height:1.25}
p{margin:0}
a{color:var(--accent)}
.eyebrow{font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:600}
.lead{color:var(--muted);margin-top:8px}
.stats{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:14px;font-size:.85rem;color:var(--muted);font-variant-numeric:tabular-nums}
.stats b{color:var(--fg)}
.claves{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:12px;counter-reset:k}
.claves li{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px;display:flex;flex-direction:column;gap:4px}
.cf{font-size:.82rem}
.cf a{text-decoration:none}
.temas{display:flex;flex-direction:column;gap:14px}
.tema{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:10px;min-width:0}
.meta{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.sec{font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600}
.pill{font-size:.78rem;font-weight:600;padding:3px 10px;border-radius:99px;white-space:nowrap}
.pill.ok{background:var(--okbg);color:var(--ok)}.pill.mid{background:var(--midbg);color:var(--mid)}.pill.warn{background:var(--warnbg);color:var(--warn)}.pill.bad{background:var(--badbg);color:var(--bad)}
.lbl{display:block;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;font-weight:600;color:var(--muted);margin-bottom:2px}
.pq,.prim,.idea{font-size:.92rem}
.idea{background:var(--soft);border-radius:8px;padding:10px 12px}
.alert{background:var(--midbg);border-radius:8px;padding:10px 12px;font-size:.9rem}
.alert .lbl{color:var(--mid)}
.alert ul,.fu{margin:0;padding-left:18px;display:flex;flex-direction:column;gap:6px}
.fu{margin-top:8px;font-size:.88rem}
.fu a{text-decoration:none;color:var(--fg)}.fu a b{color:var(--accent)}
.otras{font-size:.82rem;color:var(--muted);margin-top:6px}
details summary{cursor:pointer;font-weight:600;font-size:.88rem;color:var(--accent);min-height:32px;display:flex;align-items:center}
details summary:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.nota{font-size:.85rem;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}
.leyenda{display:flex;flex-wrap:wrap;gap:6px}

.ult{display:flex;flex-direction:column;gap:10px}
.g{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:6px;min-width:0}
.g h3{font-size:1rem}
.g .sub{font-size:.8rem;color:var(--muted)}
.aviso{background:var(--midbg);color:var(--fg);border-radius:8px;padding:10px 12px;font-size:.88rem}
.ideaobj{display:flex;flex-direction:column;gap:6px}
.ideaobj ol,.ideaobj ul{margin:0;padding-left:20px}
footer{font-size:.82rem;color:var(--muted);border-top:1px solid var(--line);padding-top:14px;display:flex;flex-direction:column;gap:4px}
"""


def leer(ruta):
    p = BASE / ruta
    return json.loads(p.read_text()) if p.exists() else None


def link(url, txt):
    return f'<a href="{e(url)}" target="_blank" rel="noopener">{txt}</a>' if url else txt


def fuentes(fs):
    return "".join(f'<li>{link(f.get("url"), "<b>" + e(f.get("medio")) + "</b> · " + e(f.get("titulo")))}</li>' for f in fs or [])


def idea(i):
    if not i:
        return ""
    if isinstance(i, str):
        return f'<p class="idea"><span class="lbl">Idea de carrusel</span> {e(i)}</p>'
    partes = []
    for k, lab in (("enfoque", "Enfoque"), ("gancho", "Gancho")):
        if i.get(k):
            partes.append(f'<p><b>{lab}.</b> {e(i[k])}</p>')
    if i.get("placas"):
        partes.append("<div><b>Placas</b><ol>" + "".join(f"<li>{e(p)}</li>" for p in i["placas"]) + "</ol></div>")
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
<meta property="og:title" content="{titulo}"><meta property="og:description" content="{desc}"><meta property="og:type" content="website">
<meta name="description" content="{desc}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Inter:wght@400;500;600&display=swap">
<style>{CSS}
.nav{{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}}
.btn{{font:inherit;background:none;cursor:pointer;display:inline-flex;align-items:center;min-height:40px;padding:8px 16px;border-radius:99px;border:1px solid var(--accent);color:var(--accent);text-decoration:none;font-weight:600;font-size:.9rem}}
.btn.on{{background:var(--accent);color:var(--surface)}}
.dia{{font-size:1.5rem;border-bottom:2px solid var(--accent);padding-bottom:6px}}
.ed-sep{{font-family:var(--display);font-size:1.05rem;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}}
</style></head><body>
<main>
<header>
  <div class="eyebrow">Motor Soda · La Sodería</div>
  <h1>{titulo_h1}</h1>
  <p class="lead">{lead}</p>
  <nav class="nav">{nav}</nav>
</header>
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
        (BASE / f"archivo/{fecha}.html").write_text(pagina(f"Edición del {fecha_larga(fecha)}", f"{len(eds)} edición(es) curada(s).", bloque_ediciones(eds), nav("archivo", "../"), ahora_txt, len(notas), medios))
        temas = sum(len(x.get("temas") or []) for x in eds)
        items += f'<li><a href="archivo/{fecha}.html"><b>{e(fecha_larga(fecha).capitalize())}</b></a> · {len(eds)} edición(es), {temas} temas</li>'
    cuerpo = f'<section><h2>Todas las ediciones</h2><ul class="fu">{items or "<li>Todavía no hay ediciones.</li>"}</ul></section>'
    (BASE / "archivo.html").write_text(pagina("Archivo", "Todas las ediciones curadas, por día.", cuerpo, nav("archivo"), ahora_txt, len(notas), medios))
    print(f"ok | hoy {len(eds_hoy)} | ayer {len(eds_ayer)} | días en archivo {len(por_fecha)}")


if __name__ == "__main__":
    main()
