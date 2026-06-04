from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ORIGINAL = ROOT / "01_datos" / "originales"
DATA_FINAL = ROOT / "01_datos" / "final"
REPORTS_FINAL = ROOT / "04_informes" / "final"
NOTEBOOK_DIR = ROOT / "02_notebooks"

SPACE_PATH = DATA_ORIGINAL / "Space_Missions_Cleaned.csv"
GCAT_PATH = DATA_ORIGINAL / "launchlog.tsv"
UCS_PATH = DATA_ORIGINAL / "UCS-Satellite-Database 5-1-2023.xlsx"
AUDIT_HTML = REPORTS_FINAL / "analisis_dataset_final.html"
AUDIT_MD = REPORTS_FINAL / "analisis_dataset_final.md"

CSV_OUT = DATA_FINAL / "datos_finales_espacio_v2.csv"
PARQUET_OUT = DATA_FINAL / "datos_finales_espacio_v2.parquet"
DECISIONS_OUT = REPORTS_FINAL / "decisiones_dataset_final.md"
NOTEBOOK_OUT = NOTEBOOK_DIR / "construccion_dataset_final.ipynb"


QUESTION_COLUMNS = {
    "Evolucion de lanzamientos": ["year", "decade", "space_era", "preferred_for_launch_count"],
    "Liderazgo de actores": ["year", "country", "launch_provider", "satellite_operator_country"],
    "Publico vs privado": ["year", "organization_type", "launch_provider", "satellite_operator"],
    "Tasa de exito": ["year", "mission_success_binary", "mission_status"],
    "Tendencias actuales": ["year", "orbit_group", "purpose_group", "mass_group", "satellite_mass_kg"],
}

PROVISIONAL_METRICS_FROM_AUDIT = {
    "Evolucion de lanzamientos": 1.00,
    "Liderazgo de actores": 1.00,
    "Publico vs privado": 0.4594,
    "Tasa de exito": 0.9332,
    "Tendencias actuales": 0.0229,
}

HIGH_VALUE_COLUMNS = {
    "source_dataset", "record_level", "launch_id", "launch_date", "year", "decade", "space_era",
    "launch_frequency_period", "mission_name", "satellite_name", "launch_provider", "country",
    "launch_site", "launch_vehicle", "mission_status", "mission_success_binary", "payload_count",
    "preferred_for_launch_count", "ucs_match_found", "satellite_operator", "satellite_operator_country",
    "satellite_users", "satellite_purpose", "purpose_group", "orbit_type", "orbit_group",
    "satellite_mass_kg", "mass_group", "organization_type",
}

OPTIONAL_HIGH_NULL_BUT_USEFUL = {
    "satellite_operator", "satellite_operator_country", "satellite_users", "satellite_purpose",
    "satellite_detailed_purpose", "orbit_type", "orbit_subtype", "satellite_mass_kg",
    "ucs_launch_vehicle", "ucs_launch_site", "cospar_number", "norad_number",
}

CATEGORICAL_UNKNOWN_COLUMNS = [
    "record_level", "mission_name", "satellite_name", "launch_provider", "country", "launch_site",
    "launch_vehicle", "mission_status", "rocket_status", "satellite_operator",
    "satellite_operator_country", "satellite_users", "satellite_purpose", "satellite_detailed_purpose",
    "orbit_type", "orbit_subtype", "ucs_launch_vehicle", "ucs_launch_site", "cospar_number",
    "norad_number", "organization_type", "purpose_group", "orbit_group", "mass_group",
    "launch_frequency_period", "space_era", "decade",
]

COUNTRY_ALIASES = {
    "": "Unknown", "nan": "Unknown", "none": "Unknown", "unknown": "Unknown", "unks": "Unknown",
    "us": "United States", "usa": "United States", "u.s.": "United States", "u.s.a.": "United States",
    "united states": "United States", "united states of america": "United States", "united states of america (usa)": "United States",
    "su": "USSR/Russia", "ussr": "USSR/Russia", "soviet union": "USSR/Russia",
    "ru": "Russia", "russia": "Russia", "russian federation": "Russia",
    "cn": "China", "china": "China", "pr china": "China", "people's republic of china": "China", "peoples republic of china": "China",
    "uk": "United Kingdom", "gb": "United Kingdom", "united kingdom": "United Kingdom",
    "j": "Japan", "jp": "Japan", "japan": "Japan",
    "in": "India", "india": "India",
    "f": "France", "fr": "France", "france": "France",
    "d": "Germany", "de": "Germany", "germany": "Germany",
    "i": "Italy", "it": "Italy", "italy": "Italy",
    "e": "Spain", "es": "Spain", "spain": "Spain",
    "ca": "Canada", "canada": "Canada",
    "kr": "South Korea", "south korea": "South Korea", "republic of korea": "South Korea",
    "kp": "North Korea", "north korea": "North Korea",
    "ir": "Iran", "iran": "Iran",
    "il": "Israel", "israel": "Israel",
    "br": "Brazil", "brazil": "Brazil",
    "ua": "Ukraine", "ukraine": "Ukraine",
    "au": "Australia", "australia": "Australia",
    "nz": "New Zealand", "new zealand": "New Zealand",
    "eu": "Europe/ESA", "esa": "Europe/ESA", "i-esa": "Europe/ESA", "i-eu": "Europe/ESA", "eumetsat": "Europe/ESA",
    "uae": "United Arab Emirates", "united arab emirates": "United Arab Emirates",
}

