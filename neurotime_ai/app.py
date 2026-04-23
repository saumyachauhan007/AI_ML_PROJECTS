#!/usr/bin/env python3
"""
NeuroTime AI — Behavior Intelligence & Time Leakage Detection System
Run with:  python neurotime_ai.py
Then open: http://localhost:8080
"""

import http.server
import json
import random
import math
import urllib.parse
from http import HTTPStatus

# ─────────────────────────────────────────────────────
# MOCK MODEL  (drop-in replace with real pickle model)
# ─────────────────────────────────────────────────────
def predict_cluster(data):
    study, phone, social, breaks, sleep = data
    if study >= 7:
        return 0   # Focused
    elif sleep < 4:
        return 2   # Burnout
    else:
        return 1   # Distracted

def run_analysis(data):
    cluster = predict_cluster(data)
    labels  = ["Focused", "Distracted", "Burnout"]
    leakage = round(data[1] * 0.3 + data[2] * 0.4 + data[3] * 0.2, 1)
    return {
        "profile":    labels[cluster],
        "score":      round(sum(data) / len(data), 1),
        "leakage":    leakage,
        "confidence": random.randint(87, 98),
    }

def get_insights(data):
    study, phone, social, breaks, sleep = data
    issues, tips = [], []
    if phone  > 7: issues.append("📱 High phone screen time");       tips.append("⏱ Use app timers — cut phone by 30 %")
    if social > 7: issues.append("🌐 Social media overload");        tips.append("📅 Batch social media to 2 blocks/day")
    if sleep  < 5: issues.append("😴 Sleep deficit detected");       tips.append("🛌 Aim for 7–8 hrs with consistent schedule")
    if breaks > 7: issues.append("☕ Too many breaks");              tips.append("🍅 Try Pomodoro: 25 min work / 5 min break")
    if study  < 3: issues.append("📚 Study time critically low");    tips.append("🌅 Protect a 3-hr deep-work morning block")
    if not tips:   tips.append("✅ Excellent habits — keep it up!")
    return issues, tips

# ─────────────────────────────────────────────────────
# HTML  (full single-page app)
# ─────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>NeuroTime AI</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet"/>
<style>
/* ── RESET & BASE ── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:          #0b0f1a;
  --bg2:         #111827;
  --bg3:         #1a2235;
  --card:        #141c2e;
  --card2:       #1e2d44;
  --border:      rgba(255,255,255,0.07);
  --accent:      #00d4ff;
  --accent2:     #7c3aed;
  --accent3:     #f59e0b;
  --green:       #10b981;
  --red:         #ef4444;
  --orange:      #f97316;
  --text:        #e2e8f0;
  --text2:       #94a3b8;
  --text3:       #64748b;
  --glow:        0 0 40px rgba(0,212,255,0.12);
  --glow-strong: 0 0 60px rgba(0,212,255,0.22);
  --r:           16px;
  --r2:          24px;
  --font:        'Space Grotesk',sans-serif;
  --mono:        'JetBrains Mono',monospace;
}
html{scroll-behavior:smooth}
body{
  font-family:var(--font);
  background:var(--bg);
  color:var(--text);
  min-height:100vh;
  overflow-x:hidden;
}

/* ── ANIMATED BACKGROUND ── */
body::before{
  content:'';
  position:fixed;inset:0;
  background:
    radial-gradient(ellipse 80% 50% at 20% 10%, rgba(0,212,255,0.06) 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(124,58,237,0.07) 0%, transparent 60%),
    radial-gradient(ellipse 40% 60% at 50% 50%, rgba(245,158,11,0.03) 0%, transparent 70%);
  pointer-events:none;z-index:0;
  animation:bgPulse 8s ease-in-out infinite alternate;
}
@keyframes bgPulse{
  from{opacity:.6}
  to{opacity:1}
}

/* ── LAYOUT ── */
.wrapper{position:relative;z-index:1;max-width:1200px;margin:0 auto;padding:0 24px 80px}

/* ── HEADER ── */
header{
  padding:40px 0 32px;
  display:flex;align-items:center;gap:16px;
  animation:slideDown .6s ease both;
}
@keyframes slideDown{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
.logo-ring{
  width:54px;height:54px;border-radius:50%;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  display:grid;place-items:center;font-size:24px;
  box-shadow:var(--glow-strong);
  animation:spin 12s linear infinite;
}
@keyframes spin{to{filter:hue-rotate(360deg)}}
.header-text h1{font-size:2rem;font-weight:800;letter-spacing:-.03em;line-height:1}
.header-text h1 span{
  background:linear-gradient(90deg,var(--accent),var(--accent2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.header-text p{color:var(--text2);font-size:.85rem;margin-top:4px;font-family:var(--mono)}

/* ── STATUS BAR ── */
.status-bar{
  display:grid;grid-template-columns:repeat(4,1fr);gap:12px;
  margin-bottom:32px;
  animation:fadeUp .5s .2s ease both;
}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
.stat-card{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--r);padding:16px 20px;
  transition:border-color .3s,box-shadow .3s;
}
.stat-card:hover{border-color:rgba(0,212,255,.25);box-shadow:var(--glow)}
.stat-card .label{font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text3);margin-bottom:6px}
.stat-card .value{font-size:1.1rem;font-weight:700;font-family:var(--mono);color:var(--accent)}

/* ── TABS ── */
.tab-row{
  display:flex;gap:6px;margin-bottom:28px;
  border-bottom:1px solid var(--border);padding-bottom:0;
  animation:fadeUp .5s .3s ease both;
}
.tab-btn{
  background:transparent;border:none;cursor:pointer;
  color:var(--text2);font-family:var(--font);font-size:.9rem;font-weight:600;
  padding:12px 20px;border-radius:var(--r) var(--r) 0 0;
  position:relative;transition:color .2s;
  white-space:nowrap;
}
.tab-btn::after{
  content:'';position:absolute;bottom:-1px;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--accent),var(--accent2));
  transform:scaleX(0);transition:transform .25s;border-radius:2px;
}
.tab-btn:hover{color:var(--text)}
.tab-btn.active{color:var(--accent)}
.tab-btn.active::after{transform:scaleX(1)}
.tab-panel{display:none;animation:tabFade .35s ease}
.tab-panel.active{display:block}
@keyframes tabFade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* ── SECTION TITLE ── */
.sec-title{font-size:1.3rem;font-weight:700;margin-bottom:6px}
.sec-sub{color:var(--text2);font-size:.85rem;margin-bottom:24px}

