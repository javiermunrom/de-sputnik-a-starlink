# Storyboard de visualizacion final

## Titulo de trabajo

**De Sputnik a Starlink: como el espacio dejo de ser una carrera entre superpotencias y se convirtio en una economia orbital**

## Enfoque

La visualizacion no debe ser un dashboard. Debe ser un ensayo visual interactivo de tipo scrollytelling, donde cada bloque narrativo revela una transformacion historica: primero la competencia estatal, despues la consolidacion de nuevos actores, finalmente la aceleracion comercial reciente.

La historia debe guiar al lector por una pregunta central:

**Quien controla el acceso al espacio, y como ha cambiado ese control desde 1957?**

Las cinco preguntas de investigacion se integran como capitulos de esa misma historia.

## FASE 1 - Narrativa que emerge de los datos

### Historia mas potente

La narrativa mas fuerte es:

**Del monopolio geopolitico al mercado orbital.**

El dataset muestra una secuencia clara:

- 1957-1969: inicio de la carrera espacial, dominada por Estados Unidos y la URSS/Rusia.
- 1970-1991: consolidacion del dominio sovietico en volumen de lanzamientos.
- 1992-2009: fragmentacion posterior a la Guerra Fria y aparicion gradual de operadores comerciales.
- 2010-2019: aceleracion de China y aparicion visible de SpaceX.
- 2020-2026: salto cuantitativo de la nueva economia espacial, con SpaceX como actor dominante reciente.

### Justificacion cuantitativa

El dataset definitivo v2 contiene 11.627 registros y 7.303 registros preferentes para conteos historicos. La cobertura temporal va de 1957 a 2026.

Datos clave para sostener la historia:

| Evidencia | Lectura narrativa |
| --- | --- |
| En 2025 hay 329 lanzamientos preferentes, el maximo de la serie. | La etapa reciente no solo recupera la actividad espacial: la supera historicamente. |
| La decada de 2020 acumula 1.390 lanzamientos preferentes pese a estar incompleta. | La aceleracion actual es excepcional. |
| 1957-1969: Estados Unidos 555 lanzamientos y URSS/Rusia 449. | El inicio fue una carrera bipolar. |
| 1970-1991: URSS/Rusia 1.989 lanzamientos frente a Estados Unidos 400. | La URSS/Rusia domina el volumen durante la fase madura de la Guerra Fria. |
| 2010-2019: China 199, Estados Unidos 218 y Rusia 178. | El liderazgo se vuelve multipolar. |
| 2020-2026: Estados Unidos 631, China 414 y Rusia 107. | El eje contemporaneo se desplaza hacia Estados Unidos y China. |
| 2020-2026: SpaceX 587 lanzamientos, CASC 325. | El liderazgo reciente no es solo estadounidense: es empresarial. |
| SpaceX representa el 42,23% de los lanzamientos preferentes de 2020-2026. | SpaceX justifica una seccion propia. |
| 1957-1969: 86,65% de registros clasificados como publicos. 2020-2026: 52,81% privados. | La pregunta publico/privado es el giro dramatico de la historia. |
| La tasa de exito pasa de 80,70% en 1957-1969 a 95,36% en 2020-2026. | La actividad espacial se vuelve mas rutinaria y fiable. |
| En registros enriquecidos UCS, comunicaciones y observacion terrestre dominan los propositos. | La actividad actual esta orientada a servicios orbitales, no solo exploracion. |

### Tesis visual

**La humanidad no esta simplemente lanzando mas cohetes. Esta cambiando el significado del espacio: de escenario de prestigio geopolitico a infraestructura economica global.**

## FASE 2 - Storyboard completo

### Seccion 1 - Portada: De Sputnik a Starlink

**Objetivo narrativo:** introducir la transformacion historica en una frase y situar al lector emocionalmente.

**Mensaje principal:** desde 1957, el espacio ha pasado de simbolo de poder estatal a infraestructura comercial.

**Datos utilizados:** rango temporal 1957-2026, conteo acumulado de lanzamientos preferentes, top hitos temporales.

**Visualizacion:** hero visual con contador animado de lanzamientos acumulados y linea temporal minima en la parte inferior.

**Interaccion:** scroll inicial activa un contador desde 1957 hasta 2026. El contador se detiene en hitos: 1957, 1969, 1991, 2010, 2020, 2025.

