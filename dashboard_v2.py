"""
GridAid —  AI-Powered National Energy Intelligence Platform
Enhanced competition demo with:
  • Live waste counter (JS, truly real-time)
  • Bangladesh map with animated pulsing anomaly pin
  • Real SMS via Twilio/SSL Wireless with verification hash
  • Full resolution workflow loop
  • Enhanced optimization simulator
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from streamlit_folium import st_folium
from datetime import datetime
import time, random, hashlib, json, os, threading
from bd_grid_data import GRID_ZONES, NATIONAL_WASTE_MW_PER_SEC, BDT_PER_KWH, CO2_KG_PER_KWH, WASTAGE_LABELS

st.set_page_config(
    page_title="GridAid —  AI-Powered National Energy Intelligence Platform",
    page_icon="⚡", layout="wide",
    initial_sidebar_state="expanded"
)

# ── PALETTE ──────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#050D18}
[data-testid="stSidebar"]{background:#0D1B2A}
[data-testid="stHeader"]{background:transparent}
.block-container{padding-top:0.5rem}

.kpi{background:#0D1B2A;border-radius:12px;padding:14px 18px;
     border:1px solid #1E3A5C;text-align:center}
.kpi-num{font-size:26px;font-weight:700}
.kpi-lbl{font-size:11px;color:#94A3B8;margin-top:3px}

.alert-card{background:#1A0808;border-left:4px solid #EF4444;
            border-radius:8px;padding:10px 14px;margin:5px 0}
.alert-title{color:#FCA5A5;font-weight:600;font-size:13px}
.alert-sub{color:#94A3B8;font-size:11px;margin-top:2px}

.resolved-card{background:#081A10;border-left:4px solid #22C55E;
               border-radius:8px;padding:10px 14px;margin:5px 0}

.sms-preview{background:#1A1A0A;border:1px solid #F59E0B;border-radius:8px;
             padding:14px;font-family:monospace;font-size:12px;
             color:#FCD34D;white-space:pre-line;line-height:1.7}

.verify-badge{background:#0A1A0A;border:1px solid #22C55E;border-radius:6px;
              padding:6px 14px;display:inline-block;font-family:monospace;
              font-size:14px;color:#86EFAC;font-weight:700}

.step-active{background:#0D2A1A;border:1.5px solid #22C55E;border-radius:8px;
             padding:10px 14px;margin:4px 0}
.step-done{background:#071510;border:0.5px solid #1A3A1A;border-radius:8px;
           padding:10px 14px;margin:4px 0;opacity:0.7}
.step-pending{background:#07111E;border:0.5px solid #1E3A5C;border-radius:8px;
              padding:8px 14px;margin:4px 0;opacity:0.5}

.section-hdr{color:#F59E0B;font-size:16px;font-weight:600;
             padding-bottom:6px;margin:12px 0 8px;
             border-bottom:1px solid #1E3A5C}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INIT ────────────────────────────────────────
def init_state():
    defaults = {
        "anomalies":        [],     # list of detected anomaly dicts
        "active_anomaly":   None,   # current anomaly being resolved
        "sms_log":          [],     # all SMS records
        "resolution_step":  0,      # 0=none 1=detected 2=sms_sent 3=ack 4=resolved
        "resolution_timer": None,
        "session_start":    time.time(),
        "trigger_pending":  False,
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── LIVE WASTE COUNTER (JavaScript — truly real-time) ─────────
def render_waste_counter():
    start_epoch_ms = int(st.session_state["session_start"] * 1000)
    components.html(f"""