/* ── INPUT GRID ── */
.input-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:32px}
.inp-card{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--r2);padding:20px 16px;
  transition:border-color .3s,box-shadow .3s,transform .2s;
  cursor:default;
}
.inp-card:hover{
  border-color:rgba(0,212,255,.3);
  box-shadow:var(--glow);
  transform:translateY(-2px);
}
.inp-card .inp-icon{font-size:1.6rem;margin-bottom:10px}
.inp-card .inp-label{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--text2);margin-bottom:12px}
.inp-card .slider-wrap{position:relative}
.inp-card input[type=range]{
  width:100%;-webkit-appearance:none;appearance:none;
  height:6px;border-radius:3px;outline:none;cursor:pointer;
  background:var(--bg3);
  transition:background .2s;
}
.inp-card input[type=range]::-webkit-slider-thumb{
  -webkit-appearance:none;appearance:none;
  width:18px;height:18px;border-radius:50%;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  cursor:pointer;box-shadow:0 0 10px rgba(0,212,255,.5);
  transition:transform .15s;
}
.inp-card input[type=range]::-webkit-slider-thumb:hover{transform:scale(1.3)}
.inp-val{
  font-family:var(--mono);font-size:1.6rem;font-weight:700;
  color:var(--accent);text-align:center;margin-top:10px;
  transition:color .3s;
}
.inp-bar{
  height:4px;border-radius:2px;margin-top:8px;
  background:var(--bg3);overflow:hidden;
}
.inp-bar-fill{
  height:100%;border-radius:2px;
  background:linear-gradient(90deg,var(--accent),var(--accent2));
  transition:width .3s ease;
}
.inp-desc{font-size:.72rem;color:var(--text3);margin-top:8px;text-align:center}

/* ── SUMMARY GRID ── */
.summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px}
.sum-card{
  background:var(--card2);border:1px solid var(--border);
  border-radius:var(--r);padding:18px;
  transition:transform .2s,box-shadow .2s;
}
.sum-card:hover{transform:translateY(-2px);box-shadow:var(--glow)}
.sum-card .s-label{font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text3);margin-bottom:8px}
.sum-card .s-val{font-size:1.5rem;font-weight:800;font-family:var(--mono)}
.sum-card .s-delta{font-size:.75rem;margin-top:4px;font-family:var(--mono)}
.delta-good{color:var(--green)}
.delta-bad {color:var(--red)}

/* ── RUN BUTTON ── */
.run-btn{
  display:inline-flex;align-items:center;gap:10px;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;border:none;cursor:pointer;
  font-family:var(--font);font-size:1rem;font-weight:700;
  padding:14px 32px;border-radius:var(--r);
  box-shadow:0 4px 24px rgba(0,212,255,.25);
  transition:transform .2s,box-shadow .2s,opacity .2s;
  position:relative;overflow:hidden;
}
.run-btn::before{
  content:'';position:absolute;inset:0;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.15),transparent);
  transform:translateX(-100%);
  transition:transform .5s;
}
.run-btn:hover{transform:translateY(-2px);box-shadow:0 8px 32px rgba(0,212,255,.4)}
.run-btn:hover::before{transform:translateX(100%)}
.run-btn:active{transform:translateY(0)}
.run-btn .spinner{
  width:18px;height:18px;border:2px solid rgba(255,255,255,.3);
  border-top-color:#fff;border-radius:50%;
  animation:spin2 .7s linear infinite;display:none;
}
@keyframes spin2{to{transform:rotate(360deg)}}
.run-btn.loading .spinner{display:block}
.run-btn.loading .btn-text{opacity:.7}

/* ── PROGRESS BAR ── */
.progress-wrap{margin:16px 0;display:none}
.progress-wrap.show{display:block;animation:fadeUp .3s ease}
.progress-bar{
  height:6px;background:var(--bg3);border-radius:3px;overflow:hidden;
}
.progress-fill{
  height:100%;width:0%;
  background:linear-gradient(90deg,var(--accent),var(--accent2));
  border-radius:3px;transition:width .3s ease;
}
.progress-msg{font-size:.8rem;color:var(--text2);font-family:var(--mono);margin-top:8px}

/* ── PROFILE BANNER ── */
.profile-banner{
  border-radius:var(--r2);padding:24px 28px;
  display:flex;align-items:center;gap:20px;
  margin:24px 0;
  animation:popIn .5s cubic-bezier(.34,1.56,.64,1) both;
  border:1px solid;
}
@keyframes popIn{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:scale(1)}}
.profile-banner.focused {background:rgba(16,185,129,.1);border-color:rgba(16,185,129,.3)}
.profile-banner.distracted{background:rgba(249,115,22,.1);border-color:rgba(249,115,22,.3)}
.profile-banner.burnout  {background:rgba(239,68,68,.1);border-color:rgba(239,68,68,.3)}
.pb-emoji{font-size:2.5rem}
.pb-tag{font-size:.7rem;font-weight:800;text-transform:uppercase;letter-spacing:.15em;font-family:var(--mono);margin-bottom:4px}
.pb-name{font-size:1.4rem;font-weight:800}
.pb-desc{font-size:.85rem;color:var(--text2);margin-top:4px}

/* ── METRICS GRID ── */
.metrics-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:28px}
.met-card{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--r);padding:20px;
  animation:fadeUp .4s ease both;
  transition:transform .2s;
}
.met-card:hover{transform:translateY(-2px)}
.met-card .m-label{font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text3);margin-bottom:10px}
.met-card .m-val{font-size:1.6rem;font-weight:800;font-family:var(--mono);color:var(--accent)}
.met-card .m-sub{font-size:.75rem;color:var(--text2);margin-top:4px;font-family:var(--mono)}

/* ── CHARTS ── */
.charts-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}
.chart-card{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--r2);padding:24px;
  transition:border-color .3s;
}
.chart-card:hover{border-color:rgba(0,212,255,.2)}
.chart-title{font-size:.8rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--text3);margin-bottom:20px}
canvas{display:block;width:100%!important}

/* ── GAUGE ── */
.gauge-row{display:grid;grid-template-columns:1fr 1fr 2fr;gap:16px;margin-bottom:24px}
.gauge-card{background:var(--card);border:1px solid var(--border);border-radius:var(--r2);padding:24px}
.gauge-svg{display:block;margin:0 auto}
.gauge-info{display:flex;flex-direction:column;justify-content:center;gap:12px}
.gauge-badge{
  border-radius:var(--r);padding:12px 16px;
  font-size:.85rem;font-weight:600;
  display:flex;align-items:center;gap:8px;
}
.gauge-badge.low   {background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.3);color:var(--green)}
.gauge-badge.med   {background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.3);color:var(--orange)}
.gauge-badge.high  {background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);color:var(--red)}

