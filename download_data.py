"""Downloads the CatNat CSV and the departments GeoJSON into data/ (cached).

Usage: python download_data.py [--force]
"""
import sys

from utils.io import CSV_PATH, GEOJSON_PATH, ensure_csv, ensure_geojson, resolve_csv_url

if __name__ == "__main__":
    if "--force" in sys.argv:
        CSV_PATH.unlink(missing_ok=True)
        GEOJSON_PATH.unlink(missing_ok=True)
    print("CSV:", resolve_csv_url())
    print("->", ensure_csv())
    print("->", ensure_geojson())