**Wireframe conceptual:**

```text
+--------------------------------------------------+
| Imagen hero: Tierra / cohete / horizonte espacial |
|                                                  |
| DE SPUTNIK A STARLINK                            |
| Como el espacio paso de carrera geopolitica       |
| a economia orbital                               |
|                                                  |
| [contador acumulado] lanzamientos desde 1957      |
| 1957 ---- 1969 ---- 1991 ---- 2010 ---- 2026     |
+--------------------------------------------------+
```

### Seccion 2 - El primer pulso: la carrera espacial

**Objetivo narrativo:** mostrar que la actividad espacial nace como competicion estatal intensa.

**Mensaje principal:** el periodo 1957-1969 fue una carrera bipolar entre Estados Unidos y la URSS/Rusia.

**Datos utilizados:** registros preferentes 1957-1969, `year`, `country`, `space_era`, `mission_success_binary`.

**Visualizacion:** linea temporal anual con dos capas resaltadas: Estados Unidos y URSS/Rusia. Sobre la linea aparecen anotaciones de Sputnik, Gagarin y Apollo 11.

**Interaccion:** avance por scroll. Al entrar en 1957 aparece Sputnik; al entrar en 1961 aparece Gagarin; al entrar en 1969 aparece Apollo 11.

**Mensaje de apoyo:** en esta etapa Estados Unidos suma 555 lanzamientos preferentes y URSS/Rusia 449.

### Seccion 3 - Cuando la URSS gano el volumen

**Objetivo narrativo:** romper la lectura simplista de que Estados Unidos domina toda la historia espacial.

**Mensaje principal:** tras el primer impulso, la URSS/Rusia domina el volumen de lanzamientos durante buena parte de la Guerra Fria.

**Datos utilizados:** `year`, `country`, `preferred_for_launch_count`, periodo 1970-1991.

**Visualizacion:** stacked area chart por pais/actor con foco en Estados Unidos, URSS/Rusia, China, Europa/ESA, India y otros.

**Interaccion:** slider temporal o scroll-driven year scrubber. Al mover el año se actualiza un ranking lateral con pais lider, lanzamientos y porcentaje.

**Mensaje de apoyo:** entre 1970 y 1991, URSS/Rusia concentra 1.989 lanzamientos preferentes frente a 400 de Estados Unidos.

**Wireframe conceptual:**

```text
+--------------------------+-----------------------+
| Stacked area 1957-2026    | Ranking del año       |
|                          | 1. URSS/Rusia 101     |
| color por pais           | 2. Estados Unidos ... |
|                          |                       |
| [slider año] 1976         | Nota narrativa        |
+--------------------------+-----------------------+
```

### Seccion 4 - Despues de la Guerra Fria: se abre el tablero

**Objetivo narrativo:** mostrar la transicion del mundo bipolar a un escenario mas fragmentado.

**Mensaje principal:** tras 1991, el liderazgo se reparte entre Estados Unidos, Rusia, China, Europa, India, Japon y empresas emergentes.

**Datos utilizados:** `year`, `country`, `launch_provider`, `space_era`.

**Visualizacion:** small multiples por periodo historico. Cada panel muestra top actores del periodo.

**Interaccion:** al pasar por cada panel, se resalta el actor que entra o gana peso. China aparece progresivamente desde un rol marginal hasta actor central.

**Mensaje de apoyo:** en 2010-2019, Estados Unidos suma 218 lanzamientos, China 199 y Rusia 178: el liderazgo ya no es bipolar.

### Seccion 5 - La caida del monopolio estatal

**Objetivo narrativo:** responder la pregunta publico vs privado como giro central de la historia.

**Mensaje principal:** el espacio deja de estar controlado casi exclusivamente por instituciones publicas y pasa a tener mayoria privada en la etapa reciente.

**Datos utilizados:** `year`, `organization_type`, `preferred_for_launch_count`, `launch_provider`.

**Visualizacion:** area apilada Public / Private / Mixed / Unknown, con una linea vertical en 2010 y otra en 2020.

**Interaccion:** scroll-driven transition. Primero solo se ve Public. Despues emerge Private. Al llegar a 2020-2026 se muestra el dato principal: 52,81% privado.

**Mensaje de apoyo:** 1957-1969: 86,65% publico. 2020-2026: 52,81% privado.

