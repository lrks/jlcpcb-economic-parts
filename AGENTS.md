# Repository Notes for Agents

This repository builds HTML and CSV lists of JLCPCB Economic Parts.

## Data Flow

- `download.py` fetches JSON pages from the JLCPCB API.
- `generate-csv.py` converts `parts-page*.json` into `economic-parts.csv`.
- `generate-html.py` converts `economic-parts.csv` into:
  - `economic-parts.html`
  - `economic-parts-active.html`
- GitHub Actions moves generated files into `dist/` before deploying GitHub Pages.

## Local Generation

When regenerating output locally, keep the repository root clean after verification:

```sh
python3 generate-csv.py
python3 generate-html.py
mkdir -p dist
mv economic-parts.csv dist/
mv economic-parts.html dist/index.html
mv economic-parts-active.html dist/active.html
```

## CSV Notes

- The published CSV is downloaded by GitHub Actions before generating a new CSV.
- Deleted parts are preserved from the old CSV when they are not present in the new JSON data.
- The `firstSeen` column is displayed on the full HTML list. Existing active parts from CSVs that predate the column are initialized with the first run timestamp after tracking begins.
- Keep existing CSV column order stable when adding fields; append new columns when practical.
- The `category` column stores the broad category. The `type` column stores the subcategory.

## GitHub Actions

The workflow in `.github/workflows/deploy.yaml` runs on pushes to `main` and on a weekly schedule. It downloads data, generates CSV/HTML, uploads `dist/`, and deploys GitHub Pages.
