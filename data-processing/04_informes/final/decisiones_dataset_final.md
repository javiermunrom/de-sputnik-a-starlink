# Decisiones del dataset final v2

## Objetivo
Optimizar el dataset para responder la evolucion de lanzamientos, liderazgo espacial, publico vs privado, exito de misiones y tendencias actuales. No se optimiza por reducir columnas, sino por valor analitico para visualizacion.

## FASE 1 - Problemas extraidos de la auditoria existente
| Problema | Impacto | Accion propuesta |
| --- | --- | --- |
| La masa satelital esta muy incompleta; usarla solo para tendencias parciales o subconjuntos enriquecidos. | Medio | Mitigar en pipeline v2 |
| GCAT y Space_Missions pueden solaparse; para conteos usar preferred_for_launch_count para evitar doble conteo. | Alto | Mitigar en pipeline v2 |
| Los registros de 2026 pueden estar incompletos porque el anio esta en curso o depende de actualizaciones de GCAT. | Medio | Mitigar en pipeline v2 |
| Mantener las tablas de normalizacion de paises y organizaciones junto al dataset final. | Medio | Corregir en v2 y documentar |
| Validar manualmente la clasificacion `organization_type` en actores ambiguos. | Medio | Corregir en v2 y documentar |
| Usar `preferred_for_launch_count == True` para evitar doble conteo historico. | Alto | Corregir en v2 y documentar |
| Columnas UCS muy incompletas por bajo match de nombres | Medio | Conservar las variables de valor analitico, marcar ucs_match_found y usar No UCS match. |
| Variantes de paises y organizaciones | Alto | Aplicar tablas de equivalencia para paises, organizaciones y operadores. |
| Campos de masa, orbita y proposito no cubren todos los lanzamientos | Medio | Usarlos para tendencias actuales y subconjuntos enriquecidos, no para conteos historicos globales. |
| Solape entre GCAT y Space_Missions | Alto | Mantener preferred_for_launch_count y usar GCAT para conteos historicos. |

## FASE 2 - Revision de columnas
| Columna | Utilidad analitica 0-10 | Utilidad preguntas 0-10 | Calidad datos 0-10 | % nulos | Redundancia | Decision | Preguntas asociadas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ucs_satellite_name | 5 | 3 | 0.5 | 95.42 | no | eliminar | apoyo/trazabilidad |
| year | 8 | 10 | 10.0 | 0.0 | no | mantener | Evolucion de lanzamientos; Liderazgo de actores; Publico vs privado; Tasa de exito; Tendencias actuales |
| launch_provider | 8 | 9 | 10.0 | 0.0 | no | mantener | Liderazgo de actores; Publico vs privado |
| source_dataset | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| record_level | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| launch_date | 8 | 6 | 5.7 | 43.04 | no | mantener | apoyo/trazabilidad |
| decade | 8 | 6 | 10.0 | 0.0 | no | mantener | Evolucion de lanzamientos |
| space_era | 8 | 6 | 10.0 | 0.0 | no | mantener | Evolucion de lanzamientos |
| launch_frequency_period | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| mission_name | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| satellite_name | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| country | 8 | 6 | 10.0 | 0.0 | no | mantener | Liderazgo de actores |
| launch_site | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| launch_vehicle | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| mission_status | 8 | 6 | 10.0 | 0.0 | no | mantener | Tasa de exito |
| mission_success_binary | 8 | 6 | 9.8 | 2.03 | no | mantener | Tasa de exito |
| payload_count | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| preferred_for_launch_count | 8 | 6 | 10.0 | 0.0 | no | mantener | Evolucion de lanzamientos |
| ucs_match_found | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| satellite_operator | 8 | 6 | 10.0 | 0.0 | no | mantener | Publico vs privado |
| purpose_group | 8 | 6 | 10.0 | 0.0 | no | mantener | Tendencias actuales |
| organization_type | 8 | 6 | 10.0 | 0.0 | no | mantener | Publico vs privado |
| launch_id | 8 | 6 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| satellite_operator_country | 8 | 6 | 10.0 | 0.0 | si | transformar | Liderazgo de actores |
| satellite_users | 8 | 6 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| satellite_purpose | 8 | 6 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| orbit_type | 8 | 6 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| orbit_group | 8 | 6 | 10.0 | 0.0 | si | transformar | Tendencias actuales |
| satellite_mass_kg | 8 | 6 | 4.0 | 95.83 | si | transformar | Tendencias actuales |
| mass_group | 8 | 6 | 10.0 | 0.0 | si | transformar | Tendencias actuales |
| satellite_detailed_purpose | 7 | 3 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| orbit_subtype | 7 | 3 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| ucs_launch_vehicle | 7 | 3 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| ucs_launch_site | 7 | 3 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| cospar_number | 7 | 3 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| norad_number | 7 | 3 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| source_record_id | 5 | 3 | 10.0 | 0.0 | no | transformar | apoyo/trazabilidad |
| launch_date_raw | 5 | 3 | 10.0 | 0.0 | no | transformar | apoyo/trazabilidad |
| rocket_status | 5 | 3 | 10.0 | 0.0 | no | transformar | apoyo/trazabilidad |
| name_key | 5 | 3 | 10.0 | 0.09 | no | transformar | apoyo/trazabilidad |
| source_count | 3 | 3 | 10.0 | 0.0 | no | transformar/eliminar si no documenta trazabilidad | apoyo/trazabilidad |

