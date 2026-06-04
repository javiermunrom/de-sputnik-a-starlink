from __future__ import annotations

from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
import html
import json
import re

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import get_plotlyjs


ROOT = Path(__file__).resolve().parents[1]
DATASET_PARQUET = ROOT / "01_datos" / "final" / "datos_finales_espacio_v2.parquet"
DATASET_CSV = ROOT / "01_datos" / "final" / "datos_finales_espacio_v2.csv"
REPORTS_DIR = ROOT / "04_informes" / "final"
HTML_OUT = REPORTS_DIR / "analisis_dataset_final.html"
MD_OUT = REPORTS_DIR / "analisis_dataset_final.md"
CURRENT_YEAR = datetime.now().year


DESCRIPTION_HINTS = {
    "source_dataset": "Fuente original del registro base.",
    "source_record_id": "Identificador del registro en la fuente original.",
    "record_level": "Nivel de observacion: lanzamiento, satelite o agrupacion de payloads.",
    "launch_id": "Identificador del lanzamiento o evento normalizado.",
    "launch_date": "Fecha del lanzamiento cuando se pudo parsear.",
    "year": "Anio del evento; eje temporal principal del analisis.",
    "mission_name": "Nombre de mision o descripcion del evento.",
    "satellite_name": "Nombre de satelite, payload o carga util asociada.",
    "launch_provider": "Organizacion, agencia o empresa responsable del lanzamiento.",
    "country": "Pais o estado asociado al lanzamiento u operador.",
    "launch_site": "Sitio de lanzamiento.",
    "launch_vehicle": "Vehiculo lanzador o cohete.",
    "mission_status": "Resultado o estado de la mision/lanzamiento.",
    "rocket_status": "Estado operativo del cohete en la fuente Space_Missions.",
    "source_count": "Conteo original usado por la fuente.",
    "preferred_for_launch_count": "Marca de registros recomendados para conteos historicos de lanzamientos.",
    "launch_date_raw": "Fecha sin transformar procedente de la fuente original.",
    "payload_count": "Numero de payloads u objetos asociados en el registro agregado.",
    "name_key": "Clave normalizada de nombre para integracion entre fuentes.",
    "ucs_satellite_name": "Nombre oficial del satelite procedente de UCS.",
    "satellite_operator": "Operador o propietario del satelite segun UCS.",
    "satellite_operator_country": "Pais del operador/propietario segun UCS.",
    "satellite_users": "Tipo de usuarios del satelite segun UCS.",
    "satellite_purpose": "Proposito declarado del satelite.",
    "satellite_detailed_purpose": "Proposito detallado del satelite.",
    "orbit_type": "Clase orbital principal.",
    "orbit_subtype": "Tipo orbital detallado.",
    "satellite_mass_kg": "Masa de lanzamiento del satelite en kg cuando existe.",
    "ucs_launch_vehicle": "Vehiculo de lanzamiento procedente de UCS.",
    "ucs_launch_site": "Sitio de lanzamiento procedente de UCS.",
    "cospar_number": "Identificador COSPAR.",
    "norad_number": "Identificador NORAD.",
    "decade": "Decada derivada del anio.",
    "cold_war_period": "Indicador del periodo 1957-1991.",
    "post_cold_war_period": "Indicador del periodo posterior a la Guerra Fria.",
    "space_era": "Etapa historica de la actividad espacial.",
    "launch_frequency_period": "Periodo interpretativo segun dinamica de frecuencia de lanzamientos.",
    "ucs_match_found": "Indica si el registro tuvo enriquecimiento UCS por nombre normalizado.",
    "organization_type": "Clasificacion heuristica publico/privado/desconocido.",
    "mission_success_binary": "Exito binario de mision: 1 exito, 0 fallo, nulo desconocido.",
    "orbit_group": "Grupo orbital simplificado.",
    "mass_group": "Grupo de masa derivado.",
    "purpose_group": "Grupo de proposito derivado.",
}


CATEGORY_KEYWORDS = {
    "lanzamientos": ["launch", "year", "date", "vehicle", "site", "count"],
    "paises": ["country", "state"],
    "organizaciones": ["provider", "operator", "owner", "agency", "company"],
    "empresas": ["provider", "operator", "organization_type"],
    "satelites": ["satellite", "payload", "norad", "cospar", "name_key"],
    "misiones": ["mission", "status", "success"],
    "orbitas": ["orbit", "apogee", "perigee", "inclination"],
    "masa": ["mass", "kg", "weight"],
    "proposito": ["purpose", "users"],
    "exito_fallo": ["success", "status", "failure"],
}


def esc(value) -> str:
    return html.escape("" if pd.isna(value) else str(value), quote=True)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def normalize_text(value) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip().lower())


def normalize_key(value) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize_text(value))


def load_dataset() -> pd.DataFrame:
    if DATASET_PARQUET.exists():
        df = pd.read_parquet(DATASET_PARQUET)
    elif DATASET_CSV.exists():
        df = pd.read_csv(DATASET_CSV, low_memory=False)
    else:
        raise FileNotFoundError("No se encontro datos_finales_espacio_v2.parquet ni datos_finales_espacio_v2.csv")
    return df


def infer_source(row) -> str:
    launch_id = str(row.get("launch_id", ""))
    if launch_id.startswith("space_"):
        base = "Space_Missions"
    elif re.match(r"^(19|20)\d{2}[- ]", launch_id):
        base = "GCAT"
    else:
        base = "Fuente no identificada"
    if pd.notna(row.get("ucs_satellite_name")) or pd.notna(row.get("satellite_operator")):
        return f"{base} + UCS"
    return base


