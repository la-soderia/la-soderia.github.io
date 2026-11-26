# Cómo se arma cada edición del Motor Soda

Hay 2 ediciones por día, a las **11 h** y a las **15 h** (hora argentina). El objetivo es dejarle a J los temas del día **chequeados** para que redacte los carruseles de Soda.
Soda es un medio hecho por y para jóvenes. **No defiende a ningún sector**: informa con datos y con fuentes.

## Material disponible
- `data/crudo.json`: notas de RSS de portales y de Google Noticias, de los últimos 7 días.
- `data/candidatos.json`: la salida de `scripts/prefiltro.py`, que se corre primero. Tiene las notas de las últimas 24 h, sin ruido y agrupadas, con un **pre-semáforo** automático. El agrupado es grueso: **fusionar a mano** los grupos que hablan de lo mismo. Por ejemplo, el dólar o un mismo informe pueden venir en 5 grupos.
- `data/fuentes.json`: qué medios son de la lista seria (`lista_seria: true`).
- `data/x.json` (más adelante): posteos de X leídos sin login. Son **alertas, nunca fuentes**.
- `data/edicion.json`: la edición anterior, para dar continuidad y no repetir.

## Temas que entran
Política, economía, juventud y educación, sociedad y cultura. Deporte o espectáculos solo si se volvieron tema social o político.
**Breaking** solo si es muy relevante: una medida de gobierno, un hecho grave o algo que cambie la agenda del día.
Prioridad para Soda: lo que **le pega a los pibes y pibas**. Por ejemplo universidad, empleo joven, alquileres, apuestas online, salud mental, bolsillo y derechos.

## Semáforo de chequeo (obligatorio en cada tema)
- 🟢 **Confirmado**:
  - 2 o más fuentes de la lista seria **de redacciones distintas y que no se citan entre sí**. Mejor si son de líneas editoriales distintas (por ejemplo, La Nación + Página/12).
  - O una **fuente primaria**: documento oficial, dato del INDEC o BCRA, Boletín Oficial, paper de Fundar, Argentinos por la Educación o Ecofeminita, o la declaración textual de la persona involucrada.
- 🟡 **Parcial**: una sola fuente seria, o varias que **repiten el mismo cable** o la misma fuente. Va en la sección "Para chequear", con la fuente aclarada.
- 🟠 **Sin confirmar**: solo X o solo medios fuera de la lista. **No va en la edición**: queda en `seguimiento`.
- 🔴 **Falso**: una fuente primaria o 2 serias lo desmienten. En el sitio se muestra como "Falso". Si se viralizó, se propone como posible carrusel de "esto es falso".

### Reglas del chequeo
1. El pre-semáforo del script es **solo una pista**. Siempre se revisa que las fuentes sean independientes de verdad: 10 portales que levantan el mismo cable cuentan como 1.
2. **Cifras:** si los medios dan números distintos (por ejemplo 20.000 o 30.000, o 1.100 o 1.139 puntos), **se marca la discrepancia** en `alertas` y se busca el dato primario. Nunca se elige un número "a ojo".
3. Lo que es **interpretación** de un medio se atribuye ("según La Política Online…"). Los hechos van sin adjetivos.
4. Para cada dato duro se indica la fuente primaria si existe (`primaria: {nombre, url}`).
5. No se inventan datos, citas ni contexto. Si algo no está en las notas, no va.

## Pasos
1. Correr `python3 scripts/prefiltro.py 24`.
2. Leer `data/candidatos.json`, fusionar los grupos parecidos y descartar el ruido que se haya colado: homónimos, servicios (fechas de cobro de ANSES, cotizaciones repetidas), exterior sin impacto local, farándula.
3. Elegir **entre 6 y 10 temas**, ordenados por relevancia para el público de Soda.
4. Para cada tema escribir:
   - `titulo`: propio, claro, sin clickbait.
   - `resumen`: 2 o 3 oraciones con palabras propias, con un registro periodístico, coloquial pero serio, sin vulgaridades.
   - `por_que_importa`: 1 oración que explique por qué le importa a un pibe o una piba.
   - `semaforo`: 🟢, 🟡 o 🔴.
   - `fuentes`: 2 o 3 notas principales, de líneas distintas si se puede, con medio y url. El resto va en `otras`.
   - `primaria`: si existe.
   - `alertas`: discrepancias, datos a verificar o el "ojo con".
   - `idea_carrusel`: para los 2 o 3 temas con más potencial, un objeto `{enfoque, portada, placas[], copy, audiovisual[], a_chequear[]}` según `CRITERIO-SODA.md` (modelo, el carrusel del tren San Martín). Sin gráficos; los carruseles llevan archivos audiovisuales o fotografías. **El carrusel lo redacta J.**
5. `claves`: 4 o 5 puntos de "Lo que tenés que saber", cada uno con sus fuentes.
6. `para_chequear`: los temas 🟡, con lo que falta para confirmarlos.
7. `seguimiento`: los 🟠, con lo que se dice y dónde.
8. **Continuidad**: un tema queda vigente 24 h desde que se sumó o se actualizó. Si sigue, se repite con el mismo `id` y la info al día. Si resultó falso, se pasa a 🔴 Falso.
9. Antes de guardar, revisar: ¿cada tema tiene semáforo y fuentes? ¿Hay alguna cifra sin fuente? ¿Se marcaron las discrepancias?

## Estilo de redacción (pedido de J)
Esto vale para los resúmenes, las claves, el "por qué importa" y las ideas de carrusel.
- Escribir de forma directa, afirmativa y fluida. Si algo se puede afirmar en positivo, se afirma; no usar contrastes innecesarios del tipo "no es X, sino Y" o "no se trata de X, sino de Y".
- No usar dos puntos dentro de los textos redactados. Los títulos de los medios citados se copian tal cual.
- Preferir oraciones conectadas, con punto y coma cuando unen ideas de la misma explicación, a una seguidilla de frases cortas.
- No cerrar con fórmulas como "en resumen" o "en definitiva", ni con una frase que repita lo ya dicho.

## Límites
- No reproducir notas completas: solo resúmenes propios con link.
- No usar fotos de personas sacadas de la web.
- No iniciar sesión en ninguna red. Nunca contraseñas.
- **Siempre gratis**: nada de APIs ni servicios pagos.