## FASE 3 - Propuesta de eliminacion/conservacion
Columnas eliminables o candidatas a no incorporar desde las fuentes originales:
| Columna | Utilidad analitica 0-10 | Utilidad preguntas 0-10 | Calidad datos 0-10 | % nulos | Redundancia | Decision | Preguntas asociadas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ucs_satellite_name | 5 | 3 | 0.5 | 95.42 | no | eliminar | apoyo/trazabilidad |
| source_count | 3 | 3 | 10.0 | 0.0 | no | transformar/eliminar si no documenta trazabilidad | apoyo/trazabilidad |

Columnas recomendadas para conservar o transformar:
| Columna | Utilidad analitica 0-10 | Utilidad preguntas 0-10 | Calidad datos 0-10 | % nulos | Redundancia | Decision | Preguntas asociadas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| year | 8 | 10 | 10.0 | 0.0 | no | mantener | Evolucion de lanzamientos; Liderazgo de actores; Publico vs privado; Tasa de exito; Tendencias actuales |
| launch_provider | 8 | 9 | 10.0 | 0.0 | no | mantener | Liderazgo de actores; Publico vs privado |
| source_dataset | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| record_level | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| launch_date | 8 | 6 | 5.7 | 43.04 | no | mantener | apoyo/trazabilidad |
| decade | 8 | 6 | 10.0 | 0.0 | no | mantener | Evolucion de lanzamientos |
| space_era | 8 | 6 | 10.0 | 0.0 | no | mantener | Evolucion de lanzamientos |
| launch_frequency_period | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| mission_name | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| satellite_name | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| country | 8 | 6 | 10.0 | 0.0 | no | mantener | Liderazgo de actores |
| launch_site | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| launch_vehicle | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| mission_status | 8 | 6 | 10.0 | 0.0 | no | mantener | Tasa de exito |
| mission_success_binary | 8 | 6 | 9.8 | 2.03 | no | mantener | Tasa de exito |
| payload_count | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| preferred_for_launch_count | 8 | 6 | 10.0 | 0.0 | no | mantener | Evolucion de lanzamientos |
| ucs_match_found | 8 | 6 | 10.0 | 0.0 | no | mantener | apoyo/trazabilidad |
| satellite_operator | 8 | 6 | 10.0 | 0.0 | no | mantener | Publico vs privado |
| purpose_group | 8 | 6 | 10.0 | 0.0 | no | mantener | Tendencias actuales |
| organization_type | 8 | 6 | 10.0 | 0.0 | no | mantener | Publico vs privado |
| launch_id | 8 | 6 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| satellite_operator_country | 8 | 6 | 10.0 | 0.0 | si | transformar | Liderazgo de actores |
| satellite_users | 8 | 6 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| satellite_purpose | 8 | 6 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| orbit_type | 8 | 6 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| orbit_group | 8 | 6 | 10.0 | 0.0 | si | transformar | Tendencias actuales |
| satellite_mass_kg | 8 | 6 | 4.0 | 95.83 | si | transformar | Tendencias actuales |
| mass_group | 8 | 6 | 10.0 | 0.0 | si | transformar | Tendencias actuales |
| satellite_detailed_purpose | 7 | 3 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| orbit_subtype | 7 | 3 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| ucs_launch_vehicle | 7 | 3 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| ucs_launch_site | 7 | 3 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| cospar_number | 7 | 3 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| norad_number | 7 | 3 | 10.0 | 0.0 | si | transformar | apoyo/trazabilidad |
| source_record_id | 5 | 3 | 10.0 | 0.0 | no | transformar | apoyo/trazabilidad |
| launch_date_raw | 5 | 3 | 10.0 | 0.0 | no | transformar | apoyo/trazabilidad |
| rocket_status | 5 | 3 | 10.0 | 0.0 | no | transformar | apoyo/trazabilidad |
| name_key | 5 | 3 | 10.0 | 0.09 | no | transformar | apoyo/trazabilidad |

