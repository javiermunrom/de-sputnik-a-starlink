from __future__ import annotations

from pathlib import Path
import html
import json
import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import get_plotlyjs


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "01_datos" / "final" / "datos_finales_espacio_v2.parquet"
OUT = ROOT / "04_informes" / "final" / "exploracion_visualizaciones.html"

TOP_COUNTRIES = ["United States", "USSR/Russia", "Russia", "China", "Japan", "India", "Europe/ESA", "France", "United Kingdom"]
TOP_PROVIDER_COUNT = 10
PERIODS = {
    "1957-1969": (1957, 1969),
    "1970-1991": (1970, 1991),
    "1992-2009": (1992, 2009),
    "2010-2019": (2010, 2019),
    "2020-2026": (2020, 2026),
}

COLORS = {
    "United States": "#2563eb",
    "USSR/Russia": "#991b1b",
    "Russia": "#dc2626",
    "China": "#ef4444",
    "Japan": "#7c3aed",
    "India": "#16a34a",
    "Europe/ESA": "#0891b2",
    "France": "#60a5fa",
    "United Kingdom": "#f59e0b",
    "Other": "#94a3b8",
    "Public": "#1d4ed8",
    "Private": "#f97316",
    "Mixed": "#9333ea",
    "Unknown": "#9ca3af",
    "Success": "#16a34a",
    "Failure": "#dc2626",
    "Partial Failure": "#f59e0b",
}

PLOTLY_COLORWAY = ["#2563eb", "#ef4444", "#16a34a", "#f97316", "#7c3aed", "#0891b2", "#f59e0b", "#db2777", "#64748b"]
ERA_BANDS = [
    (1957, 1969, "Carrera espacial", "#dbeafe"),
    (1970, 1991, "Guerra Fria madura", "#fee2e2"),
    (1992, 2009, "Globalizacion", "#dcfce7"),
    (2010, 2019, "Comercializacion", "#ffedd5"),
    (2020, 2026, "Mega-constelaciones", "#ede9fe"),
]


def esc(value) -> str:
    return html.escape("" if pd.isna(value) else str(value), quote=True)


def slug(text: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in text)
    return "-".join(part for part in safe.split("-") if part)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = pd.read_parquet(DATASET)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    launch = df[df["preferred_for_launch_count"].fillna(False)].copy()
    launch = launch.dropna(subset=["year"])
    launch["year"] = launch["year"].astype(int)
    enriched = df[df["ucs_match_found"].fillna(False)].copy()
    return df, launch, enriched


def period_label(year: int) -> str:
    for label, (start, end) in PERIODS.items():
        if start <= int(year) <= end:
            return label
    return "Other"


def simplify_country(value: str) -> str:
    value = str(value)
    return value if value in TOP_COUNTRIES else "Other"


def add_era_bands(fig: go.Figure) -> None:
    for start, end, label, color in ERA_BANDS:
        fig.add_vrect(x0=start, x1=end, fillcolor=color, opacity=0.28, line_width=0, layer="below")
        fig.add_annotation(x=(start + end) / 2, y=1.05, yref="paper", text=label, showarrow=False, font=dict(size=11, color="#334155"))


def clean_category(value: str) -> str:
    value = "Unknown" if pd.isna(value) else str(value)
    return value if value and value.lower() not in {"nan", "none"} else "Unknown"


