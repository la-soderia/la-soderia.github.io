# Criterio Soda para recomendar carruseles

Este archivo guía la `idea_carrusel` de cada edición. **El carrusel lo redacta J**; el motor solo recomienda un enfoque y un borrador de placas. Se actualiza cada vez que J comparte carruseles nuevos o corrige el criterio.

## Formato de los carruseles de Soda
Los carruseles combinan placas de texto con **archivos audiovisuales o fotografías** (videos de declaraciones, capturas de documentos oficiales, fotos de la marcha, etcétera). **Nunca llevan gráficos.**

## Reglas de redacción (pedidas por J)
- **Precisión en cada mención.** Si se menciona una fiscalía, un juzgado o un organismo, se dice cuál ("la Fiscalía Federal N.° X a cargo de…", "el juzgado federal de Daniel Rafecas"). Si el dato todavía no está en las fuentes, se marca "a chequear cuál" en lugar de dejarlo genérico.
- **Siglas siempre desarrolladas** la primera vez ("el Consejo Interuniversitario Nacional (CIN)", "el Instituto Nacional de Estadística y Censos (INDEC)").
- **Personas con nombre completo y cargo** la primera vez ("Javier Milei, presidente de la Nación"; "Luis Caputo, ministro de Economía"; "Axel Kicillof, gobernador de la provincia de Buenos Aires").
- Escritura directa, afirmativa y fluida; nada de contrastes del tipo "no es X, sino Y"; sin dos puntos dentro de los textos; oraciones conectadas, con punto y coma cuando unen ideas de la misma explicación; sin cierres que repitan lo ya dicho.
- No usar ganchos de fórmula como "¿Viste…? Seguro que sí".

## Cómo escribir la `idea_carrusel`
Para los 2 o 3 temas con más potencial, un objeto con
- `enfoque`, que en una o dos oraciones explica qué se cuenta y por qué le importa al público de Soda.
- `placas`, con 3 a 6 textos de placa ya redactados con estas reglas, una idea por placa.
- `audiovisual`, que indica qué videos, fotografías o capturas acompañan cada placa y de dónde salen (la declaración original, la página del Boletín Oficial, la foto de la marcha, el informe en el sitio del Senado).
- `a_chequear`, con lo que J tiene que confirmar antes de publicar (qué fiscalía, la cifra exacta, el horario).

Todo lo que se afirme en la idea tiene que estar 🟢 o figurar en `a_chequear`.