def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = pd.to_numeric(out.get("year"), errors="coerce")
    if "launch_date" in out.columns:
        out["launch_date"] = pd.to_datetime(out["launch_date"], errors="coerce", utc=True)
    source_missing = "source_dataset" not in out or out["source_dataset"].isna().mean() > 0.9
    if source_missing:
        out["source_inferred"] = out.apply(infer_source, axis=1)
    else:
        out["source_inferred"] = out["source_dataset"].fillna(out.apply(infer_source, axis=1))
        if "ucs_match_found" in out:
            out.loc[out["ucs_match_found"].fillna(False), "source_inferred"] = out.loc[out["ucs_match_found"].fillna(False), "source_inferred"].astype(str) + " + UCS"
    if "decade" not in out:
        out["decade"] = (out["year"] // 10 * 10).astype("Int64").astype(str) + "s"
        out.loc[out["year"].isna(), "decade"] = "unknown"
    return out


def memory_mb(df: pd.DataFrame) -> float:
    return df.memory_usage(deep=True).sum() / 1024**2


def table_html(df: pd.DataFrame, table_id: str, max_rows: int | None = None) -> str:
    data = df.copy()
    if max_rows is not None:
        data = data.head(max_rows)
    headers = "".join(f"<th>{esc(col)}</th>" for col in data.columns)
    rows = []
    for _, row in data.iterrows():
        cells = "".join(f"<td>{esc(value)}</td>" for value in row.tolist())
        rows.append(f"<tr>{cells}</tr>")
    return f"""
    <div class="table-toolbar"><input class="datatable-search" data-table="{table_id}" placeholder="Filtrar tabla..."></div>
    <div class="table-responsive"><table id="{table_id}" class="table table-striped table-hover datatable">
      <thead><tr>{headers}</tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table></div>
    """


def fig_html(fig) -> str:
    fig.update_layout(template="plotly_white", margin=dict(l=40, r=20, t=60, b=40), height=420)
    return pio.to_html(fig, include_plotlyjs=False, full_html=False, config={"displaylogo": False, "responsive": True})


def infer_description(col: str) -> str:
    if col in DESCRIPTION_HINTS:
        return DESCRIPTION_HINTS[col]
    lower = col.lower()
    if "date" in lower:
        return "Variable temporal o fecha inferida por nombre."
    if "id" in lower or "key" in lower:
        return "Identificador o clave candidata."
    if "status" in lower:
        return "Variable de estado o resultado."
    if "count" in lower:
        return "Variable de conteo."
    return "Descripcion inferida no disponible; revisar significado en la fuente original."


def variable_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        rows.append({
            "nombre": col,
            "tipo": str(df[col].dtype),
            "descripcion_inferida": infer_description(col),
            "nulos_pct": round(df[col].isna().mean() * 100, 2),
            "valores_unicos": int(df[col].nunique(dropna=True)),
        })
    return pd.DataFrame(rows).sort_values(["nulos_pct", "nombre"], ascending=[False, True])


def quality_analysis(df: pd.DataFrame) -> dict:
    null_pct_by_col = (df.isna().mean() * 100).sort_values(ascending=False)
    unique_counts = df.nunique(dropna=True)
    constant_cols = unique_counts[unique_counts <= 1].index.tolist()
    high_card_cols = unique_counts[(unique_counts / max(len(df), 1) > 0.85) & (unique_counts > 50)].index.tolist()
    low_card_cols = unique_counts[(unique_counts <= 5) & (unique_counts > 1)].index.tolist()
    warnings = []

    for col in df.columns:
        lower = col.lower()
        if "date" in lower:
            parsed = pd.to_datetime(df[col], errors="coerce", utc=True, format="mixed")
            original_non_null = df[col].notna().sum()
            if original_non_null and parsed.notna().sum() / original_non_null < 0.8:
                warnings.append({"tipo": "fecha mal parseada", "columna": col, "detalle": "Menos del 80% de valores no nulos se parsean como fecha."})
        if df[col].dtype == "object":
            sample = df[col].dropna().astype(str)
            if len(sample) > 0:
                numeric_ratio = pd.to_numeric(sample.str.replace(",", ".", regex=False), errors="coerce").notna().mean()
                if numeric_ratio > 0.9:
                    warnings.append({"tipo": "numero almacenado como texto", "columna": col, "detalle": f"{numeric_ratio:.0%} de valores parecen numericos."})
                stripped = sample.str.strip()
                if (sample != stripped).mean() > 0.01:
                    warnings.append({"tipo": "categoria inconsistente", "columna": col, "detalle": "Hay espacios al inicio o final."})
                if sample.str.lower().nunique() < sample.nunique() and sample.nunique() <= 1000:
                    warnings.append({"tipo": "categoria inconsistente", "columna": col, "detalle": "Hay variantes por mayusculas/minusculas."})

    return {
        "total_null_pct": round(df.isna().mean().mean() * 100, 2),
        "top_nulls": null_pct_by_col.head(15).reset_index().rename(columns={"index": "columna", 0: "nulos_pct"}),
        "no_nulls": pd.DataFrame({"columna": null_pct_by_col[null_pct_by_col == 0].index.tolist()}),
        "duplicates": int(df.duplicated().sum()),
        "duplicates_pct": round(df.duplicated().mean() * 100, 2),
        "constant_cols": constant_cols,
        "high_card_cols": high_card_cols,
        "low_card_cols": low_card_cols,
        "warnings": pd.DataFrame(warnings),
    }


def relationships(df: pd.DataFrame) -> dict:
    numeric = df.select_dtypes(include=[np.number, "boolean"]).copy()
    corr_rows = []
    if numeric.shape[1] >= 2:
        corr = numeric.corr(numeric_only=True).abs()
        for i, col_a in enumerate(corr.columns):
            for col_b in corr.columns[i + 1:]:
                value = corr.loc[col_a, col_b]
                if pd.notna(value) and value >= 0.85:
                    corr_rows.append({"columna_1": col_a, "columna_2": col_b, "correlacion_abs": round(float(value), 3)})

    redundancy_rows = []
    cols = list(df.columns)
    for i, a in enumerate(cols):
        sa = df[a].fillna("__NA__").astype(str).map(normalize_text)
        for b in cols[i + 1:]:
            sb = df[b].fillna("__NA__").astype(str).map(normalize_text)
            equal_ratio = (sa == sb).mean()
            if equal_ratio >= 0.95:
                redundancy_rows.append({"columna_1": a, "columna_2": b, "coincidencia_pct": round(equal_ratio * 100, 2)})

    key_rows = []
    for col in df.columns:
        unique_ratio = df[col].nunique(dropna=True) / max(df[col].notna().sum(), 1)
        non_null_pct = df[col].notna().mean() * 100
        if unique_ratio > 0.98 and non_null_pct > 90:
            key_rows.append({"columna": col, "unicidad_pct": round(unique_ratio * 100, 2), "no_nulos_pct": round(non_null_pct, 2), "tipo": "clave primaria posible"})
        elif unique_ratio > 0.90 and non_null_pct > 70:
            key_rows.append({"columna": col, "unicidad_pct": round(unique_ratio * 100, 2), "no_nulos_pct": round(non_null_pct, 2), "tipo": "clave candidata"})

    removable = sorted(set([row["columna_2"] for row in redundancy_rows] + [c for c in df.columns if df[c].isna().mean() > 0.95]))
    return {
        "correlations": pd.DataFrame(corr_rows).sort_values("correlacion_abs", ascending=False) if corr_rows else pd.DataFrame(columns=["columna_1", "columna_2", "correlacion_abs"]),
        "redundant": pd.DataFrame(redundancy_rows).sort_values("coincidencia_pct", ascending=False) if redundancy_rows else pd.DataFrame(columns=["columna_1", "columna_2", "coincidencia_pct"]),
        "keys": pd.DataFrame(key_rows).sort_values(["tipo", "unicidad_pct"], ascending=[True, False]) if key_rows else pd.DataFrame(columns=["columna", "unicidad_pct", "no_nulos_pct", "tipo"]),
        "removable": removable,
    }


def temporal_analysis(df: pd.DataFrame) -> dict:
    years = pd.to_numeric(df["year"], errors="coerce").dropna().astype(int)
    by_year = years.value_counts().sort_index().reset_index()
    by_year.columns = ["year", "registros"]
    by_decade = df.dropna(subset=["year"]).copy()
    by_decade["decada"] = (by_decade["year"] // 10 * 10).astype(int).astype(str) + "s"
    by_decade = by_decade["decada"].value_counts().sort_index().reset_index()
    by_decade.columns = ["decada", "registros"]
    full_range = set(range(int(years.min()), int(years.max()) + 1)) if len(years) else set()
    gaps = sorted(full_range - set(years.unique()))
    q10 = by_year["registros"].quantile(0.10) if not by_year.empty else 0
    q90 = by_year["registros"].quantile(0.90) if not by_year.empty else 0
    sparse = by_year[by_year["registros"] <= q10].head(20)
    dense = by_year[by_year["registros"] >= q90].sort_values("registros", ascending=False).head(20)
    sufficient = bool(len(years) and years.min() <= 1957 and years.max() >= 2023 and len(gaps) == 0)
    return {"years": years, "by_year": by_year, "by_decade": by_decade, "gaps": gaps, "sparse": sparse, "dense": dense, "sufficient": sufficient}


def variable_importance(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        normalized = col.lower()
        categories = [cat for cat, keys in CATEGORY_KEYWORDS.items() if any(k in normalized for k in keys)]
        non_null = 1 - df[col].isna().mean()
        uniqueness = min(1, df[col].nunique(dropna=True) / max(len(df), 1) * 5)
        category_score = len(categories) / 3
        score = min(100, round((non_null * 45 + uniqueness * 20 + category_score * 35), 2))
        rows.append({"variable": col, "categorias_detectadas": ", ".join(categories) if categories else "general", "no_nulos_pct": round(non_null * 100, 2), "valores_unicos": int(df[col].nunique(dropna=True)), "ranking_utilidad": score})
    return pd.DataFrame(rows).sort_values("ranking_utilidad", ascending=False)


def consistency_analysis(df: pd.DataFrame) -> dict:
    country_map = {
        "usa": "United States", "us": "United States", "u.s.": "United States", "united states": "United States",
        "russia": "Russia", "russian federation": "Russia", "su": "USSR/Russia", "ussr": "USSR/Russia",
        "china": "China", "pr china": "China", "people's republic of china": "China", "uk": "United Kingdom", "united kingdom": "United Kingdom",
    }
    country_rows = []
    if "country" in df:
        values = df["country"].dropna().astype(str).str.strip()
        grouped = {}
        for value in values.unique():
            key = normalize_text(value).replace(".", "")
            canonical = country_map.get(key, value)
            grouped.setdefault(canonical, []).append(value)
        for canonical, variants in grouped.items():
            if len(set(variants)) > 1 or canonical != variants[0]:
                country_rows.append({"canonico_sugerido": canonical, "variantes": ", ".join(sorted(set(variants))[:10])})

    org_pairs = []
    org_col = "launch_provider" if "launch_provider" in df else None
    if org_col:
        orgs = df[org_col].dropna().astype(str).str.strip().value_counts().head(150).index.tolist()
        for i, a in enumerate(orgs):
            for b in orgs[i + 1:]:
                a_key, b_key = normalize_key(a), normalize_key(b)
                if not a_key or not b_key or a_key == b_key:
                    continue
                ratio = SequenceMatcher(None, a_key, b_key).ratio()
                if ratio >= 0.86 or a_key in b_key or b_key in a_key:
                    org_pairs.append({"organizacion_1": a, "organizacion_2": b, "similitud": round(ratio, 3), "recomendacion": "Revisar posible duplicado o alias."})
    category_rows = []
    for col in ["organization_type", "orbit_group", "purpose_group", "mass_group", "mission_status"]:
        if col in df:
            raw_unique = df[col].dropna().astype(str).nunique()
            norm_unique = df[col].dropna().astype(str).map(normalize_text).nunique()
            if raw_unique != norm_unique:
                category_rows.append({"columna": col, "unicos_originales": raw_unique, "unicos_normalizados": norm_unique, "recomendacion": "Normalizar mayusculas, espacios y signos."})

    return {
        "countries": pd.DataFrame(country_rows),
        "organizations": pd.DataFrame(org_pairs).sort_values("similitud", ascending=False).head(30) if org_pairs else pd.DataFrame(columns=["organizacion_1", "organizacion_2", "similitud", "recomendacion"]),
        "categories": pd.DataFrame(category_rows),
    }


def capability_for_questions(df: pd.DataFrame, temporal: dict) -> pd.DataFrame:
    def col_quality(cols):
        available = [c for c in cols if c in df]
        if not available:
            return 0
        ratios = []
        for col in available:
            series = df[col]
            if series.dtype == "object":
                normalized = series.astype(str).str.strip().str.lower()
                valid = series.notna() & ~normalized.isin(["unknown", "no ucs match", "nan", "none", ""])
                ratios.append(valid.mean())
            else:
                ratios.append(series.notna().mean())
        return round(np.mean(ratios) * 100, 2)

    rows = [
        {"pregunta": "1. Evolucion de lanzamientos", "columnas_necesarias": "year, preferred_for_launch_count", "calidad_columnas_pct": col_quality(["year", "preferred_for_launch_count"]), "cobertura_temporal": f"{int(temporal['years'].min())}-{int(temporal['years'].max())}" if len(temporal["years"]) else "No disponible", "nivel_confianza": "Alta", "graficos": "linea temporal; area acumulada; barras por decada"},
        {"pregunta": "2. Liderazgo de actores", "columnas_necesarias": "year, country, launch_provider", "calidad_columnas_pct": col_quality(["year", "country", "launch_provider"]), "cobertura_temporal": "Paises y organizaciones disponibles", "nivel_confianza": "Alta", "graficos": "stacked area; streamgraph; ranking temporal; bump chart"},
        {"pregunta": "3. Publico vs privado", "columnas_necesarias": "year, organization_type", "calidad_columnas_pct": col_quality(["year", "organization_type"]), "cobertura_temporal": "Clasificacion inferida; revisar unknown", "nivel_confianza": "Media", "graficos": "area apilada; barras temporales; Sankey"},
        {"pregunta": "4. Tasa de exito", "columnas_necesarias": "year, mission_success_binary", "calidad_columnas_pct": col_quality(["year", "mission_success_binary"]), "cobertura_temporal": "Buena para mision_status normalizado", "nivel_confianza": "Alta" if df.get("mission_success_binary", pd.Series(dtype=float)).notna().mean() > 0.7 else "Media", "graficos": "linea temporal; heatmap"},
        {"pregunta": "5. Tendencias actuales", "columnas_necesarias": "satellite_purpose, orbit_group, mass_group, satellite_operator", "calidad_columnas_pct": col_quality(["satellite_purpose", "orbit_group", "mass_group", "satellite_operator"]), "cobertura_temporal": "Depende del enriquecimiento UCS", "nivel_confianza": "Media-Baja", "graficos": "treemap; sunburst; network; bubble chart"},
    ]
    return pd.DataFrame(rows)


def build_figures(df: pd.DataFrame, temporal: dict) -> dict:
    figs = {}
    launch_df = df[df.get("preferred_for_launch_count", False).fillna(False)] if "preferred_for_launch_count" in df else df
    if launch_df.empty:
        launch_df = df
    if not temporal["by_year"].empty:
        figs["yearly"] = px.line(temporal["by_year"], x="year", y="registros", markers=True, title="Registros por anio")
    if not temporal["by_decade"].empty:
        figs["decade"] = px.bar(temporal["by_decade"], x="decada", y="registros", title="Registros por decada")
    if "country" in launch_df:
        country = launch_df["country"].fillna("Desconocido").astype(str).value_counts().head(20).reset_index()
        country.columns = ["country", "registros"]
        figs["country"] = px.bar(country, x="country", y="registros", title="Top paises")
    if "launch_provider" in launch_df:
        org = launch_df["launch_provider"].fillna("Desconocido").astype(str).value_counts().head(20).reset_index()
        org.columns = ["launch_provider", "registros"]
        figs["org"] = px.bar(org, x="launch_provider", y="registros", title="Top organizaciones")
    if {"year", "organization_type"}.issubset(df.columns):
        pubpriv = df.dropna(subset=["year"]).groupby(["year", "organization_type"]).size().reset_index(name="registros")
        figs["pubpriv"] = px.area(pubpriv, x="year", y="registros", color="organization_type", title="Evolucion publico vs privado")
    if {"year", "mission_success_binary"}.issubset(df.columns):
        success = df.dropna(subset=["year", "mission_success_binary"]).groupby("year")["mission_success_binary"].mean().reset_index(name="tasa_exito")
        figs["success"] = px.line(success, x="year", y="tasa_exito", markers=True, title="Tasa de exito anual")
    if "orbit_group" in df:
        orbit_values = df["orbit_group"].dropna().astype(str)
        orbit_values = orbit_values[~orbit_values.str.lower().isin(["unknown", "no ucs match"])]
        orbit = orbit_values.value_counts().head(15).reset_index()
        orbit.columns = ["orbit_group", "registros"]
        if not orbit.empty:
            figs["orbit"] = px.bar(orbit, x="orbit_group", y="registros", title="Distribucion de orbitas en registros enriquecidos")
    if "purpose_group" in df:
        purpose_values = df["purpose_group"].dropna().astype(str)
        purpose_values = purpose_values[~purpose_values.str.lower().isin(["unknown", "no ucs match"])]
        purpose = purpose_values.value_counts().head(15).reset_index()
        purpose.columns = ["purpose_group", "registros"]
        if not purpose.empty:
            figs["purpose"] = px.treemap(purpose, path=["purpose_group"], values="registros", title="Distribucion de propositos en registros enriquecidos")
    mass_col = "satellite_mass_kg" if "satellite_mass_kg" in df.columns else "satellite_mass" if "satellite_mass" in df.columns else None
    if mass_col and {"year", mass_col}.issubset(df.columns):
        mass = df.copy()
        mass[mass_col] = pd.to_numeric(mass[mass_col], errors="coerce")
        mass = mass.dropna(subset=["year", mass_col]).groupby("year")[mass_col].median().reset_index()
        if not mass.empty:
            figs["mass"] = px.line(mass, x="year", y=mass_col, markers=True, title="Mediana anual de masa satelital")
    if {"orbit_group", "purpose_group"}.issubset(df.columns):
        trend = df.fillna({"orbit_group": "unknown", "purpose_group": "unknown"}).copy()
        trend = trend[~trend["orbit_group"].astype(str).str.lower().isin(["unknown", "no ucs match"])]
        trend = trend[~trend["purpose_group"].astype(str).str.lower().isin(["unknown", "no ucs match"])]
        trend = trend.groupby(["orbit_group", "purpose_group"]).size().reset_index(name="registros")
        trend = trend.sort_values("registros", ascending=False).head(40)
        if not trend.empty:
            figs["sunburst"] = px.sunburst(trend, path=["orbit_group", "purpose_group"], values="registros", title="Orbita y proposito en registros enriquecidos")
    return figs


def make_metric_cards(metrics: list[tuple[str, str, str]]) -> str:
    return "<div class='metric-grid'>" + "".join(f"<div class='metric-card'><div class='metric-label'>{esc(label)}</div><div class='metric-value'>{esc(value)}</div><div class='metric-note'>{esc(note)}</div></div>" for label, value, note in metrics) + "</div>"


def unordered(items: list[str]) -> str:
    if not items:
        return "<p>No se detectaron elementos relevantes.</p>"
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def build_report(df: pd.DataFrame) -> tuple[str, str]:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    original_df = df.drop(columns=["source_inferred"], errors="ignore")
    dictionary = variable_dictionary(original_df)
    quality = quality_analysis(original_df)
    rel = relationships(original_df)
    temporal = temporal_analysis(df)
    importance = variable_importance(original_df)
    consistency = consistency_analysis(original_df)
    questions = capability_for_questions(df, temporal)
    figs = build_figures(df, temporal)

    year_min = int(temporal["years"].min()) if len(temporal["years"]) else "No disponible"
    year_max = int(temporal["years"].max()) if len(temporal["years"]) else "No disponible"
    source_counts = df["source_inferred"].value_counts().reset_index()
    source_counts.columns = ["origen_inferido", "registros"]
    source_text = ", ".join(source_counts["origen_inferido"].tolist())
    source_warning = "La columna source_dataset esta vacia o incompleta; el informe usa source_inferred para auditar origenes." if "source_dataset" in df and df["source_dataset"].isna().mean() > 0.9 else "La fuente source_dataset esta corregida e informada en el dataset definitivo v2."

    success = df["mission_success_binary"].dropna() if "mission_success_binary" in df else pd.Series(dtype=float)
    success_pct = round((success == 1).mean() * 100, 2) if len(success) else None
    failure_pct = round((success == 0).mean() * 100, 2) if len(success) else None

    figures_html = {name: fig_html(fig) for name, fig in figs.items()}
    plotly_js = get_plotlyjs()

    sections = []
    nav_items = []

    def add_section(title: str, body: str):
        section_id = slug(title)
        nav_items.append(f"<a href='#{section_id}'>{esc(title)}</a>")
        sections.append(f"<section id='{section_id}' class='report-section'><h2>{esc(title)}</h2>{body}</section>")

    summary_text = (
        f"El dataset final definitivo v2 contiene {len(original_df):,} registros y {original_df.shape[1]:,} columnas, con cobertura temporal {year_min}-{year_max}. "
        f"Integra informacion historica de lanzamientos y enriquecimiento satelital. La auditoria detecta {quality['total_null_pct']}% de nulos globales, "
        f"{quality['duplicates']} filas duplicadas y {len(rel['removable'])} columnas candidatas a revision o eliminacion. "
        "Es adecuado para estudiar la evolucion espacial desde 1957, aunque las tendencias de orbitas, propositos y masas dependen del nivel de union con UCS."
    )

    add_section("1 - Resumen ejecutivo", f"""
        {make_metric_cards([
            ("Filas", f"{len(original_df):,}", "Registros del dataset final v2"),
            ("Columnas", f"{original_df.shape[1]:,}", "Variables originales disponibles"),
            ("Memoria", f"{memory_mb(original_df):.2f} MB", "Uso en memoria"),
            ("Cobertura", f"{year_min}-{year_max}", "Rango temporal"),
            ("Nulos", f"{quality['total_null_pct']}%", "Promedio global"),
            ("Generado", generated, "Fecha del informe"),
        ])}
        <div class='callout'><strong>Resumen automatico.</strong> {esc(summary_text)}</div>
        <h3>Datasets de origen utilizados</h3>{table_html(source_counts, 'tbl_sources')}
        <div class='warning'>{esc(source_warning)}</div>
    """)

    add_section("2 - Diccionario de variables", table_html(dictionary, "tbl_dictionary"))

    quality_body = f"""
        <h3>Nulos</h3>
        {make_metric_cards([("Nulos globales", f"{quality['total_null_pct']}%", "Promedio sobre todas las celdas"), ("Columnas sin nulos", str(len(quality['no_nulls'])), "Completas"), ("Top columna con nulos", f"{quality['top_nulls'].iloc[0]['nulos_pct']:.2f}%" if not quality['top_nulls'].empty else "0%", quality['top_nulls'].iloc[0]['columna'] if not quality['top_nulls'].empty else "Sin nulos")])}
        {table_html(quality['top_nulls'], 'tbl_top_nulls')}
        <h3>Columnas sin nulos</h3>{table_html(quality['no_nulls'], 'tbl_no_nulls')}
        <h3>Duplicados</h3>{make_metric_cards([("Filas duplicadas", str(quality['duplicates']), "Duplicados exactos"), ("Duplicados %", f"{quality['duplicates_pct']}%", "Sobre el total")])}
        <h3>Cardinalidad</h3>
        <div class='grid-3'><div><h4>Constantes</h4>{unordered(quality['constant_cols'])}</div><div><h4>Muy alta</h4>{unordered(quality['high_card_cols'])}</div><div><h4>Muy baja</h4>{unordered(quality['low_card_cols'])}</div></div>
        <h3>Advertencias de tipos de datos</h3>{table_html(quality['warnings'] if not quality['warnings'].empty else pd.DataFrame([{"tipo":"sin advertencias criticas", "columna":"", "detalle":"No se detectaron problemas automaticos relevantes."}]), 'tbl_type_warnings')}
    """
    add_section("3 - Calidad de datos", quality_body)

    relation_body = f"""
        <h3>Correlaciones altas</h3>{table_html(rel['correlations'], 'tbl_correlations')}
        <h3>Columnas redundantes o practicamente iguales</h3>{table_html(rel['redundant'], 'tbl_redundant')}
        <h3>Claves primarias o candidatas</h3>{table_html(rel['keys'], 'tbl_keys')}
        <div class='callout'><strong>Columnas que podrian eliminarse o revisarse:</strong> {esc(', '.join(rel['removable']) if rel['removable'] else 'No hay candidatas claras por redundancia exacta o nulos extremos.')}</div>
        <p>Las columnas que contienen informacion practicamente igual aparecen en la tabla de redundancia. Deben revisarse antes de eliminarse, especialmente si proceden de fuentes distintas.</p>
    """
    add_section("4 - Relaciones entre columnas", relation_body)

    temporal_body = f"""
        {make_metric_cards([("Anio minimo", str(year_min), "Primer registro temporal"), ("Anio maximo", str(year_max), "Ultimo registro temporal"), ("Huecos temporales", str(len(temporal['gaps'])), "Anios sin registros en el rango")])}
        {figures_html.get('yearly', '')}
        {figures_html.get('decade', '')}
        <h3>Huecos temporales</h3><p>{esc(', '.join(map(str, temporal['gaps'])) if temporal['gaps'] else 'No se detectan huecos dentro del rango temporal.')}</p>
        <h3>Periodos con pocos datos</h3>{table_html(temporal['sparse'], 'tbl_sparse_years')}
        <h3>Periodos con muchos datos</h3>{table_html(temporal['dense'], 'tbl_dense_years')}
        <div class='callout'><strong>Evaluacion:</strong> {'La cobertura temporal es suficiente para estudiar la evolucion espacial desde 1957.' if temporal['sufficient'] else 'La cobertura temporal es util, pero presenta limitaciones que deben comentarse.'}</div>
    """
    add_section("5 - Cobertura temporal", temporal_body)

    add_section("6 - Variables mas importantes", f"""
        <p>Ranking calculado por completitud, unicidad util y relacion semantica con lanzamientos, paises, organizaciones, satelites, misiones, orbitas, masa, proposito y exito/fallo.</p>
        {table_html(importance, 'tbl_importance')}
    """)

    consistency_body = f"""
        <h3>Paises escritos de varias formas</h3>{table_html(consistency['countries'] if not consistency['countries'].empty else pd.DataFrame([{"canonico_sugerido":"Sin problemas claros", "variantes":"No se detectaron variantes automaticas relevantes."}]), 'tbl_country_consistency')}
        <h3>Organizaciones duplicadas o nombres similares</h3>{table_html(consistency['organizations'], 'tbl_org_consistency')}
        <h3>Categorias inconsistentes</h3>{table_html(consistency['categories'] if not consistency['categories'].empty else pd.DataFrame([{"columna":"Sin problemas claros", "unicos_originales":"", "unicos_normalizados":"", "recomendacion":"No se detectaron inconsistencias automaticas relevantes."}]), 'tbl_category_consistency')}
        <div class='callout'><strong>Recomendacion:</strong> crear tablas de equivalencias para paises y organizaciones antes de la visualizacion final, especialmente para USA/United States y nombres comerciales como SpaceX/Space Exploration Technologies.</div>
    """
    add_section("7 - Analisis de consistencia", consistency_body)

    q_body = f"""
        {table_html(questions, 'tbl_questions')}
        <h3>Pregunta 1 - Evolucion de lanzamientos</h3><p>Columnas: <code>year</code>, <code>preferred_for_launch_count</code>. Confianza alta por cobertura {year_min}-{year_max}.</p>{figures_html.get('yearly', '')}
        <h3>Pregunta 2 - Liderazgo de actores</h3><p>Columnas: <code>country</code>, <code>launch_provider</code>, <code>year</code>. Hay paises y organizaciones disponibles para rankings temporales.</p>{figures_html.get('country', '')}{figures_html.get('org', '')}
        <h3>Pregunta 3 - Publico vs privado</h3><p>Existe <code>organization_type</code>, pero es heuristica. Conviene revisar valores <code>unknown</code>.</p>{figures_html.get('pubpriv', '')}
        <h3>Pregunta 4 - Tasa de exito</h3><p>Columna: <code>mission_success_binary</code>. Exito: {esc(success_pct)}%. Fallo: {esc(failure_pct)}% sobre valores conocidos.</p>{figures_html.get('success', '')}
        <h3>Pregunta 5 - Tendencias actuales</h3><p>Variables: <code>satellite_purpose</code>, <code>orbit_group</code>, <code>mass_group</code>, <code>satellite_mass_kg</code>, <code>satellite_operator</code>. La confianza depende del match con UCS.</p>{figures_html.get('orbit', '')}{figures_html.get('purpose', '')}{figures_html.get('mass', '')}{figures_html.get('sunburst', '')}
    """
    add_section("8 - Analisis especifico para preguntas de investigacion", q_body)

    additional = pd.DataFrame([
        {"pregunta_adicional": "Como evoluciona la concentracion de lanzamientos por operador?", "variables": "year, launch_provider", "valor": "Mide liderazgo y dependencia de pocos actores."},
        {"pregunta_adicional": "Que peso tiene SpaceX en la nueva carrera espacial?", "variables": "year, launch_provider, organization_type", "valor": "Tiene alto potencial narrativo desde 2010."},
        {"pregunta_adicional": "Como cambia el protagonismo de China?", "variables": "year, country, launch_provider", "valor": "Permite contrastar liderazgo geopolitico."},
        {"pregunta_adicional": "Que orbitas y propositos dominan la actividad reciente?", "variables": "year, orbit_group, purpose_group", "valor": "Conecta actividad espacial con uso tecnologico."},
        {"pregunta_adicional": "Ha cambiado la masa tipica de los satelites?", "variables": "year, satellite_mass_kg, mass_group", "valor": "Aporta lectura sobre miniaturizacion y constelaciones."},
    ])
    add_section("9 - Preguntas adicionales interesantes", table_html(additional, "tbl_additional"))

    derived = pd.DataFrame([
        {"variable": "decade", "estado": "ya existe", "utilidad": "Comparar cambios por periodos largos."},
        {"variable": "space_era", "estado": "ya existe", "utilidad": "Clasificar Early Space Age, Space Race, Post Cold War y Commercial Space Age."},
        {"variable": "launch_frequency_period", "estado": "ya existe", "utilidad": "Segmentar etapas de frecuencia de lanzamientos para narrativa historica."},
        {"variable": "actor_public_private", "estado": "ya existe como organization_type", "utilidad": "Responder equilibrio publico/privado."},
        {"variable": "orbit_group", "estado": "ya existe", "utilidad": "Simplificar categorias orbitales."},
        {"variable": "mass_group", "estado": "ya existe", "utilidad": "Comparar masas sin ruido de valores extremos."},
    ])
    add_section("10 - Variables derivadas recomendadas", table_html(derived, "tbl_derived"))

    viz = pd.DataFrame([
        {"Pregunta": "Evolucion de lanzamientos", "Variables": "year, conteo", "Tipo grafico": "Linea temporal", "Justificacion": "Muestra tendencia continua", "Mejor": "Si"},
        {"Pregunta": "Evolucion de lanzamientos", "Variables": "decade, conteo", "Tipo grafico": "Barras por decada", "Justificacion": "Resume periodos historicos", "Mejor": "Alternativa"},
        {"Pregunta": "Liderazgo de actores", "Variables": "year, country", "Tipo grafico": "Stacked area", "Justificacion": "Compara participacion por actor", "Mejor": "Si"},
        {"Pregunta": "Liderazgo de actores", "Variables": "year, launch_provider", "Tipo grafico": "Bump chart", "Justificacion": "Ranking temporal narrativo", "Mejor": "Alternativa"},
        {"Pregunta": "Publico vs privado", "Variables": "year, organization_type", "Tipo grafico": "Area apilada", "Justificacion": "Evidencia cambio de equilibrio", "Mejor": "Si"},
        {"Pregunta": "Tasa de exito", "Variables": "year, mission_success_binary", "Tipo grafico": "Linea + media movil", "Justificacion": "Muestra mejora o deterioro", "Mejor": "Si"},
        {"Pregunta": "Tendencias actuales", "Variables": "orbit_group, purpose_group", "Tipo grafico": "Sunburst", "Justificacion": "Relacion jerarquica orbita-proposito", "Mejor": "Si"},
        {"Pregunta": "Tendencias actuales", "Variables": "satellite_mass_kg, year, purpose_group", "Tipo grafico": "Bubble chart", "Justificacion": "Cruza masa, tiempo y uso", "Mejor": "Alternativa"},
    ])
    add_section("11 - Seleccion de visualizaciones finales", table_html(viz, "tbl_visualizations"))

    risks = []
    if quality["total_null_pct"] > 25:
        risks.append("El porcentaje global de nulos es alto por columnas procedentes de UCS que no tienen match para todos los lanzamientos.")
    if "source_dataset" in df and df["source_dataset"].isna().mean() > 0.9:
        risks.append("La fuente original no esta informada en source_dataset; se recomienda regenerar el dataset corrigiendo esa columna.")
    if "organization_type" in df and (df["organization_type"].astype(str).str.lower() == "unknown").mean() > 0.3:
        risks.append("La clasificacion publico/privado contiene muchos valores unknown, lo que reduce confianza de la pregunta 3.")
    mass_risk_col = "satellite_mass_kg" if "satellite_mass_kg" in df.columns else "satellite_mass" if "satellite_mass" in df.columns else None
    if mass_risk_col and df[mass_risk_col].isna().mean() > 0.5:
        risks.append("La masa satelital esta muy incompleta; usarla solo para tendencias parciales o subconjuntos enriquecidos.")
    risks.append("GCAT y Space_Missions pueden solaparse; para conteos usar preferred_for_launch_count para evitar doble conteo.")
    risks.append("Los registros de 2026 pueden estar incompletos porque el anio esta en curso o depende de actualizaciones de GCAT.")
    add_section("12 - Riesgos y limitaciones", unordered(risks))

    conclusion = pd.DataFrame([
        {"pregunta": "Es adecuado este dataset para la PEC?", "respuesta": "Si", "detalle": "Tiene cobertura 1957-2026 y variables clave para evolucion, actores y exito."},
        {"pregunta": "Puede responder las 5 preguntas?", "respuesta": "Si, con matices", "detalle": "Responde muy bien lanzamientos, actores y exito; tendencias actuales dependen del enriquecimiento UCS."},
        {"pregunta": "Que preguntas responde mejor?", "respuesta": "1, 2 y 4", "detalle": "Son las que tienen mayor cobertura temporal y menor dependencia de campos incompletos."},
        {"pregunta": "Visualizaciones con mas potencial narrativo", "respuesta": "Linea temporal, stacked area, area publico/privado y sunburst", "detalle": "Combinan evolucion historica y cambio de actores."},
        {"pregunta": "Que mejorar antes de la entrega?", "respuesta": "Validacion interpretativa", "detalle": "Revisar manualmente organization_type en actores ambiguos y usar tablas de normalizacion para visualizaciones finales."},
    ])
    add_section("13 - Conclusion final", table_html(conclusion, "tbl_conclusion"))

    css = """
    :root{--bg:#f5f7fb;--panel:#ffffff;--ink:#1f2937;--muted:#6b7280;--brand:#244c9a;--brand2:#12a3b8;--line:#e5e7eb;--warn:#fff7ed;--warnline:#fdba74}
    *{box-sizing:border-box} body{margin:0;font-family:Inter,Segoe UI,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.55}
    .layout{display:flex}.sidebar{position:fixed;inset:0 auto 0 0;width:280px;background:#0f172a;color:white;padding:24px 18px;overflow:auto}.sidebar h1{font-size:19px;margin:0 0 8px}.sidebar .subtitle{color:#cbd5e1;font-size:13px;margin-bottom:22px}.sidebar a{display:block;color:#e5e7eb;text-decoration:none;padding:9px 10px;border-radius:9px;font-size:14px}.sidebar a:hover{background:#1e293b;color:white}
    main{margin-left:280px;width:calc(100% - 280px);padding:28px}.hero{background:linear-gradient(135deg,#14336d,#12a3b8);color:white;border-radius:22px;padding:30px;margin-bottom:22px;box-shadow:0 12px 35px rgba(15,23,42,.18)}.hero h1{margin:0;font-size:30px}.hero p{max-width:980px;color:#e0f2fe}
    .report-section{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:24px;margin-bottom:22px;box-shadow:0 8px 24px rgba(15,23,42,.05)}h2{margin:0 0 18px;font-size:24px;color:#102a5c}h3{margin-top:24px;color:#17417f}h4{margin-bottom:8px}.metric-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin:16px 0}.metric-card{border:1px solid var(--line);border-radius:16px;padding:16px;background:linear-gradient(180deg,#fff,#f8fafc)}.metric-label{font-size:12px;text-transform:uppercase;color:var(--muted);letter-spacing:.04em}.metric-value{font-size:24px;font-weight:800;color:var(--brand);margin:5px 0}.metric-note{font-size:12px;color:var(--muted)}
    .callout{border-left:5px solid var(--brand2);background:#ecfeff;padding:14px 16px;border-radius:12px;margin:16px 0}.warning{border-left:5px solid var(--warnline);background:var(--warn);padding:14px 16px;border-radius:12px;margin:16px 0}.grid-3{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}.table-toolbar{display:flex;justify-content:flex-end;margin:10px 0}.datatable-search{max-width:340px;width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:10px}.table-responsive{overflow:auto;border:1px solid var(--line);border-radius:14px}table{border-collapse:collapse;width:100%;background:white;font-size:13px}th,td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}th{position:sticky;top:0;background:#eef2ff;color:#0f172a;cursor:pointer;white-space:nowrap}tr:nth-child(even){background:#f8fafc}.plotly-graph-div{width:100%!important}.footer{color:var(--muted);text-align:center;margin:24px 0}
    @media(max-width:900px){.sidebar{position:relative;width:100%;height:auto}.layout{display:block}main{margin-left:0;width:100%;padding:14px}.hero h1{font-size:24px}}
    """

    js = """
    function enhanceTables(){
      document.querySelectorAll('table.datatable').forEach(table=>{
        table.querySelectorAll('th').forEach((th,idx)=>{th.addEventListener('click',()=>sortTable(table,idx));});
      });
      document.querySelectorAll('.datatable-search').forEach(input=>{
        input.addEventListener('input',()=>{
          const table=document.getElementById(input.dataset.table); const q=input.value.toLowerCase();
          table.querySelectorAll('tbody tr').forEach(tr=>{tr.style.display=tr.innerText.toLowerCase().includes(q)?'':'none';});
        });
      });
    }
    function sortTable(table, col){
      const tbody=table.tBodies[0]; const rows=Array.from(tbody.rows); const asc=table.dataset.sortCol!=col || table.dataset.sortAsc!='true';
      rows.sort((a,b)=>{let av=a.cells[col].innerText.trim(), bv=b.cells[col].innerText.trim(); let an=parseFloat(av.replace(',','.')), bn=parseFloat(bv.replace(',','.')); if(!isNaN(an)&&!isNaN(bn)){return asc?an-bn:bn-an;} return asc?av.localeCompare(bv):bv.localeCompare(av);});
      rows.forEach(r=>tbody.appendChild(r)); table.dataset.sortCol=col; table.dataset.sortAsc=asc;
    }
    document.addEventListener('DOMContentLoaded', enhanceTables);
    """

    html_doc = f"""<!doctype html>
    <html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Analisis del Dataset Final Espacial v2</title><style>{css}</style><script>{plotly_js}</script></head>
    <body><div class="layout"><nav class="sidebar"><h1>Auditoria Dataset Final</h1><div class="subtitle">Parte II - Actividad espacial</div>{''.join(nav_items)}</nav>
    <main><div class="hero"><h1>Analisis exhaustivo del dataset final v2</h1><p>Informe interactivo de calidad, exploracion, viabilidad analitica, preguntas de investigacion y propuestas de visualizacion. Generado el {esc(generated)}.</p></div>
    {''.join(sections)}<div class="footer">Informe local autonomo generado con Python, Plotly y tablas interactivas estilo DataTables.</div></main></div><script>{js}</script></body></html>"""

    md_summary = f"""# Analisis del dataset final v2

Generado: {generated}

## Resumen ejecutivo

- Filas: {len(original_df):,}
- Columnas: {original_df.shape[1]:,}
- Memoria: {memory_mb(original_df):.2f} MB
- Cobertura temporal: {year_min}-{year_max}
- Origenes auditados: {source_text}
- Nulos globales: {quality['total_null_pct']}%
- Duplicados exactos: {quality['duplicates']} ({quality['duplicates_pct']}%)

## Conclusion

El dataset es adecuado para la PEC y permite responder las cinco preguntas, con mayor confianza en evolucion de lanzamientos, liderazgo de actores y tasa de exito. Las tendencias actuales basadas en orbitas, propositos y masa tienen menor confianza por la incompletitud del enriquecimiento UCS.

## Riesgos principales

{chr(10).join('- ' + item for item in risks)}

## Visualizaciones recomendadas

- Linea temporal de lanzamientos por anio.
- Area apilada por pais o actor.
- Area apilada publico/privado.
- Linea temporal de tasa de exito.
- Sunburst de orbita y proposito.
- Bubble chart de masa, tiempo y proposito.

## Mejoras antes de entrega

- Mantener las tablas de normalizacion de paises y organizaciones junto al dataset final.
- Validar manualmente la clasificacion `organization_type` en actores ambiguos.
- Usar `preferred_for_launch_count == True` para evitar doble conteo historico.
"""

    return html_doc, md_summary


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    df = prepare_dataset(load_dataset())
    html_doc, md_summary = build_report(df)
    HTML_OUT.write_text(html_doc, encoding="utf-8")
    MD_OUT.write_text(md_summary, encoding="utf-8")
    print(f"HTML generado: {HTML_OUT}")
    print(f"Markdown generado: {MD_OUT}")


if __name__ == "__main__":
    main()