def period_dataframe(launch: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for period, (start, end) in PERIODS.items():
        sub = launch[launch["year"].between(start, end)]
        rows.append({"period": period, "start": start, "end": end, "records": len(sub)})
    return pd.DataFrame(rows)


def fig_html(fig: go.Figure, height: int = 470) -> str:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=45, r=25, t=70, b=45),
        font=dict(family="Inter, Segoe UI, Arial", size=13),
        hoverlabel=dict(bgcolor="white"),
        colorway=PLOTLY_COLORWAY,
        title=dict(font=dict(size=20, color="#142c61")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return pio.to_html(fig, include_plotlyjs=False, full_html=False, config={"displaylogo": False, "responsive": True})


def evaluate(question: str, chart: str) -> dict[str, int | str]:
    scores = {
        "P1 Cronologia narrativa": (10, 10, 8, 9, 10),
        "P1 Linea temporal": (9, 9, 7, 8, 10),
        "P1 Area acumulada": (8, 8, 7, 8, 9),
        "P1 Promedio etapas": (9, 9, 6, 8, 9),
        "P1 Reloj radial": (7, 8, 8, 9, 8),
        "P1 Ridgeline": (6, 7, 8, 8, 7),
        "P1 Heatmap temporal": (8, 7, 8, 8, 8),
        "P2 Streamgraph": (8, 9, 8, 9, 9),
        "P2 Lider anual": (9, 9, 7, 8, 9),
        "P2 Stacked Area": (8, 9, 8, 8, 9),
        "P2 Bump Chart": (7, 9, 7, 8, 9),
        "P2 Ranking interactivo": (9, 10, 8, 9, 10),
        "P2 Racing Bars": (8, 9, 7, 8, 8),
        "P2 Mapa por periodo": (7, 7, 7, 9, 7),
        "P2 Mapa mundial": (7, 6, 7, 8, 7),
        "P3 Area apilada": (9, 9, 7, 8, 10),
        "P3 Cobertura clasificacion": (9, 8, 6, 7, 9),
        "P3 Sankey": (7, 8, 7, 8, 8),
        "P3 Slope Chart": (9, 8, 6, 8, 9),
        "P3 Radar etapas": (8, 9, 8, 9, 9),
        "P3 Marimekko": (6, 7, 8, 7, 7),
        "P4 Linea exito": (9, 8, 7, 8, 10),
        "P4 Barras etapa": (9, 8, 6, 8, 9),
        "P4 Heatmap pais-anio": (7, 7, 9, 8, 8),
        "P4 Burbuja fallos": (8, 8, 8, 9, 8),
        "P4 Small multiples": (8, 8, 8, 8, 8),
        "P4 Anillo decada": (8, 8, 7, 9, 8),
        "P4 Barras decada": (9, 7, 6, 8, 9),
        "P5 Sunburst": (7, 9, 8, 9, 9),
        "P5 Treemap": (8, 8, 8, 9, 8),
        "P5 Parallel Categories": (7, 9, 9, 8, 9),
        "P5 Selector tendencias": (9, 9, 8, 8, 10),
        "P5 Matriz orbita uso": (9, 9, 7, 8, 9),
        "P5 Operadores usos": (9, 9, 8, 8, 9),
        "P5 Packed Circles": (6, 7, 7, 8, 7),
        "P5 Network Graph": (5, 8, 9, 7, 7),
        "EXP Timeline hitos": (9, 9, 5, 8, 8),
        "EXP Beeswarm": (6, 7, 9, 8, 6),
        "EXP Streamgraph": (6, 8, 9, 8, 7),
        "EXP Globe mapa": (6, 7, 7, 9, 6),
        "EXP Sankey historico": (7, 8, 9, 8, 7),
        "EXP Ranking temporal": (8, 9, 7, 8, 8),
    }
    clarity, narrative, density, aesthetic, fit = scores[chart]
    total = round(np.mean([clarity, narrative, density, aesthetic, fit]), 2)
    return {
        "pregunta": question,
        "grafico": chart,
        "claridad": clarity,
        "capacidad narrativa": narrative,
        "densidad informacion": density,
        "estetica": aesthetic,
        "adecuacion": fit,
        "promedio": total,
    }


def notes_html(advantages: list[str], disadvantages: list[str], observations: list[str], score: dict) -> str:
    def list_html(items):
        return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"

    score_items = [
        ("Claridad", score["claridad"]),
        ("Narrativa", score["capacidad narrativa"]),
        ("Densidad", score["densidad informacion"]),
        ("Estetica", score["estetica"]),
        ("Adecuacion", score["adecuacion"]),
    ]
    score_html = "".join(
        f"<div class='score-pill'><span>{esc(label)}</span><strong>{value}/10</strong></div>" for label, value in score_items
    )
    return f"""
    <div class="evaluation-grid">
      <div><h4>Ventajas</h4>{list_html(advantages)}</div>
      <div><h4>Inconvenientes</h4>{list_html(disadvantages)}</div>
      <div><h4>Observaciones automaticas</h4>{list_html(observations)}</div>
    </div>
    <div class="score-row">{score_html}<div class='score-total'>Promedio: {score['promedio']}/10</div></div>
    """


def chart_card(title: str, question: str, chart_id: str, chart_html: str, advantages: list[str], disadvantages: list[str], observations: list[str], scores: list[dict]) -> str:
    score = evaluate(question, chart_id)
    scores.append(score)
    return f"""
    <article class="chart-card" id="{slug(chart_id)}">
      <div class="chart-head">
        <h3>{esc(title)}</h3>
        <span class="badge-score">{score['promedio']}/10</span>
      </div>
      <div class="chart-box">{chart_html}</div>
      {notes_html(advantages, disadvantages, observations, score)}
    </article>
    """


def question_section(title: str, subtitle: str, cards: list[str]) -> str:
    sid = slug(title)
    return f"""
    <section class="question-section" id="{sid}">
      <div class="section-title"><p>{esc(subtitle)}</p><h2>{esc(title)}</h2></div>
      {''.join(cards)}
    </section>
    """


def build_q1(launch: pd.DataFrame, scores: list[dict]) -> str:
    yearly = launch.groupby("year").size().reset_index(name="lanzamientos")
    yearly["acumulado"] = yearly["lanzamientos"].cumsum()
    yearly["media_movil_5"] = yearly["lanzamientos"].rolling(5, min_periods=1).mean()
    max_row = yearly.loc[yearly["lanzamientos"].idxmax()]
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=yearly["year"], y=yearly["lanzamientos"], name="Lanzamientos anuales", marker=dict(color="#93c5fd"), opacity=0.72, hovertemplate="%{x}<br>Lanzamientos: %{y}<extra></extra>"))
    fig1.add_trace(go.Scatter(x=yearly["year"], y=yearly["media_movil_5"], mode="lines", name="Media movil 5 anos", line=dict(color="#1d4ed8", width=4), hovertemplate="%{x}<br>Media movil: %{y:.1f}<extra></extra>"))
    add_era_bands(fig1)
    for year, label in [(1957, "Sputnik"), (1969, "Apollo 11"), (1991, "Fin Guerra Fria"), (2010, "Era comercial"), (2020, "Mega-constelaciones")]:
        fig1.add_vline(x=year, line_dash="dot", line_color="#475569", opacity=0.45)
        fig1.add_annotation(x=year, y=0.92, yref="paper", text=label, showarrow=False, textangle=-90, font=dict(size=10, color="#334155"))
    fig1.update_xaxes(rangeslider=dict(visible=True))
    fig1.update_yaxes(title="Lanzamientos")
    fig1.update_layout(title="Cronologia narrativa: de Sputnik a la economia orbital")
    fig1.add_annotation(x=int(max_row["year"]), y=int(max_row["lanzamientos"]), text=f"Maximo: {int(max_row['year'])} ({int(max_row['lanzamientos'])})", showarrow=True, arrowhead=2, bgcolor="white")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=yearly["year"], y=yearly["acumulado"], mode="lines", fill="tozeroy", fillcolor="rgba(37,99,235,.18)", line=dict(color="#2563eb", width=4), hovertemplate="%{x}<br>Acumulado: %{y}<extra></extra>"))
    add_era_bands(fig2)
    fig2.update_xaxes(rangeslider=dict(visible=True))
    fig2.update_layout(title="Area acumulada: cuando la pendiente se acelera, cambia el modelo espacial")
    fig2.update_yaxes(title="Lanzamientos acumulados")
    period_rows = []
    for period, (start, end) in PERIODS.items():
        sub = yearly[yearly["year"].between(start, end)]
        years = end - start + 1
        total = int(sub["lanzamientos"].sum())
        period_rows.append({"period": period, "total": total, "media_anual": total / years, "years": years})
    period_summary = pd.DataFrame(period_rows)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=period_summary["period"],
        y=period_summary["media_anual"],
        marker=dict(color=["#60a5fa", "#ef4444", "#16a34a", "#f97316", "#7c3aed"], line=dict(color="white", width=1.5)),
        text=period_summary["media_anual"].round(1).astype(str) + " / ano",
        textposition="outside",
        customdata=np.stack([period_summary["total"], period_summary["years"]], axis=-1),
        hovertemplate="%{x}<br>Media anual: %{y:.1f}<br>Total: %{customdata[0]}<br>Anos: %{customdata[1]}<extra></extra>",
    ))
    fig3.add_trace(go.Scatter(
        x=period_summary["period"],
        y=period_summary["media_anual"],
        mode="lines+markers",
        line=dict(color="#0f172a", width=3),
        marker=dict(size=9, color="#0f172a"),
        name="Cambio entre etapas",
        hoverinfo="skip",
    ))
    fig3.update_layout(title="Promedio anual por etapa: aqui si se ve la aceleracion", showlegend=False)
    fig3.update_yaxes(title="Lanzamientos medios por ano", rangemode="tozero")

    observations = [
        f"El maximo anual detectado es {int(max_row['year'])}, con {int(max_row['lanzamientos'])} lanzamientos preferentes.",
        "La decada de 2020 destaca pese a estar incompleta.",
        "La serie muestra oleadas historicas, no crecimiento lineal uniforme.",
    ]
    cards = [
        chart_card("1. Cronologia narrativa", "Pregunta 1", "P1 Cronologia narrativa", fig_html(fig1, 520), ["Une volumen anual, tendencia suavizada y etapas historicas.", "El range slider permite explorar cualquier periodo sin perder la historia."], ["Necesita seleccionar pocos hitos para no saturar.", "La media movil suaviza picos concretos."], observations, scores),
        chart_card("2. Area acumulada", "Pregunta 1", "P1 Area acumulada", fig_html(fig2), ["Comunica magnitud acumulada y aceleracion reciente.", "Funciona bien como grafico emocional de crecimiento."], ["Oculta caidas o periodos de baja actividad.", "Por si sola no deja clara la pendiente de cada etapa."], ["Se acompana con el grafico de promedio por etapa para que la aceleracion sea evidente."], scores),
        chart_card("3. Promedio anual por etapa", "Pregunta 1", "P1 Promedio etapas", fig_html(fig3, 440), ["Hace visible la aceleracion reciente sin depender de leer pendientes.", "Responde crecimiento, estancamientos y situacion actual de forma directa."], ["Resume etapas y pierde detalle anual.", "Debe ir despues de la cronologia, no sustituirla."], ["La etapa 2020-2026 se entiende como cambio de ritmo, no solo como acumulado."], scores),
    ]
    return question_section("Pregunta 1 - Evolucion de lanzamientos", "Como ha evolucionado el numero de lanzamientos desde 1957?", cards)