**Nota metodologica visible:** `organization_type` es una clasificacion heuristica; los Unknown deben tratarse como incertidumbre, no como categoria interpretativa principal.

### Seccion 6 - SpaceX cambia la escala

**Objetivo narrativo:** comprobar si SpaceX merece una seccion propia y explicar por que.

**Mensaje principal:** SpaceX no es solo un actor mas; en los datos recientes cambia la escala anual de lanzamientos.

**Datos utilizados:** `year`, `launch_provider`, `country`, `organization_type`, periodo 2010-2026.

**Visualizacion principal:** bar chart race o ranking animado de proveedores por año desde 2010.

**Alternativa mas sobria:** linea comparativa SpaceX vs CASC vs Roscosmos vs Rocket Lab vs ULA.

**Interaccion:** scroll revela tres momentos: entrada de SpaceX, cruce con CASC, dominio 2022-2025.

**Mensaje de apoyo:** SpaceX tiene 672 lanzamientos preferentes en toda la serie, 587 de ellos entre 2020 y 2026. En ese periodo representa el 42,23% del total.

**Decision:** si se busca rigor y elegancia, usar linea comparativa anotada. Si se busca impacto, usar racing bars, pero limitarlo a 2010-2026 para evitar ruido.

### Seccion 7 - De riesgo experimental a infraestructura fiable

**Objetivo narrativo:** mostrar la maduracion tecnologica.

**Mensaje principal:** la tasa de exito aumenta fuertemente tras la etapa inicial y se mantiene alta en la era reciente.

**Datos utilizados:** `year`, `mission_success_binary`, `mission_status`.

**Visualizacion:** linea de tasa de exito anual con media movil de 5 años y puntos de eventos historicos.

**Interaccion:** hover enriquecido sobre años clave. Tooltips narrativos para 1957, 1969, 1986, 2003, 2015, 2020.

**Mensaje de apoyo:** tasa de exito conocida 1957-1969: 80,70%; 2020-2026: 95,36%.

**Cuidado narrativo:** no convertir la tasa en una historia triunfalista. Incluir nota: los codigos de estado proceden de fuentes distintas y algunos registros quedan sin clasificar.

### Seccion 8 - La nueva economia orbital

**Objetivo narrativo:** mostrar que la actividad espacial actual esta vinculada a servicios: comunicaciones, observacion, navegacion, ciencia y defensa.

**Mensaje principal:** el espacio actual se parece cada vez mas a una capa de infraestructura: redes, datos, navegacion, observacion.

**Datos utilizados:** registros con `ucs_match_found`, `purpose_group`, `orbit_group`, `satellite_operator`, `satellite_mass_kg`, `mass_group`.

**Visualizacion:** sunburst orbita -> proposito, filtrado a registros enriquecidos UCS.

**Interaccion:** clic en sector para mostrar una tarjeta narrativa:

- Comunicaciones: conectividad, television, internet, constelaciones.
- Earth Observation: clima, agricultura, vigilancia, respuesta a emergencias.
- Navigation: GPS y sistemas equivalentes.
- Science: exploracion y conocimiento.
- Military: seguridad y observacion estrategica.

**Mensaje de apoyo:** en registros enriquecidos, comunicaciones suma 254 registros y observacion terrestre 199. GEO y LEO dominan el reparto orbital enriquecido.

**Limitacion visible:** UCS enriquece 532 registros, por lo que esta seccion representa el subconjunto con atributos orbitales, no todos los lanzamientos historicos.

### Seccion 9 - Que hay actualmente en orbita

**Objetivo narrativo:** cerrar el foco contemporaneo con una imagen de composicion funcional del espacio.

**Mensaje principal:** la actividad actual esta organizada alrededor de usos concretos, no solo hitos historicos.

**Datos utilizados:** `purpose_group`, `satellite_operator`, `orbit_group`, `mass_group`, `satellite_mass_kg` en registros enriquecidos.

**Visualizacion:** treemap por `purpose_group`, subdividido por operador u orbita.

**Interaccion:** clic para cambiar jerarquia: proposito -> operador, proposito -> orbita, orbita -> proposito.

**Mensaje de apoyo:** comunicaciones y observacion terrestre deben ocupar el centro visual.

### Seccion 10 - Conclusion: del simbolo al sistema

