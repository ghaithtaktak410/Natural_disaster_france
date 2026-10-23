"""Part 2: map, comparisons, seasons and delays."""
import streamlit as st

from utils import prep, viz
from utils.io import load_geojson


def render(f, q):
    st.header("2. A closer look")
    if f.empty:
        st.warning("No data with these filters.")
        return
    t_map, t_cmp, t_season, t_delay = st.tabs(["Map", "Comparisons", "Seasons", "Delays"])

    with t_map:
        labels = {
            "communes": "Communes hit",
            "arretes_par_commune": "Decrees per commune hit",
            "evenements": "Different events",
        }
        metric = st.radio("What to show", list(labels), format_func=labels.get, horizontal=True, key="map_metric")
        g = prep.by_dep(f)
        geo = load_geojson()
        if geo is None:
            st.warning("The background map could not be downloaded. Here is a table instead.")
            st.dataframe(g.sort_values(metric, ascending=False), hide_index=True)
        else:
            viz.show(
                viz.dep_map(g[~g["code_dep"].str.len().eq(3)], geo, metric, labels[metric]),
                f"Map of the departments of mainland France coloured by \"{labels[metric]}\". "
                "The darker the colour, the higher the value.",
                "map",
            )
            drom = g[g["code_dep"].str.len().eq(3)]
            if not drom.empty:
                st.caption("Overseas departments (not on the map):")
                st.dataframe(drom[["dep", "arretes", "evenements", "communes"]].rename(columns={
                    "dep": "Department", "arretes": "Decrees by commune", "evenements": "Events",
                    "communes": "Communes"}), hide_index=True)
        st.caption("The number of communes depends on the size of the department (a big department has more communes). "
                   "The number of decrees per commune shows better the places that were hit several times.")

    with t_cmp:
        viz.show(viz.region_bars(prep.by_region_peril(f)),
                 "Horizontal bars: number of communes hit per region, with one colour per peril. Regions are sorted from the least to the most hit.",
                 "regions")
        viz.show(viz.peril_small_multiples(prep.by_year_peril(f)),
                 "One small line chart per peril, with the number of communes hit each year. Each chart has its own scale.",
                 "small")

    with t_season:
        viz.show(viz.season_heatmap(prep.month_peril(f)),
                 "Coloured table: one row per peril, one column per start month. The darker the cell, the more events start that month.",
                 "season")
        st.caption("Each event is counted once, even if it hits many communes.")

    with t_delay:
        d = prep.delay_sample(f)
        if d.empty:
            st.info("Cannot compute a delay with these filters.")
        else:
            viz.show(viz.delay_ecdf(d),
                     "Cumulative curves: for each peril, the share of events recognised in less than N days (log scale).",
                     "delay")
            med = d.groupby("type", observed=True)["delay_days"].median().sort_values()
            st.caption("Median delay in days: " + " / ".join(f"{k} {v:.0f}" for k, v in med.items()))