def build_q2(launch: pd.DataFrame, scores: list[dict]) -> str:
    data = launch.copy()
    data["country_simple"] = data["country"].map(simplify_country)
    yearly = data.groupby(["year", "country_simple"]).size().reset_index(name="lanzamientos")
    leaders = yearly.loc[yearly.groupby("year")["lanzamientos"].idxmax()].copy()
    total_yearly = data.groupby("year").size().reset_index(name="total")
    total_by_country = data["country_simple"].value_counts()
    top_msg = f"Los paises/actores con mas registros son: {', '.join(total_by_country.head(5).index.tolist())}."

    fig1 = go.Figure()
    actor_order = ["USSR/Russia", "United States", "Russia", "China", "Europe/ESA", "Japan", "India", "Other"]
    full_years = pd.DataFrame({"year": sorted(data["year"].unique())})
    for country in actor_order:
        sub = yearly[yearly["country_simple"].eq(country)]
        sub = full_years.merge(sub, on="year", how="left").fillna({"country_simple": country, "lanzamientos": 0})
        fig1.add_trace(go.Scatter(x=sub["year"], y=sub["lanzamientos"], mode="lines", stackgroup="one", name=country, line=dict(width=0.5), fillcolor=COLORS.get(country, "#94a3b8"), hovertemplate=f"{country}<br>%{{x}}: %{{y}} lanzamientos<extra></extra>"))
    fig1.add_trace(go.Scatter(x=total_yearly["year"], y=total_yearly["total"], mode="lines", name="Total anual", line=dict(color="#0f172a", width=3), hovertemplate="%{x}<br>Total: %{y}<extra></extra>"))
    add_era_bands(fig1)
    fig1.update_xaxes(rangeslider=dict(visible=True))
    fig1.update_yaxes(title="Lanzamientos")
    fig1.update_layout(title="Area de actores + total: quien ocupa el espacio en cada etapa")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=leaders["year"],
        y=[1] * len(leaders),
        marker=dict(color=[COLORS.get(c, "#94a3b8") for c in leaders["country_simple"]]),
        customdata=np.stack([leaders["country_simple"], leaders["lanzamientos"]], axis=-1),
        hovertemplate="%{x}<br>Lider: %{customdata[0]}<br>Lanzamientos del lider: %{customdata[1]}<extra></extra>",
    ))
    for country in actor_order[:-1]:
        years = leaders[leaders["country_simple"].eq(country)]["year"]
        if not years.empty:
            fig2.add_annotation(x=int(years.median()), y=1.18, text=country, showarrow=False, font=dict(size=11, color=COLORS.get(country, "#334155")))
    add_era_bands(fig2)
    fig2.update_xaxes(rangeslider=dict(visible=True), title="Ano")
    fig2.update_yaxes(visible=False, range=[0, 1.35])
    fig2.update_layout(title="Cinta de liderazgo anual: quien queda primero cada ano", showlegend=False)

    period_rows = []
    for period, (start, end) in PERIODS.items():
        sub = data[data["year"].between(start, end)]
        for provider, n in sub["launch_provider"].value_counts().head(TOP_PROVIDER_COUNT).items():
            period_rows.append({"period": period, "launch_provider": provider, "lanzamientos": n})
    period_rank = pd.DataFrame(period_rows)
    fixed_providers = period_rank.groupby("launch_provider")["lanzamientos"].sum().sort_values(ascending=False).head(16).index.tolist()
    fixed_rows = []
    for period in PERIODS:
        counts = period_rank[period_rank["period"].eq(period)].set_index("launch_provider")["lanzamientos"]
        for provider in fixed_providers:
            fixed_rows.append({"period": period, "launch_provider": provider, "lanzamientos": int(counts.get(provider, 0))})
    period_rank = pd.DataFrame(fixed_rows)
    provider_color = {provider: PLOTLY_COLORWAY[i % len(PLOTLY_COLORWAY)] for i, provider in enumerate(period_rank["launch_provider"].drop_duplicates())}
    first_period = next(iter(PERIODS.keys()))
    max_rank_value = max(period_rank["lanzamientos"].max(), 1)

    def ranking_bar_trace(period: str) -> go.Bar:
        sub = period_rank[period_rank["period"].eq(period)].sort_values(["lanzamientos", "launch_provider"], ascending=[True, True])
        return go.Bar(
            x=sub["lanzamientos"],
            y=sub["launch_provider"],
            orientation="h",
            marker=dict(color=[provider_color.get(p, "#64748b") for p in sub["launch_provider"]]),
            text=sub["lanzamientos"],
            textposition="auto",
            hovertemplate="%{y}<br>Lanzamientos: %{x}<extra></extra>",
        )

    fig3 = go.Figure(data=[ranking_bar_trace(first_period)], frames=[go.Frame(data=[ranking_bar_trace(period)], name=period, layout=go.Layout(title_text=f"Ranking de proveedores - {period}")) for period in PERIODS])
    fig3.update_layout(
        title=f"Ranking interactivo de proveedores - {first_period}",
        yaxis=dict(categoryorder="total ascending"),
        xaxis=dict(title="Lanzamientos", range=[0, max_rank_value * 1.12]),
        showlegend=False,
        transition=dict(duration=1300, easing="cubic-in-out"),
        sliders=[{"currentvalue": {"prefix": "Periodo: "}, "steps": [{"args": [[period], {"frame": {"duration": 1200, "redraw": True}, "transition": {"duration": 1300, "easing": "cubic-in-out"}, "mode": "immediate"}], "label": period, "method": "animate"} for period in PERIODS]}],
        updatemenus=[{"type": "buttons", "showactive": False, "x": 1, "y": 1.14, "buttons": [{"label": "Play lento", "method": "animate", "args": [None, {"frame": {"duration": 1800, "redraw": True}, "transition": {"duration": 1400, "easing": "cubic-in-out"}, "fromcurrent": True}]}, {"label": "Pausa", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}]}]}],
    )

    map_rows = []
    for period, (start, end) in PERIODS.items():
        sub = data[data["year"].between(start, end)].groupby("country").size().reset_index(name="lanzamientos")
        sub["period"] = period
        map_rows.append(sub)
    map_df = pd.concat(map_rows, ignore_index=True)
    max_map = max(map_df["lanzamientos"].max(), 1)
    fig4 = px.choropleth(map_df, locations="country", locationmode="country names", color="lanzamientos", hover_name="country", animation_frame="period", title="Mapa mundial por periodo historico", color_continuous_scale="Plasma", range_color=[0, max_map])
    fig4.update_geos(projection_type="natural earth")
    fig4.update_layout(coloraxis_colorbar=dict(title="Lanzamientos<br>misma escala"), transition=dict(duration=1500, easing="cubic-in-out"), updatemenus=[{"type": "buttons", "showactive": False, "x": 0.02, "y": 0, "buttons": [{"label": "Play lento", "method": "animate", "args": [None, {"frame": {"duration": 1800, "redraw": True}, "transition": {"duration": 1200, "easing": "cubic-in-out"}, "fromcurrent": True}]}, {"label": "Pausa", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}]}]}])

    cards = [
        chart_card("1. Area de actores + total", "Pregunta 2", "P2 Streamgraph", fig_html(fig1, 520), ["Mantiene la idea del streamgraph pero con total anual encima para leer mejor.", "Permite aislar actores desde la leyenda."], ["Los actores pequenos quedan comprimidos.", "Requiere simplificar paises en 'Other'."], [top_msg, "Si se usa en la pieza final conviene anotar URSS/Rusia, EEUU, China y SpaceX/CASC en el tramo reciente."], scores),
        chart_card("2. Cinta de liderazgo anual", "Pregunta 2", "P2 Lider anual", fig_html(fig2, 360), ["Se entiende de un vistazo quien lidera cada ano.", "Complementa el area porque no mezcla liderazgo con volumen."], ["No muestra segundos puestos.", "Debe leerse junto al volumen anual."], ["Es una alternativa mejor al bump chart para contar cambios de liderazgo sin ruido."], scores),
        chart_card("3. Ranking interactivo por periodo", "Pregunta 2", "P2 Ranking interactivo", fig_html(fig3, 560), ["Permite seleccionar periodo y ver quien lidera en cada etapa.", "Hace visible el salto de SpaceX en 2020-2026."], ["No muestra continuidad anual dentro del periodo.", "Los nombres largos de proveedores pueden ocupar espacio."], ["SpaceX domina 2020-2026; CASC aparece como gran actor reciente."], scores),
        chart_card("4. Mapa mundial por periodo", "Pregunta 2", "P2 Mapa por periodo", fig_html(fig4), ["Aporta lectura geografica inmediata.", "Usa la misma escala en todos los periodos para que el crecimiento sea comparable."], ["No muestra bien actores supranacionales ni URSS/Rusia historica.", "Menos potente que graficos temporales para liderazgo."], ["El mapa es mas util como apoyo contextual que como grafico central."], scores),
    ]
    return question_section("Pregunta 2 - Liderazgo de actores", "Que actores han liderado la actividad espacial? Incluye clic en pais via hover/click de Plotly y filtro temporal mediante range slider cuando aplica.", cards)