/* ── INSIGHTS ── */
.insights-cols{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:28px}
.insight-list{display:flex;flex-direction:column;gap:10px}
.issue-item{
  background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);
  border-radius:var(--r);padding:12px 16px;
  font-size:.88rem;color:var(--text);
  animation:slideRight .4s ease both;
}
.tip-item{
  background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2);
  border-radius:var(--r);padding:12px 16px;
  font-size:.88rem;color:var(--text);
  animation:slideRight .4s ease both;
}
@keyframes slideRight{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:translateX(0)}}

/* ── SCORE BREAKDOWN ── */
.score-breakdown{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:28px}
.score-cell{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--r);padding:16px;text-align:center;
}
.score-cell .sc-icon{font-size:1.4rem;margin-bottom:6px}
.score-cell .sc-label{font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text3);margin-bottom:8px}
.score-cell .sc-val{font-size:1.4rem;font-weight:800;font-family:var(--mono);color:var(--accent)}

/* ── ACTIONS TABLE ── */
.action-row{
  display:grid;grid-template-columns:140px 1fr;gap:12px;
  align-items:center;padding:12px 0;
  border-bottom:1px solid var(--border);
}
.action-row:last-child{border-bottom:none}
.priority-tag{
  display:inline-flex;align-items:center;gap:6px;
  padding:4px 12px;border-radius:20px;font-size:.72rem;font-weight:700;
  text-transform:uppercase;letter-spacing:.08em;font-family:var(--mono);
}
.pt-critical{background:rgba(239,68,68,.15);color:var(--red)}
.pt-high    {background:rgba(249,115,22,.15);color:var(--orange)}
.pt-medium  {background:rgba(245,158,11,.15);color:var(--accent3)}
.action-text{font-size:.88rem;color:var(--text2)}

/* ── HISTORY ── */
.hist-summary{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px}
.hist-table-header{
  display:grid;grid-template-columns:60px 1fr 1fr 1fr 1fr;gap:8px;
  padding:10px 16px;
  font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text3);
  background:var(--bg3);border-radius:var(--r) var(--r) 0 0;
  font-weight:700;font-family:var(--mono);
}
.hist-row{
  display:grid;grid-template-columns:60px 1fr 1fr 1fr 1fr;gap:8px;
  padding:12px 16px;align-items:center;
  background:var(--card);border-bottom:1px solid var(--border);
  transition:background .2s;font-size:.88rem;
}
.hist-row:hover{background:var(--card2)}
.hist-row:last-child{border-radius:0 0 var(--r) var(--r);border-bottom:none}
.run-num{font-family:var(--mono);color:var(--text3);font-weight:700}
.profile-pill{
  display:inline-flex;align-items:center;gap:6px;
  padding:3px 10px;border-radius:20px;font-size:.78rem;font-weight:600;
}
.pill-focused   {background:rgba(16,185,129,.15);color:var(--green)}
.pill-distracted{background:rgba(249,115,22,.15);color:var(--orange)}
.pill-burnout   {background:rgba(239,68,68,.15);color:var(--red)}

/* ── CLEAR BTN ── */
.clear-btn{
  background:transparent;border:1px solid rgba(239,68,68,.3);
  color:var(--red);border-radius:var(--r);padding:10px 24px;
  font-family:var(--font);font-size:.88rem;font-weight:600;
  cursor:pointer;transition:all .2s;margin-top:16px;
}
.clear-btn:hover{background:rgba(239,68,68,.1)}

/* ── DIVIDER ── */
.divider{height:1px;background:var(--border);margin:24px 0}

/* ── INFO BOX ── */
.info-box{
  background:rgba(0,212,255,.06);border:1px solid rgba(0,212,255,.2);
  border-radius:var(--r);padding:14px 18px;
  font-size:.87rem;color:var(--text2);
  display:flex;align-items:center;gap:12px;
}
.info-box .info-icon{font-size:1.1rem;flex-shrink:0}

/* ── FOOTER ── */
footer{
  border-top:1px solid var(--border);
  padding:24px 0;margin-top:40px;
  display:flex;justify-content:space-between;align-items:center;
  font-size:.78rem;color:var(--text3);font-family:var(--mono);
  position:relative;z-index:1;
}

/* ── TOAST ── */
.toast{
  position:fixed;bottom:32px;right:32px;z-index:999;
  background:var(--card2);border:1px solid rgba(0,212,255,.3);
  border-radius:var(--r);padding:14px 20px;
  box-shadow:0 8px 32px rgba(0,0,0,.5);
  display:flex;align-items:center;gap:12px;
  font-size:.88rem;
  transform:translateY(80px);opacity:0;
  transition:all .4s cubic-bezier(.34,1.56,.64,1);
  pointer-events:none;
}
.toast.show{transform:translateY(0);opacity:1}
.toast-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);flex-shrink:0}

/* ── RESPONSIVE ── */
@media(max-width:900px){
  .input-grid,.metrics-grid,.charts-row,.gauge-row{grid-template-columns:1fr 1fr}
  .status-bar,.summary-grid,.hist-summary,.score-breakdown{grid-template-columns:1fr 1fr}
  .insights-cols{grid-template-columns:1fr}
}
@media(max-width:600px){
  .input-grid,.metrics-grid,.charts-row,.gauge-row,
  .status-bar,.summary-grid,.hist-summary,.score-breakdown{grid-template-columns:1fr}
  header h1{font-size:1.5rem}
}
</style>
</head>
<body>
<div class="wrapper">

<!-- HEADER -->
<header>
  <div class="logo-ring">⏳</div>
  <div class="header-text">
    <h1>Neuro<span>Time</span> AI</h1>
    <p>Behavior Intelligence &amp; Time Leakage Detection System</p>
  </div>
</header>

<!-- STATUS BAR -->
<div class="status-bar" style="animation-delay:.1s">
  <div class="stat-card"><div class="label">Model</div><div class="value">K-Means</div></div>
  <div class="stat-card"><div class="label">Features</div><div class="value">5 inputs</div></div>
  <div class="stat-card"><div class="label">Type</div><div class="value">Behavior AI</div></div>
  <div class="stat-card"><div class="label">Status</div><div class="value" id="modelStatus">🔧 Demo</div></div>
</div>

