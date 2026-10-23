"""Cleaning, quality checks and pre-aggregations (pure functions, so they can be tested)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from utils.io import SEEDS, load_raw

REGION_NAMES = SEEDS["region_names"]
PERIL_NAMES = SEEDS["peril_names"]
LAG = SEEDS["reliability_lag_years"]
LONG_DAYS = SEEDS["long_event_days"]
DUP_KEY = ["code_commune", "type", "debut", "fin", "arrete"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
RGA = PERIL_NAMES["Retrait-gonflement des argiles"]
DROUGHT = PERIL_NAMES["Sécheresse"]


def _fix_shifted_midnight(s: pd.Series) -> tuple[pd.Series, int]:
    """Timestamps at 01:00 or 02:00 are shifted midnights (time zone / daylight saving problem at export).

    I checked this on the data: after rounding to the next midnight, 100% of the values are at 00:00
    and quarter ends fall on the 30th/31st (not the 29th/30th). Returns (fixed series, number fixed).
    """
    t = pd.to_datetime(s, errors="coerce")
    shifted = t.dt.hour.isin([1, 2])
    fixed = t.where(~shifted, t.dt.normalize() + pd.Timedelta(days=1))
    return fixed.dt.normalize(), int(shifted.sum())


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Returns (clean table, quality report). Every step is counted."""
    q: dict = {"rows_raw": len(raw)}
    df = raw.copy()

    # 1. Exact duplicates (same commune + same decree + same dates + same peril)
    dup = df.duplicated(subset=DUP_KEY, keep="first")
    q["duplicates"] = int(dup.sum())
    df = df.loc[~dup].copy()

    # 2. Dates: shifted timestamps -> midnight
    shifted_total = 0
    for c in ["debut", "fin", "arrete"]:
        df[c], n = _fix_shifted_midnight(df[c])
        shifted_total += n
    q["shifted_timestamps"] = shifted_total
    q["unparseable_dates"] = int(df[["debut", "fin", "arrete"]].isna().any(axis=1).sum())
    df = df.dropna(subset=["debut", "fin", "arrete"])

    # 3. Codes: region on 2 characters (overseas codes come without the leading zero)
    padded = (df["code_reg"].str.len() < 2).sum()
    q["unpadded_region_codes"] = int(padded)
    df["code_reg"] = df["code_reg"].str.zfill(2)
    df["region"] = df["code_reg"].map(REGION_NAMES).fillna("Unknown")
    df["is_drom"] = df["code_dep"].str.len() == 3

    # 4. Derived variables
    df["year"] = df["debut"].dt.year.astype("int16")
    df["year_arrete"] = df["arrete"].dt.year.astype("int16")
    df["month"] = df["debut"].dt.month.astype("int8")
    df["duration_days"] = (df["fin"] - df["debut"]).dt.days + 1
    df["delay_days"] = (df["arrete"] - df["fin"]).dt.days
    df["event_id"] = pd.factorize(pd.MultiIndex.from_frame(df[["type", "debut", "fin", "arrete"]]))[0].astype("int32")

    # 5. Consistency checks (we flag them, we don't delete)
    q["arrete_before_end"] = int((df["delay_days"] < 0).sum())
    q["fin_before_debut"] = int((df["fin"] < df["debut"]).sum())
    q["long_events"] = int((df["duration_days"] > LONG_DAYS).sum())
    q["max_duration"] = int(df["duration_days"].max())

    # English peril names, plus a version where "Clay shrink-swell" (category that appears in 2022) is merged into "Drought"
    df["type"] = df["type"].replace(PERIL_NAMES)
    df["type_merged"] = df["type"].replace({RGA: DROUGHT})

    for c in ["type", "type_merged", "region", "dep", "code_dep", "code_reg"]:
        df[c] = df[c].astype("category")

    keep = ["code_commune", "commune", "code_dep", "dep", "code_reg", "region", "is_drom", "type", "type_merged", "event_id",
            "debut", "fin", "arrete", "year", "year_arrete", "month", "duration_days", "delay_days"]
    df = df[keep].reset_index(drop=True)

    q["rows_clean"] = len(df)
    q["missing_pct"] = (raw.isna().mean() * 100).round(1).to_dict()
    q["last_arrete_year"] = int(df["year_arrete"].max())
    q["last_reliable_year"] = q["last_arrete_year"] - LAG
    q["first_year"] = int(df["year"].min())
    q["n_events"] = int(df["event_id"].nunique())
    q["n_communes"] = int(df["code_commune"].nunique())
    rga = df[df["type"] == RGA]
    q["rga_event_years"] = (int(rga["year"].min()), int(rga["year"].max())) if len(rga) else None
    q["rga_arrete_years"] = (int(rga["year_arrete"].min()), int(rga["year_arrete"].max())) if len(rga) else None
    q["rga_rows"] = len(rga)
    return df, q


