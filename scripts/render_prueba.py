#!/usr/bin/env python3
"""Genera una vista HTML de una edición (para revisión interna)."""
import json, sys, html
from pathlib import Path
from urllib.parse import urlparse
BASE = Path(__file__).resolve().parent.parent
ed = json.loads((BASE / (sys.argv[1] if len(sys.argv) > 1 else "data/edicion-prueba.json")).read_text())
out = Path(sys.argv[2] if len(sys.argv) > 2 else BASE.parent / "prueba/edicion-prueba.html")
e = lambda s: html.escape(s or "")
SEM = {"🟢": ("ok", "Confirmado"), "🟡": ("mid", "Parcial"), "🟠": ("warn", "Sin confirmar"), "🔴": ("bad", "Falso")}

def fuentes(fs):
    return "".join(f'<li><a href="{e(f["url"])}" target="_blank" rel="noopener"><b>{e(f["medio"])}</b> · {e(f["titulo"])}</a></li>' for f in fs)

def tema(t, i):
    cls, lab = SEM[t["semaforo"]]
    prim = t.get("primaria")
    prim_html = ""
    if prim:
        nom = prim.get("nombre") or f'{prim.get("medio")} · {prim.get("titulo")}'
        prim_html = f'<p class="prim"><span class="lbl">Fuente primaria</span> ' + (f'<a href="{e(prim["url"])}" target="_blank" rel="noopener">{e(nom)}</a>' if prim.get("url") else e(nom)) + '</p>'
    al = "".join(f"<li>{e(a)}</li>" for a in t.get("alertas", []))
    otras = ", ".join(e(o) for o in t.get("otras") or [])
    return f'''<article class="tema" id="{e(t["id"])}">
  <div class="meta"><span class="sec">{e(t.get("seccion",""))}</span><span class="pill {cls}">{t["semaforo"]} {lab}</span></div>
  <h3>{e(t["titulo"])}</h3>
  <p>{e(t["resumen"])}</p>
  <p class="pq"><span class="lbl">Por qué importa</span> {e(t.get("por_que_importa",""))}</p>
  {prim_html}
  <details><summary>Fuentes ({len(t["fuentes"])}{" + " + str(len(t.get("otras") or [])) + " más" if t.get("otras") else ""})</summary><ul class="fu">{fuentes(t["fuentes"])}</ul>{f'<p class="otras">También: {otras}</p>' if otras else ""}</details>
  {f'<div class="alert"><span class="lbl">Ojo antes de publicar</span><ul>{al}</ul></div>' if al else ""}
  {f'<p class="idea"><span class="lbl">Idea de carrusel</span> {e(t["idea_carrusel"])}</p>' if t.get("idea_carrusel") else ""}
</article>'''