**Objetivo narrativo:** sintetizar la historia y responder las cinco preguntas en una conclusion memorable.

**Mensaje principal:** desde Sputnik hasta Starlink, el espacio paso de ser demostracion de poder a convertirse en infraestructura economica y geopolitica.

**Datos utilizados:** resumen de KPIs finales.

**Visualizacion:** pantalla final con cinco tarjetas-respuesta, una por pregunta de investigacion.

**Interaccion:** botones para volver a explorar cada capitulo.

**Texto final sugerido:**

> En 1957, llegar al espacio era una declaracion de poder. En 2025, lanzar al espacio es parte de una cadena de suministro, una red de comunicaciones y una economia orbital. La carrera no ha terminado: ha cambiado de forma.

## FASE 3 - Estructura recomendada de la experiencia

| Seccion | Titulo | Funcion narrativa | Grafico principal | Interaccion |
| --- | --- | --- | --- | --- |
| 1 | De Sputnik a Starlink | Plantear tesis e impacto emocional | Contador acumulado + mini timeline | Scroll activa contador |
| 2 | El primer pulso | Nacimiento bipolar de la carrera espacial | Linea temporal Estados Unidos vs URSS/Rusia | Anotaciones por scroll |
| 3 | Quien dominaba el espacio | Mostrar dominio por pais/periodo | Stacked area por pais | Slider temporal + ranking |
| 4 | Se abre el tablero | Transicion post-Guerra Fria y multipolaridad | Small multiples por periodo | Resaltado de actores emergentes |
| 5 | Estado vs mercado | Giro publico/privado | Area apilada organization_type | Transicion temporal |
| 6 | El factor SpaceX | Explicar el salto reciente | Ranking animado o lineas comparativas | Scroll por hitos 2010-2026 |
| 7 | La fiabilidad | Mostrar maduracion tecnologica | Linea tasa exito + media movil | Hover con eventos historicos |
| 8 | Economia orbital | Mostrar usos actuales | Sunburst orbita-proposito | Clic en sectores con explicacion |
| 9 | Que hay en orbita | Composicion funcional contemporanea | Treemap | Cambio de jerarquia |
| 10 | Conclusion | Responder preguntas y cerrar tesis | Tarjetas-resumen | Navegacion a capitulos |

## FASE 4 - Visualizaciones optimas por pregunta de investigacion

| Pregunta | Mejor grafico | Alternativa | Ventajas | Inconvenientes |
| --- | --- | --- | --- | --- |
| 1. Evolucion de lanzamientos desde 1957 | Linea temporal anual con area acumulada opcional | Barras por decada | Muestra tendencia, picos y aceleracion reciente | La linea anual puede ser ruidosa; conviene añadir media movil o anotaciones |
| 2. Actores lideres por periodo | Stacked area por pais con ranking dinamico | Bump chart de ranking anual | Excelente para mostrar cambio de dominio | Stacked area puede ocultar actores pequeños; bump chart requiere simplificar top actores |
| 3. Publico vs privado | Area apilada Public/Private/Mixed/Unknown | Slope chart por periodos | Comunica muy bien el cambio estructural | Depende de clasificacion heuristica; hay que explicar Unknown |
| 4. Tasa de exito | Linea anual con media movil de 5 años | Heatmap año x actor | Muestra maduracion tecnologica | La calidad depende de estados comparables entre fuentes |
| 5. Tendencias actuales | Sunburst orbita -> proposito y treemap por proposito | Bubble chart masa-tiempo-proposito | Buen resumen de composicion orbital | Solo representa registros enriquecidos UCS; hay que indicar cobertura parcial |

## FASE 5 - Interacciones recomendadas

### Interacciones que aportan valor real

| Interaccion | Donde usarla | Valor narrativo |
| --- | --- | --- |
| Scroll-driven animation | Portada, carrera espacial, publico/privado, SpaceX | Convierte el tiempo en experiencia narrativa; evita dashboard estatico |
| Slider temporal | Seccion de liderazgo por pais | Permite comparar años y ver cambios de liderazgo concretos |
| Ranking lateral sincronizado | Stacked area y SpaceX | Traduce areas visuales a cifras legibles |
| Hover enriquecido | Tasa de exito y linea temporal | Añade contexto historico sin saturar la pantalla |
| Clic en sectores | Sunburst y treemap | Permite profundizar en propositos/orbitas sin crear demasiados graficos |
| Toggle top actores / todos | Liderazgo y proveedores | Reduce ruido y permite exploracion controlada |
| Boton "ver incertidumbre" | Publico/privado y UCS | Explica Unknown y cobertura parcial de UCS de forma transparente |

