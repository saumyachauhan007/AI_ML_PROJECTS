import streamlit as st
import pickle
import numpy as np
import plotly.graph_objects as go
import time
import os
import requests

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PlacementIQ",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  MODEL LOADING
# ─────────────────────────────────────────────
@st.cache_resource
def load_model():
    try:
        model  = pickle.load(open("model.pkl",  "rb"))
        scaler = pickle.load(open("scaler.pkl", "rb"))
        return model, scaler
    except:
        return None, None

model, scaler = load_model()

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@300;400;600&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #050709 !important;
    color: #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
}

[data-testid="stAppViewContainer"] > .main {
    background: #050709 !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #22d3ee; border-radius: 2px; }

/* ── Typography ── */
.display-font { font-family: 'Syne', sans-serif !important; }

/* ── Animated hero ── */
@keyframes scanline {
    0%   { transform: translateY(-100%); opacity: 0.03; }
    100% { transform: translateY(100vh); opacity: 0.03; }
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0; }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 20px rgba(34,211,238,0.15); }
    50%       { box-shadow: 0 0 40px rgba(34,211,238,0.35); }
}
@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* ── Hero section ── */
.hero-wrapper {
    position: relative;
    overflow: hidden;
    text-align: center;
    padding: 72px 24px 56px;
    border-bottom: 1px solid rgba(34,211,238,0.12);
    margin-bottom: 48px;
    animation: fadeUp 0.8s ease both;
}
.hero-wrapper::before {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(34,211,238,0.015) 2px,
        rgba(34,211,238,0.015) 4px
    );
    pointer-events: none;
}
.hero-scanline {
    position: absolute;
    left: 0; right: 0;
    height: 120px;
    background: linear-gradient(to bottom, transparent, rgba(34,211,238,0.04), transparent);
    animation: scanline 3.5s linear infinite;
    pointer-events: none;
}
.hero-tag {
    display: inline-block;
    font-size: 10px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #22d3ee;
    border: 1px solid rgba(34,211,238,0.3);
    padding: 5px 16px;
    border-radius: 2px;
    margin-bottom: 20px;
    background: rgba(34,211,238,0.05);
}
.hero-title {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(40px, 6vw, 76px);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -2px;
    color: #f1f5f9;
    margin-bottom: 16px;
}
.hero-title span {
    background: linear-gradient(90deg, #22d3ee, #818cf8, #22d3ee);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite;
}
.hero-sub {
    font-size: 14px;
    color: #64748b;
    letter-spacing: 1px;
    margin-bottom: 0;
}
.cursor-blink {
    display: inline-block;
    width: 10px;
    height: 18px;
    background: #22d3ee;
    vertical-align: middle;
    margin-left: 4px;
    animation: blink 1s step-end infinite;
}

/* ── Step indicator ── */
.step-bar {
    display: flex;
    justify-content: center;
    gap: 0;
    margin-bottom: 40px;
    animation: fadeUp 0.8s 0.2s ease both;
    opacity: 0;
    animation-fill-mode: forwards;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 24px;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #334155;
    border: 1px solid #1e293b;
    cursor: default;
    transition: all 0.3s;
    position: relative;
}
.step-item.active {
    color: #22d3ee;
    border-color: rgba(34,211,238,0.4);
    background: rgba(34,211,238,0.05);
    animation: glowPulse 2s ease-in-out infinite;
}
.step-item.done {
    color: #4ade80;
    border-color: rgba(74,222,128,0.3);
    background: rgba(74,222,128,0.04);
}
.step-num {
    font-size: 18px;
    font-weight: 700;
    font-family: 'Syne', sans-serif;
}

/* ── Section label ── */
.section-label {
    font-size: 10px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #22d3ee;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, rgba(34,211,238,0.3), transparent);
}
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 28px;
    letter-spacing: -0.5px;
}

/* ── Cards ── */
.card {
    background: rgba(15,23,42,0.7);
    border: 1px solid #1e293b;
    border-radius: 4px;
    padding: 28px;
    margin-bottom: 16px;
    transition: border-color 0.3s, box-shadow 0.3s;
    animation: fadeUp 0.6s ease both;
}
.card:hover {
    border-color: rgba(34,211,238,0.25);
    box-shadow: 0 0 30px rgba(34,211,238,0.06);
}