def build_q3(launch: pd.DataFrame, scores: list[dict]) -> str:
    data = launch.copy()
    data["period"] = data["year"].map(period_label)
    yearly = data.groupby(["year", "organization_type"]).size().reset_index(name="lanzamientos")
    fig1 = px.area(yearly, x="year", y="lanzamientos", color="organization_type", title="Area apilada publico/privado", color_discrete_map=COLORS)
    fig1.update_traces(stackgroup="one", groupnorm="percent")
    fig1.update_xaxes(rangeslider=dict(visible=True))
    fig1.update_yaxes(title="Peso relativo", ticksuffix="%")
    add_era_bands(fig1)
    unknown_share = data["organization_type"].eq("Unknown").mean() * 100
    fig1.add_annotation(x=0.01, y=0.98, xref="paper", yref="paper", text=f"Aviso: Unknown representa {unknown_share:.1f}% del total", showarrow=False, align="left", bgcolor="#fff7ed", bordercolor="#fdba74", font=dict(color="#9a3412"))

    coverage_rows = []
    for period in PERIODS:
        sub = data[data["period"].eq(period)]
        unknown = int(sub["organization_type"].eq("Unknown").sum())
        classified = int(len(sub) - unknown)
        coverage_rows.append({"period": period, "tipo": "Clasificado", "n": classified})
        coverage_rows.append({"period": period, "tipo": "Unknown", "n": unknown})
    coverage = pd.DataFrame(coverage_rows)
    fig2 = px.bar(coverage, x="period", y="n", color="tipo", title="Cobertura de clasificacion publico/privado", color_discrete_map={"Clasificado": "#0f766e", "Unknown": "#9ca3af"}, text="n")
    fig2.update_layout(barmode="stack")
    fig2.update_yaxes(title="Registros")

    classified = data[~data["organization_type"].eq("Unknown")].copy()
    slope = classified.groupby(["period", "organization_type"]).size().reset_index(name="n")
    period_totals = slope.groupby("period")["n"].transform("sum")
    slope["pct"] = slope["n"] / period_totals * 100
    slope = slope[slope["organization_type"].isin(["Public", "Private", "Mixed"])]
    fig3 = px.line(slope, x="period", y="pct", color="organization_type", markers=True, title="Cambio estructural entre registros clasificados", color_discrete_map=COLORS)
    fig3.update_traces(line=dict(width=5), marker=dict(size=11))
    fig3.update_yaxes(title="Porcentaje dentro de registros clasificados", ticksuffix="%", range=[0, 100])
    fig3.add_annotation(x="1957-1969", y=float(slope[(slope["period"].eq("1957-1969")) & (slope["organization_type"].eq("Public"))]["pct"].max()), text="Predominio publico", showarrow=True, arrowhead=2, bgcolor="white")
    recent_private = slope[(slope["period"].eq("2020-2026")) & (slope["organization_type"].eq("Private"))]
    if not recent_private.empty:
        fig3.add_annotation(x="2020-2026", y=float(recent_private["pct"].iloc[0]), text="Sube el privado", showarrow=True, arrowhead=2, bgcolor="white")

    cards = [
        chart_card("1. Area 100% publico/privado", "Pregunta 3", "P3 Area apilada", fig_html(fig1), ["Es la opcion mas clara para explicar la transicion.", "Mantiene continuidad temporal y muestra el equilibrio relativo."], ["Unknown debe explicarse para no inducir lectura falsa.", "No muestra volumen absoluto."], ["En 2020-2026 el bloque privado supera al publico en registros clasificados."], scores),
        chart_card("2. Cuanto Unknown hay", "Pregunta 3", "P3 Cobertura clasificacion", fig_html(fig2, 420), ["Hace transparente la limitacion del dataset.", "Evita vender como certeza lo que no esta clasificado."], ["No cuenta la historia principal por si solo.", "Debe funcionar como aviso metodologico."], ["La lectura publico/privado debe distinguir total historico y registros clasificados."], scores),
        chart_card("3. Slope publico vs privado", "Pregunta 3", "P3 Slope Chart", fig_html(fig3, 500), ["Muestra claramente como baja Public y sube Private.", "Usa solo registros clasificados para no mezclar incertidumbre con tendencia."], ["Al excluir Unknown cambia la base de calculo.", "No muestra volumen absoluto."], ["Este grafico es mejor para la conclusion: del Estado a empresas privadas."], scores),
    ]
    return question_section("Pregunta 3 - Equilibrio publico/privado", "Como ha cambiado el equilibrio entre agencias publicas y empresas privadas? Incluye seleccion de decada mediante facetas, periodos y range sliders.", cards)