### Interacciones a evitar

| Interaccion | Motivo |
| --- | --- |
| Filtros globales multiples estilo dashboard | Rompen la narrativa y desplazan la carga al usuario |
| Zoom libre en todos los graficos | No aporta a la historia principal y complica movil/accesibilidad |
| Animaciones permanentes no controladas | Pueden distraer y dificultar lectura |
| Mapas geograficos como visualizacion central | La pregunta principal es temporal y de liderazgo; un mapa puede ser decorativo si no aporta cambio temporal claro |

## FASE 6 - Fotografias e imagenes

Las imagenes deben funcionar como transiciones narrativas, no como decoracion. Usar preferentemente recursos NASA, Wikimedia Commons o archivos institucionales con licencia clara.

| Imagen | Seccion | Por que usarla | Integracion visual |
| --- | --- | --- | --- |
| Sputnik 1 | Portada / inicio | Simbolo del comienzo de la era espacial | Imagen granulada en blanco y negro como fondo inicial; overlay oscuro para contraste |
| Yuri Gagarin | Carrera espacial | Humaniza el hito sovietico y el contexto de 1961 | Aparicion lateral como tarjeta historica al pasar por 1961 |
| Apollo 11 / Saturn V | Carrera espacial | Resume el punto emocional del esfuerzo estadounidense | Transicion a pantalla completa breve antes de 1969 |
| Soyuz / cosmódromo Baikonur | Dominio sovietico | Refuerza el volumen sostenido de URSS/Rusia en los 70-80 | Imagen de textura de fondo en seccion stacked area |
| Space Shuttle | Fiabilidad | Permite introducir que la rutina espacial tambien implica riesgo | Imagen puntual asociada a anotaciones de 1986 y 2003 |
| Long March | Multipolaridad / China | Visualiza la entrada de China como actor central contemporaneo | Imagen en panel de 2010-2026 junto a ranking |
| Falcon 9 landing | SpaceX | Representa reutilizacion y economia comercial | Hero secundario de la seccion SpaceX |
| Starship | Cierre | Sugiere futuro e incertidumbre | Imagen final con pregunta abierta: quien controlara la proxima etapa? |
| Constelacion Starlink / satelites | Economia orbital | Conecta lanzamientos con infraestructura de comunicaciones | Fondo sutil de puntos orbitales en sunburst/treemap |

### Tratamiento visual de imagenes

- Usar duotono azul oscuro / blanco para unificar fuentes historicas distintas.
- Aplicar overlays para garantizar contraste de texto.
- Evitar collages recargados.
- Incluir creditos discretos al final o en tooltip informativo.

## FASE 7 - Accesibilidad

### Color

- Usar paleta apta para daltonismo.
- No codificar Public/Private solo por color; añadir etiquetas directas.
- Propuesta de paleta:
- Public: azul profundo.
- Private: naranja/coral.
- Mixed: morado.
- Unknown: gris neutro.
- United States: azul.
- USSR/Russia: rojo oscuro.
- China: rojo brillante o granate.
- Europe/ESA: turquesa.
- India: verde.
- Otros: gris claro.

### Contraste y tipografia

- Texto principal minimo 18 px en escritorio y 16 px en movil.
- Titulares grandes con alto contraste.
- Evitar texto blanco sobre imagen sin overlay oscuro minimo 60%.
- Etiquetas directas en lineas clave para no depender de leyendas.

### Movimiento

- Respetar `prefers-reduced-motion`.
- Toda animacion debe tener estado final legible sin depender del movimiento.
- Evitar autoplay continuo; usar scroll como control natural.

### Movil

- En movil, sustituir visualizaciones muy anchas por versiones simplificadas:
- Stacked area -> tarjetas por periodo + small multiples.
- Ranking animado -> lista ordenada por año seleccionado.
- Sunburst -> treemap o lista jerarquica accesible.
- Sliders grandes, con targets tactiles minimos de 44 px.

### Lectores de pantalla

