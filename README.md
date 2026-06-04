# De Sputnik a Starlink

Visualizacion editorial sobre la evolucion de la actividad espacial desde 1957.

Publicacion: https://javiermunrom.github.io/de-sputnik-a-starlink/

## Desarrollo

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Despliegue

El sitio se despliega en GitHub Pages mediante GitHub Actions al subir cambios a `main`.

---

## Procesamiento de datos

El pipeline de construccion del dataset final esta en [`data-processing/`](data-processing/).

```
data-processing/
├── 01_datos/
│   ├── originales/          # Fuentes originales (GCAT, Space_Missions, UCS)
│   └── final/               # Dataset consolidado (CSV + Parquet)
├── 02_notebooks/            # Notebook reproducible
├── 03_scripts/              # Pipeline Python de ETL
│   ├── pipeline_dataset_final.py          # Pipeline principal
│   ├── generar_analisis_dataset_final.py  # Auditoria de calidad
│   └── generar_exploracion_visualizaciones.py  # Prototipos
├── 04_informes/final/       # Decisiones de diseño, storyboard y tablas de evaluacion
├── requirements.txt
└── setup.sh
```

### Pipeline

1. **Carga** de las tres fuentes originales (Space_Missions CSV, GCAT TSV, UCS Excel)
2. **Limpieza** y normalizacion de paises, organizaciones, orbitas y propositos
3. **Integracion** por concatenaicon de Space_Missions + GCAT y fusion con UCS mediante clave normalizada de nombre
4. **Variables derivadas**: año, decada, era espacial, tipo de organizacion, clasificacion de exito, grupo de orbita y proposito
5. **Evaluacion** de columnas, deteccion de redundancias y validacion contra preguntas de investigacion
6. **Exportacion** a CSV, Parquet, tablas auxiliares de decision e informe de diseño

Para reproducir:

```bash
cd data-processing
python -m venv .venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows
pip install -r requirements.txt
python 03_scripts/pipeline_dataset_final.py
```