/* ── Slider customization ── */
.stSlider > div > div > div > div {
    background: linear-gradient(to right, #22d3ee, #818cf8) !important;
    height: 4px !important;
    border-radius: 2px !important;
}
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: #22d3ee !important;
    border: 2px solid #050709 !important;
    width: 14px !important;
    height: 14px !important;
}
.stSlider label {
    color: #94a3b8 !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* ── Number input ── */
.stNumberInput label {
    color: #94a3b8 !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
.stNumberInput input {
    background: #0d1117 !important;
    border: 1px solid #1e293b !important;
    border-radius: 4px !important;
    color: #22d3ee !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 20px !important;
    font-weight: 600 !important;
}
.stNumberInput input:focus {
    border-color: rgba(34,211,238,0.5) !important;
    box-shadow: 0 0 0 2px rgba(34,211,238,0.1) !important;
}

/* ── Select box ── */
.stSelectbox label {
    color: #94a3b8 !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
[data-baseweb="select"] > div {
    background: #0d1117 !important;
    border: 1px solid #1e293b !important;
    border-radius: 4px !important;
    color: #f1f5f9 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-baseweb="select"] > div:hover {
    border-color: rgba(34,211,238,0.4) !important;
}
[data-baseweb="menu"] {
    background: #0d1117 !important;
    border: 1px solid rgba(34,211,238,0.2) !important;
}
[data-baseweb="menu"] li {
    color: #94a3b8 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}
[data-baseweb="menu"] li:hover {
    background: rgba(34,211,238,0.08) !important;
    color: #22d3ee !important;
}

/* ── Radio ── */
.stRadio label {
    color: #94a3b8 !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stRadio [data-baseweb="radio"] span:first-child {
    border-color: #334155 !important;
    background: transparent !important;
}
.stRadio [aria-checked="true"] span:first-child {
    background: #22d3ee !important;
    border-color: #22d3ee !important;
}

/* ── Buttons ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #0e7490, #1e40af) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 16px 32px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    transition: all 0.3s !important;
    position: relative;
    overflow: hidden;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 40px rgba(14,116,144,0.5) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Secondary button */
.btn-secondary > button {
    background: rgba(34,211,238,0.05) !important;
    border: 1px solid rgba(34,211,238,0.3) !important;
    color: #22d3ee !important;
}
.btn-secondary > button:hover {
    background: rgba(34,211,238,0.1) !important;
    box-shadow: 0 0 20px rgba(34,211,238,0.2) !important;
}

/* ── Metric cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-bottom: 32px;
}
.metric-card {
    background: #0d1117;
    border: 1px solid #1e293b;
    border-radius: 4px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    animation: fadeUp 0.5s ease both;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(to right, #22d3ee, #818cf8);
}
.metric-label {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 10px;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: #f1f5f9;
    line-height: 1;
}
.metric-value .unit {
    font-size: 14px;
    color: #64748b;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 400;
    margin-left: 4px;
}
.metric-badge {
    display: inline-block;
    margin-top: 8px;
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 2px;
}
.badge-green  { background: rgba(74,222,128,0.1);  color: #4ade80; }
.badge-yellow { background: rgba(250,204,21,0.1);  color: #facc15; }
.badge-red    { background: rgba(239,68,68,0.1);   color: #ef4444; }
.badge-blue   { background: rgba(34,211,238,0.1);  color: #22d3ee; }

/* ── Skill bar ── */
.skill-row {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 14px;
    animation: fadeUp 0.5s ease both;
}
.skill-label {
    width: 130px;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #64748b;
    flex-shrink: 0;
}
.skill-track {
    flex: 1;
    height: 6px;
    background: #1e293b;
    border-radius: 3px;
    overflow: hidden;
    position: relative;
}
.skill-fill {
    height: 100%;
    border-radius: 3px;
    position: relative;
    transition: width 1s cubic-bezier(0.4,0,0.2,1);
}
.skill-fill::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 6px; height: 100%;
    background: rgba(255,255,255,0.4);
    border-radius: 50%;
    filter: blur(2px);
}
.skill-score {
    width: 36px;
    font-size: 13px;
    font-weight: 600;
    color: #94a3b8;
    text-align: right;
    flex-shrink: 0;
}

/* ── AI feedback box ── */
.ai-feedback {
    background: #050c14;
    border: 1px solid rgba(34,211,238,0.2);
    border-left: 3px solid #22d3ee;
    border-radius: 4px;
    padding: 24px;
    font-size: 13px;
    line-height: 1.9;
    color: #94a3b8;
    white-space: pre-wrap;
    animation: fadeUp 0.6s ease both;
}
.ai-feedback strong, .ai-feedback b { color: #22d3ee; }

/* ── Terminal output ── */
.terminal {
    background: #050c14;
    border: 1px solid #1e293b;
    border-radius: 4px;
    padding: 20px;
    font-size: 12px;
    line-height: 2;
    color: #4ade80;
}
.terminal .t-comment { color: #334155; }
.terminal .t-key     { color: #22d3ee; }
.terminal .t-val     { color: #f1f5f9; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1e293b !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #475569 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 12px 24px !important;
    border: none !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #22d3ee !important;
    border-bottom: 2px solid #22d3ee !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 28px !important;
}

/* ── Dividers ── */
hr { border-color: #1e293b !important; margin: 36px 0 !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    color: #64748b !important;
    background: #0d1117 !important;
    border: 1px solid #1e293b !important;
    border-radius: 4px !important;
    padding: 12px 16px !important;
}
.streamlit-expanderContent {
    background: #0d1117 !important;
    border: 1px solid #1e293b !important;
    border-top: none !important;
    border-radius: 0 0 4px 4px !important;
}

/* ── Plotly overrides ── */
.js-plotly-plot .plotly .bg { fill: transparent !important; }

/* ── Info / warning / success ── */
.stAlert {
    background: #0d1117 !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}

/* ── Padding fix ── */
.block-container { padding: 0 40px 80px !important; max-width: 1400px !important; }

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
def _init():
    defaults = dict(
        step=1,
        basics={},
        coding_scores={},
        dsa_scores={},
        comm_scores={},
        result=None,
        overall=None,
        ai_feedback=None,
        show_results=False,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
CYAN   = "#22d3ee"
INDIGO = "#818cf8"
GREEN  = "#4ade80"
AMBER  = "#facc15"
RED    = "#ef4444"

def skill_bar_html(label, score, color=CYAN, delay=0):
    pct = int(score * 10)
    return f"""
    <div class="skill-row" style="animation-delay:{delay}s">
        <div class="skill-label">{label}</div>
        <div class="skill-track">
            <div class="skill-fill" style="width:{pct}%;background:linear-gradient(to right,{color},{color}88);"></div>
        </div>
        <div class="skill-score">{score:.1f}</div>
    </div>"""

def metric_card_html(label, value, unit="", badge_text="", badge_class="badge-blue", delay=0):
    return f"""
    <div class="metric-card" style="animation-delay:{delay}s">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}<span class="unit">{unit}</span></div>
        {"<span class='metric-badge "+badge_class+"'>"+badge_text+"</span>" if badge_text else ""}
    </div>"""

def get_level(score):
    if score >= 12: return ("HIGH TIER",   "badge-green",  GREEN)
    if score >= 7:  return ("MID TIER",    "badge-yellow", AMBER)
    return               ("ENTRY TIER",   "badge-red",    RED)

def get_ai_feedback(cgpa, coding, dsa, comm, readiness, predicted_lpa, branch, years_exp):
    """Call Anthropic API for personalized feedback."""
    try:
        prompt = f"""You are a senior campus placement advisor. A student has used a placement predictor tool.

Here are their stats:
- CGPA: {cgpa}
- Coding Skills (avg 1-10): {coding:.1f}
- DSA Skills (avg 1-10): {dsa:.1f}
- Communication Skills (avg 1-10): {comm:.1f}
- Interview Readiness (1-10): {readiness}
- Branch: {branch}
- Internship/Project Experience: {years_exp}
- Model-predicted salary: {predicted_lpa:.1f} LPA

Write a sharp, brutally honest yet motivating placement report in 4 sections:
1. **PROFILE ASSESSMENT** — 2 sentences on their overall standing
2. **CRITICAL GAPS** — top 2-3 specific weaknesses with exact action items (be specific: e.g. "Solve 3 DP problems daily on Codeforces for 30 days")
3. **STRENGTHS TO LEVERAGE** — what they should highlight in interviews
4. **30-DAY SPRINT PLAN** — a concrete week-by-week micro-plan

Keep it under 280 words. Use plain text (no markdown). Be direct, like a mentor who doesn't sugarcoat things."""

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30,
        )
        data = response.json()
        if "content" in data:
            return data["content"][0]["text"]
        return None
    except Exception as e:
        return f"Could not generate AI feedback: {e}"

# ─────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
    <div class="hero-scanline"></div>
    <div class="hero-tag">◈ Placement Intelligence System v2.0</div>
    <h1 class="hero-title">Know your worth<br><span>before they decide it.</span></h1>
    <p class="hero-sub">Multi-dimensional placement analysis · AI-powered coaching · Real-time insights</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  STEP INDICATOR
# ─────────────────────────────────────────────
step = st.session_state.step

def step_cls(n):
    if n < step:  return "done"
    if n == step: return "active"
    return ""

steps = [
    (1, "01", "Profile"),
    (2, "02", "Coding"),
    (3, "03", "DSA"),
    (4, "04", "Communication"),
    (5, "05", "Results"),
]
bar_html = '<div class="step-bar">'
for n, num, label in steps:
    cls = step_cls(n)
    bar_html += f'<div class="step-item {cls}"><span class="step-num">{num}</span>{label}</div>'
bar_html += "</div>"
st.markdown(bar_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  STEP 1 — BASIC PROFILE
# ─────────────────────────────────────────────
if step == 1:
    st.markdown('<div class="section-label">Step 01 — Foundation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Build your academic profile</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=7.5, step=0.1, format="%.1f")
        with col2:
            branch = st.selectbox("Branch / Specialization", [
                "Computer Science", "Information Technology", "Electronics",
                "Mechanical", "Civil", "Electrical", "Chemical", "Data Science",
                "AI / ML", "Other"
            ])
        with col3:
            grad_year = st.selectbox("Graduation Year", [2024, 2025, 2026, 2027])

        col4, col5 = st.columns(2)
        with col4:
            experience = st.selectbox("Internship / Project Experience", [
                "None", "1 Project", "2–3 Projects", "1 Internship",
                "2+ Internships", "Research / Publication"
            ])
        with col5:
            readiness = st.slider("Interview Readiness", 1, 10, 5,
                                  help="Self-rate: mock interviews, company research, resume quality")

        backlogs = st.radio("Active Backlogs?", ["None", "1–2", "3+"], horizontal=True)

        st.markdown('</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("CONTINUE → CODING SKILLS", key="btn1"):
            st.session_state.basics = dict(
                cgpa=cgpa, branch=branch, grad_year=grad_year,
                experience=experience, readiness=readiness, backlogs=backlogs
            )
            st.session_state.step = 2
            st.rerun()

# ─────────────────────────────────────────────
#  STEP 2 — CODING
# ─────────────────────────────────────────────
elif step == 2:
    st.markdown('<div class="section-label">Step 02 — Technical Core</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Evaluate your coding intelligence</div>', unsafe_allow_html=True)

    coding_dims = {
        "Problem Solving":     "Breaking down problems, pattern recognition",
        "Code Quality":        "Clean code, naming, structure, readability",
        "Debugging Speed":     "Finding & fixing bugs under time pressure",
        "Practice Consistency":"Daily practice frequency, contest participation",
        "Language Proficiency":"Depth in your primary language (C++/Java/Python)",
    }

    st.markdown('<div class="card">', unsafe_allow_html=True)

    scores = {}
    for dim, hint in coding_dims.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            scores[dim] = st.slider(dim, 1, 10, 5, help=hint, key=f"c_{dim}")
        with col2:
            val = scores[dim]
            color = GREEN if val >= 7 else AMBER if val >= 4 else RED
            st.markdown(f"<div style='padding-top:28px;font-family:Syne,sans-serif;font-size:24px;font-weight:800;color:{color}'>{val}</div>", unsafe_allow_html=True)

    avg = np.mean(list(scores.values()))
    st.markdown(f"""
    <div style="margin-top:20px;padding:14px 20px;background:#0d1117;border:1px solid #1e293b;border-radius:4px;display:flex;justify-content:space-between;align-items:center">
        <span style="font-size:11px;letter-spacing:2px;color:#475569;text-transform:uppercase">Coding Average</span>
        <span style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:{GREEN if avg>=7 else AMBER if avg>=5 else RED}">{avg:.2f}<span style="font-size:14px;color:#475569;font-family:'JetBrains Mono',monospace"> / 10</span></span>
    </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("← BACK", key="btn2b"):
            st.session_state.step = 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        if st.button("CONTINUE → DSA DEPTH", key="btn2"):
            st.session_state.coding_scores = scores
            st.session_state.step = 3
            st.rerun()

# ─────────────────────────────────────────────
#  STEP 3 — DSA
# ─────────────────────────────────────────────
elif step == 3:
    st.markdown('<div class="section-label">Step 03 — Algorithmic Depth</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Rate your DSA mastery</div>', unsafe_allow_html=True)

    dsa_dims = {
        "Arrays & Strings":        "1D/2D arrays, sliding window, two-pointer",
        "Linked Lists & Stacks":   "Reversal, cycle detection, monotonic stacks",
        "Trees & Graphs":          "BFS, DFS, Dijkstra, Union-Find",
        "Dynamic Programming":     "Memoization, tabulation, classic DP problems",
        "Searching & Sorting":     "Binary search, merge sort, quick select",
        "Complexity Analysis":     "Big-O space & time reasoning during interviews",
    }

    st.markdown('<div class="card">', unsafe_allow_html=True)

    scores = {}
    for dim, hint in dsa_dims.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            scores[dim] = st.slider(dim, 1, 10, 5, help=hint, key=f"d_{dim}")
        with col2:
            val = scores[dim]
            color = GREEN if val >= 7 else AMBER if val >= 4 else RED
            st.markdown(f"<div style='padding-top:28px;font-family:Syne,sans-serif;font-size:24px;font-weight:800;color:{color}'>{val}</div>", unsafe_allow_html=True)

    avg = np.mean(list(scores.values()))
    st.markdown(f"""
    <div style="margin-top:20px;padding:14px 20px;background:#0d1117;border:1px solid #1e293b;border-radius:4px;display:flex;justify-content:space-between;align-items:center">
        <span style="font-size:11px;letter-spacing:2px;color:#475569;text-transform:uppercase">DSA Average</span>
        <span style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:{GREEN if avg>=7 else AMBER if avg>=5 else RED}">{avg:.2f}<span style="font-size:14px;color:#475569;font-family:'JetBrains Mono',monospace"> / 10</span></span>
    </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("← BACK", key="btn3b"):
            st.session_state.step = 2
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        if st.button("CONTINUE → COMMUNICATION", key="btn3"):
            st.session_state.dsa_scores = scores
            st.session_state.step = 4
            st.rerun()

# ─────────────────────────────────────────────
#  STEP 4 — COMMUNICATION
# ─────────────────────────────────────────────
elif step == 4:
    st.markdown('<div class="section-label">Step 04 — Soft Skills</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">How well do you communicate?</div>', unsafe_allow_html=True)

    comm_dims = {
        "Verbal Confidence":    "Speaking clearly, pace, filler words",
        "Structured Answers":   "STAR method, logical flow in responses",
        "Technical Explaining": "Breaking down code/concepts to interviewers",
        "Group Discussion":     "Handling GDs, debates, leadership moments",
        "Listening & Empathy":  "Understanding questions before answering",
    }

    st.markdown('<div class="card">', unsafe_allow_html=True)

    scores = {}
    for dim, hint in comm_dims.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            scores[dim] = st.slider(dim, 1, 10, 5, help=hint, key=f"cm_{dim}")
        with col2:
            val = scores[dim]
            color = GREEN if val >= 7 else AMBER if val >= 4 else RED
            st.markdown(f"<div style='padding-top:28px;font-family:Syne,sans-serif;font-size:24px;font-weight:800;color:{color}'>{val}</div>", unsafe_allow_html=True)

    avg = np.mean(list(scores.values()))
    st.markdown(f"""
    <div style="margin-top:20px;padding:14px 20px;background:#0d1117;border:1px solid #1e293b;border-radius:4px;display:flex;justify-content:space-between;align-items:center">
        <span style="font-size:11px;letter-spacing:2px;color:#475569;text-transform:uppercase">Communication Average</span>
        <span style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:{GREEN if avg>=7 else AMBER if avg>=5 else RED}">{avg:.2f}<span style="font-size:14px;color:#475569;font-family:'JetBrains Mono',monospace"> / 10</span></span>
    </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("← BACK", key="btn4b"):
            st.session_state.step = 3
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        if st.button("⚡ GENERATE FULL ANALYSIS", key="btn4"):
            st.session_state.comm_scores = scores
            st.session_state.step = 5
            st.rerun()

# ─────────────────────────────────────────────
#  STEP 5 — RESULTS
# ─────────────────────────────────────────────
elif step == 5:
    b      = st.session_state.basics
    coding = np.mean(list(st.session_state.coding_scores.values()))
    dsa    = np.mean(list(st.session_state.dsa_scores.values()))
    comm   = np.mean(list(st.session_state.comm_scores.values()))
    readiness = b["readiness"]
    cgpa       = b["cgpa"]
    overall    = round((coding + dsa + comm + readiness) / 4, 2)

    # CGPA penalty for backlogs
    effective_cgpa = cgpa
    if b["backlogs"] == "3+":     effective_cgpa -= 0.5
    elif b["backlogs"] == "1–2":  effective_cgpa -= 0.2

    # Experience bonus
    exp_map = {"None":0,"1 Project":0.3,"2–3 Projects":0.6,
               "1 Internship":1.0,"2+ Internships":1.8,"Research / Publication":2.0}
    exp_bonus = exp_map.get(b["experience"], 0)

    # Model prediction or fallback formula
    if model and scaler:
        try:
            X = np.array([[effective_cgpa, coding, dsa, comm, readiness]])
            X_scaled = scaler.transform(X)
            predicted = float(model.predict(X_scaled)[0]) + exp_bonus
        except:
            predicted = round(overall * 1.8 + effective_cgpa * 0.6 + exp_bonus, 2)
    else:
        predicted = round(overall * 1.8 + effective_cgpa * 0.6 + exp_bonus, 2)

    predicted = round(max(2.0, min(predicted, 45.0)), 2)
    level_text, badge_cls, level_color = get_level(predicted)

    st.session_state.result  = predicted
    st.session_state.overall = overall

    # ── Header ──
    st.markdown('<div class="section-label">Step 05 — Intelligence Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Your placement blueprint</div>', unsafe_allow_html=True)

    # ── Terminal summary ──
    st.markdown(f"""
    <div class="terminal">
        <span class="t-comment">// PlacementIQ · Analysis Complete · {time.strftime("%Y-%m-%d %H:%M")}</span><br>
        <span class="t-key">candidate.branch</span>     = <span class="t-val">"{b['branch']}"</span><br>
        <span class="t-key">candidate.cgpa</span>        = <span class="t-val">{cgpa}</span><br>
        <span class="t-key">candidate.experience</span>  = <span class="t-val">"{b['experience']}"</span><br>
        <span class="t-key">scores.coding</span>         = <span class="t-val">{coding:.2f}</span><br>
        <span class="t-key">scores.dsa</span>            = <span class="t-val">{dsa:.2f}</span><br>
        <span class="t-key">scores.communication</span>  = <span class="t-val">{comm:.2f}</span><br>
        <span class="t-key">scores.readiness</span>      = <span class="t-val">{readiness}</span><br>
        <span class="t-key">prediction.salary_lpa</span> = <span class="t-val">{predicted} ▸ {level_text}</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Metric cards ──
    st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
    st.markdown(
        metric_card_html("Predicted Salary", f"{predicted}", "LPA", level_text, badge_cls, 0) +
        metric_card_html("Profile Score",    f"{overall}",   "/10", "Overall", "badge-blue", 0.1) +
        metric_card_html("CGPA",             f"{cgpa}",      "",    "Academic", "badge-blue", 0.2) +
        metric_card_html("Coding Index",     f"{coding:.1f}","/10", "Technical", "badge-blue", 0.3) +
        metric_card_html("DSA Index",        f"{dsa:.1f}",   "/10", "Algorithmic", "badge-blue", 0.4) +
        metric_card_html("Comm Index",       f"{comm:.1f}",  "/10", "Soft Skills", "badge-blue", 0.5),
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs(["◈ RADAR", "◈ BREAKDOWN", "◈ COMPARISONS", "◈ AI MENTOR"])

    # ── Tab 1: Radar ──
    with tab1:
        categories = ["Coding", "DSA", "Communication", "Readiness", "CGPA/10"]
        vals = [coding, dsa, comm, readiness, cgpa]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(34,211,238,0.08)",
            line=dict(color=CYAN, width=2),
            name="Your Profile"
        ))
        # Benchmark overlay
        bench = [7.5, 7.0, 6.5, 7.0, 8.0]
        fig_radar.add_trace(go.Scatterpolar(
            r=bench + [bench[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(129,140,248,0.04)",
            line=dict(color=INDIGO, width=1.5, dash="dot"),
            name="Industry Benchmark"
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0,10], tickcolor="#1e293b",
                                gridcolor="#1e293b", linecolor="#1e293b",
                                tickfont=dict(color="#475569", size=10)),
                angularaxis=dict(tickcolor="#1e293b", gridcolor="#1e293b",
                                 linecolor="#1e293b", tickfont=dict(color="#64748b", size=11))
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color="#64748b", size=11), bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=40, b=40, l=40, r=40),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ── Tab 2: Skill breakdown ──
    with tab2:
        st.markdown('<div class="section-label" style="margin-bottom:24px">Coding Skills</div>', unsafe_allow_html=True)
        bars = ""
        for i, (k, v) in enumerate(st.session_state.coding_scores.items()):
            bars += skill_bar_html(k, v, CYAN, i * 0.08)
        st.markdown(bars, unsafe_allow_html=True)

        st.markdown('<br><div class="section-label" style="margin-bottom:24px">DSA Skills</div>', unsafe_allow_html=True)
        bars = ""
        for i, (k, v) in enumerate(st.session_state.dsa_scores.items()):
            bars += skill_bar_html(k, v, INDIGO, i * 0.08)
        st.markdown(bars, unsafe_allow_html=True)

        st.markdown('<br><div class="section-label" style="margin-bottom:24px">Communication Skills</div>', unsafe_allow_html=True)
        bars = ""
        for i, (k, v) in enumerate(st.session_state.comm_scores.items()):
            bars += skill_bar_html(k, v, GREEN, i * 0.08)
        st.markdown(bars, unsafe_allow_html=True)

    # ── Tab 3: Comparisons ──
    with tab3:
        fig_bar = go.Figure()
        labels  = ["Coding", "DSA", "Communication", "Readiness"]
        user_v  = [coding, dsa, comm, readiness]
        bench_v = [7.5, 7.0, 6.5, 7.0]

        fig_bar.add_trace(go.Bar(
            name="Your Score", x=labels, y=user_v,
            marker_color=[CYAN, INDIGO, GREEN, AMBER],
            marker_line_width=0, width=0.3
        ))
        fig_bar.add_trace(go.Bar(
            name="Benchmark", x=labels, y=bench_v,
            marker_color="rgba(255,255,255,0.06)",
            marker_line=dict(color="rgba(255,255,255,0.15)", width=1),
            width=0.3
        ))
        fig_bar.update_layout(
            barmode="overlay",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono", color="#64748b", size=11),
            xaxis=dict(tickcolor="#1e293b", gridcolor="rgba(0,0,0,0)", linecolor="#1e293b"),
            yaxis=dict(tickcolor="#1e293b", gridcolor="#1e293b", linecolor="rgba(0,0,0,0)", range=[0,10]),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#64748b")),
            margin=dict(t=20, b=20),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Salary range gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=predicted,
            delta={"reference": 7.0, "valueformat": ".1f",
                   "increasing": {"color": GREEN}, "decreasing": {"color": RED}},
            number={"suffix": " LPA", "font": {"size": 36, "color": "#f1f5f9",
                                                "family": "Syne"}},
            title={"text": "Predicted Package", "font": {"color": "#64748b", "size": 13, "family": "JetBrains Mono"}},
            gauge={
                "axis": {"range": [0, 40], "tickcolor": "#334155",
                         "tickfont": {"color": "#475569", "size": 10}},
                "bar":  {"color": level_color, "thickness": 0.25},
                "bgcolor": "#0d1117",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  6],  "color": "#0d1117"},
                    {"range": [6,  12], "color": "#111827"},
                    {"range": [12, 40], "color": "#0f2318"},
                ],
                "threshold": {
                    "line": {"color": "#22d3ee", "width": 2},
                    "thickness": 0.75,
                    "value": predicted
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="JetBrains Mono"),
            margin=dict(t=40, b=20),
            height=300,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # ── Tab 4: AI Mentor ──
    with tab4:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
            <div style="width:8px;height:8px;background:#4ade80;border-radius:50%;box-shadow:0 0 8px #4ade80;animation:glowPulse 2s infinite"></div>
            <span style="font-size:11px;letter-spacing:2px;color:#64748b;text-transform:uppercase">AI Mentor Connected</span>
        </div>""", unsafe_allow_html=True)

        if st.session_state.ai_feedback is None:
            if st.button("⚡ GENERATE AI MENTOR FEEDBACK", key="ai_btn"):
                with st.spinner("Analysing your profile..."):
                    feedback = get_ai_feedback(
                        cgpa, coding, dsa, comm, readiness,
                        predicted, b["branch"], b["experience"]
                    )
                    st.session_state.ai_feedback = feedback
                    st.rerun()
        else:
            st.markdown(f'<div class="ai-feedback">{st.session_state.ai_feedback}</div>',
                        unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("↺ REGENERATE FEEDBACK", key="regen"):
                st.session_state.ai_feedback = None
                st.rerun()

    st.markdown("---")

    # ── Recommendations ──
    st.markdown('<div class="section-label" style="margin-bottom:16px">Quick Diagnostics</div>', unsafe_allow_html=True)

    weaknesses = []
    if coding < 6:     weaknesses.append(("Coding", "LeetCode 75 list, daily contest participation"))
    if dsa < 6:        weaknesses.append(("DSA", "Striver's A2Z sheet, focus on DP & Graphs"))
    if comm < 6:       weaknesses.append(("Communication", "Mock GDs on YouTube, Pramp.com for mock interviews"))
    if readiness < 6:  weaknesses.append(("Interview Prep", "Glassdoor company-specific prep, STAR method practice"))
    if cgpa < 6.5:     weaknesses.append(("CGPA", "Supplement with strong projects / internships to compensate"))

    if not weaknesses:
        st.markdown(f"""
        <div style="background:rgba(74,222,128,0.05);border:1px solid rgba(74,222,128,0.2);border-radius:4px;padding:20px;color:#4ade80;font-size:13px;letter-spacing:1px">
            ✓ All dimensions above threshold. Focus on company-specific prep and competitive programming.
        </div>""", unsafe_allow_html=True)
    else:
        cols = st.columns(len(weaknesses))
        for i, (area, fix) in enumerate(weaknesses):
            with cols[i]:
                st.markdown(f"""
                <div style="background:#0d1117;border:1px solid #1e293b;border-top:2px solid {AMBER};border-radius:4px;padding:16px">
                    <div style="font-size:10px;letter-spacing:2px;color:{AMBER};text-transform:uppercase;margin-bottom:8px">⚠ {area}</div>
                    <div style="font-size:12px;color:#64748b;line-height:1.7">{fix}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("← EDIT INPUTS", key="back_btn"):
            st.session_state.step = 4
            st.session_state.ai_feedback = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        if st.button("↺ START NEW ANALYSIS", key="reset_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()