- Cada grafico debe tener resumen textual previo.
- Incluir tablas alternativas plegables para rankings clave.
- Los tooltips no deben contener informacion unica; todo evento importante debe estar tambien en texto narrativo.

## FASE 8 - Tecnologia recomendada

### Recomendacion principal

**Svelte + D3 + componentes SVG/Canvas ligeros.**

Justificacion:

- Svelte permite construir una experiencia narrativa fluida sin la complejidad de React para un proyecto acotado.
- D3 da control total sobre transiciones, escalas, anotaciones y scrollytelling.
- Es ideal para una visualizacion tipo The Pudding / NYT, donde el layout y la narrativa importan tanto como los graficos.
- Permite optimizar versiones moviles y accesibles.

### Alternativa pragmatica

**HTML/CSS/JavaScript + D3 + IntersectionObserver.**

Justificacion:

- Menos dependencia de framework.
- Suficiente para una PEC si se quiere entregar un HTML local autonomo.
- Control directo de scrollytelling.

### Uso puntual de Plotly

Plotly puede usarse para prototipos o graficos secundarios, pero no deberia ser la base de la pieza final si se busca una experiencia memorable. Plotly tiende a aspecto de dashboard y limita el control fino del scrollytelling.

### Herramientas no recomendadas como base

| Herramienta | Motivo |
| --- | --- |
| Tableau Public | Buena exploracion, pero resultado tiende a dashboard y menor control narrativo. |
| Flourish | Rapido para racing bars, pero menos flexible para una historia integrada y reproducible. |
| Observable | Excelente para ensayo visual, pero puede complicar entrega local si se exige empaquetado autonomo. |
| React | Potente, pero mas pesado que Svelte para esta pieza concreta. |

## FASE 9 - Entregable final propuesto

### Formato recomendado

Una pagina web narrativa vertical:

```text
index.html
assets/
  data/
    datos_finales_espacio_v2.parquet o csv procesado a json compacto
  images/
    sputnik.webp
    apollo11.webp
    long_march.webp
    falcon9.webp
  scripts/
    charts.js
    scrolly.js
  styles/
    main.css
```

### Principios de diseño

- Una pregunta por pantalla.
- Un grafico dominante por seccion.
- Texto corto, editorial, con datos concretos.
- Anotaciones directas sobre los graficos.
- Interacciones limitadas y justificadas.
- Incertidumbre visible, especialmente en `organization_type` y campos UCS.

### Respuestas finales que debe dejar claras

| Pregunta | Respuesta narrativa esperada |
| --- | --- |
| Evolucion de lanzamientos | La actividad crece por oleadas: arranque rapido, meseta de Guerra Fria, caida post-sovietica y explosion comercial reciente. |
| Liderazgo espacial | El liderazgo pasa de Estados Unidos/URSS a un escenario donde Estados Unidos, China y empresas privadas dominan la etapa reciente. |
| Publico vs privado | El espacio nace estatal, pero en 2020-2026 los actores privados superan a los publicos en los registros clasificados. |
| Tasa de exito | La fiabilidad mejora desde una etapa experimental hasta niveles cercanos al 95% en la era reciente. |
| Tendencias actuales | Los datos enriquecidos muestran una economia orbital centrada en comunicaciones, observacion terrestre y orbitas GEO/LEO. |

## Story arc final

```text
1. Asombro: Sputnik abre una frontera.
2. Competicion: Estados Unidos y URSS/Rusia convierten el espacio en poder.
3. Dominio: la URSS/Rusia gana volumen durante la Guerra Fria.
4. Fragmentacion: el mundo post-1991 abre el tablero.
5. Cambio estructural: lo privado emerge y supera a lo publico en la etapa reciente.
6. Aceleracion: SpaceX cambia la escala del lanzamiento orbital.
7. Madurez: lanzar se vuelve mas fiable.
8. Utilidad: el espacio se convierte en infraestructura economica.
9. Cierre: de plantar banderas a operar redes orbitales.
```

## Decision creativa final

La pieza debe evitar el tono enciclopedico. No debe intentar mostrar todas las columnas ni todos los paises. Debe actuar como una historia editorial basada en datos, con una tesis clara:

**El espacio ya no es solo una carrera por llegar mas lejos; es una competicion por operar la infraestructura que rodea la Tierra.**
