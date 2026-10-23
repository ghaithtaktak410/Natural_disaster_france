"""Part 4: what I take from this."""
import streamlit as st


def _peril_sentence(f):
    """Describes the two perils with the most decrees, using the filtered data."""
    g = f.groupby("type", observed=True).agg(rows=("event_id", "size"), events=("event_id", "nunique"))
    g = g[g["rows"] > 0].sort_values("rows", ascending=False).head(2)
    if g.empty:
        return "With the current filters there is no peril to compare."
    parts = [f"{name} ({int(r.rows):,} decrees by commune for {int(r.events):,} events, "
             f"about {r.rows / r.events:.0f} communes per event)" for name, r in g.iterrows()]
    return "With the selected filters, the perils with the most decrees are " + " and ".join(parts) + "."


def render(f, q):
    st.header("4. What I take from this")
    rga_year = q["rga_arrete_years"][0] if q["rga_arrete_years"] else "recent years"
    st.write(
        f"""
1. The register shows which disasters were **recognised** by the State, not necessarily which ones caused the most damage.
2. {_peril_sentence(f)} A high number of communes per event means the peril hits a lot of communes at once.
3. The number of decrees per commune is more useful than the total to find places that were hit several times.
4. We should not rely on the last years: after {q['last_reliable_year']}, the numbers are still incomplete.

**To go further**, we could:
- divide by the population or the area of the communes to compare more fairly;
- cross the data with Météo-France or Géorisques data to separate the phenomenon from the procedure;
- look at the effect of the rule change on clay (all its decrees were taken in {rga_year}).
"""
    )
    st.caption("Source: [Arrêtés de catastrophe naturelle par commune](https://www.data.gouv.fr/datasets/arretes-de-catastrophe-naturelle-par-commune), "
               f"data.gouv.fr, Licence Ouverte 2.0. Last decree in the file: {q['last_arrete_year']}.")
