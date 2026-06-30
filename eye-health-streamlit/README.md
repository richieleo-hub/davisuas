# Eye-Health Analytics — Streamlit Dashboard

Interactive dashboard exploring lifestyle, screen habits, and vision across
10,000 respondents. Native Streamlit rebuild of the Plotly.js version, with the
dataset bundled as `eye_data.csv` so it runs anywhere with no local Excel file.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501.

## Deploy to Streamlit Community Cloud

1. Push this `eye-health-streamlit/` folder to a public GitHub repo.
2. Go to https://share.streamlit.io → **Create app** → **Deploy a public app from GitHub**.
3. Pick the repo/branch, set **Main file path** to `app.py`
   (or `eye-health-streamlit/app.py` if the folder is not the repo root).
4. Click **Deploy**. Streamlit installs `requirements.txt` automatically.

## Files

| File | Purpose |
|------|---------|
| `app.py` | The dashboard (filters, KPIs, 5 charts, drill table) |
| `eye_data.csv` | Cleaned dataset, 10,000 rows × 11 attributes |
| `requirements.txt` | Python dependencies |
| `.streamlit/config.toml` | Teal/coral light theme |

## Notes

The dataset has **no date or geographic column**, so a date-range slider and map
are replaced by age / screen-time range sliders and a live Pearson correlation
heatmap. Eye-health score is a 0–100 composite. All correlations recompute with
the active filters.