<!-- TABS -->
<div class="tab-row">
  <button class="tab-btn active" onclick="switchTab('input',this)">📥 Input</button>
  <button class="tab-btn" onclick="switchTab('analysis',this)">📊 Analysis</button>
  <button class="tab-btn" onclick="switchTab('insights',this)">💡 Insights</button>
  <button class="tab-btn" onclick="switchTab('history',this)">📜 History</button>
</div>

<!-- ════ TAB: INPUT ════ -->
<div class="tab-panel active" id="tab-input">
  <div class="sec-title">Daily Behavior Parameters</div>
  <div class="sec-sub">Rate each behavior from 0 (none) to 10 (maximum). Be honest for accurate results.</div>

  <div class="input-grid" id="inputGrid"></div>

  <div class="divider"></div>
  <div class="sec-title" style="font-size:1.1rem">Live Summary</div>
  <div style="height:12px"></div>
  <div class="summary-grid" id="summaryGrid"></div>
  <div style="height:16px"></div>
  <div class="info-box">
    <span class="info-icon">ℹ️</span>
    Head to the <strong>Analysis</strong> tab and click <strong>Run Deep Analysis</strong> to get your profile.
  </div>
</div>

<!-- ════ TAB: ANALYSIS ════ -->
<div class="tab-panel" id="tab-analysis">
  <div class="sec-title">Behavioral Analysis Engine</div>
  <div class="sec-sub">Feed your behavioral data through the K-Means clustering model for instant profiling.</div>

  <button class="run-btn" id="runBtn" onclick="runAnalysis()">
    <div class="spinner" id="spinner"></div>
    <span class="btn-text">🚀 Run Deep Analysis</span>
  </button>

  <div class="progress-wrap" id="progressWrap">
    <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
    <div class="progress-msg" id="progressMsg">Initialising model…</div>
  </div>

  <div id="analysisResult" style="display:none">
    <div class="profile-banner" id="profileBanner">
      <div class="pb-emoji" id="pbEmoji"></div>
      <div>
        <div class="pb-tag" id="pbTag"></div>
        <div class="pb-name" id="pbName"></div>
        <div class="pb-desc" id="pbDesc"></div>
      </div>
    </div>

    <div class="metrics-grid" id="metricsGrid"></div>

    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-title">Activity Breakdown</div>
        <canvas id="barChart" height="220"></canvas>
      </div>
      <div class="chart-card">
        <div class="chart-title">Behavior Radar</div>
        <canvas id="radarChart" height="220"></canvas>
      </div>
    </div>

    <div class="gauge-row">
      <div class="gauge-card">
        <div class="chart-title" style="text-align:center">Time Leakage (hrs)</div>
        <canvas id="gaugeChart" height="160"></canvas>
      </div>
      <div class="gauge-card gauge-info" id="gaugeInfo"></div>
      <div class="gauge-card" style="display:flex;flex-direction:column;justify-content:center;gap:12px">
        <div style="font-weight:700;font-size:.95rem">What is Time Leakage?</div>
        <div style="font-size:.83rem;color:var(--text2);line-height:1.6">
          Time Leakage is the estimated hours lost to unproductive behaviours.
          It is calculated from your phone usage, social media time, and break frequency.
          <strong style="color:var(--accent)">Lower is better — aim to keep it under 3 hrs/day.</strong>
        </div>
      </div>
    </div>
  </div>

  <div class="info-box" id="noAnalysisInfo">
    <span class="info-icon">📊</span>
    No analysis yet. Enter your data in <strong>Input</strong> and click <strong>Run Deep Analysis</strong> above.
  </div>
</div>

<!-- ════ TAB: INSIGHTS ════ -->
<div class="tab-panel" id="tab-insights">
  <div class="sec-title">Personalised Insight Engine</div>
  <div class="sec-sub">AI-generated recommendations based on your behavioral fingerprint.</div>
  <div id="insightsContent">
    <div class="info-box"><span class="info-icon">💡</span>Run an analysis first to unlock insights.</div>
  </div>
</div>

<!-- ════ TAB: HISTORY ════ -->
<div class="tab-panel" id="tab-history">
  <div class="sec-title">Analysis History</div>
  <div class="sec-sub">Track your behavioral patterns over time.</div>
  <div id="historyContent">
    <div class="info-box"><span class="info-icon">📜</span>No history yet. Run your first analysis to see results here.</div>
  </div>
</div>

</div><!-- /wrapper -->

<!-- FOOTER -->
<div class="wrapper" style="padding-top:0">
  <footer>
    <span>⏳ NeuroTime AI — Behavior Intelligence System</span>
    <span>🧠 Model: K-Means Clustering | Features: 5</span>
    <span>Built with Python &amp; Canvas API</span>
  </footer>
</div>

<!-- TOAST -->
<div class="toast" id="toast"><div class="toast-dot"></div><span id="toastMsg"></span></div>

<script>
// ── STATE ──────────────────────────────────────
const FEATURES=[
  {key:'Study',  icon:'📚',color:'#3b82f6',desc:'Focused study/work hours'},
  {key:'Phone',  icon:'📱',color:'#e85d26',desc:'Phone screen time (hrs)'},
  {key:'Social', icon:'🌐',color:'#f4a261',desc:'Social media hours'},
  {key:'Breaks', icon:'☕',color:'#2a9d8f',desc:'Break intervals taken'},
  {key:'Sleep',  icon:'😴',color:'#8b5cf6',desc:'Sleep hours last night'},
];
const PROFILES={
  Focused:   {emoji:'🎯',tag:'FOCUSED MODE',   cls:'focused',   desc:'Peak cognitive mode. You\'re locked in.',color:'#10b981'},
  Distracted:{emoji:'⚡',tag:'DISTRACTED MODE',cls:'distracted',desc:'Attention is fragmented. Time to recalibrate.',color:'#f97316'},
  Burnout:   {emoji:'🔥',tag:'BURNOUT MODE',   cls:'burnout',   desc:'Overload detected. Rest is non-negotiable.',color:'#ef4444'},
};
let data=[5,5,5,5,5];
let history=[];
let lastResult=null;
let barChartInstance=null,radarChartInstance=null,gaugeChartInstance=null,histChartInstance=null;

// ── INIT ──────────────────────────────────────
buildInputGrid();
updateSummary();