@st.cache_data(show_spinner="Cleaning and aggregating the data...")
def get_data() -> tuple[pd.DataFrame, dict]:
    return clean(load_raw())


# ---------- Filters and aggregations (called with the sidebar choices) ----------

def peril_options(df: pd.DataFrame, merge_rga: bool) -> list[str]:
    col = "type_merged" if merge_rga else "type"
    return sorted(df[col].astype(str).unique())


def apply_filters(df: pd.DataFrame, years: tuple[int, int], perils: list[str], regions: list[str],
                  merge_rga: bool = True) -> pd.DataFrame:
    """Filters the table, then exposes the chosen peril column (raw or merged) as ``type``."""
    col = "type_merged" if merge_rga else "type"
    m = df["year"].between(years[0], years[1]) & df[col].isin(perils) & df["region"].isin(regions)
    f = df.loc[m]
    return f.assign(type=f[col]) if merge_rga else f


def kpis(f: pd.DataFrame) -> dict:
    if f.empty:
        return {k: 0 for k in ["rows", "events", "communes", "deps", "median_duration", "median_delay"]}
    return {
        "rows": len(f),
        "events": int(f["event_id"].nunique()),
        "communes": int(f["code_commune"].nunique()),
        "deps": int(f["code_dep"].nunique()),
        "median_duration": float(f["duration_days"].median()),
        "median_delay": float(f["delay_days"].median()),
    }


def by_year_peril(f: pd.DataFrame) -> pd.DataFrame:
    """Distinct communes hit per year and per peril."""
    return (f.groupby(["year", "type"], observed=True)["code_commune"].nunique()
              .rename("communes").reset_index())


def by_dep(f: pd.DataFrame) -> pd.DataFrame:
    g = f.groupby(["code_dep", "dep"], observed=True).agg(
        arretes=("event_id", "size"),
        evenements=("event_id", "nunique"),
        communes=("code_commune", "nunique"),
    ).reset_index()
    g["arretes_par_commune"] = (g["arretes"] / g["communes"]).round(2)
    g["code_dep"] = g["code_dep"].astype(str)
    g["dep"] = g["dep"].astype(str)
    return g[g["arretes"] > 0]


def by_region_peril(f: pd.DataFrame) -> pd.DataFrame:
    return (f.groupby(["region", "type"], observed=True)["code_commune"].nunique()
              .rename("communes").reset_index())


def month_peril(f: pd.DataFrame) -> pd.DataFrame:
    """Start month of the events (each event counted once)."""
    ev = f.drop_duplicates("event_id")
    g = ev.groupby(["month", "type"], observed=True).size().rename("evenements").reset_index()
    g["mois"] = g["month"].map(lambda m: MONTHS[m - 1])
    return g


def delay_sample(f: pd.DataFrame) -> pd.DataFrame:
    """One point per event (not per commune), so big events don't weigh more."""
    ev = f.drop_duplicates("event_id")
    return ev[ev["delay_days"] >= 0][["type", "delay_days"]]