def build_q4(launch: pd.DataFrame, scores: list[dict]) -> str:
    data = launch.dropna(subset=["mission_success_binary"]).copy()
    yearly = data.groupby("year").agg(tasa_exito=("mission_success_binary", "mean"), lanzamientos=("mission_success_binary", "size")).reset_index()
    yearly["media_movil_5"] = yearly["tasa_exito"].rolling(5, min_periods=1).mean()
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=yearly["year"], y=yearly["lanzamientos"], name="Volumen", marker=dict(color="rgba(148,163,184,.35)"), yaxis="y2", hovertemplate="%{x}<br>Lanzamientos con estado: %{y}<extra></extra>"))
    fig1.add_trace(go.Scatter(x=yearly["year"], y=yearly["tasa_exito"], mode="lines+markers", name="Tasa anual", line=dict(color="#93c5fd"), hovertemplate="%{x}<br>Exito anual: %{y:.1%}<extra></extra>"))
    fig1.add_trace(go.Scatter(x=yearly["year"], y=yearly["media_movil_5"], mode="lines", name="Media movil 5", line=dict(color="#1d4ed8", width=4), hovertemplate="%{x}<br>Media movil: %{y:.1%}<extra></extra>"))
    add_era_bands(fig1)
    fig1.update_layout(title="Fiabilidad espacial: del experimento a la operacion rutinaria", yaxis=dict(tickformat=".0%", range=[0, 1.02], title="Tasa de exito"), yaxis2=dict(title="Lanzamientos", overlaying="y", side="right", showgrid=False, rangemode="tozero"))
    fig1.update_xaxes(rangeslider=dict(visible=True))

    period_rows = []
    for period, (start, end) in PERIODS.items():
        sub = data[data["year"].between(start, end)]
        period_rows.append({"period": period, "tasa_exito": sub["mission_success_binary"].mean(), "lanzamientos": len(sub)})
    period_success = pd.DataFrame(period_rows)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=period_success["period"],
        y=period_success["tasa_exito"],
        marker=dict(color=period_success["tasa_exito"], colorscale="RdYlGn", cmin=0, cmax=1, line=dict(color="white", width=1.5)),
        text=period_success["tasa_exito"].mul(100).round(1).astype(str) + "%",
        textposition="outside",
        customdata=period_success["lanzamientos"],
        hovertemplate="%{x}<br>Exito medio: %{y:.1%}<br>Lanzamientos: %{customdata}<extra></extra>",
    ))
    fig2.update_layout(title="Resumen por etapa: la fiabilidad se vuelve rutina", showlegend=False)
    fig2.update_yaxes(title="Tasa media de exito", tickformat=".0%", range=[0, 1.08])

    early = data[data["year"].between(1957, 1969)]["mission_success_binary"].mean() * 100
    recent = data[data["year"].between(2020, 2026)]["mission_success_binary"].mean() * 100
    cards = [
        chart_card("1. Linea de fiabilidad + volumen", "Pregunta 4", "P4 Linea exito", fig_html(fig1, 520), ["Mejor lectura de tendencia y maduracion.", "Combina exito con volumen para evitar conclusiones por anos pequenos."], ["La tasa anual puede fluctuar con pocos lanzamientos.", "Necesita nota metodologica sobre codigos de estado."], [f"La tasa pasa de {early:.2f}% en 1957-1969 a {recent:.2f}% en 2020-2026."], scores),
        chart_card("2. Resumen por etapa", "Pregunta 4", "P4 Barras etapa", fig_html(fig2, 420), ["Refuerza la conclusion sin introducir otro lenguaje visual complejo.", "Permite comparar fiabilidad media entre etapas."], ["Promedia anos con volumenes distintos.", "Pierde detalle anual."], ["Sirve como cierre: el espacio pasa de experimento arriesgado a actividad de alta fiabilidad."], scores),
    ]
    return question_section("Pregunta 4 - Tasa de exito", "Como ha evolucionado la tasa de exito de las misiones?", cards)