function buildInputGrid(){
  const grid=document.getElementById('inputGrid');
  grid.innerHTML='';
  FEATURES.forEach((f,i)=>{
    grid.innerHTML+=`
    <div class="inp-card" style="animation:fadeUp .4s ${i*0.07}s ease both">
      <div class="inp-icon">${f.icon}</div>
      <div class="inp-label">${f.key}</div>
      <div class="slider-wrap">
        <input type="range" min="0" max="10" value="${data[i]}" 
               id="slider_${i}" oninput="onSlider(${i},this.value)"
               style="accent-color:${f.color}">
      </div>
      <div class="inp-val" id="val_${i}">${data[i]}</div>
      <div class="inp-bar"><div class="inp-bar-fill" id="bar_${i}" style="width:${data[i]*10}%;background:${f.color}"></div></div>
      <div class="inp-desc">${f.desc}</div>
    </div>`;
  });
}

function onSlider(i,v){
  data[i]=parseInt(v);
  document.getElementById(`val_${i}`).textContent=v;
  document.getElementById(`bar_${i}`).style.width=(v*10)+'%';
  updateSummary();
}

function updateSummary(){
  const productive=data[0];
  const distraction=data[1]+data[2];
  const recovery=data[3]+data[4];
  const bal=distraction?+(productive/distraction).toFixed(2):productive;
  const balGood=bal>=1;
  document.getElementById('summaryGrid').innerHTML=`
    <div class="sum-card">
      <div class="s-label">🎯 Productive Time</div>
      <div class="s-val" style="color:#3b82f6">${productive} hrs</div>
      <div class="s-delta delta-good">Study / work hours</div>
    </div>
    <div class="sum-card">
      <div class="s-label">📱 Distraction Load</div>
      <div class="s-val" style="color:#e85d26">${distraction} hrs</div>
      <div class="s-delta delta-bad">Phone + Social</div>
    </div>
    <div class="sum-card">
      <div class="s-label">😴 Recovery Score</div>
      <div class="s-val" style="color:#8b5cf6">${recovery} hrs</div>
      <div class="s-delta delta-good">Breaks + Sleep</div>
    </div>
    <div class="sum-card">
      <div class="s-label">⚖️ Balance Index</div>
      <div class="s-val" style="color:${balGood?'#10b981':'#ef4444'}">${bal}</div>
      <div class="s-delta ${balGood?'delta-good':'delta-bad'}">${balGood?'✓ Good':'⚠ Low'}</div>
    </div>`;
}

// ── TABS ──────────────────────────────────────
function switchTab(name,btn){
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  btn.classList.add('active');
}

// ── RUN ANALYSIS ──────────────────────────────
async function runAnalysis(){
  const btn=document.getElementById('runBtn');
  btn.classList.add('loading');
  btn.disabled=true;
  const pw=document.getElementById('progressWrap');
  const pf=document.getElementById('progressFill');
  const pm=document.getElementById('progressMsg');
  pw.classList.add('show');

  const steps=[
    [20,'Loading behavioral vectors…'],
    [45,'Scaling features…'],
    [70,'Running K-Means inference…'],
    [90,'Generating profile…'],
    [100,'Done!'],
  ];
  for(const [pct,msg] of steps){
    pf.style.width=pct+'%';
    pm.textContent=msg;
    await sleep(280);
  }
  await sleep(200);
  pw.classList.remove('show');
  btn.classList.remove('loading');
  btn.disabled=false;

  try{
    const resp=await fetch('/api/analyze',{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({data})
    });
    const result=await resp.json();
    lastResult=result;
    history.push({...result,inputs:[...data]});
    showResult(result);
    showToast(`Analysis complete — ${result.profile} mode detected`);
  }catch(e){
    showToast('Analysis error: '+e.message);
  }
}

function showResult(r){
  document.getElementById('noAnalysisInfo').style.display='none';
  const res=document.getElementById('analysisResult');
  res.style.display='block';

  const p=PROFILES[r.profile];
  const banner=document.getElementById('profileBanner');
  banner.className='profile-banner '+p.cls;
  document.getElementById('pbEmoji').textContent=p.emoji;
  document.getElementById('pbTag').textContent=p.tag;
  document.getElementById('pbTag').style.color=p.color;
  document.getElementById('pbName').textContent=r.profile+' Mode';
  document.getElementById('pbDesc').textContent=p.desc;

  document.getElementById('metricsGrid').innerHTML=`
    <div class="met-card" style="animation-delay:.05s">
      <div class="m-label">🧠 Behavior Profile</div>
      <div class="m-val" style="color:${p.color}">${r.profile}</div>
    </div>
    <div class="met-card" style="animation-delay:.1s">
      <div class="m-label">📊 Focus Score</div>
      <div class="m-val">${r.score}</div>
      <div class="m-sub">out of 10.0</div>
    </div>
    <div class="met-card" style="animation-delay:.15s">
      <div class="m-label">⚠️ Time Leakage</div>
      <div class="m-val" style="color:#ef4444">${r.leakage}h</div>
      <div class="m-sub" style="color:#ef4444">hrs wasted</div>
    </div>
    <div class="met-card" style="animation-delay:.2s">
      <div class="m-label">✅ Confidence</div>
      <div class="m-val" style="color:#10b981">${r.confidence}%</div>
    </div>`;

  drawBar();
  drawRadar();
  drawGauge(r.leakage);
  updateInsights();
  updateHistory();
}

// ── CHART: BAR ────────────────────────────────
function drawBar(){
  const ctx=document.getElementById('barChart').getContext('2d');
  if(barChartInstance){barChartInstance.destroy()}
  barChartInstance=new SimpleBarChart(ctx,{
    labels:FEATURES.map(f=>f.key),
    values:data,
    colors:FEATURES.map(f=>f.color),
  });
}

// ── CHART: RADAR ──────────────────────────────
function drawRadar(){
  const ctx=document.getElementById('radarChart').getContext('2d');
  if(radarChartInstance){radarChartInstance.destroy()}
  radarChartInstance=new SimpleRadarChart(ctx,{
    labels:FEATURES.map(f=>f.key),
    values:data,
    color:'#00d4ff',
  });
}

// ── CHART: GAUGE ─────────────────────────────
function drawGauge(leakage){
  const ctx=document.getElementById('gaugeChart').getContext('2d');
  if(gaugeChartInstance){gaugeChartInstance.destroy()}
  gaugeChartInstance=new SimpleGaugeChart(ctx,{value:leakage,max:10});

  const pct=leakage/10*100;
  const gi=document.getElementById('gaugeInfo');
  if(pct<30)
    gi.innerHTML=`<div class="gauge-badge low">🟢 <strong>Low leakage (${Math.round(pct)}%)</strong></div><p style="font-size:.82rem;color:var(--text2)">Your time management is solid.</p>`;
  else if(pct<60)
    gi.innerHTML=`<div class="gauge-badge med">🟡 <strong>Moderate leakage (${Math.round(pct)}%)</strong></div><p style="font-size:.82rem;color:var(--text2)">Some room for improvement.</p>`;
  else
    gi.innerHTML=`<div class="gauge-badge high">🔴 <strong>High leakage (${Math.round(pct)}%)</strong></div><p style="font-size:.82rem;color:var(--text2)">Significant time being wasted.</p>`;
}

