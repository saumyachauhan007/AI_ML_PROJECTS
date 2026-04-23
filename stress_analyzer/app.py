"""
NeuroBalance — AI Wellness Intelligence Platform
Run: streamlit run app.py
Requirements: streamlit, numpy, scikit-learn, plotly, pandas
Install: pip install streamlit numpy scikit-learn plotly pandas
No external model files needed — trains on startup.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import time
import random
import math

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="NeuroBalance · Wellness OS",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  TRAIN MODEL IN-MEMORY (no pickle needed)
# ─────────────────────────────────────────────
@st.cache_resource
def build_model():
    rng = np.random.default_rng(42)
    n = 3000

    sleep    = rng.uniform(1, 10, n)
    screen   = rng.uniform(1, 10, n)
    work     = rng.uniform(1, 10, n)
    exercise = rng.uniform(1, 10, n)
    social   = rng.uniform(1, 10, n)
    nutrition= rng.uniform(1, 10, n)
    hydration= rng.uniform(1, 10, n)
    mindful  = rng.uniform(1, 10, n)

    # Realistic stress formula
    stress_score = (
        -1.5 * sleep
        +  1.2 * screen
        +  1.8 * work
        -  1.4 * exercise
        -  0.8 * social
        -  0.6 * nutrition
        -  0.5 * hydration
        -  0.9 * mindful
        + rng.normal(0, 2, n)
    )

    labels = np.where(stress_score < -3, 0,
             np.where(stress_score < 3, 1, 2))   # 0=Low, 1=Med, 2=High

    X = np.column_stack([sleep, screen, work, exercise, social, nutrition, hydration, mindful])

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GradientBoostingClassifier(n_estimators=200, max_depth=4, random_state=42))
    ])
    pipe.fit(X, labels)
    return pipe

# ─────────────────────────────────────────────
#  GLOBAL CSS  — Monochrome clinical + amber accent
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:        #0a0a0a;
    --surface:   #111111;
    --border:    #222222;
    --muted:     #444444;
    --text:      #e8e8e8;
    --dim:       #888888;
    --accent:    #f59e0b;
    --accent2:   #10b981;
    --danger:    #ef4444;
    --warn:      #f97316;
    --low:       #10b981;
    --med:       #f59e0b;
    --high:      #ef4444;
    --mono:      'DM Mono', monospace;
    --sans:      'DM Sans', sans-serif;
    --display:   'Syne', sans-serif;
}

/* Reset */
html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem 3rem !important; max-width: 1400px !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── Typography ── */
h1, h2, h3 { font-family: var(--display) !important; letter-spacing: -0.03em; }

/* ── Top nav bar ── */
.nav-bar {
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid var(--border);
    padding: 1.2rem 0 1rem 0;
    margin-bottom: 2.5rem;
}
.nav-logo {
    font-family: var(--display);
    font-size: 1.1rem; font-weight: 800;
    letter-spacing: 0.05em; color: var(--text);
}
.nav-logo span { color: var(--accent); }
.nav-tag {
    font-family: var(--mono); font-size: 0.65rem;
    color: var(--dim); letter-spacing: 0.12em; text-transform: uppercase;
}

/* ── Section label ── */
.section-label {
    font-family: var(--mono); font-size: 0.65rem; font-weight: 500;
    color: var(--muted); letter-spacing: 0.18em; text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* ── Glass cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
}
.card-sm {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}

/* ── Metric tiles ── */
.metric-grid {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;
    margin: 1.5rem 0;
}
.metric-tile {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.4rem;
}
.metric-tile .label {
    font-family: var(--mono); font-size: 0.62rem;
    color: var(--dim); letter-spacing: 0.14em; text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.metric-tile .value {
    font-family: var(--display); font-size: 2rem; font-weight: 800;
    line-height: 1; color: var(--text);
}
.metric-tile .sub {
    font-size: 0.72rem; color: var(--dim); margin-top: 0.3rem;
}

/* ── Input group ── */
.input-group {
    display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.8rem;
}
.input-label {
    font-family: var(--mono); font-size: 0.68rem;
    color: var(--dim); letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 0.2rem;
}

/* ── Slider override ── */
.stSlider > div > div > div > div {
    background: var(--accent) !important;
}
.stSlider [data-baseweb="slider"] { padding: 0 !important; }

/* ── Run button ── */
.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--display) !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.8rem 2.4rem !important;
    width: 100% !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── Stress badge ── */
.stress-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    font-family: var(--mono); font-size: 0.72rem; font-weight: 500;
    letter-spacing: 0.1em; text-transform: uppercase;
}
.badge-low  { background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.badge-med  { background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.badge-high { background: rgba(239,68,68,0.12);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

/* ── Insight row ── */
.insight-row {
    display: flex; align-items: flex-start; gap: 0.8rem;
    padding: 1rem 0; border-bottom: 1px solid var(--border);
}
.insight-row:last-child { border-bottom: none; }
.insight-icon { font-size: 1.1rem; margin-top: 0.05rem; }
.insight-text { font-size: 0.88rem; color: var(--dim); line-height: 1.55; }
.insight-text strong { color: var(--text); }

/* ── Score bar ── */
.score-bar-wrap { margin: 0.6rem 0 1.2rem; }
.score-bar-label {
    display: flex; justify-content: space-between;
    font-family: var(--mono); font-size: 0.65rem; color: var(--dim);
    margin-bottom: 0.3rem;
}
.score-bar-track {
    height: 5px; background: var(--border);
    border-radius: 999px; overflow: hidden;
}
.score-bar-fill { height: 100%; border-radius: 999px; transition: width 0.6s ease; }

/* ── Horizontal divider ── */
hr { border: none; border-top: 1px solid var(--border) !important; margin: 2rem 0 !important; }

/* ── Timeline log ── */
.log-line {
    display: flex; align-items: center; gap: 0.7rem;
    font-family: var(--mono); font-size: 0.72rem; color: var(--dim);
    padding: 0.35rem 0;
}
.log-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); flex-shrink: 0; }
.log-time { color: var(--muted); min-width: 60px; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--dim) !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--border) !important;
    color: var(--text) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Plotly dark fix ── */
.js-plotly-plot .plotly .bg { fill: transparent !important; }

/* scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  NAV BAR
# ─────────────────────────────────────────────
st.markdown("""
<div class="nav-bar">
    <div class="nav-logo">NEURO<span>BALANCE</span></div>
    <div style="display:flex;gap:2rem;align-items:center">
        <span class="nav-tag">Wellness Intelligence OS</span>
        <span class="nav-tag" style="color:#444">v2.4.1</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────