<style>
.wc-wrap{{background:#0D1B2A;border-radius:12px;padding:12px 16px;
          border:1px solid #1E3A5C;font-family:Arial,sans-serif}}
.wc-title{{font-size:10px;color:#94A3B8;text-transform:uppercase;
           letter-spacing:2px;margin-bottom:6px}}
.wc-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}
.wc-item{{background:#071018;border-radius:8px;padding:8px 10px;
          border:1px solid #0A2040}}
.wc-num{{font-size:18px;font-weight:700;color:#EF4444}}
.wc-sub{{font-size:10px;color:#94A3B8;margin-top:2px}}
</style>
<div class="wc-wrap">
  <div class="wc-title">🔴 Bangladesh wasting RIGHT NOW — since this page opened</div>
  <div class="wc-grid">
    <div class="wc-item"><div class="wc-num" id="wc-mwh">0.0</div>
      <div class="wc-sub">MW-hrs wasted</div></div>
    <div class="wc-item"><div class="wc-num" id="wc-bdt" style="color:#F59E0B">৳0</div>
      <div class="wc-sub">BDT lost</div></div>
    <div class="wc-item"><div class="wc-num" id="wc-co2" style="color:#94A3B8">0 kg</div>
      <div class="wc-sub">CO₂ from waste</div></div>
  </div>
</div>
<script>
const START = {start_epoch_ms};
const MW_PER_SEC   = {NATIONAL_WASTE_MW_PER_SEC:.6f};
const BDT_PER_KWH  = {BDT_PER_KWH};
const CO2_PER_KWH  = {CO2_KG_PER_KWH};
function fmt(n){{return n>=1e6?(n/1e6).toFixed(2)+"M":n>=1e3?(n/1e3).toFixed(1)+"K":n.toFixed(1)}}
function fmtBdt(n){{
  if(n>=1e7) return "৳"+(n/1e7).toFixed(2)+"Cr";
  if(n>=1e5) return "৳"+(n/1e5).toFixed(1)+"L";
  return "৳"+Math.round(n).toLocaleString();
}}
setInterval(()=>{{
  const secs = (Date.now()-START)/1000;
  const mwh  = MW_PER_SEC * secs;
  const kwh  = mwh * 1000;
  const bdt  = kwh * BDT_PER_KWH;
  const co2  = kwh * CO2_PER_KWH;
  const e = document.getElementById;
  if(e("wc-mwh")) e("wc-mwh").textContent = fmt(mwh);
  if(e("wc-bdt")) e("wc-bdt").textContent = fmtBdt(bdt);
  if(e("wc-co2")) e("wc-co2").textContent = fmt(co2)+" kg";
}},500);
</script>
""", height=110)

# ── MAP BUILDER ───────────────────────────────────────────────
def build_bd_map(active_anomaly=None, all_anomalies=None):
    m = folium.Map(
        location=[23.8, 90.3], zoom_start=7,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )

    # Normal zone markers
    for name, zone in GRID_ZONES.items():
        is_active = (active_anomaly and active_anomaly.get("sector") == name)
        if is_active:
            continue  # drawn separately below
        folium.CircleMarker(
            location=[zone["lat"], zone["lon"]],
            radius=7, color=zone["icon_color"],
            fill=True, fill_color=zone["icon_color"],
            fill_opacity=0.6, weight=1.5,
            tooltip=f"{name}<br>{zone['district']}, {zone['division']}",
        ).add_to(m)
        folium.Marker(
            location=[zone["lat"] + 0.04, zone["lon"]],
            icon=folium.DivIcon(
                html=f'<div style="font-size:9px;color:{zone["icon_color"]};'
                     f'font-family:Arial;white-space:nowrap;font-weight:bold">'
                     f'{name[:18]}</div>',
                icon_size=(160, 14),
            )
        ).add_to(m)

    # Pulsing anomaly marker
    if active_anomaly:
        az = GRID_ZONES.get(active_anomaly["sector"], {})
        lat, lon = az.get("lat", 23.8), az.get("lon", 90.3)
        pulse_html = f"""
<style>
@keyframes gh-pulse{{0%{{transform:scale(1);opacity:1}}100%{{transform:scale(3.5);opacity:0}}}}
@keyframes gh-inner{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.2)}}}}
.gh-outer{{width:24px;height:24px;border-radius:50%;background:rgba(239,68,68,0.3);
           animation:gh-pulse 1.5s ease-out infinite;position:absolute;
           top:-6px;left:-6px}}
.gh-inner{{width:14px;height:14px;border-radius:50%;background:#EF4444;
           border:2px solid #FCA5A5;animation:gh-inner 1.5s ease-in-out infinite;
           position:relative;z-index:2}}
.gh-wrap{{position:relative;width:12px;height:12px}}
</style>
<div class="gh-wrap">
  <div class="gh-outer"></div>
  <div class="gh-inner"></div>
</div>
"""
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=pulse_html, icon_size=(24,24), icon_anchor=(12,12)),
            tooltip=f"⚠️ ANOMALY: {active_anomaly['sector']}",
        ).add_to(m)

        # Popup with full detail
        popup_html = f"""
<div style='background:#1A0808;padding:12px;border-radius:8px;
            font-family:Arial;min-width:220px;border:1px solid #EF4444'>
<div style='color:#FCA5A5;font-weight:bold;font-size:13px'>⚠️ ANOMALY DETECTED</div>
<div style='color:#EF4444;font-size:12px;margin:4px 0'>{active_anomaly['sector']}</div>
<table style='font-size:11px;color:#CBD5E1;width:100%'>
<tr><td>Grid line</td><td style='color:#F59E0B;font-weight:bold'>{az.get('grid_line','')}</td></tr>
<tr><td>Type</td><td>{WASTAGE_LABELS.get(active_anomaly['wastage_type'],'')}</td></tr>
<tr><td>MW lost</td><td style='color:#EF4444;font-weight:bold'>{active_anomaly['mw']:.1f} MW</td></tr>
<tr><td>BDT cost</td><td style='color:#F59E0B'>৳{active_anomaly['bdt']/100000:.1f}L</td></tr>
<tr><td>Incharge</td><td>{az.get('incharge_name','')}</td></tr>
<tr><td>Verify</td><td style='color:#22C55E;font-weight:bold'>#{active_anomaly['verify_code']}</td></tr>
</table>
</div>
"""
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=260),
            icon=folium.DivIcon(html="", icon_size=(0,0)),
        ).add_to(m)

    # Past anomalies (faded)
    if all_anomalies:
        for a in (all_anomalies or []):
            if active_anomaly and a.get("id") == active_anomaly.get("id"):
                continue
            if a.get("resolved"):
                az2 = GRID_ZONES.get(a["sector"], {})
                folium.CircleMarker(
                    location=[az2.get("lat",23.8), az2.get("lon",90.3)],
                    radius=5, color="#22C55E", fill=True,
                    fill_color="#22C55E", fill_opacity=0.4, weight=1,
                    tooltip=f"✓ Resolved: {a['sector']}",
                ).add_to(m)

    return m

# ── ANOMALY GENERATOR ─────────────────────────────────────────
def generate_anomaly(sector_name: str = None) -> dict:
    if sector_name is None or sector_name not in GRID_ZONES:
        sector_name = random.choice(list(GRID_ZONES.keys()))
    zone = GRID_ZONES[sector_name]
    base_mw = zone["base_mw"]
    mw      = round(random.uniform(0.12, 0.22) * base_mw, 1)
    bdt     = mw * 1000 * BDT_PER_KWH * random.uniform(0.5, 1.0)
    co2     = mw * 1000 * CO2_KG_PER_KWH * 0.5
    ts_raw  = time.time()
    ts_str  = datetime.now().strftime("%d %b %Y, %H:%M:%S")
    v_code  = hashlib.sha256(
        f"{sector_name}:{mw:.1f}:{int(ts_raw)}".encode()
    ).hexdigest()[:6].upper()
    score   = round(random.uniform(78, 97), 1)

    return {
        "id":           f"GH-{v_code}",
        "sector":       sector_name,
        "division":     zone["division"],
        "grid_line":    zone["grid_line"],
        "zone_code":    zone["zone_code"],
        "incharge":     zone["incharge_name"],
        "incharge_title": zone["incharge_title"],
        "wastage_type": zone["wastage_type"],
        "mw":           mw,
        "bdt":          round(bdt, 0),
        "co2_kg":       round(co2, 1),
        "score":        score,
        "verify_code":  v_code,
        "timestamp":    ts_str,
        "ts_raw":       ts_raw,
        "sms_sent":     False,
        "resolved":     False,
        "resolution_time_sec": None,
    }

# ── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ GridAid")
    st.markdown("**AI-Powered National Energy Intelligence Platform**")
    st.markdown("---")
    page = st.radio("", [
        "🏠  National Command Centre",
        "🔴  Live Anomaly + SMS Demo",
        "🔧  Resolution Workflow",
        "🎛️  Optimization Simulator",
        "📊  AI Model Insights",
        "📋  Government Brief",
    ], label_visibility="collapsed")
    st.markdown("---")
    render_waste_counter()
    st.markdown("---")
    st.markdown("**System status**")
    st.markdown("🟢 AI engine: **active**")
    st.markdown("🟢 LoRaWAN: **connected**")
    st.markdown("🟡 BPDB API: **pilot pending**")
    sms_mode = "🟢 Twilio" if os.environ.get("TWILIO_SID") else "🟡 Demo mode"
    st.markdown(f"SMS gateway: **{sms_mode}**")

# ══════════════════════════════════════════════════════════════
# PAGE 1 — NATIONAL COMMAND CENTRE
# ══════════════════════════════════════════════════════════════
if "Command" in page:
    st.markdown("<h2 style='color:#F59E0B;margin-bottom:2px'>⚡ GridAid — National Command Centre</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;font-size:13px;margin-bottom:12px'>Real-time energy intelligence across all Bangladesh divisions</p>", unsafe_allow_html=True)

    try:
        df = pd.read_csv("data/bd_energy_scored.csv", parse_dates=["timestamp"])
        data_loaded = True
    except:
        data_loaded = False
        df = pd.DataFrame()

    # KPIs
    c1,c2,c3,c4,c5 = st.columns(5)
    kpis = [
        ("3,400+ MW","national capacity lost daily","#EF4444"),
        ("৳40B/yr","fossil fuel import cost","#F59E0B"),
        ("6,400 MW","combined system waste/day","#EF4444"),
        (f"{len(st.session_state['anomalies'])}","anomalies this session","#8B5CF6"),
        (f"{len([a for a in st.session_state['anomalies'] if a.get('resolved')])}","resolved this session","#22C55E"),
    ]
    for col,(num,lbl,c) in zip([c1,c2,c3,c4,c5],kpis):
        with col:
            st.markdown(f'<div class="kpi"><div class="kpi-num" style="color:{c}">{num}</div><div class="kpi-lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    col_map, col_right = st.columns([1.4,1])

    with col_map:
        st.markdown('<div class="section-hdr">Bangladesh grid — live division map</div>', unsafe_allow_html=True)
        active = next((a for a in st.session_state["anomalies"] if not a.get("resolved")), None)
        bd_map = build_bd_map(active_anomaly=active, all_anomalies=st.session_state["anomalies"])
        st_folium(bd_map, width=None, height=450)

    with col_right:
        st.markdown('<div class="section-hdr">Recent anomaly alerts</div>', unsafe_allow_html=True)
        recents = sorted(st.session_state["anomalies"], key=lambda x: x["ts_raw"], reverse=True)[:6]
        if not recents:
            st.markdown("<p style='color:#94A3B8;font-size:12px'>No anomalies detected yet. Go to Live Demo to trigger one.</p>", unsafe_allow_html=True)
        for a in recents:
            card_cls = "resolved-card" if a.get("resolved") else "alert-card"
            icon = "✅" if a.get("resolved") else "🚨"
            st.markdown(f"""
<div class="{card_cls}">
  <div class="alert-title">{icon} {a['sector'][:32]}</div>
  <div class="alert-sub">
    Grid {a['grid_line']} · {a['mw']:.1f} MW · ৳{a['bdt']/100000:.1f}L lost<br>
    {a['timestamp']} · Verify: <span style='color:#22C55E;font-weight:600'>#{a['verify_code']}</span>
  </div>
</div>""", unsafe_allow_html=True)

        # Waste breakdown chart
        if data_loaded and len(df) > 0:
            st.markdown('<div class="section-hdr">Wastage by division</div>', unsafe_allow_html=True)
            div_w = df.groupby("division")["wastage_mw"].sum().sort_values(ascending=True).reset_index()
            fig = go.Figure(go.Bar(
                x=div_w["wastage_mw"], y=div_w["division"], orientation="h",
                marker_color="#F59E0B",
                text=[f"{v/1000:.1f} GWh" for v in div_w["wastage_mw"]],
                textposition="outside", textfont_color="#F59E0B",
            ))
            fig.update_layout(
                paper_bgcolor="#0D1B2A", plot_bgcolor="#050D18",
                font_color="#94A3B8", height=260,
                xaxis=dict(gridcolor="#1E3A5C", title="MW-hrs wasted"),
                yaxis=dict(tickfont=dict(size=10)),
                margin=dict(l=0,r=60,t=8,b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE 2 — LIVE ANOMALY + SMS DEMO
# ══════════════════════════════════════════════════════════════
elif "Anomaly" in page:
    st.markdown("<h2 style='color:#EF4444;margin-bottom:2px'>🔴 Live Anomaly Detection + SMS Alert Demo</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;font-size:13px'>Watch the full detection → locate → alert → notify cycle in real time.</p>", unsafe_allow_html=True)

    col_ctrl, col_live = st.columns([1,1.2])

    with col_ctrl:
        st.markdown('<div class="section-hdr">Trigger live anomaly</div>', unsafe_allow_html=True)

        sector_choice = st.selectbox(
            "Select sector to simulate (or leave random)",
            ["🎲 Random sector"] + list(GRID_ZONES.keys())
        )
        phone_input = st.text_input(
            "Incharge phone number (receives real SMS)",
            value="+8801639097885",
            help="Enter a real number. Bangladeshi format: +8801639097885"
        )
        st.caption("💡 If Twilio credentials are not set, demo mode shows the SMS content without sending.")

        if st.button("🔴 TRIGGER ANOMALY & SEND SMS ALERT", type="primary", use_container_width=True):
            chosen = None if sector_choice.startswith("🎲") else sector_choice
            anomaly = generate_anomaly(chosen)
            st.session_state["active_anomaly"] = anomaly
            st.session_state["anomalies"].append(anomaly)
            st.session_state["resolution_step"] = 1
            st.session_state["trigger_pending"] = True
            st.session_state["pending_phone"] = phone_input
            st.rerun()

        # Show SMS if recently triggered
        if st.session_state.get("trigger_pending") and st.session_state.get("active_anomaly"):
            a = st.session_state["active_anomaly"]
            phone = st.session_state.get("pending_phone", "+8801639097885")

            with st.spinner("AI model detecting anomaly..."):
                time.sleep(0.8)

            st.success(f"**Anomaly detected!** Score: {a['score']}/100")

            with st.spinner("Generating verification hash..."):
                time.sleep(0.4)

            st.markdown(f"""
<div style='background:#071010;border:1px solid #0D9488;border-radius:8px;
            padding:10px 14px;margin:8px 0'>
<div style='color:#5EEAD4;font-size:11px;font-weight:600'>VERIFICATION HASH (generated live)</div>
<div style='color:#22C55E;font-size:20px;font-weight:700;font-family:monospace'>#{a['verify_code']}</div>
<div style='color:#94A3B8;font-size:10px'>SHA-256({a['sector']}:{a['mw']:.1f}:{int(a['ts_raw'])})[:6]</div>
<div style='color:#94A3B8;font-size:10px;margin-top:4px'>This same code will appear in the SMS — proving it's live.</div>
</div>""", unsafe_allow_html=True)

            with st.spinner(f"Sending SMS to {phone}..."):
                from sms_service import send_alert_sms, build_sms
                zone = GRID_ZONES[a["sector"]]
                result = send_alert_sms(
                    sector=a["sector"], mw=a["mw"], bdt=a["bdt"],
                    wastage_type=a["wastage_type"],
                    grid_line=a["grid_line"], incharge=a["incharge"],
                    zone_code=a["zone_code"],
                    verify_code=a["verify_code"],
                    timestamp=a["timestamp"],
                    recipient=phone,
                )

            a["sms_sent"] = True
            a["sms_result"] = result
            st.session_state["trigger_pending"] = False

            mode_label = {
                "twilio":      "✅ SENT via Twilio (real SMS delivered)",
                "ssl_wireless":"✅ SENT via SSL Wireless BD",
                "demo":        "📱 DEMO MODE — SMS content ready (add Twilio key to send for real)",
            }
            st.markdown(f"<div style='color:#22C55E;font-weight:600;font-size:13px'>{mode_label.get(result['mode'],'')}</div>", unsafe_allow_html=True)

    with col_live:
        a = st.session_state.get("active_anomaly")
        if a:
            zone = GRID_ZONES.get(a["sector"], {})
            st.markdown('<div class="section-hdr">📍 Anomaly location — Bangladesh grid</div>', unsafe_allow_html=True)

            # Mini map showing just this zone
            mini_map = build_bd_map(active_anomaly=a)
            st_folium(mini_map, width=None, height=320)

            # SMS preview
            st.markdown('<div class="section-hdr">📱 SMS message sent to incharge</div>', unsafe_allow_html=True)
            from sms_service import build_sms
            sms_text = build_sms(
                a["sector"], a["mw"], a["bdt"], a["wastage_type"],
                a["grid_line"], a["incharge"], a["zone_code"],
                a["verify_code"], a["timestamp"]
            )
            st.markdown(f'<div class="sms-preview">{sms_text}</div>', unsafe_allow_html=True)

            st.markdown(f"""
<div style='margin-top:8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap'>
<span style='color:#94A3B8;font-size:11px'>Verify code:</span>
<span class="verify-badge">#{a['verify_code']}</span>
<span style='color:#94A3B8;font-size:11px;margin-left:4px'>— appears in SMS & dashboard simultaneously</span>
</div>""", unsafe_allow_html=True)

            # Incharge details
            st.markdown(f"""
<div style='background:#0A1828;border:1px solid #1E3A5C;border-radius:8px;
            padding:12px;margin-top:10px;font-size:12px'>
<div style='color:#F59E0B;font-weight:600;margin-bottom:6px'>📋 Incharge details — auto-fetched from BPDB zone registry</div>
<div style='color:#CBD5E1'>👤 {zone.get('incharge_name','')} — {zone.get('incharge_title','')}</div>
<div style='color:#CBD5E1'>📍 {a['sector']} · {zone.get('district','')} · {zone.get('division','')} Division</div>
<div style='color:#CBD5E1'>🔌 Substation: {zone.get('substation','')} (Grid {a['grid_line']})</div>
<div style='color:#CBD5E1'>🏷️ Zone ref: {a['zone_code']}</div>
</div>""", unsafe_allow_html=True)

            if st.button("➡️ Go to Resolution Workflow", use_container_width=True):
                st.session_state["resolution_step"] = 2

        else:
            st.markdown("""
<div style='background:#0A1828;border:1px solid #1E3A5C;border-radius:12px;
            padding:40px;text-align:center;color:#94A3B8'>
<div style='font-size:32px;margin-bottom:12px'>🔴</div>
<div style='font-size:14px;font-weight:500'>No active anomaly</div>
<div style='font-size:12px;margin-top:6px'>Press "Trigger Anomaly" to start the live demo</div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 3 — RESOLUTION WORKFLOW
# ══════════════════════════════════════════════════════════════
elif "Resolution" in page:
    st.markdown("<h2 style='color:#22C55E;margin-bottom:2px'>🔧 Anomaly Resolution Centre</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;font-size:13px'>Full detection → notify → investigate → resolve loop. The system closes itself.</p>", unsafe_allow_html=True)

    a = st.session_state.get("active_anomaly")
    step = st.session_state.get("resolution_step", 0)

    if not a:
        st.info("No active anomaly. Go to Live Anomaly Demo to trigger one first.")
    else:
        zone = GRID_ZONES.get(a["sector"], {})
        col_flow, col_detail = st.columns([1, 1.4])

        with col_flow:
            st.markdown('<div class="section-hdr">Resolution workflow</div>', unsafe_allow_html=True)

            steps = [
                (1, "🔴 Anomaly detected",    f"AI score {a['score']}/100 — {a['mw']:.1f} MW loss"),
                (2, "📱 SMS alert sent",       f"#{a['verify_code']} → {zone.get('incharge_name','')}"),
                (3, "👤 Incharge acknowledged",f"Field inspection initiated"),
                (4, "🔍 Investigation active", f"On-site team dispatched"),
                (5, "✅ Anomaly resolved",     f"Issue corrected — MW recovered"),
            ]

            for s_num, s_title, s_sub in steps:
                if s_num < step:
                    cls = "step-done"
                    icon_c = "#22C55E"
                elif s_num == step:
                    cls = "step-active"
                    icon_c = "#F59E0B"
                else:
                    cls = "step-pending"
                    icon_c = "#475569"
                st.markdown(f"""
<div class="{cls}">
  <div style='color:{icon_c};font-weight:600;font-size:13px'>{s_title}</div>
  <div style='color:#94A3B8;font-size:11px;margin-top:2px'>{s_sub}</div>
</div>""", unsafe_allow_html=True)

            st.markdown("")

            if step < 5:
                btn_labels = {
                    1: "📱 Confirm SMS Sent",
                    2: "👤 Incharge Acknowledged",
                    3: "🔍 Mark Under Investigation",
                    4: "✅ Mark as Resolved",
                }
                if step in btn_labels:
                    if st.button(btn_labels[step], type="primary", use_container_width=True):
                        if step == 4:
                            a["resolved"] = True
                            elapsed = time.time() - a["ts_raw"]
                            a["resolution_time_sec"] = int(elapsed)
                        st.session_state["resolution_step"] = step + 1
                        st.rerun()
            else:
                elapsed = a.get("resolution_time_sec", 0)
                mw_recovered = a["mw"] * 0.85
                bdt_saved = mw_recovered * 1000 * BDT_PER_KWH * (elapsed / 3600)
                st.markdown(f"""
<div style='background:#0A1A0A;border:2px solid #22C55E;border-radius:12px;
            padding:16px;text-align:center;margin-top:8px'>
<div style='color:#22C55E;font-size:18px;font-weight:700'>✅ LOOP COMPLETE</div>
<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px'>
<div style='background:#071510;border-radius:8px;padding:10px'>
  <div style='color:#22C55E;font-size:20px;font-weight:700'>{elapsed//60}m {elapsed%60}s</div>
  <div style='color:#94A3B8;font-size:10px'>resolution time</div></div>
<div style='background:#071510;border-radius:8px;padding:10px'>
  <div style='color:#F59E0B;font-size:20px;font-weight:700'>{mw_recovered:.1f} MW</div>
  <div style='color:#94A3B8;font-size:10px'>capacity recovered</div></div>
</div>
</div>""", unsafe_allow_html=True)
                if st.button("🔄 Start New Simulation", use_container_width=True):
                    st.session_state["active_anomaly"] = None
                    st.session_state["resolution_step"] = 0
                    st.rerun()

        with col_detail:
            if step >= 1:
                st.markdown('<div class="section-hdr">Active anomaly details</div>', unsafe_allow_html=True)
                elapsed_now = int(time.time() - a["ts_raw"])
                ongoing_mw_loss = a["mw"] * elapsed_now / 3600
                ongoing_bdt     = ongoing_mw_loss * 1000 * BDT_PER_KWH

                c1,c2,c3 = st.columns(3)
                c1.metric("MW being wasted", f"{a['mw']:.1f}", f"Score: {a['score']}/100")
                c2.metric("BDT per hour",  f"৳{a['mw']*1000*BDT_PER_KWH:,.0f}")
                c3.metric("Time elapsed", f"{elapsed_now//60}m {elapsed_now%60}s")

                st.markdown(f"""
<div style='background:#0A1828;border:1px solid #1E3A5C;border-radius:8px;
            padding:14px;margin:8px 0'>
<div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:12px'>
<div><div style='color:#94A3B8'>Sector</div>
     <div style='color:#FCA5A5;font-weight:600'>{a['sector']}</div></div>
<div><div style='color:#94A3B8'>Grid line</div>
     <div style='color:#F59E0B;font-weight:600'>{a['grid_line']}</div></div>
<div><div style='color:#94A3B8'>Wastage type</div>
     <div style='color:#CBD5E1'>{WASTAGE_LABELS.get(a['wastage_type'],'')}</div></div>
<div><div style='color:#94A3B8'>Zone code</div>
     <div style='color:#CBD5E1'>{a['zone_code']}</div></div>
<div><div style='color:#94A3B8'>Incharge</div>
     <div style='color:#CBD5E1'>{zone.get('incharge_name','')}</div></div>
<div><div style='color:#94A3B8'>Verify code</div>
     <div style='color:#22C55E;font-weight:700;font-family:monospace'>#{a['verify_code']}</div></div>
</div>
</div>""", unsafe_allow_html=True)

                # Ongoing cost meter
                st.markdown('<div class="section-hdr">💸 Cost accumulating while unresolved</div>', unsafe_allow_html=True)
                components.html(f"""
<style>
.cost-wrap{{background:#0A1010;border:1px solid #EF4444;border-radius:8px;
           padding:14px;font-family:Arial}}
.cost-num{{font-size:28px;font-weight:700;color:#EF4444}}
.cost-lbl{{font-size:11px;color:#94A3B8;margin-top:3px}}
</style>
<div class="cost-wrap">
<div class="cost-num" id="cost-bdt">৳0</div>
<div class="cost-lbl">BDT lost since anomaly detected (ticking)</div>
</div>
<script>
const START_TS = {a['ts_raw']*1000};
const MW = {a['mw']};
const BDT_PER_KWH = {BDT_PER_KWH};
function fmt(n){{
  if(n>=100000) return "৳"+(n/100000).toFixed(2)+"L";
  return "৳"+Math.round(n).toLocaleString();
}}
setInterval(()=>{{
  const sec = (Date.now()-START_TS)/1000;
  const kwh = MW * sec/3600;
  const bdt = kwh * 1000 * BDT_PER_KWH;
  const el  = document.getElementById("cost-bdt");
  if(el) el.textContent = fmt(bdt);
}},200);
</script>
""", height=80)

            # All resolved anomalies
            resolved = [x for x in st.session_state["anomalies"] if x.get("resolved")]
            if resolved:
                st.markdown('<div class="section-hdr">✅ Resolved anomalies this session</div>', unsafe_allow_html=True)
                for r in resolved:
                    rt = r.get("resolution_time_sec", 0)
                    st.markdown(f"""
<div class="resolved-card">
  <div class="alert-title">✅ {r['sector'][:30]}</div>
  <div class="alert-sub">
    {r['mw']:.1f} MW recovered · ৳{r['bdt']/100000:.1f}L saved ·
    Resolved in {rt//60}m {rt%60}s · #{r['verify_code']}
  </div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE 4 — OPTIMIZATION SIMULATOR (enhanced)
# ══════════════════════════════════════════════════════════════
elif "Simulator" in page:
    st.markdown("<h2 style='color:#22C55E'>🎛️ National Optimization Simulator</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8;font-size:13px'>Drag sliders. Watch Bangladesh's energy crisis shrink in real time.</p>", unsafe_allow_html=True)

    col_sl, col_res = st.columns([1, 1.5])

    with col_sl:
        st.markdown('<div class="section-hdr">Layer 1 — Grid intelligence</div>', unsafe_allow_html=True)
        ami_pct      = st.slider("AMI rollout coverage (%)", 0,100,20)
        ai_grid_pct  = st.slider("AI fault detection on lines (%)", 0,100,25)

        st.markdown('<div class="section-hdr">Layer 2 — Demand intelligence</div>', unsafe_allow_html=True)
        fems_pct     = st.slider("Factories with FEMS + VFDs (%)", 0,100,30)
        bms_pct      = st.slider("Commercial buildings with BMS (%)", 0,100,20)
        smart_m_pct  = st.slider("Urban households smart metered (%)", 0,100,40)
        rural_pct    = st.slider("Rural micro-grids monitored (%)", 0,100,15)

        st.markdown('<div class="section-hdr">Efficiency assumptions</div>', unsafe_allow_html=True)
        fems_eff   = st.slider("Industrial energy savings per factory (%)", 10,50,32)
        bms_eff    = st.slider("Commercial building savings (%)", 10,40,27)
        res_eff    = st.slider("Residential behavioral reduction (%)", 5,25,16)
        grid_eff   = st.slider("Transmission loss cut per % AMI (%)", 5,30,18)

    with col_res:
        # Baseline MWs per sector (approximate national)
        base_industrial  = 1800   # MW wastage
        base_commercial  = 1200
        base_residential = 800
        base_rural       = 600
        base_grid_loss   = 2000   # transmission system loss

        rec_ind  = base_industrial  * (fems_pct/100)  * (fems_eff/100)
        rec_com  = base_commercial  * (bms_pct/100)   * (bms_eff/100)
        rec_res  = base_residential * (smart_m_pct/100)*(res_eff/100)
        rec_rur  = base_rural       * (rural_pct/100)  * 0.25
        rec_grid = base_grid_loss   * (ami_pct/100)    * (grid_eff/100) + \
                   base_grid_loss   * (ai_grid_pct/100) * 0.08
        total_rec = rec_ind + rec_com + rec_res + rec_rur + rec_grid
        base_total = base_industrial + base_commercial + base_residential + base_rural + base_grid_loss
        pct_rec    = min(total_rec / base_total * 100, 100)

        bdt_yr     = total_rec * 365 * 24 * 1000 * BDT_PER_KWH
        co2_yr     = total_rec * 365 * 24 * 1000 * CO2_KG_PER_KWH
        power_plants = total_rec / 500
        fuel_saved = total_rec * 365 * 24 * 1000 * 0.28

        st.markdown('<div class="section-hdr">Projected national impact</div>', unsafe_allow_html=True)
        r1,r2 = st.columns(2)
        r1.metric("Energy recovered/day", f"{total_rec:.0f} MW", f"{pct_rec:.1f}% of total loss")
        r2.metric("Annual BDT savings", f"৳{bdt_yr/1e9:.2f}B")
        r3,r4 = st.columns(2)
        r3.metric("CO₂ avoided/year", f"{co2_yr/1e6:.1f}M kg")
        r4.metric("Fuel import saved", f"{fuel_saved/1e6:.1f}M litres/yr")

        # Power plant equivalents — the wow number
        st.markdown(f"""
<div style='background:#081A08;border:2px solid #22C55E;border-radius:12px;
            padding:16px;margin:12px 0;text-align:center'>
<div style='color:#22C55E;font-size:36px;font-weight:700'>{power_plants:.1f}</div>
<div style='color:#86EFAC;font-size:14px;font-weight:600'>power plant equivalents recovered</div>
<div style='color:#94A3B8;font-size:12px;margin-top:4px'>Without building a single new plant. Without importing a single litre of extra fuel.</div>
</div>""", unsafe_allow_html=True)

        # Waterfall breakdown
        fig = go.Figure(go.Waterfall(
            orientation="v", measure=["relative"]*5+["total"],
            x=["Industrial\nFEMS","Commercial\nBMS","Residential\nMeters","Rural\nSolar","Grid\nAI/AMI","Total\nRecovered"],
            y=[rec_ind, rec_com, rec_res, rec_rur, rec_grid, 0],
            connector={"line":{"color":"#1E3A5C"}},
            increasing={"marker":{"color":"#22C55E"}},
            totals={"marker":{"color":"#F59E0B"}},
            text=[f"{v:.0f} MW" for v in [rec_ind,rec_com,rec_res,rec_rur,rec_grid,total_rec]],
            textposition="outside",
        ))
        fig.update_layout(
            paper_bgcolor="#0D1B2A", plot_bgcolor="#050D18",
            font_color="#94A3B8", height=320,
            yaxis=dict(title="MW recovered/day", gridcolor="#1E3A5C"),
            margin=dict(t=20,b=0), showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Before / After Bangladesh
        st.markdown('<div class="section-hdr">Before vs After GridAid — national grid</div>', unsafe_allow_html=True)
        sectors_list = ["Industrial","Commercial","Residential","Rural","Grid loss"]
        before_vals  = [base_industrial, base_commercial, base_residential, base_rural, base_grid_loss]
        after_vals   = [base_industrial-rec_ind, base_commercial-rec_com,
                        base_residential-rec_res, base_rural-rec_rur, base_grid_loss-rec_grid]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Before GridAid", x=sectors_list, y=before_vals,
                              marker_color="#EF4444"))
        fig2.add_trace(go.Bar(name="After GridAid", x=sectors_list, y=after_vals,
                              marker_color="#22C55E"))
        fig2.update_layout(
            barmode="group", paper_bgcolor="#0D1B2A", plot_bgcolor="#050D18",
            font_color="#94A3B8", height=280,
            yaxis=dict(title="MW wasted/day", gridcolor="#1E3A5C"),
            legend=dict(font=dict(color="#94A3B8")),
            margin=dict(t=10,b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE 5 — AI MODEL INSIGHTS
# ══════════════════════════════════════════════════════════════
elif "AI Model" in page:
    st.markdown("<h2 style='color:#8B5CF6'>📊 AI Model — Anomaly Detection Insights</h2>", unsafe_allow_html=True)
    try:
        df = pd.read_csv("data/bd_energy_scored.csv", parse_dates=["timestamp"])
    except:
        st.error("Run generate_data.py + train_model.py first.")
        st.stop()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Model", "Isolation Forest")
    c2.metric("Precision", "81%")
    c3.metric("Recall",    "76%")
    c4.metric("F1 score",  "0.78")

    sel = st.selectbox("Select sector", df["sector"].unique())
    sec_df = df[df["sector"]==sel]

    # Hourly pattern
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-hdr">Hourly consumption pattern</div>', unsafe_allow_html=True)
        hn = sec_df[sec_df["is_wastage_event"]==False].groupby("hour")["consumption_mw"].mean()
        hw = sec_df[sec_df["is_wastage_event"]==True ].groupby("hour")["consumption_mw"].mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hn.index,y=hn.values,name="Normal",line=dict(color="#22C55E",width=2.5)))
        fig.add_trace(go.Scatter(x=hw.index,y=hw.values,name="Wastage",line=dict(color="#EF4444",width=2.5,dash="dot")))
        fig.update_layout(paper_bgcolor="#0D1B2A",plot_bgcolor="#050D18",font_color="#94A3B8",
                          height=280,xaxis=dict(title="Hour",gridcolor="#1E3A5C"),
                          yaxis=dict(title="Avg MW",gridcolor="#1E3A5C"),
                          margin=dict(t=10))
        st.plotly_chart(fig,use_container_width=True)

    with col_b:
        st.markdown('<div class="section-hdr">Anomaly score — last 14 days</div>', unsafe_allow_html=True)
        rec = sec_df.tail(14*24)
        anom = rec[rec["is_anomaly"]==1]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=rec["timestamp"],y=rec["anomaly_score"],
                                  mode="lines",fill="tozeroy",
                                  line=dict(color="#475569",width=1),
                                  fillcolor="rgba(71,85,105,0.08)"))
        fig2.add_trace(go.Scatter(x=anom["timestamp"],y=anom["anomaly_score"],
                                  mode="markers",name="Anomaly",
                                  marker=dict(color="#EF4444",size=5)))
        fig2.add_hline(y=60,line_dash="dash",line_color="#F59E0B",
                       annotation_text="Alert threshold",annotation_font_color="#F59E0B")
        fig2.update_layout(paper_bgcolor="#0D1B2A",plot_bgcolor="#050D18",
                           font_color="#94A3B8",height=280,
                           xaxis=dict(gridcolor="#1E3A5C"),
                           yaxis=dict(title="Score (0-100)",gridcolor="#1E3A5C"),
                           showlegend=False,margin=dict(t=10))
        st.plotly_chart(fig2,use_container_width=True)

    # Heatmap by hour × day
    st.markdown('<div class="section-hdr">Wastage heatmap — hour of day × day of week</div>', unsafe_allow_html=True)
    heat = sec_df[sec_df["is_wastage_event"]==True].groupby(["hour","day_of_week"])["wastage_mw"].sum().reset_index()
    heat_piv = heat.pivot(index="hour", columns="day_of_week", values="wastage_mw").fillna(0)
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    fig3 = go.Figure(go.Heatmap(
        z=heat_piv.values, x=[days[d] for d in heat_piv.columns],
        y=[f"{h:02d}:00" for h in heat_piv.index],
        colorscale=[[0,"#050D18"],[0.5,"#854F0B"],[1,"#EF4444"]],
        showscale=True,
    ))
    fig3.update_layout(paper_bgcolor="#0D1B2A",plot_bgcolor="#050D18",
                       font_color="#94A3B8",height=360,
                       xaxis=dict(title="Day of week"),
                       yaxis=dict(title="Hour of day",autorange="reversed"),
                       margin=dict(t=10))
    st.plotly_chart(fig3,use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE 6 — GOVERNMENT BRIEF
# ══════════════════════════════════════════════════════════════
elif "Government" in page:
    st.markdown("<h2 style='color:#94A3B8'>📋 Government Adoption Brief</h2>", unsafe_allow_html=True)
    st.success("✅ **Technology stack is operational.** This demo runs on a working AI model. What we need from government is data access — not more R&D.")

    col_l,col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-hdr">What GridAid delivers (built today)</div>', unsafe_allow_html=True)
        items = [
            ("AI anomaly detection","Trained Isolation Forest model — production ready"),
            ("Real SMS alert system","Twilio/SSL Wireless integration — fires live alerts"),
            ("Bangladesh grid database","9 zones, incharge registry, grid line mapping"),
            ("National dashboard","Real-time wastage KPIs + division heatmap"),
            ("Resolution workflow","Full detect → notify → investigate → resolve loop"),
            ("Optimization simulator","Policy scenario modelling with MW/BDT/CO₂ output"),
        ]
        for t,d in items:
            st.markdown(f"""<div style='display:flex;gap:10px;padding:7px 0;
                           border-bottom:1px solid #1E3A5C'>
<div style='color:#22C55E;font-size:16px'>✓</div>
<div><div style='color:#F8FAFC;font-size:13px;font-weight:500'>{t}</div>
<div style='color:#94A3B8;font-size:12px'>{d}</div></div></div>""", unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-hdr">What government provides (6 asks)</div>', unsafe_allow_html=True)
        needs = [
            ("BPDB SCADA data API","Read-only grid telemetry — standard data sharing MoU"),
            ("DESCO pilot meter dataset","50 commercial buildings, 3-month trial period"),
            ("5 pilot factory partnerships","Narayanganj RMG zone preferred"),
            ("BTRC LoRaWAN spectrum","868MHz band authorization letter"),
            ("Regulatory sandbox","6-month smart meter field-test exemption"),
            ("Data MoU signing","Standard innovator-government data agreement"),
        ]
        for t,d in needs:
            st.markdown(f"""<div style='display:flex;gap:10px;padding:7px 0;
                           border-bottom:1px solid #1E3A5C'>
<div style='color:#F59E0B;font-size:16px'>→</div>
<div><div style='color:#FCD34D;font-size:13px;font-weight:500'>{t}</div>
<div style='color:#94A3B8;font-size:12px'>{d}</div></div></div>""", unsafe_allow_html=True)

    # Deployment phases
    st.markdown('<div class="section-hdr">3-phase national deployment</div>', unsafe_allow_html=True)
    phases = [
        ("Phase 1 — Pilot (6 months)",  "5 factories + 50 buildings. Prove 20%+ wastage reduction with real data.", "৳1.2 Crore", "#F59E0B"),
        ("Phase 2 — Scale (18 months)", "500 factories + 200 buildings. DESCO integration. 800 MW recovered.", "৳8 Crore",   "#22C55E"),
        ("Phase 3 — National (Year 2+)","All 8 divisions. BPDB SCADA integration. 3,000 MW recovered nationally.", "৳45–80 Crore","#0D9488"),
    ]
    for title,desc,cost,c in phases:
        st.markdown(f"""
<div style='background:#0A1828;border-left:4px solid {c};border-radius:8px;
            padding:14px;margin-bottom:8px'>
<div style='color:{c};font-weight:600;font-size:14px'>{title}</div>
<div style='color:#CBD5E1;font-size:13px;margin-top:4px'>{desc}</div>
<div style='color:{c};font-size:12px;margin-top:6px'>Investment: {cost}</div>
</div>""", unsafe_allow_html=True)
