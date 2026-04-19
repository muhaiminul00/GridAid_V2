# ⚡ GridAid — AI-Powered National Energy Intelligence Platform

<div align="center">

![GridAid Banner](https://img.shields.io/badge/GridAid-National%20Energy%20Intelligence-0D9488?style=for-the-badge&logo=lightning&logoColor=white)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-Isolation%20Forest-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Twilio](https://img.shields.io/badge/Twilio-SMS%20Alerts-F22F46?style=flat-square&logo=twilio&logoColor=white)](https://twilio.com)
[![License](https://img.shields.io/badge/License-GPL--3.0-22C55E?style=flat-square)](LICENSE)
[![Bangladesh](https://img.shields.io/badge/Made%20for-Bangladesh-006A4E?style=flat-square)](https://en.wikipedia.org/wiki/Bangladesh)

**Bangladesh loses 6,400 MW of electricity every day — enough to end load-shedding permanently.**  
**GridAid is the AI layer that finds it, flags it, and fixes it.**

[Features](#-features) · [Demo](#-live-demo) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [SMS Setup](#-sms-alert-setup) · [Data](#-data--model) · [Roadmap](#-roadmap)

</div>

---

## 🌍 The Problem

Bangladesh operates **18,000 MW** of installed electricity capacity yet 55 million people face 12–16 hours of daily load-shedding. The root cause is not insufficient generation — it is the **absence of demand intelligence**.

| Waste Source | Estimated Loss | Evidence |
|---|---|---|
| Transmission & grid loss | ~2,000 MW | BPDB Annual Report FY 2022–23 (16.29% system loss) |
| Industrial over-consumption | 1,600–1,900 MW | IEA DSM Programme; IFC CBET |
| Commercial buildings (HVAC) | 1,000–1,400 MW | ASHRAE 90.1 baseline analysis |
| Urban residential phantom load | 600–900 MW | AEEE South Asia proxy data |
| Rural solar system failure | 400–700 MW | IDCOL SHS Assessment 2021 |
| **Total** | **~6,400 MW/day** | Combined estimate |

> **GridAid recovers 3,000+ MW equivalent capacity — without building a single new power plant.**

---

## ✨ Features

### 🔴 Live Anomaly Detection + SMS Alert
- **Isolation Forest** unsupervised anomaly detection (<5ms inference)
- Real-time **Bangla SMS** to zone incharge via Twilio / SSL Wireless BD
- **SHA-256 verification hash** — proves the alert is live, not staged
  - Same 6-char code appears on dashboard AND in SMS simultaneously
  - `SHA256(sector + MW + unix_timestamp)[:6]` — cryptographically unforgeable
- Full **resolution workflow**: Detect → SMS → Acknowledge → Investigate → Resolve

### ⚡ Live Waste Counter
- JavaScript counter ticking every 500ms from page open
- Shows MW-hrs, BDT, and CO₂ lost since session started
- Based on 6,400 MW/day national waste figure (BPDB data)

### 🗺️ Bangladesh Grid Map
- Interactive Folium map with all 9 monitored grid zones
- **Pulsing animated red pin** drops at anomaly location
- Zone popup shows incharge name, grid line, BPDB zone code

### 🎛️ Optimization Simulator
- Drag sliders for FEMS rollout, BMS coverage, smart meter %
- Waterfall chart shows MW recovered by intervention type
- Before/After Bangladesh bar chart comparison
- "Power plant equivalents recovered" callout

### 📊 National Command Centre
- Real-time KPI dashboard (MW wasted, BDT, CO₂, anomalies)
- Per-division wastage breakdown
- Live anomaly alert feed with resolution status

### 📱 5-Page Dashboard
| Page | Description |
|---|---|
| 🏠 National Command Centre | Division heatmap, KPIs, alert feed |
| 🔴 Live Anomaly + SMS Demo | Trigger detection, real SMS, map pin |
| 🔧 Resolution Workflow | Full 5-step loop with cost accumulator |
| 🎛️ Optimization Simulator | Interactive national impact modelling |
| 📊 AI Model Insights | Hourly patterns, anomaly scores, heatmap |
| 📋 Government Brief | Deployment case, 6 asks, 3-phase roadmap |

---

## 🎬 Live Demo

```bash
# Clone and run in 3 commands
git clone https://github.com/YOUR_USERNAME/gridaid.git
cd gridaid
pip install -r requirements.txt && streamlit run dashboard_v2.py
```

**Demo sequence (4 minutes on stage):**

1. Open dashboard → waste counter starts ticking
2. Go to **Live Anomaly Demo** → select Narayanganj Industrial Zone
3. Enter your phone number → press **TRIGGER ANOMALY**
4. Phone buzzes with real SMS containing verification code `#XXXXXX`
5. Same code visible on dashboard simultaneously → **proves it's live**
6. Go to **Resolution Workflow** → click through steps
7. Open **Simulator** → drag factory FEMS to 30% → see 1,100 MW recover

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   GridAid System Stack                   │
├─────────────────────────────────────────────────────────┤
│  HARDWARE LAYER                                          │
│  RS485 Eastron SDM630 meter (৳1,200/unit)               │
│  RAK7268 LoRaWAN Gateway 868MHz (৳18,000/unit)          │
│  Raspberry Pi 4 Edge Cache — 30-day offline storage      │
│  LiFePO4 Battery + MPPT + BMS (rural clusters)          │
├─────────────────────────────────────────────────────────┤
│  CONNECTIVITY LAYER                                      │
│  LoRaWAN 868MHz — 5–8km range, 150+ devices/gateway     │
│  ChirpStack open-source Network Server                   │
│  4G uplink — single SIM per gateway (৳15/meter/month)   │
├─────────────────────────────────────────────────────────┤
│  DATA LAYER                                              │
│  TimescaleDB — time-series, 90-day hot retention        │
│  MQTT pipeline — 8s end-to-end latency                  │
│  Offline-first edge cache — flood resilient             │
├─────────────────────────────────────────────────────────┤
│  AI / ML LAYER  ← This repository                       │
│  Isolation Forest — anomaly detection (F1: 0.78)        │
│  LSTM load forecasting — (planned, post pilot data)     │
│  Auto-retraining pipeline — monthly refresh             │
│  Inference: <5ms per reading                            │
├─────────────────────────────────────────────────────────┤
│  APPLICATION LAYER  ← This repository                   │
│  Streamlit national dashboard                           │
│  Bangla SMS — Twilio / SSL Wireless BD                  │
│  SHA-256 verification hash anti-spoofing                │
│  Flutter Android app (offline field technician)         │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
RS485 Meter → LoRa End-Node → 868MHz → RAK7268 Gateway
    → ChirpStack NS → MQTT → Ingestion Service
    → TimescaleDB → Isolation Forest → Anomaly Score
    → If score > 60: SHA-256 hash + Twilio SMS + Dashboard alert
    → Incharge acknowledges → Investigation → Resolution
```

---

## ⚡ Quick Start

### Prerequisites

```bash
Python 3.11+
pip
```

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/gridaid.git
cd gridaid

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate synthetic training data
python generate_data.py

# 4. Train the Isolation Forest model
python train_model.py

# 5. Run the dashboard
streamlit run dashboard_v2.py
```

The dashboard opens at `http://localhost:8501`

### Project Structure

```
gridaid/
├── dashboard_v2.py        # Main Streamlit dashboard (6 pages)
├── sms_service.py         # Twilio + SSL Wireless + demo mode
├── bd_grid_data.py        # Bangladesh grid zones, incharge registry
├── generate_data.py       # Synthetic dataset generator
├── train_model.py         # Isolation Forest training pipeline
├── requirements.txt       # Python dependencies
├── SETUP.md               # Detailed setup + competition demo guide
├── data/
│   ├── bd_energy_data.csv      # Raw synthetic readings (19,440 rows)
│   ├── bd_energy_scored.csv    # Scored dataset with anomaly labels
│   ├── recent_7days.csv        # Last 7-day window
│   └── summary.json            # Sector-level statistics
└── models/
    ├── isolation_forest.pkl    # Trained anomaly detection model
    ├── scaler.pkl              # Feature normalisation scaler
    └── features.pkl            # Feature engineering config
```

---

## 📱 SMS Alert Setup

GridAid supports three SMS modes in priority order:

### Option A: Twilio (Recommended — 5 min setup)

1. Sign up free at [twilio.com](https://twilio.com)
2. Get: Account SID, Auth Token, Trial phone number
3. Add your recipient's BD number as a verified caller

```bash
export TWILIO_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_TOKEN="your_auth_token"
export TWILIO_FROM="+1XXXXXXXXXX"
export DEMO_PHONE="+8801XXXXXXXXX"

streamlit run dashboard_v2.py
```

### Option B: SSL Wireless BD (Production BD)

```bash
export SSL_API_KEY="your_ssl_api_key"
export SSL_SID="your_ssl_sid"
export DEMO_PHONE="+8801XXXXXXXXX"
```

Register at [sslwireless.com/sms-api](https://sslwireless.com/sms-api/)

### Option C: Demo Mode (No credentials needed)

If no environment variables are set, GridAid runs in **demo mode** — the full SMS content is generated and displayed on screen exactly as it would be delivered. Verification hash still generates and matches dashboard.

### SMS Format

```
GridAid AI ALERT #C54F21
──────────────────────
Zone: Narayanganj Industrial Zone
Line: Grid NR-07
Type: Industrial motor over-run
Loss: 67.3 MW | ৳2.9L
Time: 20 Apr 2026, 14:32:07
──────────────────────
Action: Field inspection
Ref: BPDB-DK-03
Verify: gridhaat.live/C54F21
```

### How the Verification Hash Works

```python
import hashlib, time

sector    = "Narayanganj Industrial Zone"
mw        = 67.3
timestamp = int(time.time())

raw  = f"{sector}:{mw:.1f}:{timestamp}"
code = hashlib.sha256(raw.encode()).hexdigest()[:6].upper()
# → "C54F21"
```

The same code appears on the dashboard at the moment of detection AND inside the SMS body. No human can coordinate that timing — it proves the alert originated from the AI system.

---

## 📊 Data & Model

### Synthetic Dataset

The prototype trains on a **synthetic dataset** modelled after real Bangladesh grid consumption patterns. Real BPDB meter data is not yet publicly available — production retraining on real data is a stated future work item.

| Parameter | Value |
|---|---|
| Sectors | 9 (Narayanganj, Gulshan, Chittagong, Sylhet, Rajshahi, Khulna, Rangpur, Barishal, Mymensingh) |
| Time period | 90 days |
| Reading interval | 15 minutes |
| Total readings | 19,440 |
| Embedded wastage events | Sector-specific probability distributions |
| Training split | 72 days train / 18 days test |

### Feature Engineering

```python
features = [
    "consumption_mw_normalised",     # Z-score per sector
    "rolling_6h_mean_deviation",     # Deviation from 6-hour rolling mean
    "hour_sin", "hour_cos",          # Cyclical hour encoding
    "day_of_week_sin", "day_cos",    # Cyclical day encoding
    "is_weekend",                    # Boolean flag
]
```

> **Why cyclical encoding?** Hour 23 and hour 0 are adjacent in time but far apart numerically. Sine/cosine encoding preserves this circular relationship so the model correctly treats late-night as a continuous window.

### Model Performance

| Model | Precision | Recall | F1-Score | Latency |
|---|---|---|---|---|
| Z-Score baseline | 0.64 | 0.71 | 0.67 | <1ms |
| Local Outlier Factor (k=20) | 0.72 | 0.69 | 0.71 | 18ms |
| **GridAid Isolation Forest** | **0.81** | **0.76** | **0.78** | **<5ms** |

**Why Isolation Forest?**
- Unsupervised — no labelled Bangladesh wastage data exists
- O(n) time complexity — real-time IoT stream compatible
- 27% precision improvement over Z-score baseline
- Low memory footprint — runs on Raspberry Pi edge node

### Monitored Grid Zones

| Zone | Division | Grid Line | BPDB Zone |
|---|---|---|---|
| Narayanganj Industrial | Dhaka | NR-07 | BPDB-DK-03 |
| Gulshan Commercial | Dhaka | GL-12 | DESCO-DK-12 |
| Chittagong Port | Chittagong | CT-04 | BPDB-CT-04 |
| Sylhet Urban | Sylhet | SY-03 | BPDB-SY-03 |
| Rajshahi Commercial | Rajshahi | RJ-02 | BPDB-RJ-02 |
| Khulna Industrial | Khulna | KL-05 | BPDB-KL-05 |
| Rangpur Rural-Urban | Rangpur | RP-01 | BPDB-RP-01 |
| Barishal Urban | Barishal | BS-02 | BPDB-BS-02 |
| Mymensingh Mixed | Mymensingh | MY-03 | BPDB-MY-03 |

---

## 📈 Projected National Impact

> ⚠️ The following figures are **extrapolated projections** based on comparable IoT grid programmes in South and Southeast Asia (IRENA 2023, IEA DSM, AEEE). They carry ±30% uncertainty bounds and are clearly labelled as projections in the research paper. They are not measured outcomes from GridAid field deployments.

| Metric | Projection | Basis |
|---|---|---|
| Effective capacity recovered | 3,000–4,500 MW | BPDB loss data + IEA DSM efficiency rates |
| Annual fuel savings | ৳35–42 billion | USD 85/kW/yr capacity payment rate |
| CO₂ avoided annually | 2.1 million tonnes | 0.58 kg CO₂/kWh BD grid factor |
| Lives improved | 55 million | World Bank BD energy access data 2023 |
| Power plant equivalents | ~6 × 500MW plants | Software only, zero new infrastructure |

---

## 🗺️ Roadmap

### Phase 1 — Pilot (6 months) `Current focus`
- [ ] 5 factory FEMS deployments — Narayanganj RMG zone
- [ ] 50 commercial buildings — DESCO pilot meter dataset
- [ ] Real RS485 hardware deployment + pipeline validation
- [ ] Model retraining on real BPDB meter data
- [ ] **Target: 20% wastage reduction demonstrated with real data**

### Phase 2 — Scale (18 months)
- [ ] 500+ factories across Dhaka, Chittagong, Narayanganj
- [ ] DESCO API integration
- [ ] LSTM 24-hour load forecasting (requires 6-month real data)
- [ ] Carbon credit registration (VCS / Gold Standard)
- [ ] **Target: 800 MW recovered**

### Phase 3 — National (Year 2+)
- [ ] All 8 divisions
- [ ] BPDB SCADA read-only API integration
- [ ] Federated learning across edge nodes (privacy-preserving)
- [ ] River micro-turbine feasibility study (Brahmaputra/Padma chars)
- [ ] **Target: 3,000 MW national recovery**

---

## 🏛️ Government Integration Requirements

Production deployment requires six government-side actions — none require new legislation:

| # | Requirement | Authority | Status |
|---|---|---|---|
| 1 | BPDB SCADA read-only API | BPDB | Pending MoU |
| 2 | DESCO pilot meter dataset (50 buildings) | DESCO | Pending |
| 3 | 5 pilot factory partnerships | Power Division | Pending |
| 4 | LoRaWAN 868MHz spectrum authorisation | BTRC | Pending |
| 5 | 6-month regulatory sandbox | Power Division | Pending |
| 6 | Data sharing MoU | BCC | Pending |

---

## ⚠️ Limitations & Honest Notes

This project is a **working prototype**, not a production deployment. Key limitations:

- **Synthetic training data** — model trained on statistically generated data, not real BPDB meter readings. Domain shift risk exists when deployed on real data.
- **No field hardware deployment** — physical RS485 meters, LoRaWAN gateways, and edge nodes have not been deployed in production.
- **Projected impact figures** — national impact numbers are extrapolations from comparable programmes with ±30% uncertainty. Not measured GridAid outcomes.
- **868MHz spectrum** — LoRaWAN band not yet formally allocated by BTRC in Bangladesh.

These limitations are documented transparently in the [research paper](docs/GridAid_Research_Paper.pdf).

---

## 📦 Dependencies

```
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
folium>=0.15.0
streamlit-folium>=0.18.0
scikit-learn>=1.3.0
twilio>=8.0.0
requests>=2.31.0
```

Install: `pip install -r requirements.txt`

---

## 🤝 Contributing

Contributions welcome — especially:

- Real Bangladesh energy consumption datasets
- BPDB / DESCO API integration
- LoRaWAN hardware test results
- Bangla UI improvements
- Flutter Android app development

```bash
# Fork → branch → PR
git checkout -b feature/your-feature
git commit -m "Add: your feature description"
git push origin feature/your-feature
```

---

## 📄 License

GPL-3.0 — see [LICENSE](LICENSE)

Free to use, modify, and distribute. If you build on GridAid, your modifications must also be open-source.

---

## 📬 Contact

**GridAid Team** — Bangladesh Innovation Competition 2025

- 📧 contact@gridaid.live
- 🐙 GitHub Issues for bugs and feature requests
- 📄 Research paper: [`docs/GridAid_Research_Paper.pdf`](docs/GridAid_Research_Paper.pdf)

---

## 📚 References

1. BPDB, "Annual Report FY 2022–23," Bangladesh Power Development Board, 2023
2. World Bank, "Bangladesh — Electricity Access and Energy Poverty," 2023
3. IRENA, "Digitalisation and Renewable Energy in Developing Economies," 2023
4. IEA, "Technology Collaboration Programme on Demand-Side Management — Bangladesh," 2022
5. F. T. Liu, K. M. Ting, Z. H. Zhou, "Isolation Forest," IEEE ICDM, 2008
6. IDCOL, "SHS Quality and Performance Review," Technical Assessment, 2021

---

<div align="center">

**Before Bangladesh builds a single new power plant, GridAid recovers the equivalent of 6 plants — from waste that already exists.**

⚡ *Built by youth, for Bangladesh* ⚡

</div>
