# Storyboard - Natural disasters in France (CatNat)

## 1. The story in short

- **Topic:** the register of natural disaster decrees ("CatNat") by commune, 1982 to today (data.gouv.fr, GASPAR database).
- **Audience:** anyone who has heard about "natural disaster decrees" in the news and wonders what the numbers really mean. No technical background needed.
- **Starting question:** almost every commune in France is in the register. Does that mean the whole country is exposed?
- **Main message:** a decree is an administrative decision, not a measure of the disaster. The register says what the State recognised, not what hurt the most.
- **Tone:** first person, simple words, one idea per chart.

## 2. Narrative arc

| Step | Where in the app | What the user learns |
|---|---|---|
| Hook | Introduction | 34,598 communes are in the register (99% of France), but one row is one decree for one commune, not one disaster |
| Context | 1. Overview | How many decrees and events, which perils, which years stand out, and that recent years are incomplete |
| Key insights | 2. A closer look | Where (map, regions), when (seasons), how long before a decree (delays) |
| Trust | 3. Can we trust the data? | Duplicates, shifted dates, incomplete years, category problems |
| Implications | 4. What I take from this | What we can say, what we cannot say, how to go further |

## 3. Screen by screen

**Sidebar (always visible, left).** Years slider, checkbox to merge "clay shrink-swell" with "drought", Perils and Regions menus. Every key figure and chart follows these filters.

### Introduction
- **Headline:** "Almost every commune is in the register. What does that really mean?"
- **Visual:** text only, plus the audience sentence.
- **Takeaway:** the unit of the data is "one decree for one commune".

### 1. Overview
- **Headline:** "A few years dominate, and the last years are not complete."
- **Visuals:**
  - 5 key figures: decrees by commune (241,337), events (18,380), communes hit (34,580), median duration (5 d), median delay (31 d).
  - Stacked bars: communes hit per year and per peril, with the 3 highest years labelled (1999: 54,147, 1982: 30,206, 1983: 13,180) and a grey area for incomplete years.
- **Interactions:** logarithmic scale (small years become visible), years slider, peril filter, merge checkbox, hover on bars.
- **Takeaway:** the register is dominated by a few exceptional years; after the last reliable year the numbers are too low because decrees are published late.

### 2. A closer look
- **Map (departments).**
  - Headline: "Where? It depends on what we count."
  - Three indicators: communes hit, decrees per commune hit, different events.
  - Takeaway: counting communes favours departments with many communes (Pas-de-Calais, 887), while decrees per commune shows repetition (Alpes-Maritimes, about 16). Overseas departments are in a table because the background map only has mainland France.
- **Comparisons.**
  - Headline: "Which regions, which perils?"
  - Stacked horizontal bars by region (Occitanie 15,245 and Nouvelle-Aquitaine 15,179 on top), then one small line chart per peril, each with its own scale.
  - Takeaway: compare the shape of each peril over time, not the height of the curves.
- **Seasons.**
  - Headline: "When do events start?"
  - Heatmap month x peril. Floods start mostly in May and June; drought starts mostly in January, probably because drought decrees cover long periods (assumption).
- **Delays.**
  - Headline: "How long before the decree?"
  - Cumulative curves per peril, log scale, one point per event. Median delays: hail/snow 58 d, storms 79 d, floods 132 d, ground movements 187 d, drought 363 d.
  - Takeaway: the wait depends a lot on the peril. This is different from the key figure at the top (31 d), which counts every commune row, so big and fast events weigh more.

### 3. Can we trust the data?
- **Visuals:** 4 key figures (260,601 rows at the start, 15,462 duplicates removed = 5.9%, 51,111 dates fixed, 245,139 rows kept), missing values table, table of checks, "Limits of the analysis".
- **Takeaway:** the data was cleaned, assumptions are written down (shifted dates, clay merge), and some limits stay (recent years, storm category almost only 1982-1989).

### 4. What I take from this
- **Content:** four lessons (decrees are not damage, which perils stand out, decrees per commune is more useful than totals, do not trust the last years) and ideas to go further (population, Météo-France and Géorisques data, effect of the clay rule change).
- **Takeaway:** the register tells a story about recognition, not only about nature.

## 4. Design choices

- Filters in the sidebar, as the assignment asks; every number on the page follows them.
- Dark blue theme with an amber accent; serif titles; key figures in bordered boxes.
- Colour-blind friendly palette (Okabe-Ito) for perils, one colour per peril everywhere.
- Axes with titles and units, hover details, and a written description under each chart.
- Annotations: 3 highest years labelled and a grey area for incomplete years.
- Text numbers are computed from the data (not typed by hand), so they follow the filters.

## 5. Video script (2 to 4 min)

| Time | Screen | What I say |
|---|---|---|
| 0:00 - 0:25 | Introduction | The topic, the audience and the starting question |
| 0:25 - 1:15 | Overview | Key figures, labelled years, log scale, filters, merge checkbox, grey area |
| 1:15 - 2:15 | A closer look | Map (3 indicators), regions, seasons, delays |
| 2:15 - 2:45 | Data quality | Duplicates, fixed dates, remaining limits |
| 2:45 - 3:15 | Conclusion | Main message and ways to go further |

Check on screen that the numbers I say are the ones displayed when I record.
