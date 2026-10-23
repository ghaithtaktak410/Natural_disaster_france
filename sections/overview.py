"""Part 1: key figures and evolution over time."""
import streamlit as st

from utils import prep, viz


def _fmt(n):
    return f"{n:,.0f}"


def render(f, q):
    st.header("1. Overview")
    k = prep.kpis(f)
    c = st.columns(5)
    c[0].metric("Decrees by commune", _fmt(k["rows"]), help="Number of rows in the register (one decree for one commune), without duplicates.")
    c[1].metric("Events", _fmt(k["events"]), help="Different events (same peril, same dates, same decree).")
    c[2].metric("Communes hit", _fmt(k["communes"]))
    c[3].metric("Median duration", f"{k['median_duration']:.0f} d", help="Between the start and the end of the event.")
    c[4].metric("Median delay", f"{k['median_delay']:.0f} d", help="Between the end of the event and the date of the decree.")

    if f.empty:
        st.warning("No data with these filters. Try widening the selection on the left.")
        return

    g = prep.by_year_peril(f)
    log_y = st.checkbox("Logarithmic scale", value=False,
                        help="A few years are huge and hide the others. With the log scale the smaller years are easier to see.")
    tot = g.groupby("year")["communes"].sum()
    top_years = [int(y) for y in tot.nlargest(3).index]
    alt = ("Stacked bar chart: number of communes hit each year, with one colour per peril. "
           f"The {len(top_years)} highest years are {', '.join(map(str, top_years))} (labelled on the chart). ")
    if tot.index.max() > q["last_reliable_year"]:
        alt += "The grey area on the right shows the years that are not complete yet."
    viz.show(viz.trend_by_peril(g, q["last_reliable_year"], log_y), alt, "trend")
    peak = int(tot.idxmax())
    top_peril = g.groupby("type", observed=True)["communes"].sum().idxmax()
    st.write(
        f"With the selected filters, the busiest year is {peak} ({_fmt(tot.max())} communes, all perils together) "
        f"and the peril that comes back the most is \"{top_peril}\"."
    )
    st.caption(
        f"Note: after {q['last_reliable_year']}, the numbers are too low, because decrees "
        "are published with a delay (sometimes several years)."
    )
