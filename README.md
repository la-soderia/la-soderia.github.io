# Rastrillo de Motor Soda

Junta cada hora las notas de coyuntura argentina y las guarda en `data/crudo.json` (últimos 7 días, sin duplicados). Solo usa Python 3 estándar, sin instalar nada.

## Correrlo
    python3 scripts/rastrillo.py

En GitHub, `.github/workflows/rastrillo.yml` lo corre solo cada hora (minuto 23) y sube el JSON. También se puede disparar a mano desde la pestaña Actions.

## Editar fuentes: `data/fuentes.json`
Cada fuente tiene: `nombre`, `dominio`, `rss` (URL del feed; vacío si no tiene), `tipo` (`medio`, `organizacion` u `oficial`) y `lista_seria` (`true`/`false`, cuenta para el semáforo de chequeo).
- `"google_site": true` suma una búsqueda `site:dominio` en Google Noticias (para medios sin RSS o con RSS flojo).
- Una fuente con `rss` vacío y sin `google_site` solo sirve para que sus notas, cuando aparecen en las búsquedas, se acepten y se etiqueten bien.

## Editar búsquedas: `data/busquedas.txt`
Una búsqueda por línea (se les agrega `when:1d` sola). Las líneas con `#` son comentarios.

## Regla de medios del exterior
Las notas que vienen de Google Noticias solo entran si el medio es `.ar` o está en `fuentes.json`. Si una línea de `busquedas.txt` empieza con `!`, esa búsqueda acepta cualquier dominio. Los RSS de `fuentes.json` entran siempre.

## Campos de cada nota
`id`, `titulo`, `medio`, `dominio`, `url`, `url_original` (solo si se puede resolver; los links nuevos de Google no se pueden decodificar), `fecha`, `fuente_tipo`, `lista_seria`, `busquedas` y `visto` (cuándo la vio el rastrillo por primera vez). Los errores de feeds quedan en `errores` y no frenan la corrida.

## Nota para Mac
Si Python no trae certificados, el script usa los del sistema (`/etc/ssl/cert.pem`).