ORG_ALIASES = {
    "spx": "SpaceX", "spacex": "SpaceX", "space exploration technologies": "SpaceX",
    "nasa": "NASA", "jsc/msfc": "NASA", "gsfc": "NASA",
    "rvsn": "Soviet/Russian Strategic Rocket Forces", "rvsnr": "Soviet/Russian Strategic Rocket Forces",
    "fka": "Roscosmos", "roscosmos": "Roscosmos", "russian space forces": "Russian Space Forces", "vksr": "Russian Space Forces",
    "casc": "CASC", "calt": "CASC", "sast": "CASC", "cgwic/sast": "CASC",
    "isro": "ISRO", "jaxa": "JAXA", "esa": "ESA", "cnsa": "CNSA",
    "ulal": "United Launch Alliance", "ula": "United Launch Alliance", "united launch alliance": "United Launch Alliance",
    "ae": "Arianespace", "arianespace": "Arianespace",
    "rlabn": "Rocket Lab", "rocket lab": "Rocket Lab",
    "blue origin": "Blue Origin", "ngis": "Northrop Grumman", "northrop grumman": "Northrop Grumman",
    "osc": "Orbital Sciences", "orbital sciences": "Orbital Sciences", "mhi": "Mitsubishi Heavy Industries",
    "boeing": "Boeing", "lockheed martin": "Lockheed Martin", "virgin orbit": "Virgin Orbit",
    "planet labs": "Planet Labs", "oneweb": "OneWeb", "intelsat": "Intelsat", "ses": "SES", "eutelsat": "Eutelsat",
}

PUBLIC_KEYWORDS = [
    "nasa", "roscosmos", "esa", "isro", "jaxa", "cnsa", "casc", "calt", "sast", "rvsn", "russian",
    "soviet", "air force", "space force", "military", "government", "usaf", "afssd", "samso", "gsfc",
    "jsc", "msfc", "kari", "dlr", "cnes", "strategic rocket forces",
]

PRIVATE_KEYWORDS = [
    "spacex", "rocket lab", "blue origin", "arianespace", "united launch alliance", "ula", "boeing",
    "lockheed", "northrop", "orbital sciences", "mhi", "virgin", "planet", "oneweb", "intelsat",
    "ses", "eutelsat", "iridium", "maxar", "firefly", "relativity", "astra", "ispace",
]


def clean_text(value: Any) -> str | None:
    if pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).strip())
    return text if text and text.lower() not in {"nan", "none"} else None


def normalize_lookup(value: Any) -> str:
    text = clean_text(value)
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.lower().replace(".", "").replace(",", "")).strip()


