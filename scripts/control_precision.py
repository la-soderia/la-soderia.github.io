#!/usr/bin/env python3
"""Control de precisión de Soda: las reglas de la redacción, convertidas en código.

Revisa el texto redactado de una edición (títulos, resúmenes, "por qué importa",
claves e ideas de carrusel) y sale con código 1 si encuentra una falla. La
curaduría no publica hasta que este control da 0 fallas.

Uso:
    python3 scripts/control_precision.py                      # data/edicion.json
    python3 scripts/control_precision.py data/ediciones/X.json
    python3 scripts/control_precision.py --todas              # todas las ediciones (solo informa)

Reglas (ver CURADURIA.md y CRITERIO-SODA.md):
  1. Nunca "según [medio]".
  2. Jamás "un/una" para algo identificable (un juez, una fiscalía, un informe...).
  3. Siglas desarrolladas la primera vez: "Instituto ... (INDEC)".
  4. Estilo: sin "no es X, sino Y", sin dos puntos, sin "en resumen" o "en definitiva".
Las excepciones legítimas se agregan en data/control_excepciones.json.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"

GENERICOS = (
    "juez|jueza|fiscal|fiscala|fiscalía|juzgado|tribunal|camarista|"
    "informe|encuesta|estudio|relevamiento|consultora|"
    "funcionario|funcionaria|ministro|ministra|ministerio|secretario|secretaria|"
    "diputado|diputada|senador|senadora|legislador|legisladora|"
    "intendente|intendenta|gobernador|gobernadora|vocero|vocera|"
    "organismo|dependencia"
)
RE_GENERICO = re.compile(rf"\b(un|una)\s+({GENERICOS})\b", re.I)
RE_SINO = re.compile(r"\bno\s+(es|son|era|fue|se\s+trata\s+de)\b[^.;]{1,80}?,?\s+sino\b", re.I)
RE_CIERRE = re.compile(r"\b(en\s+resumen|en\s+definitiva|en\s+síntesis)\b", re.I)
RE_SIGLA = re.compile(r"(?<![\w(])([A-ZÁÉÍÓÚÑ]{3,}[0-9]?)(?![\w)])")
RE_DOS_PUNTOS = re.compile(r":(?!\d)")  # deja pasar horas (11:30)

MEDIOS_BASE = [
    "La Nación", "Clarín", "Página/12", "Página 12", "Infobae", "Perfil", "Ámbito",
    "El Cronista", "elDiarioAR", "Letra P", "La Política Online", "LPO", "TN", "A24",
    "C5N", "Crónica", "MDZ", "Minuto Uno", "El Destape", "Chequeado", "Revista Crisis",
    "Revista Cítrica", "Tiempo Argentino", "La Izquierda Diario", "Noticias Argentinas",
    "Télam", "Reuters", "AFP", "EFE", "Bloomberg", "El País", "Río Negro", "Parlamentario",
]


def cargar_json(p, defecto):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return defecto


def medios():
    nombres = set(MEDIOS_BASE)
    f = cargar_json(DATA / "fuentes.json", {})
    for item in (f.get("medios", []) if isinstance(f, dict) else f) or []:
        if isinstance(item, dict) and item.get("nombre"):
            nombres.add(item["nombre"])
    return sorted(nombres, key=len, reverse=True)


def textos(ed):
    """(ruta, texto) de todo lo redactado por la curaduría, en orden de lectura."""
    for i, c in enumerate(ed.get("claves", []) or []):
        if isinstance(c, dict) and c.get("texto"):
            yield f"claves[{i}]", c["texto"]
    for i, t in enumerate(ed.get("temas", []) or []):
        tid = t.get("id", i)
        for campo in ("titulo", "resumen", "por_que_importa"):
            if t.get(campo):
                yield f"{tid}.{campo}", t[campo]
        ic = t.get("idea_carrusel") or {}
        for campo in ("enfoque", "portada", "copy"):
            if ic.get(campo):
                yield f"{tid}.carrusel.{campo}", ic[campo]
        for j, pl in enumerate(ic.get("placas", []) or []):
            yield f"{tid}.carrusel.placa{j + 1}", pl


def controlar(ed, exc):
    fallas = []
    lista_medios = medios()
    re_segun = re.compile(
        r"\bsegún\s+(?:el\s+diario\s+|la\s+agencia\s+|el\s+portal\s+|la\s+revista\s+)?("
        + "|".join(re.escape(m) for m in lista_medios) + r")\b", re.I)
    siglas_ok = set(exc.get("siglas", []))
    frases_ok = [s.lower() for s in exc.get("frases", [])]
    vistas = set()

    for ruta, txt in textos(ed):
        plano = txt.replace("*", "")
        bajo = plano.lower()
        def marcar(regla, m):
            frag = plano[max(0, m.start() - 35): m.end() + 35].replace("\n", " ")
            if any(f in bajo for f in frases_ok if f in frag.lower()):
                return
            fallas.append((ruta, regla, frag.strip()))
        for m in re_segun.finditer(plano):
            marcar('"según [medio]"', m)
        for m in RE_GENERICO.finditer(plano):
            marcar(f'genérico "{m.group(0)}" (decir cuál o quién)', m)
        for m in RE_SINO.finditer(plano):
            marcar('"no es X, sino Y"', m)
        for m in RE_CIERRE.finditer(plano):
            marcar("cierre de resumen", m)
        if ".carrusel." not in ruta or ruta.endswith(".copy"):
            for m in RE_DOS_PUNTOS.finditer(plano):
                marcar("dos puntos", m)
        # Siglas: la primera aparición en la edición tiene que estar entre paréntesis
        for m in re.finditer(r"\(([A-ZÁÉÍÓÚÑ]{2,}[0-9]?)\)", plano):
            vistas.add(m.group(1))
        for m in RE_SIGLA.finditer(plano):
            s = m.group(1)
            if s in vistas or s in siglas_ok or re.fullmatch(r"[IVXLCDM]+", s):
                continue
            # Palabras en mayúsculas pegadas a otras en mayúsculas = texto destacado, no sigla
            antes = re.search(r"([A-ZÁÉÍÓÚÑ]+)[\s,.–-]+$", plano[:m.start()])
            despues = re.match(r"[\s,.–-]+([A-ZÁÉÍÓÚÑ]+)\b", plano[m.end():])
            if antes or despues:
                continue
            vistas.add(s)
            marcar(f'sigla "{s}" sin desarrollar la primera vez', m)
    return fallas


def main(args):
    exc = cargar_json(DATA / "control_excepciones.json", {})
    if args and args[0] == "--todas":
        archivos = sorted((DATA / "ediciones").glob("*.json"))
        total = 0
        for a in archivos:
            f = controlar(cargar_json(a, {}), exc)
            total += len(f)
            print(f"{a.name}: {len(f)} fallas")
            for ruta, regla, frag in f:
                print(f"   - {ruta} · {regla} · «{frag}»")
        print(f"\nTotal: {total} fallas en {len(archivos)} ediciones.")
        return 0
    archivo = Path(args[0]) if args else DATA / "edicion.json"
    fallas = controlar(cargar_json(archivo, {}), exc)
    if not fallas:
        print(f"OK · {archivo.name} pasa el control de precisión.")
        return 0
    print(f"FRENADO · {archivo.name} tiene {len(fallas)} fallas. Corregir y volver a correr:")
    for ruta, regla, frag in fallas:
        print(f"  - {ruta} · {regla} · «{frag}»")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