// ── INSIGHTS ──────────────────────────────────
function updateInsights(){
  if(!lastResult)return;
  const r=lastResult;
  const issues=[], tips=[];
  if(data[1]>7){issues.push('📱 High phone screen time');       tips.push('⏱ Use app timers — cut phone by 30%')}
  if(data[2]>7){issues.push('🌐 Social media overload');        tips.push('📅 Batch social media to 2 blocks/day')}
  if(data[4]<5){issues.push('😴 Sleep deficit detected');       tips.push('🛌 Aim for 7–8 hrs with consistent schedule')}
  if(data[3]>7){issues.push('☕ Too many breaks');              tips.push('🍅 Try Pomodoro: 25 min work / 5 min break')}
  if(data[0]<3){issues.push('📚 Study time critically low');    tips.push('🌅 Protect a 3-hr deep-work morning block')}
  if(!tips.length)tips.push('✅ Excellent habits — keep it up!');

  const actions=[];
  if(data[0]<5) actions.push(['🔴 Critical','pt-critical','Increase study hours to at least 5 hrs/day']);
  if(data[1]>6) actions.push(['🟠 High','pt-high','Put phone on Do Not Disturb during work blocks']);
  if(data[2]>6) actions.push(['🟠 High','pt-high','Delete social apps from home screen']);
  if(data[4]<6) actions.push(['🟡 Medium','pt-medium','Set a fixed sleep time and stick to it']);
  if(data[3]>6) actions.push(['🟡 Medium','pt-medium','Reduce break frequency — use structured intervals']);

  document.getElementById('insightsContent').innerHTML=`
    <div class="insights-cols">
      <div>
        <div style="font-weight:700;margin-bottom:14px;font-size:1rem">⚠️ Detected Issues</div>
        <div class="insight-list">
          ${issues.length
            ? issues.map((i,idx)=>`<div class="issue-item" style="animation-delay:${idx*.08}s">${i}</div>`).join('')
            : '<div class="tip-item">No issues detected!</div>'}
        </div>
      </div>
      <div>
        <div style="font-weight:700;margin-bottom:14px;font-size:1rem">🚀 Recommendations</div>
        <div class="insight-list">
          ${tips.map((t,i)=>`<div class="tip-item" style="animation-delay:${i*.08}s">${t}</div>`).join('')}
        </div>
      </div>
    </div>
    <div class="divider"></div>
    <div style="font-weight:700;margin-bottom:14px;font-size:1rem">📊 Score Breakdown</div>
    <div class="score-breakdown">
      ${FEATURES.map((f,i)=>`
        <div class="score-cell">
          <div class="sc-icon">${f.icon}</div>
          <div class="sc-label">${f.key}</div>
          <div class="sc-val" style="color:${f.color}">${data[i]}/10</div>
        </div>`).join('')}
    </div>
    <div class="divider"></div>
    <div style="font-weight:700;margin-bottom:14px;font-size:1rem">🗓 Priority Action Plan</div>
    ${actions.length
      ? actions.map(([lbl,cls,txt])=>`
          <div class="action-row">
            <div><span class="priority-tag ${cls}">${lbl}</span></div>
            <div class="action-text">${txt}</div>
          </div>`).join('')
      : '<div class="tip-item">✅ No critical actions needed — you\'re performing well!</div>'}
  `;
}

// ── HISTORY ───────────────────────────────────
function updateHistory(){
  if(!history.length){
    document.getElementById('historyContent').innerHTML=
      '<div class="info-box"><span class="info-icon">📜</span>No history yet. Run your first analysis to see results here.</div>';
    return;
  }
  const scores=history.map(h=>h.score);
  const leaks =history.map(h=>h.leakage);
  const profs =history.map(h=>h.profile);
  const most  =profs.sort((a,b)=>profs.filter(p=>p===b).length-profs.filter(p=>p===a).length)[0];
  const avgScr=(scores.reduce((a,b)=>a+b,0)/scores.length).toFixed(1);
  const avgLk =(leaks.reduce((a,b)=>a+b,0)/leaks.length).toFixed(1);

  const PILL={Focused:'pill-focused',Distracted:'pill-distracted',Burnout:'pill-burnout'};
  const ICON={Focused:'🎯',Distracted:'⚡',Burnout:'🔥'};

  document.getElementById('historyContent').innerHTML=`
    <div class="hist-summary">
      <div class="stat-card"><div class="label">Total Runs</div><div class="value">${history.length}</div></div>
      <div class="stat-card"><div class="label">Avg Focus Score</div><div class="value">${avgScr}</div></div>
      <div class="stat-card"><div class="label">Avg Leakage</div><div class="value">${avgLk} hrs</div></div>
      <div class="stat-card"><div class="label">Most Common</div><div class="value">${most}</div></div>
    </div>
    ${history.length>=2?`
    <div class="chart-card" style="margin-bottom:20px">
      <div class="chart-title">Score &amp; Leakage Over Time</div>
      <canvas id="histChart" height="160"></canvas>
    </div>`:''}
    <div class="hist-table-header">
      <div>RUN</div><div>PROFILE</div><div>FOCUS SCORE</div><div>LEAKAGE</div><div>CONFIDENCE</div>
    </div>
    ${[...history].reverse().map((h,i)=>`
      <div class="hist-row">
        <div class="run-num">#${history.length-i}</div>
        <div><span class="profile-pill ${PILL[h.profile]}">${ICON[h.profile]} ${h.profile}</span></div>
        <div style="font-family:var(--mono)">${h.score} / 10</div>
        <div style="font-family:var(--mono);color:#ef4444">${h.leakage} hrs</div>
        <div style="font-family:var(--mono);color:#10b981">${h.confidence}%</div>
      </div>`).join('')}
    <br>
    <button class="clear-btn" onclick="clearHistory()">🗑 Clear All History</button>
  `;
  if(history.length>=2){
    setTimeout(()=>{
      const ctx=document.getElementById('histChart');
      if(ctx) new SimpleLineChart(ctx.getContext('2d'),{
        runs:history.map((_,i)=>i+1),
        scores,leaks
      });
    },50);
  }
}