def normalize_name_key(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    key = re.sub(r"[^a-z0-9]+", "", text.lower())
    return key or None


def concat_unique(series: pd.Series) -> str | None:
    values = [clean_text(v) for v in series]
    unique = []
    seen = set()
    for value in values:
        if not value:
            continue
        key = value.lower()
        if key not in seen:
            seen.add(key)
            unique.append(value)
    return "; ".join(unique) if unique else None


def mode_value(series: pd.Series) -> Any:
    values = series.dropna()
    if values.empty:
        return None
    mode = values.mode(dropna=True)
    return mode.iloc[0] if not mode.empty else values.iloc[0]


def normalize_country(value: Any) -> str:
    key = normalize_lookup(value)
    if key in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[key]
    if "united states" in key:
        return "United States"
    if "russia" in key:
        return "Russia"
    if "china" in key:
        return "China"
    if "european space agency" in key:
        return "Europe/ESA"
    text = clean_text(value)
    return text if text else "Unknown"


def normalize_organization(value: Any) -> str:
    key = normalize_lookup(value)
    if key in ORG_ALIASES:
        return ORG_ALIASES[key]
    for alias, canonical in ORG_ALIASES.items():
        if alias and alias in key:
            return canonical
    text = clean_text(value)
    return text if text else "Unknown"


def classify_organization(provider: Any, operator: Any = None) -> str:
    values = " ".join(clean_text(v) or "" for v in [provider, operator]).lower()
    if not values.strip() or values.strip() == "unknown":
        return "Unknown"
    public = any(token in values for token in PUBLIC_KEYWORDS)
    private = any(token in values for token in PRIVATE_KEYWORDS)
    if public and private:
        return "Mixed"
    if private:
        return "Private"
    if public:
        return "Public"
    return "Unknown"


def parse_space_payload(detail: Any) -> str | None:
    text = clean_text(detail)
    if not text:
        return None
    return text.split("|", 1)[1].strip() if "|" in text else text


def parse_space_vehicle(detail: Any) -> str | None:
    text = clean_text(detail)
    if not text:
        return None
    return text.split("|", 1)[0].strip() if "|" in text else None


def mission_success(value: Any) -> float:
    text = normalize_lookup(value)
    if text in {"success", "os", "s"} or text.startswith("os"):
        return 1.0
    if "partial" in text:
        return 0.0
    if text in {"failure", "fail", "of", "prelaunch failure"} or text.startswith("of"):
        return 0.0
    return np.nan


def classify_orbit(value: Any) -> str:
    text = normalize_lookup(value).upper()
    if not text:
        return "Unknown"
    if "GEO" in text or "GEOSTATIONARY" in text:
        return "GEO"
    if "LEO" in text or "LOW" in text:
        return "LEO"
    if "MEO" in text or "MEDIUM" in text:
        return "MEO"
    if "HEO" in text or "ELLIP" in text:
        return "HEO"
    return clean_text(value) or "Unknown"


def classify_purpose(value: Any) -> str:
    text = normalize_lookup(value)
    groups = {
        "Communications": ["communication", "telecom", "broadcast", "internet"],
        "Earth Observation": ["earth", "observation", "remote", "imaging", "meteorology", "weather"],
        "Navigation": ["navigation", "gps", "glonass", "galileo", "beidou", "position"],
        "Science": ["science", "astronomy", "research", "space science"],
        "Military": ["military", "defense", "reconnaissance"],
        "Technology": ["technology", "demonstration", "development", "test"],
        "Human Spaceflight": ["crew", "human", "space station"],
    }
    if not text:
        return "Unknown"
    for group, tokens in groups.items():
        if any(token in text for token in tokens):
            return group
    return "Other"


def mass_group(value: Any) -> str:
    mass = pd.to_numeric(value, errors="coerce")
    if pd.isna(mass):
        return "Unknown"
    if mass < 10:
        return "<10 kg"
    if mass < 100:
        return "10-99 kg"
    if mass < 500:
        return "100-499 kg"
    if mass < 1000:
        return "500-999 kg"
    if mass < 5000:
        return "1000-4999 kg"
    return ">=5000 kg"


def space_era(year: Any) -> str:
    y = pd.to_numeric(year, errors="coerce")
    if pd.isna(y):
        return "Unknown"
    if y <= 1960:
        return "Early Space Age"
    if y <= 1991:
        return "Space Race"
    if y <= 2009:
        return "Post Cold War"
    return "Commercial Space Age"


def launch_frequency_period(year: Any) -> str:
    y = pd.to_numeric(year, errors="coerce")
    if pd.isna(y):
        return "Unknown"
    if y < 1970:
        return "Foundation"
    if y < 1992:
        return "High state-led activity"
    if y < 2010:
        return "Stabilization"
    if y < 2020:
        return "Commercial acceleration"
    return "Mega-constellation growth"


def load_original_datasets() -> dict[str, pd.DataFrame]:
    return {
        "Space_Missions": pd.read_csv(SPACE_PATH, low_memory=False),
        "GCAT": pd.read_csv(GCAT_PATH, sep="\t", low_memory=False),
        "UCS": pd.read_excel(UCS_PATH),
    }


def build_space_events(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["source_dataset"] = "Space_Missions"
    out["source_record_id"] = df.index.map(lambda i: f"space_{i}")
    out["record_level"] = "launch"
    out["launch_id"] = out["source_record_id"]
    out["launch_date_raw"] = df.get("Datum")
    out["launch_date"] = pd.to_datetime(df.get("DateTime", df.get("Datum")), errors="coerce", utc=True).dt.tz_localize(None)
    out["year"] = pd.to_numeric(df.get("Year"), errors="coerce") if "Year" in df else out["launch_date"].dt.year
    out["mission_name"] = df.get("Detail")
    out["satellite_name"] = df.get("Detail").map(parse_space_payload) if "Detail" in df else None
    out["launch_provider"] = df.get("Company Name").map(normalize_organization) if "Company Name" in df else "Unknown"
    out["country"] = df.get("Country").map(normalize_country) if "Country" in df else "Unknown"
    out["launch_site"] = df.get("Launch_Site", df.get("Location"))
    out["launch_vehicle"] = df.get("Detail").map(parse_space_vehicle) if "Detail" in df else None
    out["mission_status"] = df.get("Status Mission")
    out["rocket_status"] = df.get("Status Rocket")
    out["payload_count"] = 1
    out["source_count"] = pd.to_numeric(df.get("Count", 1), errors="coerce").fillna(1)
    out["preferred_for_launch_count"] = False
    return out.reset_index(drop=True)


def build_gcat_events(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data = data[data["Launch_Date"].notna()] if "Launch_Date" in data else data
    tag_col = "#Launch_Tag" if "#Launch_Tag" in data else "Launch_Tag" if "Launch_Tag" in data else None
    if tag_col:
        data = data[~data[tag_col].astype(str).str.startswith("# Updated")]
    if tag_col and "Launch_Date" in data:
        agg_spec = {
            "PLName": concat_unique,
            "Name": concat_unique,
            "SatOwner": mode_value,
            "SatState": mode_value,
            "LV_Type": mode_value,
            "Launch_Site": mode_value,
            "Launch_Pad": mode_value,
            "Agency": mode_value,
            "Launch_Code": mode_value,
            "Piece": "count",
        }
        agg_spec = {k: v for k, v in agg_spec.items() if k in data.columns}
        grouped = data.groupby([tag_col, "Launch_Date"], dropna=False).agg(agg_spec).reset_index()
    else:
        grouped = data.copy()
    out = pd.DataFrame(index=grouped.index)
    out["source_dataset"] = "GCAT"
    out["source_record_id"] = grouped[tag_col].astype(str) if tag_col and tag_col in grouped else grouped.index.map(lambda i: f"gcat_{i}")
    out["record_level"] = "launch_or_payload_group"
    out["launch_id"] = out["source_record_id"]
    out["launch_date_raw"] = grouped.get("Launch_Date")
    out["launch_date"] = pd.to_datetime(grouped.get("Launch_Date"), errors="coerce", format="mixed") if "Launch_Date" in grouped else pd.NaT
    out["year"] = pd.to_numeric(grouped.get("Launch_Date", pd.Series(index=grouped.index, dtype=str)).astype(str).str.extract(r"((?:19|20)\d{2})")[0], errors="coerce")
    out["mission_name"] = grouped.get("Name")
    out["satellite_name"] = grouped.get("PLName", grouped.get("Name"))
    out["launch_provider"] = grouped.get("Agency", grouped.get("SatOwner")).map(normalize_organization)
    out["country"] = grouped.get("SatState").map(normalize_country) if "SatState" in grouped else "Unknown"
    out["launch_site"] = grouped.get("Launch_Site")
    out["launch_vehicle"] = grouped.get("LV_Type")
    out["mission_status"] = grouped.get("Launch_Code")
    out["rocket_status"] = "Unknown"
    out["payload_count"] = pd.to_numeric(grouped.get("Piece", 1), errors="coerce").fillna(1)
    out["source_count"] = 1
    out["preferred_for_launch_count"] = True
    return out.reset_index(drop=True)


def build_ucs_enrichment(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    current_col = "Current Official Name of Satellite"
    alt_col = "Name of Satellite, Alternate Names"
    for _, row in df.iterrows():
        names = []
        for col in [current_col, alt_col]:
            if col in df.columns and pd.notna(row.get(col)):
                names.extend(str(row.get(col)).split(","))
        for name in names:
            key = normalize_name_key(name)
            if not key:
                continue
            rows.append({
                "name_key": key,
                "ucs_satellite_name": clean_text(row.get(current_col)),
                "satellite_operator": normalize_organization(row.get("Operator/Owner")),
                "satellite_operator_country": normalize_country(row.get("Country of Operator/Owner")),
                "satellite_users": clean_text(row.get("Users")),
                "satellite_purpose": clean_text(row.get("Purpose")),
                "satellite_detailed_purpose": clean_text(row.get("Detailed Purpose")),
                "orbit_type": clean_text(row.get("Class of Orbit")),
                "orbit_subtype": clean_text(row.get("Type of Orbit")),
                "satellite_mass_kg": pd.to_numeric(row.get("Launch Mass (kg.)"), errors="coerce"),
                "ucs_launch_vehicle": clean_text(row.get("Launch Vehicle")),
                "ucs_launch_site": clean_text(row.get("Launch Site")),
                "cospar_number": clean_text(row.get("COSPAR Number")),
                "norad_number": clean_text(row.get("NORAD Number")),
            })
    if not rows:
        return pd.DataFrame(columns=["name_key"])
    return pd.DataFrame(rows).drop_duplicates("name_key", keep="first")


def consolidate_dataset(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    base = pd.concat([
        build_space_events(datasets["Space_Missions"]),
        build_gcat_events(datasets["GCAT"]),
    ], ignore_index=True, sort=False)
    base["name_key"] = base["satellite_name"].map(normalize_name_key)
    ucs = build_ucs_enrichment(datasets["UCS"])
    out = base.merge(ucs, on="name_key", how="left") if not ucs.empty else base.copy()
    out["ucs_match_found"] = out["ucs_satellite_name"].notna()
    return out


def add_derived_variables(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int64")
    out["decade"] = out["year"].map(lambda y: f"{int(y) // 10 * 10}s" if pd.notna(y) else "Unknown")
    out["space_era"] = out["year"].map(space_era)
    out["launch_frequency_period"] = out["year"].map(launch_frequency_period)
    out["mission_success_binary"] = out["mission_status"].map(mission_success)
    out["orbit_group"] = out.get("orbit_type", pd.Series(index=out.index)).map(classify_orbit)
    out["purpose_group"] = out.get("satellite_purpose", pd.Series(index=out.index)).map(classify_purpose)
    out["mass_group"] = out.get("satellite_mass_kg", pd.Series(index=out.index)).map(mass_group)
    out["organization_type"] = [classify_organization(p, o) for p, o in zip(out.get("launch_provider"), out.get("satellite_operator"))]
    return out


def treat_nulls(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df.copy()
    rows = []
    for col in out.columns:
        null_pct = round(out[col].isna().mean() * 100, 2)
        if null_pct == 0:
            continue
        if col == "satellite_mass_kg":
            action = "mantener nulos"
            justification = "Variable numerica de alto valor para tendencias actuales; imputar mediana distorsionaria la masa real. Se usa mass_group = Unknown para visualizacion categorica."
        elif col == "launch_date":
            action = "mantener nulos e inferir year cuando sea posible"
            justification = "La fecha exacta no siempre es recuperable, pero year conserva la utilidad temporal principal."
        elif col == "mission_success_binary":
            action = "mantener nulos"
            justification = "No todos los codigos de estado son comparables; imputar exito/fallo introduceria sesgo."
        elif col in CATEGORICAL_UNKNOWN_COLUMNS:
            fill_value = "No UCS match" if col in OPTIONAL_HIGH_NULL_BUT_USEFUL else "Unknown"
            out[col] = out[col].fillna(fill_value)
            action = f"imputar con {fill_value}"
            justification = "Campo categorico: una categoria explicita permite filtrar y no confunde ausencia de dato con dato real."
        else:
            action = "mantener nulos"
            justification = "No existe una imputacion segura sin crear informacion artificial."
        rows.append({"Columna": col, "% nulos": null_pct, "Accion": action, "Justificacion": justification})
    return out, pd.DataFrame(rows)


def final_column_order(df: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "source_dataset", "source_record_id", "record_level", "launch_id", "launch_date", "launch_date_raw",
        "year", "decade", "space_era", "launch_frequency_period", "mission_name", "satellite_name",
        "launch_provider", "country", "launch_site", "launch_vehicle", "mission_status",
        "mission_success_binary", "rocket_status", "payload_count", "source_count", "preferred_for_launch_count",
        "name_key", "ucs_match_found", "ucs_satellite_name", "satellite_operator", "satellite_operator_country",
        "satellite_users", "satellite_purpose", "satellite_detailed_purpose", "purpose_group", "orbit_type",
        "orbit_subtype", "orbit_group", "satellite_mass_kg", "mass_group", "ucs_launch_vehicle", "ucs_launch_site",
        "cospar_number", "norad_number", "organization_type",
    ]
    existing = [c for c in keep if c in df.columns]
    extra = [c for c in df.columns if c not in existing]
    return df[existing + extra]


def build_normalization_tables(raw: pd.DataFrame, final: pd.DataFrame) -> dict[str, pd.DataFrame]:
    tables = {}
    if "country" in raw:
        country_raw = raw["country"].dropna().astype(str).unique()
        tables["paises"] = pd.DataFrame({"valor_original": sorted(country_raw), "valor_normalizado": [normalize_country(v) for v in sorted(country_raw)]})
    if "launch_provider" in raw:
        org_raw = raw["launch_provider"].dropna().astype(str).unique()
        tables["organizaciones"] = pd.DataFrame({"valor_original": sorted(org_raw), "valor_normalizado": [normalize_organization(v) for v in sorted(org_raw)]})
    for source_col, table_name, func in [
        ("satellite_operator", "operadores", normalize_organization),
        ("orbit_type", "orbitas", classify_orbit),
        ("satellite_purpose", "propositos", classify_purpose),
    ]:
        values = final[source_col].dropna().astype(str).unique() if source_col in final else []
        tables[table_name] = pd.DataFrame({"valor_original": sorted(values), "valor_normalizado": [func(v) for v in sorted(values)]})
    return tables


def extract_audit_findings() -> pd.DataFrame:
    rows = []
    if AUDIT_MD.exists():
        text = AUDIT_MD.read_text(encoding="utf-8", errors="ignore")
        in_risks = False
        in_improvements = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("## Riesgos"):
                in_risks, in_improvements = True, False
                continue
            if stripped.startswith("## Mejoras"):
                in_risks, in_improvements = False, True
                continue
            if stripped.startswith("## "):
                in_risks = in_improvements = False
            if stripped.startswith("- ") and (in_risks or in_improvements):
                problem = stripped[2:]
                impact = "Alto" if any(t in problem.lower() for t in ["source_dataset", "doble", "publico/privado", "nulos"]) else "Medio"
                action = "Corregir en v2 y documentar" if in_improvements else "Mitigar en pipeline v2"
                rows.append({"Problema": problem, "Impacto": impact, "Accion propuesta": action})
    rows.extend([
        {"Problema": "Columnas UCS muy incompletas por bajo match de nombres", "Impacto": "Medio", "Accion propuesta": "Conservar las variables de valor analitico, marcar ucs_match_found y usar No UCS match."},
        {"Problema": "Variantes de paises y organizaciones", "Impacto": "Alto", "Accion propuesta": "Aplicar tablas de equivalencia para paises, organizaciones y operadores."},
        {"Problema": "Campos de masa, orbita y proposito no cubren todos los lanzamientos", "Impacto": "Medio", "Accion propuesta": "Usarlos para tendencias actuales y subconjuntos enriquecidos, no para conteos historicos globales."},
        {"Problema": "Solape entre GCAT y Space_Missions", "Impacto": "Alto", "Accion propuesta": "Mantener preferred_for_launch_count y usar GCAT para conteos historicos."},
    ])
    return pd.DataFrame(rows).drop_duplicates()


def detect_redundancy(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    cols = list(df.columns)
    for i, a in enumerate(cols):
        sa = df[a].fillna("__NA__").astype(str).str.strip().str.lower()
        for b in cols[i + 1:]:
            sb = df[b].fillna("__NA__").astype(str).str.strip().str.lower()
            same = round((sa == sb).mean() * 100, 2)
            if same >= 95:
                rows.append({"columna_1": a, "columna_2": b, "coincidencia_pct": same})
    return pd.DataFrame(rows)


def evaluate_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    unique_counts = df.nunique(dropna=True)
    null_pct = df.isna().mean() * 100
    constant = unique_counts[unique_counts <= 1].index.tolist()
    almost_empty = null_pct[null_pct >= 90].index.tolist()
    redundancy = detect_redundancy(df)
    redundant_cols = set(redundancy["columna_2"].tolist()) if not redundancy.empty else set()
    rows = []
    for col in df.columns:
        used_questions = [q for q, cols in QUESTION_COLUMNS.items() if col in cols]
        non_null = 100 - null_pct[col]
        analytic = 8 if col in HIGH_VALUE_COLUMNS else 5
        if col in OPTIONAL_HIGH_NULL_BUT_USEFUL:
            analytic = max(analytic, 7)
        if col in constant:
            analytic = min(analytic, 3)
        research = min(10, 3 + len(used_questions) * 3) if used_questions else (6 if col in HIGH_VALUE_COLUMNS else 3)
        quality = max(0, min(10, round(non_null / 10, 1)))
        if col in OPTIONAL_HIGH_NULL_BUT_USEFUL:
            quality = max(quality, 4)
        redundancy_label = "si" if col in redundant_cols else "no"
        if col in constant and col not in {"source_dataset"}:
            decision = "transformar/eliminar si no documenta trazabilidad"
        elif col in almost_empty and col not in OPTIONAL_HIGH_NULL_BUT_USEFUL:
            decision = "eliminar"
        elif col in redundant_cols:
            decision = "transformar"
        elif analytic >= 7 or research >= 7:
            decision = "mantener"
        else:
            decision = "transformar"
        rows.append({
            "Columna": col,
            "Utilidad analitica 0-10": analytic,
            "Utilidad preguntas 0-10": research,
            "Calidad datos 0-10": quality,
            "% nulos": round(null_pct[col], 2),
            "Redundancia": redundancy_label,
            "Decision": decision,
            "Preguntas asociadas": "; ".join(used_questions) if used_questions else "apoyo/trazabilidad",
        })
    evaluation = pd.DataFrame(rows).sort_values(["Decision", "Utilidad preguntas 0-10", "Utilidad analitica 0-10"], ascending=[True, False, False])
    eliminable = evaluation[evaluation["Decision"].str.contains("eliminar")].copy()
    conserve = evaluation[~evaluation["Decision"].str.contains("eliminar")].copy()
    return evaluation, eliminable, conserve


def validate_questions(df: pd.DataFrame, provisional: pd.DataFrame | None = None) -> pd.DataFrame:
    checks = []
    launch_df = df[df["preferred_for_launch_count"].fillna(False)] if "preferred_for_launch_count" in df else df
    metrics = {
        "Evolucion de lanzamientos": launch_df["year"].notna().mean() if not launch_df.empty else 0,
        "Liderazgo de actores": df[["year", "country", "launch_provider"]].replace("Unknown", np.nan).notna().all(axis=1).mean(),
        "Publico vs privado": df["organization_type"].ne("Unknown").mean(),
        "Tasa de exito": df["mission_success_binary"].notna().mean(),
        "Tendencias actuales": df[["year", "orbit_group", "purpose_group"]].replace("Unknown", np.nan).notna().all(axis=1).mean(),
    }
    provisional_metrics = {}
    if provisional is not None and not provisional.empty:
        prep = provisional.copy()
        if "source_dataset" in prep and prep["source_dataset"].isna().mean() > 0.9:
            prep_source_ok = 0
        else:
            prep_source_ok = 1
        provisional_metrics = {
            "Evolucion de lanzamientos": prep.get("year", pd.Series(dtype=float)).notna().mean(),
            "Liderazgo de actores": prep[[c for c in ["year", "country", "launch_provider"] if c in prep]].notna().all(axis=1).mean(),
            "Publico vs privado": prep.get("organization_type", pd.Series(dtype=object)).astype(str).str.lower().ne("unknown").mean(),
            "Tasa de exito": prep.get("mission_success_binary", pd.Series(dtype=float)).notna().mean(),
            "Tendencias actuales": prep.get("year", pd.Series(dtype=float)).ge(2010).mean() * prep_source_ok + prep.get("orbit_group", pd.Series(dtype=object)).astype(str).str.lower().ne("unknown").mean() * 0.5,
        }
    else:
        provisional_metrics = PROVISIONAL_METRICS_FROM_AUDIT.copy()
    for question, value in metrics.items():
        confidence = "Alta" if value >= 0.75 else "Media" if value >= 0.35 else "Parcial"
        prev = provisional_metrics.get(question, np.nan)
        improvement = "No comparable" if pd.isna(prev) else round((value - prev) * 100, 2)
        checks.append({
            "Pregunta": question,
            "Cobertura util v2 %": round(value * 100, 2),
            "Cobertura provisional %": "" if pd.isna(prev) else round(prev * 100, 2),
            "Mejora pp": improvement,
            "Nivel confianza": confidence,
            "Variables clave": ", ".join(QUESTION_COLUMNS[question]),
        })
    return pd.DataFrame(checks)


def final_metrics(df: pd.DataFrame) -> pd.DataFrame:
    years = pd.to_numeric(df["year"], errors="coerce")
    return pd.DataFrame([{
        "filas": len(df),
        "columnas": df.shape[1],
        "memoria_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
        "cobertura_temporal": f"{int(years.min())}-{int(years.max())}" if years.notna().any() else "Sin year",
        "porcentaje_nulos_final": round(df.isna().mean().mean() * 100, 2),
    }])


def markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if df is None or df.empty:
        return "Sin datos."
    data = df.head(max_rows).copy() if max_rows else df.copy()
    data = data.astype(object).where(pd.notna(data), "")
    data = data.map(lambda x: str(x).replace("|", "/").replace("\n", " "))
    header = "| " + " | ".join(data.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(data.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in data.values.tolist()]
    return "\n".join([header, sep] + rows)


def write_decisions_report(results: dict[str, Any]) -> None:
    lines = [
        "# Decisiones del dataset final v2",
        "",
        "## Objetivo",
        "Optimizar el dataset para responder la evolucion de lanzamientos, liderazgo espacial, publico vs privado, exito de misiones y tendencias actuales. No se optimiza por reducir columnas, sino por valor analitico para visualizacion.",
        "",
        "## FASE 1 - Problemas extraidos de la auditoria existente",
        markdown_table(results["audit_findings"]),
        "",
        "## FASE 2 - Revision de columnas",
        markdown_table(results["column_evaluation"]),
        "",
        "## FASE 3 - Propuesta de eliminacion/conservacion",
        "Columnas eliminables o candidatas a no incorporar desde las fuentes originales:",
        markdown_table(results["eliminable_columns"]),
        "",
        "Columnas recomendadas para conservar o transformar:",
        markdown_table(results["conserved_columns"]),
        "",
        "## FASE 4 - Tratamiento de nulos",
        markdown_table(results["null_report"]),
        "",
        "## FASE 5 - Normalizacion",
        "Se normalizaron paises, organizaciones, operadores, orbitas y propositos mediante tablas de correspondencia. Las tablas completas se generan internamente y se resumen aqui.",
        "",
        "### Paises",
        markdown_table(results["normalization_tables"]["paises"], max_rows=50),
        "",
        "### Organizaciones",
        markdown_table(results["normalization_tables"]["organizaciones"], max_rows=50),
        "",
        "### Operadores",
        markdown_table(results["normalization_tables"]["operadores"], max_rows=50),
        "",
        "### Orbitas",
        markdown_table(results["normalization_tables"]["orbitas"], max_rows=50),
        "",
        "### Propositos",
        markdown_table(results["normalization_tables"]["propositos"], max_rows=50),
        "",
        "## FASE 6 - Variables derivadas anadidas",
        markdown_table(pd.DataFrame([
            {"Variable": "year", "Explicacion": "Anio del lanzamiento; eje temporal principal."},
            {"Variable": "decade", "Explicacion": "Agrupa anios por decadas para comparaciones historicas."},
            {"Variable": "space_era", "Explicacion": "Clasifica Early Space Age, Space Race, Post Cold War y Commercial Space Age."},
            {"Variable": "organization_type", "Explicacion": "Clasifica actores como Public, Private, Mixed o Unknown a partir de proveedor y operador."},
            {"Variable": "mission_success_binary", "Explicacion": "Codifica exito/fallo de mision; conserva nulos si el estado no es comparable."},
            {"Variable": "purpose_group", "Explicacion": "Agrupa propositos satelitales en categorias visualizables."},
            {"Variable": "orbit_group", "Explicacion": "Simplifica clases orbitales en LEO, MEO, GEO, HEO u otras."},
            {"Variable": "mass_group", "Explicacion": "Agrupa masa sin imputar la masa numerica original."},
            {"Variable": "launch_frequency_period", "Explicacion": "Segmenta periodos por dinamica de frecuencia de lanzamientos."},
        ])),
        "",
        "## FASE 7 - Validacion de preguntas",
        markdown_table(results["question_validation"]),
        "",
        "## FASE 8 - Metricas del dataset definitivo",
        markdown_table(results["final_metrics"]),
        "",
        "## Fusion de datasets",
        "Se usa GCAT y Space_Missions como base de eventos de lanzamiento. GCAT queda marcado como fuente preferente para conteos historicos con `preferred_for_launch_count = True`; Space_Missions se conserva para trazabilidad y comparacion, pero no para duplicar conteos. UCS se une por `name_key`, una clave normalizada a partir de nombres oficiales y alternativos de satelites.",
        "",
        "## Columnas eliminadas o no incorporadas",
        "No se incorporaron columnas `Unnamed:*` de UCS, columnas de fuentes/citas bibliograficas de UCS y comentarios libres porque aportan baja utilidad directa a las cinco preguntas y aumentan ruido. Se sustituyeron variantes crudas de pais/organizacion por valores normalizados, manteniendo identificadores y trazabilidad suficientes.",
        "",
        "## Mejora principal",
        "La v2 corrige `source_dataset`, reduce nulos categoricos con categorias informativas, normaliza actores/paises y mantiene variables UCS aunque sean incompletas cuando sirven para tendencias actuales. Esto mejora la calidad para visualizacion sin eliminar informacion analiticamente valiosa.",
    ]
    DECISIONS_OUT.write_text("\n".join(lines), encoding="utf-8")


def load_provisional_dataset() -> pd.DataFrame | None:
    # La version provisional se elimino de la entrega; se comparan metricas fijas extraidas de la auditoria previa.
    return None


def export_auxiliary_tables(results: dict[str, Any]) -> None:
    table_dir = REPORTS_FINAL / "tablas_decisiones"
    table_dir.mkdir(parents=True, exist_ok=True)
    for name in ["audit_findings", "column_evaluation", "eliminable_columns", "conserved_columns", "null_report", "question_validation", "final_metrics"]:
        results[name].to_csv(table_dir / f"{name}.csv", index=False, encoding="utf-8")
    for name, table in results["normalization_tables"].items():
        table.to_csv(table_dir / f"normalizacion_{name}.csv", index=False, encoding="utf-8")


def write_reproducible_notebook() -> None:
    import nbformat as nbf

    nb = nbf.v4.new_notebook()
    cells = []
    cells.append(nbf.v4.new_markdown_cell("# Construccion del dataset final v2\n\nNotebook reproducible desde Space_Missions_Cleaned, GCAT y UCS Satellite Database."))
    cells.append(nbf.v4.new_code_cell("from pathlib import Path\nimport sys\n\nPROJECT_ROOT = Path.cwd() if (Path.cwd() / '01_datos').exists() else Path.cwd().parent\nSCRIPTS_DIR = PROJECT_ROOT / '03_scripts'\nif str(SCRIPTS_DIR) not in sys.path:\n    sys.path.insert(0, str(SCRIPTS_DIR))\n\nfrom pipeline_dataset_final import *"))
    sections = [
        ("01_Carga", "datasets = load_original_datasets()\n{k: v.shape for k, v in datasets.items()}"),
        ("02_Analisis_Inicial", "audit_findings = extract_audit_findings()\naudit_findings"),
        ("03_Limpieza", "raw_final = consolidate_dataset(datasets)\nwith_derived = add_derived_variables(raw_final)\nclean_final, null_report = treat_nulls(with_derived)\nnull_report"),
        ("04_Normalizacion", "normalization_tables = build_normalization_tables(raw_final, clean_final)\nnormalization_tables['paises'].head(20)"),
        ("05_Fusion", "clean_final[['source_dataset', 'launch_id', 'name_key', 'ucs_match_found']].head()"),
        ("06_Variables_Derivadas", "derived_cols = ['year', 'decade', 'space_era', 'organization_type', 'mission_success_binary', 'purpose_group', 'orbit_group', 'mass_group', 'launch_frequency_period']\nclean_final[derived_cols].head()"),
        ("07_Validacion", "final = final_column_order(clean_final)\ncolumn_evaluation, eliminable_columns, conserved_columns = evaluate_columns(final)\nquestion_validation = validate_questions(final, load_provisional_dataset())\nquestion_validation"),
        ("08_Exportacion", "results = run_pipeline(write_notebook=False)\nresults['final_metrics']"),
    ]
    for title, code in sections:
        cells.append(nbf.v4.new_markdown_cell(f"## {title}"))
        cells.append(nbf.v4.new_code_cell(code))
    nb["cells"] = cells
    NOTEBOOK_OUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, NOTEBOOK_OUT)


def run_pipeline(write_notebook: bool = True) -> dict[str, Any]:
    DATA_FINAL.mkdir(parents=True, exist_ok=True)
    REPORTS_FINAL.mkdir(parents=True, exist_ok=True)
    datasets = load_original_datasets()
    audit_findings = extract_audit_findings()
    raw_final = consolidate_dataset(datasets)
    with_derived = add_derived_variables(raw_final)
    clean_final, null_report = treat_nulls(with_derived)
    final = final_column_order(clean_final)
    normalization_tables = build_normalization_tables(raw_final, final)
    column_evaluation, eliminable_columns, conserved_columns = evaluate_columns(final)
    provisional = load_provisional_dataset()
    question_validation = validate_questions(final, provisional)
    metrics = final_metrics(final)
    final.to_csv(CSV_OUT, index=False, encoding="utf-8")
    final.to_parquet(PARQUET_OUT, index=False)
    results = {
        "final_dataset": final,
        "audit_findings": audit_findings,
        "column_evaluation": column_evaluation,
        "eliminable_columns": eliminable_columns,
        "conserved_columns": conserved_columns,
        "null_report": null_report,
        "normalization_tables": normalization_tables,
        "question_validation": question_validation,
        "final_metrics": metrics,
    }
    export_auxiliary_tables(results)
    write_decisions_report(results)
    if write_notebook:
        write_reproducible_notebook()
    return results


if __name__ == "__main__":
    results = run_pipeline(write_notebook=True)
    print("Dataset CSV:", CSV_OUT)
    print("Dataset Parquet:", PARQUET_OUT)
    print("Informe decisiones:", DECISIONS_OUT)
    print("Notebook:", NOTEBOOK_OUT)
    print(results["final_metrics"].to_string(index=False))
