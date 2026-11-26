# Criterio Soda para recomendar carruseles

Este archivo guía la `idea_carrusel` de cada edición. **El carrusel lo redacta J**; el motor solo recomienda un enfoque y un borrador de placas. Se actualiza cada vez que J comparte carruseles nuevos o corrige el criterio.

## Referencia principal: "Cómo garcar a un tren lleno de gente" (tren San Martín)
Las placas están en `criterio/2026-carrusel-tren-san-martin/`, en la carpeta del proyecto. Este es el modelo a seguir.

**Arco narrativo en 6 placas**
1. **Portada.** Una frase provocadora y coloquial, con la palabra clave resaltada en rojo ("Cómo **garcar** a un tren lleno de gente"), sobre una foto de fondo del tema.
2. **El problema cotidiano**, contado desde la experiencia de quien lo vive, con una frase corta en rojo arriba ("Lento, sucio, feo, impuntual.") y después el desarrollo ("cualquiera que lo tome todos los días sabe que viajar ahí es un garrón"). Cierra presentando la solución que hubo ("la electrificación del tren").
3. **La promesa con datos concretos**, como qué se iba a hacer, entre qué estaciones, cuántos puestos de trabajo y para qué año. El dato más fuerte va en rojo.
4. **Más datos y de dónde salía la plata**, con cifras comparables (de 1 hora 40 minutos a poco más de una hora; frecuencias de 18 a 9 minutos), el organismo que financiaba (préstamo del Banco Interamericano de Desarrollo, unos 400 millones de dólares) y un giro al final ("pero, pero, pero…").
5. **El responsable**, con su foto recortada en círculo y una frase directa en rojo ("Llegó este señor y dijo que no."); qué decidió, con la cita textual entre comillas ("no eran prioritarias").
6. **Adónde fue la plata y el cierre**, con el nombre exacto del programa al que se desviaron los fondos y una frase final que interpela al lector desde su vida diaria ("La próxima vez que tomes el San Martín, acordate que estás viajando así por decisión de alguien."). Lleva el logo de Soda.

**El copy del posteo** abre con preguntas en segunda persona dirigidas a quien vive el tema ("¿Viajás en tren? ¿Te tomás el San Martín? ¿Te gustaría viajar mejor? Esta historia es para vos.").

**Lenguaje.** Rioplatense, coloquial y con humor, con palabras como garrón, guita, flama o "este señor"; segunda persona; frases clave resaltadas en rojo. El tono es filoso pero cada afirmación está respaldada por un dato concreto (cifras, nombres de programas, organismos, citas textuales).

**Lo visual.** Una foto de fondo del tema que se repite en todas las placas, el texto en blanco con los destacados en rojo, la foto del responsable recortada en círculo y el logo de Soda en la última placa. **Nunca llevan gráficos**; usan fotografías y archivos audiovisuales.

## Reglas de precisión (pedidas por J)
- **Fiscalías, juzgados y organismos identificados.** Se dice cuál ("la Fiscalía Federal N.° X a cargo de…", "el juzgado federal de Daniel Rafecas"). Si el dato no está en las fuentes, va a `a_chequear` en lugar de quedar genérico.
- **Siglas desarrolladas** la primera vez ("el Consejo Interuniversitario Nacional (CIN)").
- **Personas con nombre completo y cargo** la primera vez ("Luis Caputo, ministro de Economía de la Nación"); después se puede usar el apodo o el cargo, como hace el carrusel del tren con "Toto Caputo" y "el ministro de Economía".
- No usar ganchos de fórmula como "¿Viste…? Seguro que sí".

## Cómo escribir la `idea_carrusel`
Para los 2 o 3 temas con más potencial, un objeto con
- `enfoque`, que en una o dos oraciones explica qué historia se cuenta y a quién le habla.
- `portada`, con la frase de portada y entre asteriscos la palabra que va en rojo.
- `placas`, con 4 a 6 textos ya redactados que siguen el arco de la referencia (problema cotidiano, promesa o contexto con datos, giro, responsable con su decisión, cierre que interpela). Cada placa puede marcar entre asteriscos la frase que iría en rojo.
- `copy`, con el texto del posteo que abre con preguntas a quien vive el tema.
- `audiovisual`, que indica la foto de fondo, la foto del responsable y los videos o capturas que suman (la declaración original, el documento oficial).
- `a_chequear`, con lo que J tiene que confirmar antes de publicar.

Todo lo que se afirme tiene que estar 🟢 o figurar en `a_chequear`; el tono filoso nunca reemplaza al dato.