col_hero, col_intro = st.columns([2, 1])
with col_hero:
    st.markdown("""
    <h1 style="font-size:3.2rem;font-weight:800;margin:0;line-height:1.05;color:#e8e8e8">
    Your Mental Health,<br>
    <span style="color:#f59e0b">Quantified.</span>
    </h1>
    <p style="color:#666;font-size:0.95rem;margin-top:1rem;max-width:420px;line-height:1.7">
    Input your daily lifestyle metrics and receive a multi-dimensional stress prediction powered by a Gradient Boosting model trained on 3,000 synthetic health profiles.
    </p>
    """, unsafe_allow_html=True)

with col_intro:
    st.markdown("""
    <div class="card" style="border-left:3px solid #f59e0b">
        <div class="section-label">How it works</div>
        <div style="font-size:0.82rem;color:#888;line-height:1.8;margin-top:0.6rem">
        ① Rate 8 lifestyle dimensions<br>
        ② AI model computes stress class<br>
        ③ Feature attribution reveals drivers<br>
        ④ Personalised action plan generated
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  INPUT PANEL
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">01 — Lifestyle Inputs</div>', unsafe_allow_html=True)
st.markdown("""
<p style="color:#555;font-size:0.82rem;margin-bottom:1.4rem">
Rate each dimension honestly. 1 = poor / low, 10 = excellent / high.
</p>
""", unsafe_allow_html=True)

FEATURES = {
    "sleep":     ("😴", "Sleep Quality",       "Hours & depth of rest"),
    "screen":    ("📱", "Screen Exposure",      "Daily screen time burden"),
    "work":      ("⚡", "Workload Pressure",    "Cognitive + task load"),
    "exercise":  ("🏃", "Physical Activity",    "Movement & exercise"),
    "social":    ("👥", "Social Connection",    "Meaningful interactions"),
    "nutrition": ("🥗", "Nutrition Quality",    "Diet balance & regularity"),
    "hydration": ("💧", "Hydration",            "Daily water intake"),
    "mindful":   ("🧘", "Mindfulness",          "Meditation / calm practices"),
}

# Layout: 4 columns
cols = st.columns(4)
inputs = {}
for idx, (key, (icon, label, desc)) in enumerate(FEATURES.items()):
    with cols[idx % 4]:
        st.markdown(f"""
        <div style="margin-bottom:0.3rem">
            <span style="font-size:1.3rem">{icon}</span>
            <span style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#555;
                  letter-spacing:0.1em;text-transform:uppercase;margin-left:0.4rem">{label}</span>
        </div>
        <div style="font-size:0.72rem;color:#444;margin-bottom:0.1rem">{desc}</div>
        """, unsafe_allow_html=True)
        inputs[key] = st.slider(label, 1, 10, 5, key=key, label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  RUN BUTTON
# ─────────────────────────────────────────────
btn_col, _ = st.columns([1, 3])
with btn_col:
    run = st.button("◎  Analyse My Profile")

# ─────────────────────────────────────────────
#  RESULTS
# ─────────────────────────────────────────────
if run:
    model = build_model()

    X = np.array([[inputs[k] for k in ["sleep","screen","work","exercise","social","nutrition","hydration","mindful"]]])
    proba  = model.predict_proba(X)[0]          # [low, med, high]
    pred   = int(np.argmax(proba))
    labels = ["Low", "Medium", "High"]
    level  = labels[pred]
    confidence = round(float(proba[pred]) * 100, 1)

    # Compute domain scores (invert stress-increasing ones)
    POSITIVE = ["sleep", "exercise", "social", "nutrition", "hydration", "mindful"]
    NEGATIVE = ["screen", "work"]
    wellness_scores = {}
    for k in POSITIVE:
        wellness_scores[k] = inputs[k]
    for k in NEGATIVE:
        wellness_scores[k] = 11 - inputs[k]   # invert

    wellness_avg = round(np.mean(list(wellness_scores.values())), 1)
    risk_idx     = round(10 - wellness_avg, 1)

    badge_cls = {"Low": "badge-low", "Medium": "badge-med", "High": "badge-high"}[level]
    badge_dot = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"}[level]

    with st.spinner(""):
        time.sleep(0.6)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">02 — Analysis Results</div>', unsafe_allow_html=True)

    # ── Summary row ──
    sum_left, sum_right = st.columns([3, 1])
    with sum_left:
        st.markdown(f"""
        <div style="margin-top:0.8rem;margin-bottom:1.4rem">
            <h2 style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
                       color:#e8e8e8;margin:0 0 0.6rem 0">
                Stress Classification: <span style="color:{badge_dot}">{level}</span>
            </h2>
            <span class="stress-badge {badge_cls}">
                <span style="width:6px;height:6px;border-radius:50%;
                             background:{badge_dot};display:inline-block"></span>
                {level} Stress · {confidence}% confidence
            </span>
            &nbsp;&nbsp;
            <span style="font-family:'DM Mono',monospace;font-size:0.7rem;
                         color:#555;letter-spacing:0.08em">
                Wellness Index: {wellness_avg}/10 &nbsp;|&nbsp; Risk Score: {risk_idx}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ── 4 metric tiles ──
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-tile">
            <div class="label">Wellness Index</div>
            <div class="value">{wellness_avg}</div>
            <div class="sub">out of 10.0</div>
        </div>
        <div class="metric-tile" style="border-left:3px solid {badge_dot}">
            <div class="label">Stress Class</div>
            <div class="value" style="color:{badge_dot}">{level}</div>
            <div class="sub">{confidence}% model confidence</div>
        </div>
        <div class="metric-tile">
            <div class="label">Risk Score</div>
            <div class="value">{risk_idx}</div>
            <div class="sub">inverted wellness gap</div>
        </div>
        <div class="metric-tile">
            <div class="label">Flagged Factors</div>
            <div class="value">{sum(1 for k in POSITIVE if inputs[k]<5) + sum(1 for k in NEGATIVE if inputs[k]>6)}</div>
            <div class="sub">areas needing attention</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    #  TABS
    # ─────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["  VISUALISE  ", "  BREAKDOWN  ", "  AI INSIGHTS  ", "  HISTORY  "])

    # ─── TAB 1: Charts ───
    with tab1:
        ch1, ch2 = st.columns(2)

        # Probability bar chart
        with ch1:
            st.markdown('<div class="section-label">Stress class probability</div>', unsafe_allow_html=True)
            fig_prob = go.Figure()
            colors_p = ["#10b981", "#f59e0b", "#ef4444"]
            for i, (lbl, prob, col) in enumerate(zip(labels, proba, colors_p)):
                fig_prob.add_trace(go.Bar(
                    x=[round(prob*100,1)], y=[lbl],
                    orientation='h',
                    marker_color=col,
                    marker_line_width=0,
                    name=lbl,
                    text=[f"{round(prob*100,1)}%"],
                    textposition="outside",
                    textfont=dict(color="#888", size=11, family="DM Mono"),
                ))
            fig_prob.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=10, r=40, t=10, b=10),
                height=200,
                bargap=0.35,
                xaxis=dict(showgrid=False, showticklabels=False, range=[0, 110]),
                yaxis=dict(showgrid=False, tickfont=dict(family="DM Mono", size=11, color="#888")),
                barmode='overlay',
            )
            st.plotly_chart(fig_prob, use_container_width=True, config={"displayModeBar": False})

        # Radar chart
        with ch2:
            st.markdown('<div class="section-label">Lifestyle radar</div>', unsafe_allow_html=True)
            cats   = [FEATURES[k][1] for k in FEATURES]
            vals   = [inputs[k] for k in FEATURES]
            vals_c = vals + [vals[0]]
            cats_c = cats + [cats[0]]
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_c, theta=cats_c, fill='toself',
                fillcolor='rgba(245,158,11,0.08)',
                line=dict(color='#f59e0b', width=1.5),
                marker=dict(color='#f59e0b', size=4),
            ))
            fig_radar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(
                        visible=True, range=[0,10],
                        tickfont=dict(color="#444", size=9, family="DM Mono"),
                        gridcolor="#1a1a1a", linecolor="#1a1a1a",
                    ),
                    angularaxis=dict(
                        tickfont=dict(color="#666", size=9, family="DM Mono"),
                        gridcolor="#1a1a1a", linecolor="#1a1a1a",
                    ),
                ),
                margin=dict(l=30, r=30, t=20, b=20),
                height=260,
                showlegend=False,
            )
            st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

        # Wellness score bars (horizontal)
        st.markdown('<div class="section-label" style="margin-top:0.5rem">Wellness-adjusted scores per dimension</div>', unsafe_allow_html=True)
        bar_df = pd.DataFrame({
            "Dimension": [FEATURES[k][1] for k in FEATURES],
            "Raw":       [inputs[k] for k in FEATURES],
            "Adjusted":  [wellness_scores[k] for k in wellness_scores],
        })
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=bar_df["Dimension"], y=bar_df["Raw"],
            name="Raw Score",
            marker_color="rgba(68,68,68,0.6)",
            marker_line_width=0,
        ))
        fig_bar.add_trace(go.Bar(
            x=bar_df["Dimension"], y=bar_df["Adjusted"],
            name="Wellness-Adjusted",
            marker_color="#f59e0b",
            marker_line_width=0,
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            barmode="group",
            bargap=0.25, bargroupgap=0.08,
            height=260,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(
                tickfont=dict(color="#555", size=10, family="DM Mono"),
                gridcolor="#111", linecolor="#222",
            ),
            yaxis=dict(
                range=[0,11],
                gridcolor="#1a1a1a", linecolor="#222",
                tickfont=dict(color="#444", size=10, family="DM Mono"),
            ),
            legend=dict(
                font=dict(color="#666", size=10, family="DM Mono"),
                bgcolor="rgba(0,0,0,0)", borderwidth=0,
            ),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    # ─── TAB 2: Dimension Breakdown ───
    with tab2:
        st.markdown('<div class="section-label" style="margin-top:0.6rem">Dimension-by-dimension analysis</div>', unsafe_allow_html=True)

        THRESHOLDS = {
            "sleep":     (6, True,  "Sleep quality directly regulates cortisol and emotional resilience."),
            "screen":    (6, False, "High screen time suppresses melatonin and increases cognitive load."),
            "work":      (7, False, "Sustained high workload activates the HPA axis and raises cortisol."),
            "exercise":  (5, True,  "Physical activity is the strongest natural stress buffer available."),
            "social":    (5, True,  "Social connection reduces amygdala reactivity and loneliness-induced stress."),
            "nutrition": (5, True,  "Poor nutrition disrupts neurotransmitter synthesis including serotonin."),
            "hydration": (5, True,  "Even mild dehydration impairs mood, focus, and stress regulation."),
            "mindful":   (4, True,  "Mindfulness practice measurably reduces default-mode network rumination."),
        }

        for key, (icon, label, desc) in FEATURES.items():
            val      = inputs[key]
            thresh, is_pos, note = THRESHOLDS[key]
            flagged  = (is_pos and val < thresh) or (not is_pos and val > thresh)
            fill_pct = val * 10
            bar_col  = "#10b981" if not flagged else ("#f59e0b" if abs(val - thresh) < 2 else "#ef4444")
            status   = "⚠ Flagged" if flagged else "✓ OK"
            status_c = "#ef4444" if flagged else "#10b981"

            st.markdown(f"""
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.7rem">
                    <div>
                        <span style="font-size:1.1rem">{icon}</span>
                        <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;
                                     margin-left:0.5rem;color:#e8e8e8">{label}</span>
                        <span style="font-family:'DM Mono',monospace;font-size:0.65rem;
                                     color:#444;margin-left:0.8rem;letter-spacing:0.08em">{desc}</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:1rem">
                        <span style="font-family:'DM Mono',monospace;font-size:0.68rem;
                                     color:{status_c}">{status}</span>
                        <span style="font-family:'Syne',sans-serif;font-size:1.4rem;
                                     font-weight:800;color:{bar_col}">{val}<span style="font-size:0.8rem;color:#444">/10</span></span>
                    </div>
                </div>
                <div class="score-bar-track">
                    <div class="score-bar-fill" style="width:{fill_pct}%;background:{bar_col}"></div>
                </div>
                <p style="font-size:0.78rem;color:#555;margin:0.6rem 0 0;line-height:1.6">{note}</p>
            </div>
            """, unsafe_allow_html=True)

    # ─── TAB 3: AI Insights ───
    with tab3:
        st.markdown('<div class="section-label" style="margin-top:0.6rem">Personalised recommendations</div>', unsafe_allow_html=True)

        recs = []

        if inputs["sleep"] < 6:
            recs.append(("🌙", "Sleep Deficit Detected",
                "Your sleep score of <b>{}</b> suggests inadequate recovery. Aim for 7–9 hours with consistent bedtime/wake cycles. "
                "Blue-light blocking glasses after 9pm and a cooler room temperature (18–20°C) can improve sleep onset latency.".format(inputs["sleep"])))

        if inputs["screen"] > 6:
            recs.append(("📵", "Digital Overexposure",
                "Screen exposure at <b>{}/10</b> is stress-amplifying. Implement a 20-20-20 rule (every 20 min, look 20ft away for 20 sec) "
                "and set a hard screen cutoff 60 minutes before sleep.".format(inputs["screen"])))

        if inputs["work"] > 7:
            recs.append(("🔥", "Workload Overload",
                "Workload score of <b>{}</b> places you in high-pressure territory. Time-blocking with Pomodoro intervals (25 min focus / 5 min break) "
                "and a clear end-of-day shutdown ritual can reduce cognitive residue.".format(inputs["work"])))

        if inputs["exercise"] < 5:
            recs.append(("🏋️", "Physical Activity Gap",
                "Exercise at <b>{}/10</b> is below the therapeutic threshold. Even 20 minutes of brisk walking raises BDNF "
                "and reduces cortisol for up to 4 hours. Aim for ≥150 min moderate aerobic activity per week.".format(inputs["exercise"])))

        if inputs["social"] < 5:
            recs.append(("🤝", "Social Isolation Risk",
                "Social connection rated <b>{}/10</b> — chronic isolation elevates inflammatory markers and cortisol. "
                "Schedule one meaningful in-person interaction per day, even briefly.".format(inputs["social"])))

        if inputs["nutrition"] < 5:
            recs.append(("🥦", "Nutritional Imbalance",
                "Poor nutrition (rated <b>{}</b>) disrupts serotonin and dopamine synthesis. "
                "Prioritise tryptophan-rich foods, omega-3s (oily fish, walnuts), and magnesium (leafy greens, seeds).".format(inputs["nutrition"])))

        if inputs["hydration"] < 5:
            recs.append(("💧", "Dehydration Risk",
                "Hydration at <b>{}/10</b>. Even 1–2% dehydration increases perceived stress and impairs working memory. "
                "Target 8 glasses/day; set hourly phone reminders if needed.".format(inputs["hydration"])))

        if inputs["mindful"] < 4:
            recs.append(("🧘", "Mindfulness Deficit",
                "Mindfulness rated <b>{}/10</b> — low practice correlates with elevated default-mode network rumination. "
                "Start with 10 min/day of guided breathing using apps like Waking Up or Insight Timer.".format(inputs["mindful"])))

        if not recs:
            recs.append(("✨", "Optimal Profile",
                "All dimensions within healthy ranges. Maintain consistency — wellness gains erode within 72 hours of behavioural regression. "
                "Consider journaling to track what's working."))

        for icon, title, body in recs:
            st.markdown(f"""
            <div class="insight-row">
                <div class="insight-icon">{icon}</div>
                <div>
                    <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.9rem;
                                color:#e8e8e8;margin-bottom:0.2rem">{title}</div>
                    <div class="insight-text">{body}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Priority matrix
        st.markdown('<hr><div class="section-label">Priority action matrix</div>', unsafe_allow_html=True)

        priority_data = []
        for key, (icon, label, _) in FEATURES.items():
            ws = wellness_scores[key]
            impact_map = {"sleep": 9, "screen": 7, "work": 8, "exercise": 9,
                          "social": 6, "nutrition": 7, "hydration": 5, "mindful": 6}
            priority_data.append({
                "Dimension": label,
                "Wellness Score": ws,
                "Impact Weight": impact_map[key],
                "Priority": round((10 - ws) * impact_map[key] / 10, 1)
            })

        df_p = pd.DataFrame(priority_data).sort_values("Priority", ascending=False)

        fig_pri = go.Figure()
        fig_pri.add_trace(go.Bar(
            x=df_p["Priority"], y=df_p["Dimension"],
            orientation='h',
            marker=dict(
                color=df_p["Priority"],
                colorscale=[[0, "#10b981"], [0.5, "#f59e0b"], [1, "#ef4444"]],
                cmin=0, cmax=df_p["Priority"].max(),
                line_width=0,
            ),
            text=df_p["Priority"].apply(lambda x: f"{x}"),
            textposition="outside",
            textfont=dict(color="#666", size=10, family="DM Mono"),
        ))
        fig_pri.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=280,
            margin=dict(l=10, r=50, t=10, b=10),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(
                tickfont=dict(family="DM Mono", size=10, color="#666"),
                gridcolor="#111",
            ),
        )
        st.plotly_chart(fig_pri, use_container_width=True, config={"displayModeBar": False})

    # ─── TAB 4: Session History ───
    with tab4:
        # Store to session state
        if "history" not in st.session_state:
            st.session_state.history = []

        snapshot = {
            "Run": len(st.session_state.history) + 1,
            "Stress": level,
            "Wellness": wellness_avg,
            "Risk":     risk_idx,
            **{FEATURES[k][1][:7]: inputs[k] for k in FEATURES},
        }
        st.session_state.history.append(snapshot)

        st.markdown('<div class="section-label" style="margin-top:0.6rem">Session log</div>', unsafe_allow_html=True)

        if len(st.session_state.history) < 2:
            st.markdown("""
            <div style="text-align:center;padding:3rem;color:#333;font-family:'DM Mono',monospace;font-size:0.8rem">
            Run multiple analyses to compare across sessions.<br>
            <span style="color:#222">Change your inputs and click Analyse again.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            hist_df = pd.DataFrame(st.session_state.history)

            # Trend line
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=hist_df["Run"], y=hist_df["Wellness"],
                mode="lines+markers",
                line=dict(color="#f59e0b", width=2),
                marker=dict(color="#f59e0b", size=6),
                name="Wellness Index",
            ))
            fig_trend.add_trace(go.Scatter(
                x=hist_df["Run"], y=hist_df["Risk"],
                mode="lines+markers",
                line=dict(color="#ef4444", width=1.5, dash="dot"),
                marker=dict(color="#ef4444", size=5),
                name="Risk Score",
            ))
            fig_trend.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=220, margin=dict(l=10, r=10, t=20, b=10),
                xaxis=dict(gridcolor="#1a1a1a", tickfont=dict(color="#444", size=9, family="DM Mono")),
                yaxis=dict(gridcolor="#1a1a1a", tickfont=dict(color="#444", size=9, family="DM Mono"), range=[0,10]),
                legend=dict(font=dict(color="#666", size=9, family="DM Mono"), bgcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

        # Table
        if st.session_state.history:
            display_df = pd.DataFrame(st.session_state.history)[["Run","Stress","Wellness","Risk"]].copy()
            display_df.index = display_df["Run"]
            display_df = display_df.drop("Run", axis=1)
            st.dataframe(
                display_df,
                use_container_width=True,
                height=min(len(st.session_state.history)*40 + 60, 300),
            )

    # ── System log ──
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">System Log</div>', unsafe_allow_html=True)

    log_entries = [
        ("00:00", "Model loaded — GradientBoosting (n_estimators=200, depth=4)"),
        ("00:01", f"Input vector: {[inputs[k] for k in FEATURES]}"),
        ("00:02", f"Prediction: class={pred} ({level}) · proba={[round(p,3) for p in proba]}"),
        ("00:03", f"Wellness index computed: {wellness_avg}/10"),
        ("00:04", f"Risk score: {risk_idx} · Flagged dimensions: {sum(1 for k in POSITIVE if inputs[k]<5) + sum(1 for k in NEGATIVE if inputs[k]>6)}"),
        ("00:05", "Recommendation engine executed"),
    ]

    log_html = ""
    for t, msg in log_entries:
        log_html += f"""
        <div class="log-line">
            <div class="log-dot"></div>
            <span class="log-time">{t}</span>
            <span>{msg}</span>
        </div>"""

    st.markdown(f'<div class="card" style="padding:1rem 1.4rem">{log_html}</div>', unsafe_allow_html=True)

else:
    # ── Idle state ──
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;color:#2a2a2a">
        <div style="font-family:'DM Mono',monospace;font-size:3rem;letter-spacing:-0.05em;margin-bottom:1rem">◎</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.72rem;letter-spacing:0.2em;text-transform:uppercase;color:#333">
            Awaiting input · Set your lifestyle parameters above
        </div>
    </div>
    """, unsafe_allow_html=True)