function clearHistory(){
  history=[];lastResult=null;
  document.getElementById('analysisResult').style.display='none';
  document.getElementById('noAnalysisInfo').style.display='flex';
  document.getElementById('insightsContent').innerHTML=
    '<div class="info-box"><span class="info-icon">💡</span>Run an analysis first to unlock insights.</div>';
  updateHistory();
  showToast('History cleared');
}

// ── TOAST ─────────────────────────────────────
function showToast(msg){
  const t=document.getElementById('toast');
  document.getElementById('toastMsg').textContent=msg;
  t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),3000);
}

// ── HELPERS ───────────────────────────────────
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}

// ── CANVAS CHARTS ─────────────────────────────
class SimpleBarChart{
  constructor(ctx,{labels,values,colors}){
    this.ctx=ctx;this.labels=labels;this.values=values;this.colors=colors;
    this.frame=0;this.prog=0;
    this._raf=requestAnimationFrame(()=>this._animate());
  }
  destroy(){cancelAnimationFrame(this._raf)}
  _animate(){
    this.prog=Math.min(1,this.prog+0.05);
    this._draw(this.prog);
    if(this.prog<1)this._raf=requestAnimationFrame(()=>this._animate());
  }
  _draw(p){
    const {ctx,labels,values,colors}=this;
    const W=ctx.canvas.offsetWidth||ctx.canvas.width;
    const H=ctx.canvas.height=ctx.canvas.offsetHeight||220;
    ctx.canvas.width=W;
    ctx.clearRect(0,0,W,H);
    const n=labels.length,pad=32,bw=(W-pad*2)/n*0.55,gap=(W-pad*2)/n;
    const maxV=10;
    ctx.font='12px JetBrains Mono,monospace';
    ctx.textAlign='center';
    labels.forEach((l,i)=>{
      const x=pad+i*gap+gap/2;
      const bh=(values[i]/maxV)*(H-56)*p;
      const y=H-32-bh;
      // bar
      const grad=ctx.createLinearGradient(0,y,0,H-32);
      grad.addColorStop(0,colors[i]);
      grad.addColorStop(1,colors[i]+'44');
      ctx.fillStyle=grad;
      ctx.beginPath();
      ctx.roundRect(x-bw/2,y,bw,bh,6);
      ctx.fill();
      // value label
      if(p>0.7){
        ctx.fillStyle='#e2e8f0';
        ctx.fillText(values[i],x,y-6);
      }
      // x label
      ctx.fillStyle='#64748b';
      ctx.fillText(l,x,H-12);
    });
    // grid lines
    ctx.strokeStyle='rgba(255,255,255,0.05)';
    ctx.lineWidth=1;
    [2,4,6,8,10].forEach(v=>{
      const y=H-32-(v/maxV)*(H-56);
      ctx.beginPath();ctx.moveTo(pad,y);ctx.lineTo(W-pad,y);ctx.stroke();
      ctx.fillStyle='#475569';
      ctx.font='10px JetBrains Mono,monospace';
      ctx.textAlign='right';
      ctx.fillText(v,pad-4,y+4);
    });
  }
}

class SimpleRadarChart{
  constructor(ctx,{labels,values,color}){
    this.ctx=ctx;this.labels=labels;this.values=values;this.color=color;
    this.prog=0;
    this._raf=requestAnimationFrame(()=>this._animate());
  }
  destroy(){cancelAnimationFrame(this._raf)}
  _animate(){
    this.prog=Math.min(1,this.prog+0.05);
    this._draw(this.prog);
    if(this.prog<1)this._raf=requestAnimationFrame(()=>this._animate());
  }
  _draw(p){
    const {ctx,labels,values,color}=this;
    const W=ctx.canvas.offsetWidth||ctx.canvas.width;
    const H=ctx.canvas.height=ctx.canvas.offsetHeight||220;
    ctx.canvas.width=W;
    ctx.clearRect(0,0,W,H);
    const cx=W/2,cy=H/2,r=Math.min(W,H)/2-44;
    const n=labels.length;
    const angle=i=>-Math.PI/2+(2*Math.PI*i/n);
    // grid
    [2,4,6,8,10].forEach(v=>{
      ctx.beginPath();
      ctx.strokeStyle='rgba(255,255,255,0.07)';
      ctx.lineWidth=1;
      for(let i=0;i<n;i++){
        const a=angle(i),rv=r*v/10;
        i===0?ctx.moveTo(cx+Math.cos(a)*rv,cy+Math.sin(a)*rv)
             :ctx.lineTo(cx+Math.cos(a)*rv,cy+Math.sin(a)*rv);
      }
      ctx.closePath();ctx.stroke();
    });
    // axes
    labels.forEach((_,i)=>{
      const a=angle(i);
      ctx.beginPath();ctx.strokeStyle='rgba(255,255,255,0.08)';ctx.lineWidth=1;
      ctx.moveTo(cx,cy);ctx.lineTo(cx+Math.cos(a)*r,cy+Math.sin(a)*r);ctx.stroke();
    });
    // data
    ctx.beginPath();
    ctx.fillStyle=color+'22';
    ctx.strokeStyle=color;
    ctx.lineWidth=2.5;
    values.forEach((v,i)=>{
      const a=angle(i),rv=r*(v/10)*p;
      i===0?ctx.moveTo(cx+Math.cos(a)*rv,cy+Math.sin(a)*rv)
           :ctx.lineTo(cx+Math.cos(a)*rv,cy+Math.sin(a)*rv);
    });
    ctx.closePath();ctx.fill();ctx.stroke();
    // dots
    values.forEach((v,i)=>{
      const a=angle(i),rv=r*(v/10)*p;
      ctx.beginPath();
      ctx.arc(cx+Math.cos(a)*rv,cy+Math.sin(a)*rv,5,0,Math.PI*2);
      ctx.fillStyle=color;ctx.fill();
    });
    // labels
    if(p>0.8){
      ctx.fillStyle='#94a3b8';
      ctx.font='11px Space Grotesk,sans-serif';
      ctx.textAlign='center';
      labels.forEach((l,i)=>{
        const a=angle(i),lv=r+22;
        ctx.fillText(l,cx+Math.cos(a)*lv,cy+Math.sin(a)*lv+4);
      });
    }
  }
}

