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
SEM = {"🟢": ("ok", "Confirmado"), "🟡": ("mid", "Parcial"), "🟠": ("warn", "Sin confirmar"), "🔴": ("bad", "Desmentido")}
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
    if i.get("gancho"):
        partes.append(f'<p><b>Gancho:</b> {e(i["gancho"])}</p>')
    if i.get("placas"):
        partes.append("<div><b>Placas:</b><ol>" + "".join(f"<li>{e(p)}</li>" for p in i["placas"]) + "</ol></div>")
    for k, lab in (("grafico", "Gráfico"), ("audiovisual", "Audiovisual"), ("cierre", "Cierre")):
        if i.get(k):
            partes.append(f'<p><b>{lab}:</b> {e(i[k])}</p>')
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


def main():
    ed = leer("data/edicion.json") or leer("data/edicion-prueba.json") or {}
    cand = leer("data/candidatos.json")
    crudo = leer("data/crudo.json") or {}
    notas = crudo.get("notas") or []
    medios = len({n.get("dominio") for n in notas})
    ahora = dt.datetime.now(AR)
    ed_txt, _ = hora(ed.get("generado"))
    es_prueba = ed.get("tipo") == "prueba"
    titulo = "La Sodería · Motor Soda"
    desc = "Lo que pasó, chequeado: temas del día con semáforo de fuentes y última hora automática."
    ahora_txt, _ = hora(ahora.isoformat())
    page = f'''<!doctype html>
<html lang="es-AR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<title>{titulo}</title>
<meta property="og:title" content="{titulo}"><meta property="og:description" content="{desc}"><meta property="og:type" content="website">
<meta name="description" content="{desc}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Inter:wght@400;500;600&display=swap">
<style>{CSS}</style></head><body>
<main>
<header>
  <div class="eyebrow">Motor Soda · La Sodería</div>
  <h1>Lo que pasó, chequeado</h1>
  <p class="lead">Edición curada: {e(ed_txt)}{" (edición de prueba)" if es_prueba else ""}. Los carruseles los redacta J.</p>
</header>
<section><div class="leyenda"><span class="pill ok">🟢 2+ fuentes serias o primaria</span><span class="pill mid">🟡 una sola fuente</span><span class="pill warn">🟠 solo X: no se publica</span><span class="pill bad">🔴 desmentido</span></div></section>
{seccion_edicion(ed)}
{seccion_ultima(cand)}
<footer><span><b>Actualizado:</b> {e(ahora_txt)}</span><span>{len(notas)} notas leídas de {medios} medios.</span><span>Los links de Google Noticias redirigen a la nota original.</span></footer>
</main></body></html>
'''
    (BASE / "index.html").write_text(page)
    print(f"ok index.html | edición {ed.get('id')} | {len(page)//1024} KB")


if __name__ == "__main__":
    main()
