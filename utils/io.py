"""Getting the data: download with a local cache, then reading the raw CSV.

The raw file (~50 MB) is NOT in the zip: it is downloaded from data.gouv.fr the first time
and kept in ``data/`` (cache). See ``download_data.py``.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SEEDS = json.loads((ROOT / "seeds.json").read_text(encoding="utf-8"))

COLUMNS = SEEDS["columns"]
DATASET_API = SEEDS["dataset_api"]
FALLBACK_CSV_URL = SEEDS["fallback_csv_url"]
GEOJSON_URL = SEEDS["geojson_url"]
CSV_PATH = DATA_DIR / "catnat.csv"
GEOJSON_PATH = DATA_DIR / "departements.geojson"
TIMEOUT = 60


def _download(url: str, dest: Path) -> None:
    """Downloads ``url`` to ``dest`` safely (temporary file, then rename)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()
        fd, tmp = tempfile.mkstemp(dir=dest.parent, suffix=".part")
        with os.fdopen(fd, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    os.replace(tmp, dest)


def resolve_csv_url() -> str:
    """Looks for the latest CSV URL with the data.gouv.fr API (fallback: a fixed URL)."""
    try:
        meta = requests.get(DATASET_API, timeout=TIMEOUT).json()
        for res in meta.get("resources", []):
            if str(res.get("title", "")).lower().endswith("catnat.csv") or res.get("format") == "csv":
                if res.get("url"):
                    return res["url"]
    except Exception:  # network problem or unexpected format: use the fallback URL
        pass
    return FALLBACK_CSV_URL


def ensure_csv() -> Path:
    """Returns the CSV path: environment variable > local cache > download."""
    env = os.environ.get("CATNAT_CSV_PATH")
    if env and Path(env).exists():
        return Path(env)
    if not CSV_PATH.exists():
        _download(resolve_csv_url(), CSV_PATH)
    return CSV_PATH


def ensure_geojson() -> Path:
    if not GEOJSON_PATH.exists():
        _download(GEOJSON_URL, GEOJSON_PATH)
    return GEOJSON_PATH


@st.cache_data(show_spinner="Reading the CatNat file...")
def load_raw() -> pd.DataFrame:
    """Raw CSV: separator ';', **no header**, everything read as text (no silent conversion)."""
    return pd.read_csv(ensure_csv(), sep=";", header=None, names=COLUMNS, dtype=str)


@st.cache_data(show_spinner=False)
def load_geojson() -> dict | None:
    try:
        return json.loads(ensure_geojson().read_text(encoding="utf-8"))
    except Exception:
        return None  # the map is optional: the app still works without it