## FASE 4 - Tratamiento de nulos
| Columna | % nulos | Accion | Justificacion |
| --- | --- | --- | --- |
| launch_date | 43.04 | mantener nulos e inferir year cuando sea posible | La fecha exacta no siempre es recuperable, pero year conserva la utilidad temporal principal. |
| name_key | 0.09 | mantener nulos | No existe una imputacion segura sin crear informacion artificial. |
| ucs_satellite_name | 95.42 | mantener nulos | No existe una imputacion segura sin crear informacion artificial. |
| satellite_operator | 95.42 | imputar con No UCS match | Campo categorico: una categoria explicita permite filtrar y no confunde ausencia de dato con dato real. |
| satellite_operator_country | 95.42 | imputar con No UCS match | Campo categorico: una categoria explicita permite filtrar y no confunde ausencia de dato con dato real. |
| satellite_users | 95.42 | imputar con No UCS match | Campo categorico: una categoria explicita permite filtrar y no confunde ausencia de dato con dato real. |
| satellite_purpose | 95.42 | imputar con No UCS match | Campo categorico: una categoria explicita permite filtrar y no confunde ausencia de dato con dato real. |
| satellite_detailed_purpose | 98.33 | imputar con No UCS match | Campo categorico: una categoria explicita permite filtrar y no confunde ausencia de dato con dato real. |
| orbit_type | 95.42 | imputar con No UCS match | Campo categorico: una categoria explicita permite filtrar y no confunde ausencia de dato con dato real. |
| orbit_subtype | 98.14 | imputar con No UCS match | Campo categorico: una categoria explicita permite filtrar y no confunde ausencia de dato con dato real. |
| satellite_mass_kg | 95.83 | mantener nulos | Variable numerica de alto valor para tendencias actuales; imputar mediana distorsionaria la masa real. Se usa mass_group = Unknown para visualizacion categorica. |
| ucs_launch_vehicle | 95.42 | imputar con No UCS match | Campo categorico: una categoria explicita permite filtrar y no confunde ausencia de dato con dato real. |
| ucs_launch_site | 95.42 | imputar con No UCS match | Campo categorico: una categoria explicita permite filtrar y no confunde ausencia de dato con dato real. |
| cospar_number | 95.42 | imputar con No UCS match | Campo categorico: una categoria explicita permite filtrar y no confunde ausencia de dato con dato real. |
| norad_number | 95.42 | imputar con No UCS match | Campo categorico: una categoria explicita permite filtrar y no confunde ausencia de dato con dato real. |
| mission_success_binary | 2.03 | mantener nulos | No todos los codigos de estado son comparables; imputar exito/fallo introduceria sesgo. |

