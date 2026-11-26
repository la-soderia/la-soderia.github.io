# Criterio Soda: cómo son los carruseles

Este archivo se arma a partir de los carruseles que J publica y se actualiza cada vez que J comparte uno nuevo.
La curaduría lo usa para escribir la `idea_carrusel` de cada tema. **El carrusel lo redacta J.**

## Referencia 1: "Secreto militar del Gobierno" (octubre de 2026)
Original en `criterio/2026-10-carrusel-secreto-militar.pdf`, en la carpeta del proyecto.

**Estructura:**
1. **Gancho por contraste:** "¿Te enteraste que se murió X? **Seguro que sí.** Pero seguro no te enteraste que un día antes el Gobierno hizo Y". El gancho usa lo que todo el mundo vio para mostrar lo que pasó de largo.
2. **El dato duro y su origen:** qué se hizo y con qué herramienta. Ahí entra el contexto histórico: un decreto de 1963, firmado durante el gobierno de facto de Guido.
3. **Preguntas al lector:** "¿Hicieron público cuánto nos va a costar…?" Las pregunta en segunda persona e incluye al lector ("nuestra plata", "nos").
4. **Antecedentes en viñetas:** "No es la primera vez", con bullets cortos.
5. **Gráfico propio con datos de medios** (firma `/dicenlosmedios`): cuántas veces apareció cada tema en los títulos de la semana. En este caso, Grimau 74 contra "secreto militar" 14.
6. **Cierre con pregunta:** respeta el otro tema ("merece todos los homenajes") y deja planteada la pregunta de fondo: por qué algo que nos afecta recibe menos atención.

**Lenguaje:** segunda persona, cercano, rioplatense, con preguntas y negritas en la frase clave. No es militante: el planteo surge de los datos. Una idea por placa.

**Material:** placas de texto + gráfico propio + archivos audiovisuales (videos o capturas de las coberturas).

## Cómo escribir la `idea_carrusel` en cada edición
Para cada tema con potencial, proponer:
- `gancho`: la primera placa con el registro de Soda. Si sirve, usar el contraste con lo que todo el mundo está mirando.
- `placas`: 3 a 5 líneas, una idea por placa: dato, contexto o antecedente, pregunta.
- `grafico`: una propuesta concreta con números reales del rastrillo (ver `scripts/menciones.py`), por ejemplo menciones en títulos de la semana de A contra B. **Solo números que salgan de los datos**, con fecha y cantidad de medios.
- `audiovisual`: qué videos, capturas o documentos sumar (la declaración original, la página del Boletín Oficial, un clip de la cobertura).
- `cierre`: la pregunta final.
Todo lo que se afirme en la idea tiene que estar 🟢 o marcado como "a chequear".
