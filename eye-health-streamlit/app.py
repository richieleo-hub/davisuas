"""
Eye-Health Analytics — interactive Streamlit dashboard.

Native Streamlit rebuild of the Plotly.js dashboard. Data is bundled as
eye_data.csv (10,000 respondents, 11 attributes) so the app needs no local
Excel file and runs unchanged on Streamlit Community Cloud.

Run locally:  streamlit run app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------ palette
INK = "#0f2a30"
MUTED = "#52696f"
FAINT = "#7e9298"
TEAL = "#0d9488"
TEAL_D = "#115e59"
CORAL = "#ef6f53"
GCOL = {0: "#7fd9cb", 1: "#34b8a6", 2: "#0d9488", 3: "#0b5d57"}
GNAME = {0: "none", 1: "reading", 2: "daily", 3: "strong"}

VARS = [
    "exercise_hours", "mental_health_score", "screen_time_hours", "screen_brightness_avg",
    "age", "height_cm", "outdoor_light_exposure_hours", "night_mode_usage",
    "screen_distance_cm", "glasses_number", "eye_health_score",
]
LABEL = {
    "exercise_hours": "Exercise (hrs)", "mental_health_score": "Mental health",
    "screen_time_hours": "Screen time (hrs)", "screen_brightness_avg": "Screen brightness",
    "age": "Age", "height_cm": "Height (cm)",
    "outdoor_light_exposure_hours": "Outdoor light (hrs)", "night_mode_usage": "Night mode %",
    "screen_distance_cm": "Screen distance (cm)", "glasses_number": "Glasses level",
    "eye_health_score": "Eye-health score",
}

st.set_page_config(
    page_title="Eye-Health Analytics",
    page_icon="\U0001F441",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------ styling
st.markdown(
    """
    <style>
      .stApp { background:
          radial-gradient(1200px 500px at 80% -8%, #d9efea 0%, transparent 55%), #eef4f3; }
      .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1320px; }
      h1, h2, h3 { color: #0f2a30; letter-spacing: -.4px; }
      [data-testid="stMetric"] {
          background: #ffffff; border: 1px solid #dde8e6; border-radius: 16px;
          padding: 14px 18px; box-shadow: 0 8px 24px rgba(15,42,48,.06); }
      [data-testid="stMetricLabel"] { color: #7e9298; font-weight: 600;
          text-transform: uppercase; letter-spacing: .6px; font-size: 11.5px; }
      [data-testid="stMetricValue"] { color: #0f2a30; }
      section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #dde8e6; }
      .eh-note { color:#52696f; font-size:13px; background:#ffffff; border:1px solid #dde8e6;
          border-radius:14px; padding:12px 16px; box-shadow:0 8px 24px rgba(15,42,48,.05); }
      .eh-foot { color:#7e9298; font-size:12px; text-align:center; margin-top:18px; line-height:1.6; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ data
@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(Path(__file__).parent / "eye_data.csv")

df = load_data()
N_TOTAL = len(df)

# ------------------------------------------------------------------ header
left, right = st.columns([2.4, 1])
with left:
    st.markdown("## \U0001F441️  Eye-Health Analytics")
    st.caption(
        "Lifestyle, screen habits & vision across 10,000 respondents · interactive exploration"
    )
with right:
    st.markdown(
        "<div class='eh-note'>Filters & charts were adapted to the fields that exist in "
        "this dataset: it carries <b>no date or geographic column</b>, so a date-range slider "
        "and map are replaced by age / screen-time ranges and a correlation heatmap.</div>",
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------ sidebar filters
st.sidebar.header("Filters")
age_min, age_max = int(df.age.min()), int(df.age.max())
age_rng = st.sidebar.slider("Age range", age_min, age_max, (age_min, age_max), step=1)

scr_max = float(np.ceil(df.screen_time_hours.max()))
scr_rng = st.sidebar.slider("Screen time (hrs/day)", 0.0, scr_max, (0.0, scr_max), step=0.5)

st.sidebar.markdown("**Glasses prescription level**")
glasses_sel = []
for g in [0, 1, 2, 3]:
    if st.sidebar.checkbox(f"{g} · {GNAME[g]}", value=True, key=f"g{g}"):
        glasses_sel.append(g)
if not glasses_sel:                       # never empty
    glasses_sel = [0, 1, 2, 3]

st.sidebar.divider()
st.sidebar.markdown("**Scatter axes**")
sx = st.sidebar.selectbox("X", VARS, index=VARS.index("screen_time_hours"),
                          format_func=lambda c: LABEL[c])
sy = st.sidebar.selectbox("Y", VARS, index=VARS.index("eye_health_score"),
                          format_func=lambda c: LABEL[c])

# ------------------------------------------------------------------ filtering
mask = (
    df.age.between(*age_rng)
    & df.screen_time_hours.between(*scr_rng)
    & df.glasses_number.isin(glasses_sel)
)
f = df[mask]

if f.empty:
    st.warning("No respondents match the current filters. Try widening the age or screen-time range.")
    st.stop()

# ------------------------------------------------------------------ KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Respondents", f"{len(f):,}", f"{100*len(f)/N_TOTAL:.0f}% of 10,000 in view")
k2.metric("Avg eye-health", f"{f.eye_health_score.mean():.1f} /100")
k3.metric("Avg screen time", f"{f.screen_time_hours.mean():.1f} hrs")
k4.metric("Wear glasses", f"{100*(f.glasses_number > 0).mean():.0f}%", "prescription level ≥ 1")

st.write("")

# ------------------------------------------------------------------ plotly helpers
FONT = dict(family="Inter, sans-serif", color=INK, size=12)


def base_layout(**kw):
    lay = dict(
        font=FONT, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=54, r=18, t=10, b=42),
        hoverlabel=dict(bgcolor=INK, font=dict(color="#fff", family="Inter")),
        xaxis=dict(gridcolor="#eaf1f0", zeroline=False, automargin=True),
        yaxis=dict(gridcolor="#eaf1f0", zeroline=False, automargin=True),
    )
    lay.update(kw)
    return lay


CFG = {"displayModeBar": False, "responsive": True}

# ------------------------------------------------------------------ row 1: heatmap + scatter
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### Correlation heatmap")
    st.caption("Pearson r between every variable — recomputes live with your filters")
    corr = f[VARS].corr().values
    labels = [LABEL[v] for v in VARS]
    hm = go.Figure(go.Heatmap(
        z=corr, x=labels, y=labels, zmid=0, zmin=-1, zmax=1, xgap=2, ygap=2,
        text=np.round(corr, 2), texttemplate="%{text}",
        textfont=dict(size=9, color="#274046"),
        colorscale=[[0, CORAL], [0.25, "#f4b59f"], [0.5, "#f3f7f6"], [0.75, "#86cfc5"], [1, TEAL]],
        colorbar=dict(title="r", thickness=10, len=0.7, outlinewidth=0),
        hovertemplate="%{y} × %{x}<br>r = %{z:.3f}<extra></extra>",
    ))
    hm.update_layout(base_layout(margin=dict(l=120, r=10, t=6, b=120)))
    hm.update_xaxes(tickangle=-45, tickfont=dict(size=10))
    hm.update_yaxes(autorange="reversed", tickfont=dict(size=10))
    st.plotly_chart(hm, use_container_width=True, config=CFG)

with c2:
    st.markdown(f"#### {LABEL[sx]} vs {LABEL[sy]}")
    st.caption("Coloured by glasses level · pick the axes from the sidebar")
    sc = go.Figure()
    for g in glasses_sel:
        sub = f[f.glasses_number == g]
        sc.add_trace(go.Scattergl(
            x=sub[sx], y=sub[sy], mode="markers", name=f"glasses {g} · {GNAME[g]}",
            marker=dict(color=GCOL[g], size=5, opacity=0.5),
            customdata=np.c_[sub.id, sub.age],
            hovertemplate=("<b>ID %{customdata[0]}</b> · age %{customdata[1]}<br>"
                           + LABEL[sx] + ": %{x}<br>" + LABEL[sy] + ": %{y}<extra></extra>"),
        ))
    sc.update_layout(base_layout(
        margin=dict(l=56, r=14, t=8, b=46),
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=10.5)),
    ))
    sc.update_xaxes(title=dict(text=LABEL[sx], font=dict(size=12)))
    sc.update_yaxes(title=dict(text=LABEL[sy], font=dict(size=12)))
    st.plotly_chart(sc, use_container_width=True, config=CFG)

# ------------------------------------------------------------------ row 2: dual-axis + histogram
c3, c4 = st.columns(2)

with c3:
    st.markdown("#### Eye-health & glasses need across age")
    st.caption("Dual-axis — with age, vision declines (left) while prescriptions strengthen (right)")
    edges = [5, 20, 30, 40, 50, 60, 70, 81]
    band_labels = ["5–19", "20–29", "30–39", "40–49", "50–59", "60–69", "70–80"]
    f2 = f.assign(band=pd.cut(f.age, bins=edges, right=False, labels=band_labels))
    grp = f2.groupby("band", observed=True).agg(
        eye=("eye_health_score", "mean"),
        gl=("glasses_number", "mean"),
        n=("id", "size"),
    ).reset_index()
    grp = grp[grp.n >= 5]
    dual = go.Figure()
    dual.add_trace(go.Scatter(
        x=grp.band, y=grp.eye, mode="lines+markers", name="Eye-health (left)",
        line=dict(color=TEAL, width=3), marker=dict(size=7, color=TEAL),
        customdata=grp.n, hovertemplate="Age %{x}<br>Eye-health: %{y:.1f}<br>n = %{customdata}<extra></extra>",
    ))
    dual.add_trace(go.Scatter(
        x=grp.band, y=grp.gl, mode="lines+markers", name="Glasses level (right)", yaxis="y2",
        line=dict(color=CORAL, width=3, dash="dot"), marker=dict(size=7, color=CORAL),
        hovertemplate="Age %{x}<br>Mean glasses level: %{y:.2f}<extra></extra>",
    ))
    dual.update_layout(base_layout(
        margin=dict(l=52, r=54, t=8, b=42),
        legend=dict(orientation="h", y=1.14, x=0, font=dict(size=10.5)),
        yaxis=dict(gridcolor="#eaf1f0", zeroline=False, title=dict(text="Eye-health", font=dict(color=TEAL)), tickfont=dict(color=TEAL)),
        yaxis2=dict(overlaying="y", side="right", range=[0, 3], zeroline=False,
                    title=dict(text="Glasses level (0–3)", font=dict(color=CORAL)), tickfont=dict(color=CORAL)),
    ))
    dual.update_xaxes(title=dict(text="Age band", font=dict(size=12)))
    st.plotly_chart(dual, use_container_width=True, config=CFG)

with c4:
    st.markdown("#### Distribution of eye-health scores")
    st.caption("Histogram of the current selection with the mean marked")
    m = f.eye_health_score.mean()
    hist = go.Figure(go.Histogram(
        x=f.eye_health_score, nbinsx=34, marker=dict(color=TEAL, line=dict(color="#fff", width=0.5)),
        opacity=0.92, hovertemplate="Score %{x}<br>%{y} respondents<extra></extra>",
    ))
    hist.update_layout(base_layout(margin=dict(l=50, r=14, t=8, b=42), bargap=0.03))
    hist.update_xaxes(title=dict(text="Eye-health score", font=dict(size=12)), range=[20, 100])
    hist.update_yaxes(title=dict(text="Respondents", font=dict(size=12)))
    hist.add_vline(x=m, line=dict(color=CORAL, width=2.4, dash="dash"),
                   annotation_text=f"mean {m:.1f}", annotation_position="top",
                   annotation_font=dict(color=CORAL, size=11))
    st.plotly_chart(hist, use_container_width=True, config=CFG)

# ------------------------------------------------------------------ row 3: bar + table
c5, c6 = st.columns(2)

with c5:
    st.markdown("#### Average eye-health by glasses level")
    st.caption("Mean score per prescription group within the current filters")
    bar_grp = (df[df.age.between(*age_rng) & df.screen_time_hours.between(*scr_rng)]
               .groupby("glasses_number")
               .agg(eye=("eye_health_score", "mean"), n=("id", "size")))
    xs = [f"{g} · {GNAME[g]}" for g in [0, 1, 2, 3]]
    ys = [bar_grp.eye.get(g, 0) for g in [0, 1, 2, 3]]
    ns = [int(bar_grp.n.get(g, 0)) for g in [0, 1, 2, 3]]
    cols = [GCOL[g] if g in glasses_sel else "#d7e4e1" for g in [0, 1, 2, 3]]
    bar = go.Figure(go.Bar(
        x=xs, y=ys, marker=dict(color=cols), customdata=ns,
        text=[f"{v:.1f}" if v else "" for v in ys], textposition="outside",
        textfont=dict(size=11, color=INK),
        hovertemplate="%{x}<br>Mean eye-health: %{y:.1f}<br>n = %{customdata}<extra></extra>",
    ))
    bar.update_layout(base_layout(margin=dict(l=50, r=14, t=18, b=38)))
    bar.update_xaxes(title=dict(text="Glasses prescription level", font=dict(size=12)))
    bar.update_yaxes(title=dict(text="Mean eye-health", font=dict(size=12)),
                     range=[0, (max(ys) * 1.16) if max(ys) else 80])
    st.plotly_chart(bar, use_container_width=True, config=CFG)

with c6:
    st.markdown("#### Drill-through detail")
    st.caption(f"Sample of {len(f):,} filtered respondents")
    show = f.head(200)[[
        "id", "age", "screen_time_hours", "screen_brightness_avg", "screen_distance_cm",
        "outdoor_light_exposure_hours", "exercise_hours", "glasses_number", "eye_health_score",
    ]].rename(columns={
        "id": "ID", "age": "Age", "screen_time_hours": "Screen hrs",
        "screen_brightness_avg": "Brightness", "screen_distance_cm": "Distance cm",
        "outdoor_light_exposure_hours": "Outdoor hrs", "exercise_hours": "Exercise hrs",
        "glasses_number": "Glasses", "eye_health_score": "Eye-health",
    })
    st.dataframe(show, use_container_width=True, hide_index=True, height=320)

# ------------------------------------------------------------------ footer
st.markdown(
    "<div class='eh-foot'>Source: <b>eye_score_cleaned.xlsx</b> · 10,000 records, "
    "11 attributes, 0 missing / 0 duplicates. Correlations are Pearson and recompute live "
    "with your filters. Eye-health score is a 0–100 composite.</div>",
    unsafe_allow_html=True,
)