## FASE 5 - Normalizacion
Se normalizaron paises, organizaciones, operadores, orbitas y propositos mediante tablas de correspondencia. Las tablas completas se generan internamente y se resumen aqui.

### Paises
| valor_original | valor_normalizado |
| --- | --- |
| AO | AO |
| AR | AR |
| AT | AT |
| AZ | AZ |
| Australia | Australia |
| B | B |
| BD | BD |
| BGN | BGN |
| BM | BM |
| BO | BO |
| BT | BT |
| BY | BY |
| Barents Sea | Barents Sea |
| Brazil | Brazil |
| CH | CH |
| CL | CL |
| CSFR | CSFR |
| CSSR | CSSR |
| CZ | CZ |
| Canada | Canada |
| China | China |
| DK | DK |
| DZ | DZ |
| EE | EE |
| EG | EG |
| Europe/ESA | Europe/ESA |
| France | France |
| GR | GR |
| Germany | Germany |
| Gran Canaria | Gran Canaria |
| HK | HK |
| HKUK | HKUK |
| HU | HU |
| I-ARAB | I-ARAB |
| I-ELDO | I-ELDO |
| I-ESRO | I-ESRO |
| I-EUM | I-EUM |
| I-EUT | I-EUT |
| I-INM | I-INM |
| I-INT | I-INT |
| I-NATO | I-NATO |
| I-RASC | I-RASC |
| ID | ID |
| IE | IE |
| India | India |
| Iran | Iran |
| Israel | Israel |
| Italy | Italy |
| Japan | Japan |
| KZ | KZ |

### Organizaciones
| valor_original | valor_normalizado |
| --- | --- |
| 10ADS | 10ADS |
| 2SLS/AFSMC | 2SLS/AFSMC |
| 3SLS/AFSMC | 3SLS/AFSMC |
| 4SLS/AFSMC | 4SLS/AFSMC |
| ABLSS | ABLSS |
| ABMA | ABMA |
| ADD | ADD |
| AFBMD | AFBMD |
| AFORS/SAND | AFORS/SAND |
| AFSC | AFSC |
| AFSD | AFSD |
| AFSMC | AFSMC |
| AFSPC | AFSPC |
| AFSSD | AFSSD |
| AFSSD/MSC | AFSSD/MSC |
| AFSSD/STG | AFSSD/STG |
| AFSSD/STGL | AFSSD/STGL |
| AFSSD2 | AFSSD2 |
| AMBA | AMBA |
| ASI | ASI |
| ASTRV | ASTRV |
| Arianespace | Arianespace |
| Arm??e de l'Air | Arm??e de l'Air |
| BLOR | BLOR |
| BLS | BLS |
| Blue Origin | Blue Origin |
| Boeing | Boeing |
| CASC | CASC |
| CASIC | CASIC |
| CASIC4A | CASIC4A |
| CAST | CAST |
| CECLES | CECLES |
| CNES | CNES |
| CRA | CRA |
| CZHJ | CZHJ |
| DFK | DFK |
| Douglas | Douglas |
| EER | EER |
| ELDO | ELDO |
| ELUS | ELUS |
| ESA | ESA |
| EUROK | EUROK |
| EXPACE | EXPACE |
| Eurockot | Eurockot |
| ExPace | ExPace |
| Exos | Exos |
| FFLY | FFLY |
| GDCLS | GDCLS |
| GILM | GILM |
| GKLS | GKLS |