class SimpleGaugeChart{
  constructor(ctx,{value,max}){
    this.ctx=ctx;this.value=value;this.max=max;
    this.prog=0;
    this._raf=requestAnimationFrame(()=>this._animate());
  }
  destroy(){cancelAnimationFrame(this._raf)}
  _animate(){
    this.prog=Math.min(1,this.prog+0.04);
    this._draw(this.prog);
    if(this.prog<1)this._raf=requestAnimationFrame(()=>this._animate());
  }
  _draw(p){
    const {ctx,value,max}=this;
    const W=ctx.canvas.offsetWidth||ctx.canvas.width;
    const H=160;
    ctx.canvas.width=W;ctx.canvas.height=H;
    ctx.clearRect(0,0,W,H);
    const cx=W/2,cy=H-20,r=Math.min(W/2,H)-16;
    const start=Math.PI,end=2*Math.PI;
    // bg arc
    ctx.beginPath();
    ctx.arc(cx,cy,r,start,end);
    ctx.strokeStyle='rgba(255,255,255,0.07)';
    ctx.lineWidth=14;ctx.lineCap='round';
    ctx.stroke();
    // zones
    const zones=[
      ['#10b981',0,.3],
      ['#f59e0b',.3,.6],
      ['#ef4444',.6,1],
    ];
    zones.forEach(([c,s,e])=>{
      ctx.beginPath();
      ctx.arc(cx,cy,r,Math.PI+s*Math.PI,Math.PI+e*Math.PI);
      ctx.strokeStyle=c+'44';
      ctx.lineWidth=14;ctx.lineCap='butt';
      ctx.stroke();
    });
    // value arc
    const frac=Math.min(value/max,1)*p;
    const col=frac<.3?'#10b981':frac<.6?'#f59e0b':'#ef4444';
    ctx.beginPath();
    ctx.arc(cx,cy,r,Math.PI,Math.PI+frac*Math.PI);
    ctx.strokeStyle=col;
    ctx.lineWidth=14;ctx.lineCap='round';
    ctx.stroke();
    // needle
    const needleAngle=Math.PI+frac*Math.PI;
    ctx.save();
    ctx.translate(cx,cy);
    ctx.rotate(needleAngle);
    ctx.beginPath();
    ctx.moveTo(-8,0);ctx.lineTo(r-10,0);
    ctx.strokeStyle='#e2e8f0';
    ctx.lineWidth=2;ctx.lineCap='round';
    ctx.stroke();
    ctx.restore();
    // center dot
    ctx.beginPath();
    ctx.arc(cx,cy,7,0,Math.PI*2);
    ctx.fillStyle='#e2e8f0';ctx.fill();
    // text
    if(p>0.7){
      ctx.fillStyle='#e2e8f0';
      ctx.font=`bold 22px JetBrains Mono,monospace`;
      ctx.textAlign='center';
      ctx.fillText(value.toFixed(1)+'h',cx,cy-18);
    }
  }
}

class SimpleLineChart{
  constructor(ctx,{runs,scores,leaks}){
    this.ctx=ctx;this.runs=runs;this.scores=scores;this.leaks=leaks;
    this.prog=0;
    this._raf=requestAnimationFrame(()=>this._animate());
  }
  _animate(){
    this.prog=Math.min(1,this.prog+0.05);
    this._draw(this.prog);
    if(this.prog<1)this._raf=requestAnimationFrame(()=>this._animate());
  }
  _draw(p){
    const {ctx,runs,scores,leaks}=this;
    const W=ctx.canvas.offsetWidth||ctx.canvas.width;
    const H=160;
    ctx.canvas.width=W;ctx.canvas.height=H;
    ctx.clearRect(0,0,W,H);
    const pad=36,n=runs.length;
    const maxV=12;
    const xS=i=>(i/(n-1||1))*(W-pad*2)+pad;
    const yS=v=>H-32-(v/maxV)*(H-56);
    // grid
    [3,6,9,12].forEach(v=>{
      const y=yS(v);
      ctx.strokeStyle='rgba(255,255,255,0.05)';
      ctx.lineWidth=1;
      ctx.beginPath();ctx.moveTo(pad,y);ctx.lineTo(W-pad,y);ctx.stroke();
      ctx.fillStyle='#475569';
      ctx.font='9px JetBrains Mono,monospace';
      ctx.textAlign='right';
      ctx.fillText(v,pad-4,y+3);
    });
    const drawLine=(arr,color,dashed)=>{
      const pts=Math.max(2,Math.round(arr.length*p));
      ctx.beginPath();
      ctx.strokeStyle=color;ctx.lineWidth=2.5;ctx.lineCap='round';ctx.lineJoin='round';
      if(dashed)ctx.setLineDash([6,4]);else ctx.setLineDash([]);
      arr.slice(0,pts).forEach((v,i)=>i===0?ctx.moveTo(xS(i),yS(v)):ctx.lineTo(xS(i),yS(v)));
      ctx.stroke();
      arr.slice(0,pts).forEach((v,i)=>{
        ctx.beginPath();ctx.arc(xS(i),yS(v),4,0,Math.PI*2);
        ctx.fillStyle=color;ctx.fill();
      });
      ctx.setLineDash([]);
    };
    drawLine(scores,'#3b82f6',false);
    drawLine(leaks,'#e85d26',true);
    // legend
    ctx.font='11px Space Grotesk,sans-serif';
    ctx.textAlign='left';
    [[scores,'#3b82f6','Focus Score'],[leaks,'#e85d26','Leakage']].forEach(([_,c,l],i)=>{
      ctx.fillStyle=c;ctx.fillRect(pad+i*120,12,12,3);
      ctx.fillStyle='#94a3b8';ctx.fillText(l,pad+i*120+16,16);
    });
    // x labels
    ctx.fillStyle='#64748b';ctx.textAlign='center';
    runs.forEach((r,i)=>{
      ctx.fillText('#'+r,xS(i),H-8);
    });
  }
}
</script>
</body>
</html>
"""

# ─────────────────────────────────────────────────────
# REQUEST HANDLER
# ─────────────────────────────────────────────────────
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # suppress default logs
        pass

    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        if self.path == "/api/analyze":
            length = int(self.headers.get("Content-Length", 0))
            body   = self.rfile.read(length)
            payload= json.loads(body)
            data   = payload.get("data", [5,5,5,5,5])
            result = run_analysis(data)

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()


# ─────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────
if __name__ == "__main__":
    PORT = 8080
    server = http.server.HTTPServer(("", PORT), Handler)
    print(f"""
╔══════════════════════════════════════════╗
║        NeuroTime AI  ⏳                   ║
║  Behavior Intelligence System            ║
╠══════════════════════════════════════════╣
║  Server running at:                      ║
║  http://localhost:{PORT}                   ║
║                                          ║
║  Press Ctrl+C to stop                    ║
╚══════════════════════════════════════════╝
    """)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")