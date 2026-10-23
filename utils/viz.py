"""Plotly figures: colour-blind friendly palette (Okabe-Ito), titled axes with units, detailed hover."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.io import SEEDS
from utils.prep import MONTHS

PERIL_COLORS = SEEDS["peril_colors"]
FONT = dict(family="Inter, Segoe UI, Arial, sans-serif", size=14)
SEQ = "Magma"


def _base(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(font=FONT, height=height, margin=dict(l=10, r=10, t=40, b=10),
                      legend=dict(title=None, orientation="h", y=-0.2),
                      hoverlabel=dict(font_size=13), template="plotly_dark",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def show(fig: go.Figure, alt: str, key: str) -> None:
    """Shows the figure and a text description under it (accessibility)."""
    st.plotly_chart(fig, width="stretch", key=key, config={"displaylogo": False})
    st.caption(f"Chart description: {alt}")


def trend_by_peril(g: pd.DataFrame, last_reliable: int, log_y: bool = False) -> go.Figure:
    fig = px.bar(g, x="year", y="communes", color="type", color_discrete_map=PERIL_COLORS,
                 labels={"year": "Year the event started", "communes": "Communes hit (distinct count)",
                         "type": "Peril"},
                 title="Communes hit per year and per peril")
    fig.update_traces(hovertemplate="%{x} - %{fullData.name}<br><b>%{y:,}</b> communes<extra></extra>")
    if not g.empty and g["year"].max() > last_reliable:
        fig.add_vrect(x0=last_reliable + 0.5, x1=g["year"].max() + 0.5, fillcolor="grey", opacity=0.18,
                      line_width=0, annotation_text="incomplete years", annotation_position="top left")
    fig.update_layout(barmode="stack", xaxis=dict(dtick=2))
    # label the 3 highest years (annotations on a log axis use log10 values)
    for year, total in g.groupby("year")["communes"].sum().nlargest(3).items():
        fig.add_annotation(x=year, y=np.log10(total) if log_y else total, text=f"{year}: {total:,}",
                           showarrow=True, arrowhead=2, ax=0, ay=-28, font=dict(size=12))
    if log_y:
        fig.update_yaxes(type="log", title="Communes hit (log scale)")
    return _base(fig)


def dep_map(g: pd.DataFrame, geojson: dict, metric: str, label: str) -> go.Figure:
    """Choropleth map without an external tile background (works offline)."""
    fig = px.choropleth(
        g, geojson=geojson, locations="code_dep", featureidkey="properties.code", color=metric,
        color_continuous_scale=SEQ, hover_name="dep",
        hover_data={"code_dep": False, "arretes": ":,", "evenements": ":,", "communes": ":,",
                    "arretes_par_commune": ":.1f"},
        labels={"arretes": "Decrees (commune level)", "evenements": "Events", "communes": "Communes hit",
                "arretes_par_commune": "Decrees per commune", metric: label})
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_traces(marker_line_color="white", marker_line_width=0.5)
    fig.update_layout(coloraxis_colorbar=dict(title=label, thickness=14))
    return _base(fig, 560)


def peril_small_multiples(g: pd.DataFrame) -> go.Figure:
    top = g.groupby("type", observed=True)["communes"].sum().sort_values(ascending=False).index.tolist()
    fig = px.line(g, x="year", y="communes", facet_col="type", facet_col_wrap=3, color="type",
                  color_discrete_map=PERIL_COLORS, category_orders={"type": top},
                  labels={"year": "Year", "communes": "Communes hit"},
                  title="Evolution by peril (each chart has its own scale)")
    fig.update_yaxes(matches=None, showticklabels=True)
    fig.update_xaxes(dtick=10)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_traces(hovertemplate="%{x}: <b>%{y:,}</b> communes<extra></extra>")
    fig.update_layout(showlegend=False)
    return _base(fig, 620)


def region_bars(g: pd.DataFrame) -> go.Figure:
    order = g.groupby("region", observed=True)["communes"].sum().sort_values().index.tolist()
    fig = px.bar(g, y="region", x="communes", color="type", orientation="h", color_discrete_map=PERIL_COLORS,
                 category_orders={"region": order},
                 labels={"region": "Region", "communes": "Communes hit (sum over perils)", "type": "Peril"},
                 title="Communes hit per region and per peril")
    fig.update_traces(hovertemplate="%{y} - %{fullData.name}<br><b>%{x:,}</b> communes<extra></extra>")
    fig.update_layout(barmode="stack")
    return _base(fig, 520)


def season_heatmap(g: pd.DataFrame) -> go.Figure:
    pv = (g.pivot_table(index="type", columns="month", values="evenements", aggfunc="sum", observed=True)
            .reindex(columns=range(1, 13)).fillna(0))
    fig = go.Figure(go.Heatmap(
        z=pv.values, x=MONTHS, y=pv.index.astype(str), colorscale=SEQ,
        colorbar=dict(title="Events", thickness=14),
        hovertemplate="%{y} - %{x}<br><b>%{z:,.0f}</b> events<extra></extra>"))
    fig.update_layout(title="Start month of the events, per peril",
                      xaxis_title="Month the event started", yaxis_title="Peril")
    return _base(fig, 380)


def delay_ecdf(d: pd.DataFrame) -> go.Figure:
    fig = px.ecdf(d, x="delay_days", color="type", color_discrete_map=PERIL_COLORS, log_x=True,
                  labels={"delay_days": "Days between the end of the event and the decree (log scale)",
                          "type": "Peril", "y": "Cumulative share of events"},
                  title="How long before the decree is published?")
    fig.update_yaxes(tickformat=".0%", title="Cumulative share of events")
    fig.update_traces(hovertemplate="within %{x:,} days: <b>%{y:.0%}</b> of events<extra></extra>")
    return _base(fig)