### Operadores
| valor_original | valor_normalizado |
| --- | --- |
| APT Satellite Holdings Ltd. | APT Satellite Holdings Ltd. |
| Agency for Defense Development | Agency for Defense Development |
| Al Yah Satellite Communications Co. (YAHSAT) | Al Yah Satellite Communications Co. (YAHSAT) |
| AngoSat | AngoSat |
| Arab Satellite Communications Org. (ASCO) | Arab Satellite Communications Org. (ASCO) |
| Arianespace | Arianespace |
| Armed Forces | Armed Forces |
| Asia Broadcast Satellite Ltd. | Asia Broadcast Satellite Ltd. |
| Asia Satellite Telecommunications Co. Ltd. | Asia Satellite Telecommunications Co. Ltd. |
| Astro Digital | Astro Digital |
| Beijing Future Navigation Technology Co. Ltd. | Beijing Future Navigation Technology Co. Ltd. |
| Belintersat | Belintersat |
| Bolivarian Agency for Space Activities | Bolivarian Agency for Space Activities |
| Bulsatcom | Bulsatcom |
| CASC | CASC |
| CASIOM | CASIOM |
| CNSA | CNSA |
| Cabinet Satellite Intelligence Center (CSIC) | Cabinet Satellite Intelligence Center (CSIC) |
| Canadian Space Agency | Canadian Space Agency |
| Centre National d'Etudes Spatiales (CNES)/Délégation Générale de l'Armement (DGA) | Centre National d'Etudes Spatiales (CNES)/Délégation Générale de l'Armement (DGA) |
| Chang Guang Satellite Technology Co. Ltd. | Chang Guang Satellite Technology Co. Ltd. |
| China Academy of Space Technology (CAST) | China Academy of Space Technology (CAST) |
| China Meteorological Administration | China Meteorological Administration |
| China National Space Administration | China National Space Administration |
| China Satellite Communication Corp. (China Satcom) | China Satellite Communication Corp. (China Satcom) |
| China Telecom | China Telecom |
| China's Ministry of Land and Resources, Ministry of Environmental Protection, and Ministry of Agriculture | China's Ministry of Land and Resources, Ministry of Environmental Protection, and Ministry of Agriculture |
| Chinese Academy of Launch Vehicle Technology (CASIC) | Chinese Academy of Launch Vehicle Technology (CASIC) |
| Chinese Academy of Sciences | Chinese Academy of Sciences |
| Chinese Ministry of National Defense | Chinese Ministry of National Defense |
| Ciel Satellite Group | Ciel Satellite Group |
| Defense Ministry | Defense Ministry |
| Deimos Imaging/DMC International Imaging (DMCII) | Deimos Imaging/DMC International Imaging (DMCII) |
| DigitalGlobe Corporation | DigitalGlobe Corporation |
| DirecTV, Inc. | DirecTV, Inc. |
| Directorate General of Armaments (DGA) | Directorate General of Armaments (DGA) |
| DoD/NOAA | DoD/NOAA |
| DoD/US Navy | DoD/US Navy |
| ESA | ESA |
| EUMETSAT (European Organization for the Exploitation of Meteorological Satellites) | EUMETSAT (European Organization for the Exploitation of Meteorological Satellites) |
| Echostar Satellite Services, LLC | Echostar Satellite Services, LLC |
| Egyptian Radio and TV Union | Egyptian Radio and TV Union |
| Egyptian Space Agency | Egyptian Space Agency |
| Es’hailSat | Es’hailSat |
| European Space Operations Centre (ESOC) | European Space Operations Centre (ESOC) |
| Eutelsat | Eutelsat |
| F /ORSO (Operationally Responsive Space Office) | F /ORSO (Operationally Responsive Space Office) |
| GalaxySpace | GalaxySpace |
| Gazprom Space Systems | Gazprom Space Systems |
| Geo-Informatics and Space Technology Development Agency (GISTDA) | Geo-Informatics and Space Technology Development Agency (GISTDA) |

