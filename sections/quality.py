"""Part 3: data quality."""
import pandas as pd
import streamlit as st


def _n(x):
    return f"{x:,}"


def render(df, q):
    st.header("3. Can we trust the data?")
    c = st.columns(4)
    c[0].metric("Rows at the start", _n(q["rows_raw"]))
    c[1].metric("Duplicates removed", _n(q["duplicates"]), f"{q['duplicates'] / q['rows_raw']:.1%} of the file", delta_color="off")
    c[2].metric("Dates fixed", _n(q["shifted_timestamps"]), help="Dates at 01:00 or 02:00 put back to midnight.")
    c[3].metric("Rows kept", _n(q["rows_clean"]))

    st.subheader("Missing values")
    miss = pd.Series(q["missing_pct"], name="% missing").rename_axis("column").reset_index()
    miss = miss[miss["% missing"] > 0].sort_values("% missing", ascending=False)
    st.dataframe(miss, hide_index=True, column_config={
        "% missing": st.column_config.ProgressColumn("% missing", min_value=0, max_value=100, format="%.1f %%")})
    st.caption("The columns EPT, PETR and PNR do not apply to every commune, so it is normal that they are empty.")

    st.subheader("Checks I did")
    rga = q.get("rga_event_years")
    storms = df.loc[df["type"] == "Cyclones / Storms", "year"]
    if len(storms):
        storm_text = (f"{(storms <= 1989).mean():.0%} of its rows are from 1982-1989 and only {int((storms > 1989).sum()):,} after: "
                      "later storms are probably recorded under other categories")
    else:
        storm_text = "no rows"
    checks = pd.DataFrame([
        ("No header in the file", "I named the columns using the documentation", "fixed"),
        ("Duplicates (same commune, peril, dates and decree)", f"{_n(q['duplicates'])} rows removed", "fixed"),
        ("Dates at 01:00 or 02:00", f"{_n(q['shifted_timestamps'])} put back to midnight (this is an assumption: probably a time shift at export)", "assumption"),
        ("Overseas region codes without a leading zero", f"{_n(q['unpadded_region_codes'])} completed", "fixed"),
        ("Decree taken before the end of the event", f"{q['arrete_before_end']} rows, I kept them", "to note"),
        ("End before start", f"{q['fin_before_debut']} row(s)", "ok" if q["fin_before_debut"] == 0 else "to note"),
        ("Events longer than 365 days", f"{_n(q['long_events'])} rows, up to {_n(q['max_duration'])} days (maybe droughts over several years)", "to note"),
        ("Category \"Cyclones / Storms\"", storm_text, "to note"),
        ("Recent years", f"after {q['last_reliable_year']}, the data is not complete", "to note"),
        ("Category \"Clay shrink-swell\"",
         (f"{_n(q['rga_rows'])} rows, events from {rga[0]} to {rga[1]}, all decreed in {q['rga_arrete_years'][0]}: "
          "it looks like a reclassification of drought (you can merge them with the checkbox on the left)") if rga else "-",
         "to note"),
    ], columns=["Check", "Result", "Status"])
    st.dataframe(checks, hide_index=True, width="stretch")

    with st.expander("Limits of the analysis"):
        st.write(
            """
- A decree is not a measure of the phenomenon: the rules to be recognised change (for example for drought and clay),
  so an increase can come from the procedure and not from the climate.
- I do not say that climate change explains these numbers. This project describes the data, it does not prove that.
- Counting communes gives the same weight to a small village and to a big city.
- Overseas territories are in the numbers but not on the map (the background map only has mainland France).
"""
        )