claves = "".join(f'<li><p>{e(c["texto"])}</p><p class="cf">' + " · ".join(f'<a href="{e(f["url"])}" target="_blank" rel="noopener">{e(f["medio"])}</a>' for f in c["fuentes"]) + "</p></li>" for c in ed["claves"])
temas = "\n".join(tema(t, i) for i, t in enumerate(ed["temas"]))
pc = "".join(f'''<article class="tema chk"><div class="meta"><span class="pill mid">🟡 Parcial</span></div><h3>{e(p["titulo"])}</h3><p>{e(p["resumen"])}</p><div class="alert"><span class="lbl">Qué falta</span><p>{e(p["falta"])}</p></div><details><summary>Fuentes ({len(p["fuentes"])})</summary><ul class="fu">{fuentes(p["fuentes"])}</ul></details></article>''' for p in ed["para_chequear"])
m = ed["metricas"]
page = f'''<title>Edición de prueba · Motor Soda</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Inter:wght@400;500;600&display=swap">
<style>
/* Layout: una columna de lectura; claves arriba, temas como fichas con semáforo, "para chequear" al final */
:root{{--bg:#f3f6f7;--surface:#fff;--fg:#132026;--muted:#56666d;--line:#d9e2e5;--accent:#0b6f8c;--soft:#e3f0f3;
--ok:#1d7f46;--mid:#9a6f00;--warn:#b5520f;--bad:#b3261e;--okbg:#e2f3e8;--midbg:#fbf1d6;--warnbg:#fde7d6;--badbg:#fbe1df;
--display:'Bricolage Grotesque',system-ui,sans-serif;--body:'Inter',system-ui,sans-serif}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0e1619;--surface:#162227;--fg:#e4eef1;--muted:#97a9b0;--line:#2a3a40;--accent:#5cc3df;--soft:#1b2f36;--ok:#5fd08e;--mid:#e5bf4f;--warn:#f0955a;--bad:#f2837b;--okbg:#173527;--midbg:#3a3015;--warnbg:#3d2617;--badbg:#3f1e1c;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#0e1619;--surface:#162227;--fg:#e4eef1;--muted:#97a9b0;--line:#2a3a40;--accent:#5cc3df;--soft:#1b2f36;--ok:#5fd08e;--mid:#e5bf4f;--warn:#f0955a;--bad:#f2837b;--okbg:#173527;--midbg:#3a3015;--warnbg:#3d2617;--badbg:#3f1e1c;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--fg);font:15.5px/1.55 var(--body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 64px}}
main{{max-width:700px;margin:0 auto;display:flex;flex-direction:column;gap:32px}}
h1,h2,h3{{font-family:var(--display);margin:0;text-wrap:balance}}
h1{{font-size:2.1rem;line-height:1.05;font-weight:800}}
h2{{font-size:1.2rem;margin-bottom:12px}}
h3{{font-size:1.18rem;line-height:1.25}}
p{{margin:0}}
a{{color:var(--accent)}}
.eyebrow{{font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:600}}
.lead{{color:var(--muted);margin-top:8px}}
.stats{{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:14px;font-size:.85rem;color:var(--muted);font-variant-numeric:tabular-nums}}
.stats b{{color:var(--fg)}}
.claves{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:12px;counter-reset:k}}
.claves li{{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px;display:flex;flex-direction:column;gap:4px}}
.cf{{font-size:.82rem}}
.cf a{{text-decoration:none}}
.temas{{display:flex;flex-direction:column;gap:14px}}
.tema{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:10px;min-width:0}}
.meta{{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}}
.sec{{font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600}}
.pill{{font-size:.78rem;font-weight:600;padding:3px 10px;border-radius:99px;white-space:nowrap}}
.pill.ok{{background:var(--okbg);color:var(--ok)}}.pill.mid{{background:var(--midbg);color:var(--mid)}}.pill.warn{{background:var(--warnbg);color:var(--warn)}}.pill.bad{{background:var(--badbg);color:var(--bad)}}
.lbl{{display:block;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;font-weight:600;color:var(--muted);margin-bottom:2px}}
.pq,.prim,.idea{{font-size:.92rem}}
.idea{{background:var(--soft);border-radius:8px;padding:10px 12px}}
.alert{{background:var(--midbg);border-radius:8px;padding:10px 12px;font-size:.9rem}}
.alert .lbl{{color:var(--mid)}}
.alert ul,.fu{{margin:0;padding-left:18px;display:flex;flex-direction:column;gap:6px}}
.fu{{margin-top:8px;font-size:.88rem}}
.fu a{{text-decoration:none;color:var(--fg)}}.fu a b{{color:var(--accent)}}
.otras{{font-size:.82rem;color:var(--muted);margin-top:6px}}
details summary{{cursor:pointer;font-weight:600;font-size:.88rem;color:var(--accent);min-height:32px;display:flex;align-items:center}}
details summary:focus-visible,a:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.nota{{font-size:.85rem;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}}
.leyenda{{display:flex;flex-wrap:wrap;gap:6px}}
</style>
<main>
<header>
  <div class="eyebrow">Motor Soda · edición de prueba</div>
  <h1>Lo que pasó hoy, chequeado</h1>
  <p class="lead">Miércoles 25 de noviembre de 2026. </p>
  <div class="stats"><span><b>{m["notas_analizadas"]}</b> notas leídas</span><span><b>{m["grupos"]}</b> grupos</span><span><b>{m["temas"]}</b> temas elegidos</span></div>
</header>
<section><div class="leyenda"><span class="pill ok">🟢 2+ fuentes serias o primaria</span><span class="pill mid">🟡 una sola fuente</span><span class="pill warn">🟠 solo X: no se publica</span><span class="pill bad">🔴 falso</span></div></section>
<section><h2>Lo que tenés que saber</h2><ol class="claves">{claves}</ol></section>
<section><h2>Temas del día</h2><div class="temas">{temas}</div></section>
<section><h2>Para chequear</h2><div class="temas">{pc}</div></section>
<p class="nota">{e(ed.get("nota_x",""))} Los links de Google Noticias redirigen a la nota original.</p>
</main>'''
out.write_text(page)
print("ok", out)