### Orbitas
| valor_original | valor_normalizado |
| --- | --- |
| Elliptical | HEO |
| GEO | GEO |
| LEO | LEO |
| MEO | MEO |
| No UCS match | No UCS match |

### Propositos
| valor_original | valor_normalizado |
| --- | --- |
| Communications | Communications |
| Earth Observation | Earth Observation |
| Earth Observation/Technology Development | Earth Observation |
| Earth Science | Earth Observation |
| Navigation/Global Positioning | Navigation |
| Navigation/Regional Positioning | Navigation |
| No UCS match | Other |
| Space Observation | Earth Observation |
| Space Science | Science |
| Technology Demonstration | Technology |
| Technology Development | Technology |

## FASE 6 - Variables derivadas anadidas
| Variable | Explicacion |
| --- | --- |
| year | Anio del lanzamiento; eje temporal principal. |
| decade | Agrupa anios por decadas para comparaciones historicas. |
| space_era | Clasifica Early Space Age, Space Race, Post Cold War y Commercial Space Age. |
| organization_type | Clasifica actores como Public, Private, Mixed o Unknown a partir de proveedor y operador. |
| mission_success_binary | Codifica exito/fallo de mision; conserva nulos si el estado no es comparable. |
| purpose_group | Agrupa propositos satelitales en categorias visualizables. |
| orbit_group | Simplifica clases orbitales en LEO, MEO, GEO, HEO u otras. |
| mass_group | Agrupa masa sin imputar la masa numerica original. |
| launch_frequency_period | Segmenta periodos por dinamica de frecuencia de lanzamientos. |

## FASE 7 - Validacion de preguntas
| Pregunta | Cobertura util v2 % | Cobertura provisional % | Mejora pp | Nivel confianza | Variables clave |
| --- | --- | --- | --- | --- | --- |
| Evolucion de lanzamientos | 100.0 | 100.0 | 0.0 | Alta | year, decade, space_era, preferred_for_launch_count |
| Liderazgo de actores | 100.0 | 100.0 | 0.0 | Alta | year, country, launch_provider, satellite_operator_country |
| Publico vs privado | 72.54 | 45.94 | 26.6 | Media | year, organization_type, launch_provider, satellite_operator |
| Tasa de exito | 97.97 | 93.32 | 4.65 | Alta | year, mission_success_binary, mission_status |
| Tendencias actuales | 4.58 | 2.29 | 2.29 | Parcial | year, orbit_group, purpose_group, mass_group, satellite_mass_kg |

## FASE 8 - Metricas del dataset definitivo
| filas | columnas | memoria_mb | cobertura_temporal | porcentaje_nulos_final |
| --- | --- | --- | --- | --- |
| 11627 | 41 | 23.44 | 1957-2026 | 5.77 |

## Fusion de datasets
Se usa GCAT y Space_Missions como base de eventos de lanzamiento. GCAT queda marcado como fuente preferente para conteos historicos con `preferred_for_launch_count = True`; Space_Missions se conserva para trazabilidad y comparacion, pero no para duplicar conteos. UCS se une por `name_key`, una clave normalizada a partir de nombres oficiales y alternativos de satelites.

## Columnas eliminadas o no incorporadas
No se incorporaron columnas `Unnamed:*` de UCS, columnas de fuentes/citas bibliograficas de UCS y comentarios libres porque aportan baja utilidad directa a las cinco preguntas y aumentan ruido. Se sustituyeron variantes crudas de pais/organizacion por valores normalizados, manteniendo identificadores y trazabilidad suficientes.

## Mejora principal
La v2 corrige `source_dataset`, reduce nulos categoricos con categorias informativas, normaliza actores/paises y mantiene variables UCS aunque sean incompletas cuando sirven para tendencias actuales. Esto mejora la calidad para visualizacion sin eliminar informacion analiticamente valiosa.