def packed_circles_fig(enriched: pd.DataFrame) -> go.Figure:
    counts = enriched["purpose_group"].value_counts().reset_index()
    counts.columns = ["purpose_group", "n"]
    angles = np.linspace(0, 2 * math.pi, len(counts), endpoint=False)
    radii = np.sqrt(counts["n"] / counts["n"].max()) * 55
    x = np.cos(angles) * (radii.max() + 20)
    y = np.sin(angles) * (radii.max() + 20)
    fig = go.Figure(go.Scatter(
        x=x,
        y=y,
        mode="markers+text",
        text=counts["purpose_group"],
        textposition="middle center",
        marker=dict(size=radii, sizemode="diameter", color=counts["n"], colorscale="Viridis", showscale=True, line=dict(color="white", width=2)),
        customdata=counts["n"],
        hovertemplate="%{text}<br>Registros: %{customdata}<extra></extra>",
    ))
    fig.update_layout(title="Packed circles aproximado por proposito", xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
    return fig


def network_fig(enriched: pd.DataFrame) -> go.Figure:
    data = enriched.copy()
    data = data[~data["purpose_group"].astype(str).str.lower().isin(["unknown", "no ucs match"])]
    data = data[~data["orbit_group"].astype(str).str.lower().isin(["unknown", "no ucs match"])]
    top_ops = data["satellite_operator"].value_counts().head(10).index.tolist()
    data = data[data["satellite_operator"].isin(top_ops)]
    nodes = []
    for col, group in [("orbit_group", "Orbita"), ("purpose_group", "Proposito"), ("satellite_operator", "Operador")]:
        for value in data[col].dropna().unique():
            nodes.append((f"{group}: {value}", group, value))
    nodes = list(dict.fromkeys(nodes))
    node_index = {node[0]: i for i, node in enumerate(nodes)}
    positions = {}
    layers = {"Orbita": 0, "Proposito": 1, "Operador": 2}
    for layer in layers:
        layer_nodes = [n for n in nodes if n[1] == layer]
        for j, node in enumerate(layer_nodes):
            positions[node[0]] = (layers[layer], j - len(layer_nodes) / 2)
    edge_rows = []
    for _, row in data.iterrows():
        edge_rows.append((f"Orbita: {row['orbit_group']}", f"Proposito: {row['purpose_group']}"))
        edge_rows.append((f"Proposito: {row['purpose_group']}", f"Operador: {row['satellite_operator']}"))
    edge_counts = pd.Series(edge_rows).value_counts().head(80)
    fig = go.Figure()
    for (source, target), n in edge_counts.items():
        if source not in positions or target not in positions:
            continue
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", line=dict(width=max(1, math.sqrt(n)), color="rgba(100,116,139,.35)"), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(
        x=[positions[n[0]][0] for n in nodes if n[0] in positions],
        y=[positions[n[0]][1] for n in nodes if n[0] in positions],
        text=[n[2] for n in nodes if n[0] in positions],
        mode="markers+text",
        textposition="middle right",
        marker=dict(size=13, color=["#2563eb" if n[1] == "Orbita" else "#f97316" if n[1] == "Proposito" else "#16a34a" for n in nodes if n[0] in positions]),
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    ))
    fig.update_layout(title="Network Graph: orbitas, propositos y operadores", xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig


def build_q5(enriched: pd.DataFrame, scores: list[dict]) -> str:
    useful = enriched.copy()
    useful = useful[~useful["purpose_group"].astype(str).str.lower().isin(["unknown", "no ucs match"])]
    useful = useful[~useful["orbit_group"].astype(str).str.lower().isin(["unknown", "no ucs match"])]
    current = useful[useful["year"].between(2010, 2026)].copy()
    if len(current) < 50:
        current = useful.copy()
    current["satellite_operator"] = current["satellite_operator"].map(clean_category)
    current["satellite_users"] = current["satellite_users"].map(clean_category)

    selector_fig = go.Figure()
    selector_sources = [
        ("Propositos", "purpose_group", 12, "#2563eb"),
        ("Orbitas", "orbit_group", 12, "#f97316"),
        ("Operadores", "satellite_operator", 15, "#16a34a"),
    ]
    selector_annotations = []
    for idx, (label, col, top_n, color) in enumerate(selector_sources):
        counts = current[col].map(clean_category).value_counts().head(top_n).sort_values(ascending=True)
        pct = counts / len(current) * 100
        selector_fig.add_trace(go.Bar(x=counts.values, y=counts.index, orientation="h", name=label, visible=idx == 0, marker=dict(color=color), text=[f"{n} ({p:.1f}%)" for n, p in zip(counts.values, pct.values)], textposition="auto", hovertemplate="%{y}<br>Registros: %{x}<extra></extra>"))
        top_name = counts.index[-1] if len(counts) else "sin datos"
        top_pct = pct.iloc[-1] if len(pct) else 0
        selector_annotations.append(dict(x=0.01, y=1.12, xref="paper", yref="paper", text=f"Lectura: {top_name} concentra {top_pct:.1f}% del subconjunto reciente", showarrow=False, align="left", bgcolor="#eff6ff", bordercolor="#bfdbfe", font=dict(color="#1e3a8a")))
    selector_fig.update_layout(
        title="Selector de tendencias actuales - Propositos",
        xaxis=dict(title="Registros UCS enriquecidos"),
        annotations=[selector_annotations[0]],
        updatemenus=[{"type": "dropdown", "x": 1.02, "y": 1.12, "buttons": [{"label": label, "method": "update", "args": [{"visible": [i == idx for i in range(len(selector_sources))]}, {"title": f"Selector de tendencias actuales - {label}", "annotations": [selector_annotations[idx]]}]} for idx, (label, _, _, _) in enumerate(selector_sources)]}],
        showlegend=False,
    )

    matrix = current.groupby(["orbit_group", "purpose_group"]).size().reset_index(name="n")
    top_purposes = current["purpose_group"].value_counts().head(6).index
    matrix = matrix[matrix["purpose_group"].isin(top_purposes)]
    fig2 = px.bar(matrix, x="n", y="orbit_group", color="purpose_group", orientation="h", title="Orbita x uso: que se lanza y donde opera", color_discrete_sequence=PLOTLY_COLORWAY, text="n")
    fig2.update_layout(barmode="stack", xaxis_title="Registros", yaxis_title="Orbita")

    operator_data = current.copy()
    top_ops = operator_data["satellite_operator"].value_counts().head(10).index
    operator_data = operator_data[operator_data["satellite_operator"].isin(top_ops)]
    operator_counts = operator_data.groupby(["satellite_operator", "purpose_group"]).size().reset_index(name="n")
    fig3 = px.bar(operator_counts, x="n", y="satellite_operator", color="purpose_group", orientation="h", title="Top operadores recientes y usos que impulsan su presencia", color_discrete_sequence=PLOTLY_COLORWAY)
    fig3.update_yaxes(categoryorder="total ascending")
    fig3.update_layout(barmode="stack", xaxis_title="Registros", yaxis_title="Operador")
    top_purpose = useful["purpose_group"].value_counts().head(2).to_dict()
    obs = [f"Subconjunto enriquecido UCS usado: {len(enriched)} registros.", f"Propositos dominantes: {', '.join(top_purpose.keys())}.", "Estas visualizaciones representan tendencias actuales enriquecidas, no todos los lanzamientos historicos."]
    cards = [
        chart_card("1. Selector de tendencias mejorado", "Pregunta 5", "P5 Selector tendencias", fig_html(selector_fig, 540), ["Permite cambiar entre propositos, orbitas y operadores sin crear un dashboard.", "Incluye porcentajes y lectura automatica para que no sea solo una lista."], ["Depende del subconjunto enriquecido UCS.", "No muestra relaciones entre categorias."], obs, scores),
        chart_card("2. Orbita x uso", "Pregunta 5", "P5 Matriz orbita uso", fig_html(fig2, 470), ["Sustituye al sunburst con una lectura mas directa.", "Responde que usos dominan en cada tipo de orbita."], ["No muestra operadores.", "Agrupa propositos minoritarios."], obs, scores),
        chart_card("3. Operadores x uso", "Pregunta 5", "P5 Operadores usos", fig_html(fig3, 520), ["Muestra quienes tienen mas presencia y que usos explican esa presencia.", "Conecta economia orbital con actores concretos."], ["Depende de matches UCS.", "Los operadores con pocos satelites quedan fuera."], obs, scores),
    ]
    return question_section("Pregunta 5 - Tendencias actuales", "Que tendencias actuales observamos? Incluye clic en proposito, orbita y operador mediante interaccion Plotly.", cards)


def build_experiments(launch: pd.DataFrame, enriched: pd.DataFrame, scores: list[dict]) -> str:
    cards = []
    recent = launch[launch["year"].between(2020, 2026)].groupby("country").size().reset_index(name="n")
    fig4 = px.choropleth(recent, locations="country", locationmode="country names", color="n", hover_name="country", projection="orthographic", title="Globe / mapa interactivo 2020-2026", color_continuous_scale="Oranges")
    fig4.update_geos(showcountries=True, showcoastlines=False)
    cards.append(chart_card("1. Globe / mapa interactivo", "Experimentos", "EXP Globe mapa", fig_html(fig4), ["Aporta sensacion espacial y geografica.", "Util para portada o transicion visual."], ["No es el mejor para evolucion temporal.", "Puede sobrerrepresentar area geografica frente a lanzamientos."], ["Mantenerlo como recurso visual de apoyo, no como grafico principal."], scores))

    return question_section("EXPERIMENTOS", "Solo se conserva el recurso visual que aporta atmosfera sin confundir la narrativa principal.", cards)


def ranking_tables(scores: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.DataFrame(scores).sort_values("promedio", ascending=False)
    top_by_question = df[df["pregunta"].str.startswith("Pregunta")].sort_values(["pregunta", "promedio"], ascending=[True, False]).groupby("pregunta").head(3)
    return df, top_by_question


def table_html(df: pd.DataFrame) -> str:
    headers = "".join(f"<th>{esc(c)}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        rows.append("<tr>" + "".join(f"<td>{esc(v)}</td>" for v in row.tolist()) + "</tr>")
    return f"<div class='table-responsive'><table class='table table-striped table-hover'><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"


def final_recommendation(top: pd.DataFrame) -> str:
    selected = {}
    for question, group in top.groupby("pregunta"):
        selected[question] = group.iloc[0]["grafico"]
    items = "".join(f"<li><strong>{esc(q)}:</strong> {esc(g)}</li>" for q, g in selected.items())
    return f"""
    <div class="recommendation">
      <h3>Propuesta automatica</h3>
      <p>Si hubiera que construir la visualizacion definitiva hoy, estos serian los graficos seleccionados:</p>
      <ul>{items}</ul>
      <p>Lectura global: cronologia narrativa y promedio por etapas para evolucion, area de actores, cinta de liderazgo, ranking interactivo y mapa para liderazgo, area 100%, aviso de Unknown y slope publico/privado para el cambio de modelo, linea de fiabilidad con volumen para exito y selector/matrices simples para tendencias UCS actuales.</p>
    </div>
    """


def build_html() -> str:
    df, launch, enriched = load_data()
    scores: list[dict] = []
    sections = [
        build_q1(launch, scores),
        build_q2(launch, scores),
        build_q3(launch, scores),
        build_q4(launch, scores),
        build_q5(enriched, scores),
        build_experiments(launch, enriched, scores),
    ]
    ranking, top = ranking_tables(scores)
    nav = [
        ("Pregunta 1", "pregunta-1-evolucion-de-lanzamientos"),
        ("Pregunta 2", "pregunta-2-liderazgo-de-actores"),
        ("Pregunta 3", "pregunta-3-equilibrio-publico-privado"),
        ("Pregunta 4", "pregunta-4-tasa-de-exito"),
        ("Pregunta 5", "pregunta-5-tendencias-actuales"),
        ("Experimentos", "experimentos"),
        ("Ranking final", "ranking-final"),
    ]
    nav_html = "".join(f"<a href='#{sid}'>{esc(label)}</a>" for label, sid in nav)
    plotly_js = get_plotlyjs()
    dataset_summary = {
        "Registros totales": f"{len(df):,}",
        "Registros para conteo historico": f"{len(launch):,}",
        "Cobertura": f"{int(launch['year'].min())}-{int(launch['year'].max())}",
        "Registros enriquecidos UCS": f"{len(enriched):,}",
    }
    summary_cards = "".join(f"<div class='metric'><span>{esc(k)}</span><strong>{esc(v)}</strong></div>" for k, v in dataset_summary.items())
    css = """
    :root{--bg:#f3f6fb;--panel:#fff;--ink:#172033;--muted:#64748b;--line:#e2e8f0;--brand:#142c61;--accent:#f97316;--ok:#0f766e}
    *{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,Segoe UI,Arial,sans-serif;line-height:1.55}.layout{display:flex}.sidebar{position:fixed;left:0;top:0;bottom:0;width:280px;background:#0f172a;color:white;padding:24px 18px;overflow:auto}.sidebar h1{font-size:20px;margin:0 0 8px}.sidebar p{font-size:13px;color:#cbd5e1}.sidebar a{display:block;color:#e2e8f0;text-decoration:none;padding:10px 12px;border-radius:10px;margin:4px 0}.sidebar a:hover{background:#1e293b}.content{margin-left:280px;width:calc(100% - 280px);padding:28px}.hero{background:linear-gradient(135deg,#102a5c,#0f766e);color:white;border-radius:24px;padding:34px;margin-bottom:24px;box-shadow:0 18px 45px rgba(15,23,42,.2)}.hero h1{font-size:34px;margin:0 0 10px}.hero p{max-width:920px;color:#dbeafe}.metric-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-top:22px}.metric{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);border-radius:16px;padding:14px}.metric span{display:block;font-size:12px;text-transform:uppercase;color:#bfdbfe}.metric strong{font-size:22px}.question-section{margin-bottom:34px}.section-title{background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:22px;margin-bottom:18px}.section-title p{margin:0;color:var(--muted);text-transform:uppercase;font-size:12px;letter-spacing:.08em}.section-title h2{margin:6px 0 0;font-size:27px;color:var(--brand)}.chart-card{background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:20px;margin-bottom:22px;box-shadow:0 8px 24px rgba(15,23,42,.05)}.chart-head{display:flex;justify-content:space-between;align-items:center;gap:16px}.chart-head h3{margin:0;font-size:22px}.badge-score{background:#ecfeff;color:#0f766e;border:1px solid #99f6e4;border-radius:999px;padding:6px 12px;font-weight:800}.chart-box{margin-top:12px;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:white}.evaluation-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:16px}.evaluation-grid div{background:#f8fafc;border:1px solid var(--line);border-radius:14px;padding:13px}.evaluation-grid h4{margin:0 0 8px;color:#334155}.evaluation-grid ul{margin:0;padding-left:18px}.score-row{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-top:14px}.score-pill{display:flex;gap:8px;align-items:center;background:#eef2ff;border:1px solid #c7d2fe;border-radius:999px;padding:7px 10px;font-size:13px}.score-pill span{color:#475569}.score-total{background:#fff7ed;color:#9a3412;border:1px solid #fed7aa;border-radius:999px;padding:8px 12px;font-weight:900}.ranking-section{background:var(--panel);border:1px solid var(--line);border-radius:20px;padding:24px;margin-bottom:28px}.table-responsive{overflow:auto;border:1px solid var(--line);border-radius:14px}table{border-collapse:collapse;width:100%;background:white;font-size:13px}th,td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{background:#eef2ff}.recommendation{background:#ecfdf5;border:1px solid #99f6e4;border-radius:18px;padding:18px;margin-top:20px}.footer{text-align:center;color:var(--muted);margin:26px 0}@media(max-width:900px){.layout{display:block}.sidebar{position:relative;width:100%;height:auto}.content{margin-left:0;width:100%;padding:14px}.hero h1{font-size:26px}}
    """
    return f"""<!doctype html>
    <html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Exploracion de visualizaciones - Actividad espacial</title><style>{css}</style><script>{plotly_js}</script></head>
    <body><div class="layout"><aside class="sidebar"><h1>Galeria visual</h1><p>Prototipos para comparar alternativas antes del scrollytelling final.</p>{nav_html}</aside>
    <main class="content"><header class="hero"><h1>Exploracion visual del dataset espacial definitivo</h1><p>Galeria de prototipos conectados al dataset real. No es el diseno final: es una mesa de pruebas para evaluar claridad, narrativa, densidad, estetica y adecuacion a cada pregunta de investigacion.</p><div class="metric-row">{summary_cards}</div></header>
    {''.join(sections)}
    <section class="ranking-section" id="ranking-final"><h2>Ranking final</h2><h3>TOP 3 graficos recomendados por pregunta</h3>{table_html(top[['pregunta','grafico','claridad','capacidad narrativa','densidad informacion','estetica','adecuacion','promedio']])}<h3>Ranking global de prototipos</h3>{table_html(ranking[['pregunta','grafico','claridad','capacidad narrativa','densidad informacion','estetica','adecuacion','promedio']])}{final_recommendation(top)}</section>
    <div class="footer">HTML local unico generado con Python, Plotly embebido y estilos tipo Bootstrap.</div></main></div></body></html>"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_html(), encoding="utf-8")
    print(f"HTML generado: {OUT}")


if __name__ == "__main__":
    main()
