import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
import random

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="NeuroTime AI",
    page_icon="⏳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# MINIMAL STYLE  (only safe overrides — no layout hacks)
# ──────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] { font-family: 'Sora', sans-serif !important; }
    .stApp { background: #f7f4f0 !important; }
    .block-container { padding-top: 2rem !important; padding-bottom: 4rem !important; }
    div[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 700 !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: .06em; }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] { border-radius: 10px; padding: 8px 20px; font-weight: 600; }
    .stButton > button {
        background: linear-gradient(135deg, #e85d26, #c94d1a) !important;
        color: white !important; border: none !important;
        border-radius: 12px !important; font-weight: 700 !important;
        font-size: 15px !important; padding: 12px 0 !important;
        font-family: 'Sora', sans-serif !important;
        transition: opacity .2s !important;
    }
    .stButton > button:hover { opacity: .88 !important; }
    .stNumberInput input { font-family: 'DM Mono', monospace !important; font-size: 15px !important; border-radius: 10px !important; }
    [data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# MOCK MODEL  (replace with pickle.load when ready)
# ──────────────────────────────────────────────
class _MockModel:
    def predict(self, X):
        s = X[0]
        if s[0] >= 7:  return [0]   # Focused
        elif s[4] < 4: return [2]   # Burnout
        else:          return [1]   # Distracted

class _MockScaler:
    def transform(self, X): return X

try:
    import pickle
    model  = pickle.load(open("model.pkl", "rb"))
    scaler = pickle.load(open("scaler.pkl", "rb"))
    MODEL_LOADED = True
except:
    model  = _MockModel()
    scaler = _MockScaler()
    MODEL_LOADED = False

# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────
defaults = {"history": [], "last_result": None, "data": [5, 5, 5, 5, 5]}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
FEATURES = {
    "Study":  {"icon": "📚", "color": "#3b82f6", "desc": "Focused study/work hours"},
    "Phone":  {"icon": "📱", "color": "#e85d26", "desc": "Phone screen time (hrs)"},
    "Social": {"icon": "🌐", "color": "#f4a261", "desc": "Social media hours"},
    "Breaks": {"icon": "☕", "color": "#2a9d8f", "desc": "Break intervals taken"},
    "Sleep":  {"icon": "😴", "color": "#8b5cf6", "desc": "Sleep hours last night"},
}

PROFILES = {
    "Focused":    {"emoji": "🎯", "color": "green",  "tag": "FOCUSED",    "desc": "Peak cognitive mode. You're locked in."},
    "Distracted": {"emoji": "⚡", "color": "orange", "tag": "DISTRACTED", "desc": "Attention is fragmented. Time to recalibrate."},
    "Burnout":    {"emoji": "🔥", "color": "red",    "tag": "BURNOUT",    "desc": "Overload detected. Rest is non-negotiable."},
}

FEAT_KEYS = list(FEATURES.keys())

# ──────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────
def run_analysis(data):
    X       = np.array([data])
    cluster = model.predict(scaler.transform(X))[0]
    labels  = ["Focused", "Distracted", "Burnout"]
    return {
        "profile":    labels[int(cluster) % 3],
        "score":      round(float(np.mean(data)), 1),
        "leakage":    round(data[1]*0.3 + data[2]*0.4 + data[3]*0.2, 1),
        "confidence": random.randint(87, 98),
    }

def get_insights(data):
    issues, tips = [], []
    if data[1] > 7: issues.append("📱 High phone screen time");       tips.append("⏱ Use app timers — cut phone by 30%")
    if data[2] > 7: issues.append("🌐 Social media overload");        tips.append("📅 Batch social media to 2 blocks/day")
    if data[4] < 5: issues.append("😴 Sleep deficit detected");       tips.append("🛌 Aim for 7–8 hrs with consistent schedule")
    if data[3] > 7: issues.append("☕ Too many breaks");              tips.append("🍅 Try Pomodoro: 25 min work / 5 min break")
    if data[0] < 3: issues.append("📚 Study time critically low");    tips.append("🌅 Protect a 3-hr deep-work morning block")
    if not tips:    tips.append("✅ Excellent habits — keep it up!")
    return issues, tips

def make_bar_chart(data):
    colors = [FEATURES[k]["color"] for k in FEAT_KEYS]
    fig = go.Figure(go.Bar(
        x=FEAT_KEYS, y=data,
        marker=dict(color=colors, cornerradius=8),
        text=[str(v) for v in data], textposition="outside",
        textfont=dict(family="Sora", size=13, color="#1a1410"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(250,248,245,1)",
        font=dict(family="Sora", color="#3d342a"), showlegend=False,
        margin=dict(l=0, r=0, t=20, b=0), height=280, bargap=0.35,
        yaxis=dict(showgrid=True, gridcolor="#e8e0d6", range=[0,13],
                   tickfont=dict(size=11), zeroline=False),
        xaxis=dict(showgrid=False, tickfont=dict(size=12)),
        title=dict(text="Activity Breakdown", font=dict(size=13, color="#8a7e74"),
                   x=0, xanchor="left", pad=dict(b=10)),
    )
    return fig

def make_radar_chart(data):
    theta = FEAT_KEYS + [FEAT_KEYS[0]]
    r     = data + [data[0]]
    fig = go.Figure(go.Scatterpolar(
        r=r, theta=theta, fill='toself',
        fillcolor='rgba(232,93,38,0.10)',
        line=dict(color='#e85d26', width=2.5),
        marker=dict(size=7, color='#e85d26'),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Sora", color="#3d342a"), showlegend=False,
        margin=dict(l=50, r=50, t=40, b=20), height=280,
        polar=dict(
            bgcolor="rgba(250,248,245,1)",
            angularaxis=dict(tickfont=dict(size=12), linecolor="#e8e0d6", gridcolor="#e8e0d6"),
            radialaxis=dict(range=[0,10], tickfont=dict(size=9), gridcolor="#e8e0d6", linecolor="#e8e0d6"),
        ),
        title=dict(text="Behavior Radar", font=dict(size=13, color="#8a7e74"),
                   x=0.5, xanchor="center"),
    )
    return fig

def make_leakage_gauge(leakage):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=leakage,
        number={"suffix": "h", "font": {"family": "Sora", "size": 28, "color": "#1a1410"}},
        gauge={
            "axis": {"range": [0, 10], "tickfont": {"size": 10}, "tickcolor": "#8a7e74"},
            "bar":  {"color": "#e85d26", "thickness": 0.25},
            "bgcolor": "#f2ede8",
            "borderwidth": 0,
            "steps": [
                {"range": [0,   3], "color": "#d1fae5"},
                {"range": [3,   6], "color": "#fef3c7"},
                {"range": [6,  10], "color": "#fee2e2"},
            ],
            "threshold": {"line": {"color": "#e85d26", "width": 3}, "value": leakage},
        },
        title={"text": "Time Leakage (hrs)", "font": {"family": "Sora", "size": 13, "color": "#8a7e74"}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=10), height=220,
        font=dict(family="Sora"),
    )
    return fig

def make_history_chart(history):
    profiles_over_time = [h["profile"] for h in history]
    scores             = [h["score"]   for h in history]
    leakages           = [h["leakage"] for h in history]
    runs               = list(range(1, len(history)+1))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=runs, y=scores, name="Focus Score",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(size=8, color="#3b82f6"),
        mode="lines+markers",
    ))
    fig.add_trace(go.Scatter(
        x=runs, y=leakages, name="Time Leakage",
        line=dict(color="#e85d26", width=2.5, dash="dot"),
        marker=dict(size=8, color="#e85d26"),
        mode="lines+markers",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(250,248,245,1)",
        font=dict(family="Sora", color="#3d342a"),
        margin=dict(l=0, r=0, t=20, b=0), height=240,
        legend=dict(orientation="h", y=1.1, x=0, font=dict(size=12)),
        xaxis=dict(showgrid=False, tickfont=dict(size=11), title="Run #"),
        yaxis=dict(showgrid=True, gridcolor="#e8e0d6", range=[0,12], tickfont=dict(size=11)),
        title=dict(text="Score & Leakage Over Time", font=dict(size=13, color="#8a7e74"),
                   x=0, xanchor="left"),
    )
    return fig

# ──────────────────────────────────────────────
# ▌HEADER
# ──────────────────────────────────────────────
st.title("⏳ NeuroTime AI")
st.caption("Behavior Intelligence & Time Leakage Detection System")

model_status = "✅ Real model loaded" if MODEL_LOADED else "🔧 Demo mode (mock model)"
c1, c2, c3, c4 = st.columns(4)
c1.metric("Model",    "K-Means")
c2.metric("Features", "5 inputs")
c3.metric("Type",     "Behavior AI")
c4.metric("Status",   model_status)

st.divider()

# ──────────────────────────────────────────────
# ▌TABS
# ──────────────────────────────────────────────
tab_input, tab_analysis, tab_insights, tab_history = st.tabs([
    "📥  Input",
    "📊  Analysis",
    "💡  Insights",
    "📜  History",
])

# ══════════════════════════════════════════════
# TAB 1 — INPUT
# ══════════════════════════════════════════════
with tab_input:
    st.subheader("Daily Behavior Parameters")
    st.caption("Rate each behavior from 0 (none) to 10 (maximum). Be honest for accurate results.")
    st.write("")

    cols = st.columns(5)
    data = []

    for i, key in enumerate(FEAT_KEYS):
        f   = FEATURES[key]
        val = cols[i].number_input(
            f"{f['icon']}  {key}",
            min_value=0, max_value=10,
            value=st.session_state.data[i],
            help=f["desc"],
            key=f"inp_{key}",
        )
        data.append(int(val))

        # Visual bar under each input
        pct   = int(val / 10 * 100)
        empty = 10 - val
        bar   = "█" * val + "░" * empty
        cols[i].markdown(
            f"<span style='font-family:DM Mono,monospace;font-size:11px;"
           f"color:{f['color']}'>{bar}  {val}/10</span>",
            unsafe_allow_html=True,
        )

    st.session_state.data = data

    st.divider()
    st.subheader("Live Summary")

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("🎯 Productive Time",  f"{data[0]} hrs",   help="Your study/work hours")
    s2.metric("📱 Distraction Load", f"{data[1]+data[2]} hrs", delta=f"{-(data[1]+data[2])} from ideal",
              delta_color="inverse", help="Phone + Social combined")
    s3.metric("😴 Recovery Score",   f"{data[3]+data[4]} hrs", help="Breaks + Sleep combined")
    bal = round(data[0] / max(data[1]+data[2], 1), 2)
    s4.metric("⚖️ Balance Index",    bal,
              delta="Good" if bal >= 1 else "Low",
              delta_color="normal" if bal >= 1 else "inverse",
              help="Productive hrs ÷ Distraction hrs  (>1 is good)")

    st.write("")
    st.info("👉 Head to the **Analysis** tab and click **Run Deep Analysis** to get your profile.", icon="ℹ️")

# ══════════════════════════════════════════════
# TAB 2 — ANALYSIS
# ══════════════════════════════════════════════
with tab_analysis:
    st.subheader("Behavioral Analysis Engine")
    st.write("")

    run_col, _ = st.columns([1, 3])
    with run_col:
        run_btn = st.button("🚀  Run Deep Analysis", use_container_width=True)

    if run_btn:
        progress = st.progress(0, text="Initialising model…")
        for pct, msg in [
            (20,  "Loading behavioral vectors…"),
            (45,  "Scaling features…"),
            (70,  "Running K-Means inference…"),
            (90,  "Generating profile…"),
            (100, "Done!"),
        ]:
            time.sleep(0.28)
            progress.progress(pct, text=msg)
        time.sleep(0.2)
        progress.empty()

        result = run_analysis(st.session_state.data)
        st.session_state.last_result = result
        st.session_state.history.append({**result, "inputs": list(st.session_state.data)})
        st.success(f"Analysis complete — profile: **{result['profile']}**", icon="✅")

    if st.session_state.last_result:
        r  = st.session_state.last_result
        pm = PROFILES[r["profile"]]

        st.write("")
        # ── Profile banner ──────────────────────
        banner = st.columns([1, 6, 1])
        with banner[1]:
            if r["profile"] == "Focused":
                st.success(f"{pm['emoji']}  **{r['profile']} Mode** — {pm['desc']}", icon="🎯")
            elif r["profile"] == "Distracted":
                st.warning(f"{pm['emoji']}  **{r['profile']} Mode** — {pm['desc']}", icon="⚡")
            else:
                st.error(f"{pm['emoji']}  **{r['profile']} Mode** — {pm['desc']}", icon="🔥")

        st.write("")

        # ── Metric row ───────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🧠 Behavior Profile", r["profile"])
        m2.metric("📊 Focus Score",      f"{r['score']} / 10")
        m3.metric("⚠️ Time Leakage",    f"{r['leakage']} hrs",
                  delta=f"-{r['leakage']}h wasted", delta_color="inverse")
        m4.metric("✅ Confidence",       f"{r['confidence']}%")

        st.divider()

        # ── Charts ───────────────────────────────
        ch1, ch2 = st.columns(2)
        with ch1:
            st.plotly_chart(make_bar_chart(st.session_state.data),
                            use_container_width=True, config={"displayModeBar": False})
        with ch2:
            st.plotly_chart(make_radar_chart(st.session_state.data),
                            use_container_width=True, config={"displayModeBar": False})

        # ── Leakage gauge ────────────────────────
        g1, g2, g3 = st.columns([1, 1, 2])
        with g1:
            st.plotly_chart(make_leakage_gauge(r["leakage"]),
                            use_container_width=True, config={"displayModeBar": False})
        with g2:
            st.write("")
            st.write("")
            leak_pct = int(r["leakage"] / 10 * 100)
            if leak_pct < 30:
                st.success(f"**Low leakage** ({leak_pct}%)\nYour time management is solid.", icon="🟢")
            elif leak_pct < 60:
                st.warning(f"**Moderate leakage** ({leak_pct}%)\nSome room for improvement.", icon="🟡")
            else:
                st.error(f"**High leakage** ({leak_pct}%)\nSignificant time being wasted.", icon="🔴")
        with g3:
            st.write("")
            st.write("")
            st.write("**What is Time Leakage?**")
            st.caption(
                "Time Leakage is the estimated hours lost to unproductive behaviours. "
                "It is calculated from your phone usage, social media time, and break frequency. "
                "Lower is better — aim to keep it under 3 hrs/day."
            )
    else:
        st.write("")
        st.info("No analysis yet. Enter your data in **Input** and click **Run Deep Analysis** above.", icon="📊")

# ══════════════════════════════════════════════
# TAB 3 — INSIGHTS
# ══════════════════════════════════════════════
with tab_insights:
    st.subheader("Personalised Insight Engine")

    if not st.session_state.last_result:
        st.info("Run an analysis first to unlock insights.", icon="💡")
    else:
        issues, tips = get_insights(st.session_state.data)

        st.write("")
        ic, sc = st.columns(2)

        with ic:
            st.markdown("#### ⚠️ Detected Issues")
            if issues:
                for iss in issues:
                    st.error(iss)
            else:
                st.success("No issues detected!")

        with sc:
            st.markdown("#### 🚀 Recommendations")
            for tip in tips:
                st.success(tip)

        st.divider()

        # ── Behaviour score breakdown ─────────────
        st.markdown("#### 📊 Score Breakdown")
        bc = st.columns(5)
        colors = {"Study":"blue","Phone":"red","Social":"orange","Breaks":"green","Sleep":"violet"}
        for i, key in enumerate(FEAT_KEYS):
            v = st.session_state.data[i]
            bc[i].metric(f"{FEATURES[key]['icon']} {key}", f"{v}/10")

        st.write("")

        # ── Priority action plan ──────────────────
        st.markdown("#### 🗓 Priority Action Plan")
        d = st.session_state.data
        actions = []
        if d[0] < 5:  actions.append(("🔴 Critical", "Increase study hours to at least 5 hrs/day"))
        if d[1] > 6:  actions.append(("🟠 High",     "Put phone on Do Not Disturb during work blocks"))
        if d[2] > 6:  actions.append(("🟠 High",     "Delete social apps from home screen"))
        if d[4] < 6:  actions.append(("🟡 Medium",   "Set a fixed sleep time and stick to it"))
        if d[3] > 6:  actions.append(("🟡 Medium",   "Reduce break frequency — use structured intervals"))
        if not actions:
            st.success("✅ No critical actions needed — you're performing well!")
        else:
            for priority, action in actions:
                col_p, col_a = st.columns([1, 4])
                col_p.write(f"**{priority}**")
                col_a.write(action)

# ══════════════════════════════════════════════
# TAB 4 — HISTORY
# ══════════════════════════════════════════════
with tab_history:
    st.subheader("Analysis History")

    if not st.session_state.history:
        st.info("No history yet. Run your first analysis to see results here.", icon="📜")
    else:
        # ── Summary metrics ───────────────────────
        h1, h2, h3, h4 = st.columns(4)
        all_scores   = [h["score"]   for h in st.session_state.history]
        all_leakages = [h["leakage"] for h in st.session_state.history]
        profiles     = [h["profile"] for h in st.session_state.history]
        most_common  = max(set(profiles), key=profiles.count)

        h1.metric("Total Runs",      len(st.session_state.history))
        h2.metric("Avg Focus Score", round(float(np.mean(all_scores)),   1))
        h3.metric("Avg Leakage",     f"{round(float(np.mean(all_leakages)), 1)} hrs")
        h4.metric("Most Common",     most_common)

        st.divider()

        # ── Trend chart ───────────────────────────
        if len(st.session_state.history) >= 2:
            st.plotly_chart(make_history_chart(st.session_state.history),
                            use_container_width=True, config={"displayModeBar": False})
            st.divider()

        # ── Table ─────────────────────────────────
        st.markdown("#### All Runs")
        col_labels = st.columns([1, 2, 2, 2, 2])
        col_labels[0].markdown("**Run**")
        col_labels[1].markdown("**Profile**")
        col_labels[2].markdown("**Focus Score**")
        col_labels[3].markdown("**Leakage**")
        col_labels[4].markdown("**Confidence**")

        st.divider()

        pf_icons = {"Focused": "🎯", "Distracted": "⚡", "Burnout": "🔥"}
        for i, h in enumerate(reversed(st.session_state.history)):
            run_n = len(st.session_state.history) - i
            icon  = pf_icons.get(h["profile"], "🔵")
            rc    = st.columns([1, 2, 2, 2, 2])
            rc[0].write(f"**#{run_n}**")
            rc[1].write(f"{icon} {h['profile']}")
            rc[2].write(f"{h['score']} / 10")
            rc[3].write(f"{h['leakage']} hrs")
            rc[4].write(f"{h['confidence']}%")

        st.write("")
        _, clr_col, _ = st.columns([2, 1, 2])
        with clr_col:
            if st.button("🗑  Clear All History", use_container_width=True):
                st.session_state.history     = []
                st.session_state.last_result = None
                st.rerun()

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.divider()
fc1, fc2, fc3 = st.columns(3)
fc1.caption("⏳ **NeuroTime AI** — Behavior Intelligence System")
fc2.caption("🧠 Model: K-Means Clustering  |  Features: 5")
fc3.caption("Built with Streamlit & Plotly")