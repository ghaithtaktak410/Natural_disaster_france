"""Streamlit - Natural disasters in France (CatNat). Run with: streamlit run app.py"""
import streamlit as st

st.set_page_config(page_title="Natural disasters in France", layout="wide")

# small style tweaks: serif titles and bordered key figures
st.markdown(
    """
<style>
h1, h2, h3 { font-family: Georgia, "Times New Roman", serif; font-weight: 700; }
h2 { border-bottom: 2px solid #f2a541; padding-bottom: 0.3rem; margin-top: 2.5rem; }
[data-testid="stSidebar"] { border-right: 2px solid #f2a541; }
[data-testid="stMetric"] { border: 1px solid #3a4a73; border-radius: 6px; padding: 0.7rem 0.9rem; }
</style>
""",
    unsafe_allow_html=True,
)

from sections import conclusions, deep_dives, intro, overview, quality  # noqa: E402
from utils import prep  # noqa: E402

try:
    df, q = prep.get_data()
except Exception as e:  # no network / file missing
    st.error("Could not load the data. Run `python download_data.py` first (or set `CATNAT_CSV_PATH`).")
    st.exception(e)
    st.stop()

# ---------------- Sidebar: filters ----------------
st.sidebar.header("Filters")
y_min, y_max = q["first_year"], int(df["year"].max())
years = st.sidebar.slider("Years", y_min, y_max, (y_min, q["last_reliable_year"]),
                          help=f"After {q['last_reliable_year']}, the data is incomplete.")
merge = st.sidebar.checkbox("Merge \"clay shrink-swell\" with \"drought\"", value=True)
options = prep.peril_options(df, merge)
with st.sidebar.expander("Perils", expanded=False):
    perils = st.multiselect("Perils", options, default=options, label_visibility="collapsed")
region_opts = sorted(df["region"].astype(str).unique())
with st.sidebar.expander("Regions", expanded=False):
    regions = st.multiselect("Regions", region_opts, default=region_opts, label_visibility="collapsed")
st.sidebar.caption("These filters apply to the whole page.")

f = prep.apply_filters(df, years, perils, regions, merge)

intro.render(df, q)
overview.render(f, q)
deep_dives.render(f, q)
quality.render(df, q)
conclusions.render(f, q)
