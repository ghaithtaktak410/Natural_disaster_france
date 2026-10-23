# Natural disasters in France

Individual Streamlit project - EFREI Paris, ING2 (BI).
Dashboard about the register of natural disaster decrees (CatNat) by commune.

- Live app: https://naturaldisasterfrance-p538qmksbdekehzehkbtfu.streamlit.app/
- Demo video (2 to 4 min): https://drive.google.com/file/d/1OmwupzaSTBW8osDAC4wyL6sTRJUR1edl/view?usp=sharing
- GitHub repository: https://github.com/ghaithtaktak410/Natural_disaster_france

## Data

- Title: Arrêtés de catastrophe naturelle par commune (GASPAR database)
- Publisher on data.gouv.fr: TACCT (data from the GASPAR database of the French Ministry of Ecological Transition)
- Dataset link: https://www.data.gouv.fr/datasets/arretes-de-catastrophe-naturelle-par-commune
- File: `catnat.csv` (about 50 MB, 260,000 rows, `;` separator, no header)
- Version used: last update on data.gouv.fr on 20 July 2026 (updated once a year)
- Licence: Licence Ouverte / Open Licence version 2.0 (code `lov2` in the data.gouv.fr API, checked on 23 October 2026). The code of this project is separate from the data.
- Background map: departments GeoJSON (`gregoiredavid/france-geojson`), downloaded automatically

The raw file is not in the zip: it is downloaded the first time the app runs, into the `data/` folder.
The peril names in the file are in French, I translated them to English in the code (see `peril_names` in `seeds.json`).

## Run the project

Python 3.11 or higher is needed.

```bash
python -m venv .venv
.venv\Scripts\activate        # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python download_data.py       # optional, the app downloads the file by itself if needed
streamlit run app.py
```

There is also a Makefile (`make install`, `make data`, `make run`, `make test`).
To use a local file, set the `CATNAT_CSV_PATH` variable.

## Code organisation

```
app.py            main page: filters + order of the parts
sections/         intro, overview (key figures), deep_dives (map, comparisons...),
                  quality (data quality), conclusions
utils/io.py       downloading and reading the file
utils/prep.py     cleaning, checks, calculations
utils/viz.py      Plotly charts
seeds.json        constants (URLs, region names, peril names, colours...)
tests/            tests for the cleaning
storyboard.md     story plan and video script
```

## The story

1. Introduction: almost every commune is in the register, but one row = one decree for one commune.
2. Overview: key figures and evolution by peril.
3. Details: map by department, regions, seasons, delays before recognition.
4. Data quality: duplicates, shifted dates, incomplete years.
5. Conclusion: what we can say and what we cannot say.

## Data cleaning

- No header in the file: I named the columns using the documentation.
- 15,462 duplicates removed (same commune, peril, dates and decree).
- About 51,000 dates at 01:00 or 02:00: I put them back to midnight. This is an assumption (time shift at export), but after the fix all dates are at 00:00.
- Overseas region codes without a leading zero: completed.
- The category "clay shrink-swell" (decrees taken in 2022 for events from 2017 to 2021) can be merged with drought.
- The last years are incomplete, so the default range stops 2 years before the last decree.
- Overseas territories are not on the map (mainland background map), so I put them in a table.

## Performance, accessibility, limits

- `st.cache_data` on reading and cleaning the file.
- Colours adapted to colour blindness, axes with titles and units, a written description under each chart.
- I do not claim any cause: a decree is an administrative decision, not a measure of the phenomenon.
- The numbers can change if the file is updated on data.gouv.fr.
