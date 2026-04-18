"""
GridHaat — Bangladesh Energy Dataset Generator
Generates 90 days of hourly consumption data for 3 sectors
with realistic wastage patterns embedded.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json, os

np.random.seed(42)

SECTORS = {
    "Dhaka Industrial (Narayanganj RMG Zone)": {
        "base_mw": 420, "peak_mult": 1.6, "peak_hours": (8, 20),
        "wastage_type": "industrial_motor", "wastage_prob": 0.18,
        "division": "Dhaka", "lat": 23.62, "lon": 90.50,
    },
    "Gulshan Commercial District": {
        "base_mw": 180, "peak_mult": 1.8, "peak_hours": (10, 22),
        "wastage_type": "ac_overnight", "wastage_prob": 0.22,
        "division": "Dhaka", "lat": 23.79, "lon": 90.41,
    },
    "Chittagong Port Industrial": {
        "base_mw": 310, "peak_mult": 1.5, "peak_hours": (7, 19),
        "wastage_type": "industrial_motor", "wastage_prob": 0.15,
        "division": "Chittagong", "lat": 22.33, "lon": 91.83,
    },
    "Sylhet Urban Residential": {
        "base_mw": 95,  "peak_mult": 1.9, "peak_hours": (18, 23),
        "wastage_type": "residential_phantom", "wastage_prob": 0.25,
        "division": "Sylhet", "lat": 24.89, "lon": 91.87,
    },
    "Rajshahi Commercial": {
        "base_mw": 110, "peak_mult": 1.7, "peak_hours": (9, 21),
        "wastage_type": "ac_overnight", "wastage_prob": 0.20,
        "division": "Rajshahi", "lat": 24.37, "lon": 88.60,
    },
    "Khulna Industrial": {
        "base_mw": 140, "peak_mult": 1.4, "peak_hours": (8, 18),
        "wastage_type": "industrial_motor", "wastage_prob": 0.16,
        "division": "Khulna", "lat": 22.81, "lon": 89.55,
    },
    "Barishal Urban": {
        "base_mw": 60,  "peak_mult": 1.6, "peak_hours": (17, 22),
        "wastage_type": "residential_phantom", "wastage_prob": 0.28,
        "division": "Barishal", "lat": 22.70, "lon": 90.36,
    },
    "Rangpur Rural-Urban": {
        "base_mw": 75,  "peak_mult": 1.5, "peak_hours": (18, 22),
        "wastage_type": "pump_motor", "wastage_prob": 0.30,
        "division": "Rangpur", "lat": 25.74, "lon": 89.25,
    },
    "Mymensingh Mixed": {
        "base_mw": 85,  "peak_mult": 1.6, "peak_hours": (8, 20),
        "wastage_type": "pump_motor", "wastage_prob": 0.24,
        "division": "Mymensingh", "lat": 24.75, "lon": 90.40,
    },
}

WASTAGE_PROFILES = {
    "industrial_motor": {
        "label": "Industrial motor over-run",
        "desc": "Factory motors/compressors running beyond production hours",
        "mw_range": (15, 85),
        "hours": list(range(20, 24)) + list(range(0, 6)),
    },
    "ac_overnight": {
        "label": "AC/HVAC left running overnight",
        "desc": "Commercial building HVAC systems not shut down after hours",
        "mw_range": (8, 45),
        "hours": list(range(22, 24)) + list(range(0, 7)),
    },
    "residential_phantom": {
        "label": "Residential phantom load",
        "desc": "Always-on appliances, standby devices, unmonitored chargers",
        "mw_range": (3, 18),
        "hours": list(range(0, 24)),
    },
    "pump_motor": {
        "label": "Irrigation pump over-run",
        "desc": "Agricultural/municipal pumps running beyond schedule",
        "mw_range": (5, 30),
        "hours": list(range(0, 8)) + list(range(20, 24)),
    },
}

BDT_PER_KWH   = 8.5
CO2_KG_PER_KWH = 0.58
FUEL_LITERS_PER_KWH = 0.28

def generate_sector_data(sector_name, cfg, days=90):
    rows = []
    start = datetime(2024, 10, 1)
    for day in range(days):
        for hour in range(24):
            ts = start + timedelta(days=day, hours=hour)
            ph, ph2 = cfg["peak_hours"]
            in_peak = ph <= hour < ph2
            base = cfg["base_mw"]
            trend = 1 + 0.002 * day
            seasonal = 1 + 0.08 * np.sin(2 * np.pi * day / 365)
            daily_shape = cfg["peak_mult"] if in_peak else 0.6
            noise = np.random.normal(0, base * 0.04)
            consumption = base * trend * seasonal * daily_shape + noise
            consumption = max(consumption, base * 0.3)

            # Embed wastage events
            wastage_mw = 0.0
            is_wastage = False
            wastage_label = ""
            profile = WASTAGE_PROFILES[cfg["wastage_type"]]
            if (hour in profile["hours"] and
                    np.random.random() < cfg["wastage_prob"] / len(profile["hours"]) * 3):
                w_min, w_max = profile["mw_range"]
                wastage_mw = np.random.uniform(w_min, w_max)
                is_wastage = True
                wastage_label = profile["label"]
                consumption += wastage_mw

            # Transmission loss (13-17%)
            tx_loss_pct = np.random.uniform(0.13, 0.17)
            tx_loss_mw = consumption * tx_loss_pct
            bdt_wasted = (wastage_mw + tx_loss_mw) * 1000 * BDT_PER_KWH
            co2_wasted = (wastage_mw + tx_loss_mw) * 1000 * CO2_KG_PER_KWH
            fuel_wasted = (wastage_mw + tx_loss_mw) * 1000 * FUEL_LITERS_PER_KWH

            rows.append({
                "timestamp": ts,
                "sector": sector_name,
                "division": cfg["division"],
                "lat": cfg["lat"],
                "lon": cfg["lon"],
                "consumption_mw": round(consumption, 2),
                "wastage_mw": round(wastage_mw, 2),
                "tx_loss_mw": round(tx_loss_mw, 2),
                "total_loss_mw": round(wastage_mw + tx_loss_mw, 2),
                "is_wastage_event": is_wastage,
                "wastage_label": wastage_label,
                "wastage_type": cfg["wastage_type"] if is_wastage else "",
                "bdt_wasted": round(bdt_wasted, 0),
                "co2_kg_wasted": round(co2_wasted, 1),
                "fuel_liters_wasted": round(fuel_wasted, 1),
                "hour": hour,
                "day_of_week": ts.weekday(),
                "is_weekend": ts.weekday() >= 5,
            })
    return rows

def main():
    os.makedirs("data", exist_ok=True)
    all_rows = []
    print("Generating synthetic BD energy data...")
    for name, cfg in SECTORS.items():
        rows = generate_sector_data(name, cfg, days=90)
        all_rows.extend(rows)
        total_waste = sum(r["total_loss_mw"] for r in rows)
        total_bdt = sum(r["bdt_wasted"] for r in rows)
        n_events = sum(1 for r in rows if r["is_wastage_event"])
        print(f"  {name[:40]}: {n_events} events, {total_waste:.0f} MW-hrs lost, ৳{total_bdt/1e6:.1f}M wasted")

    df = pd.DataFrame(all_rows)
    df.to_csv("data/bd_energy_data.csv", index=False)

    # Summary stats for dashboard
    summary = {
        "total_sectors": len(SECTORS),
        "total_wastage_events": int(df["is_wastage_event"].sum()),
        "total_wastage_mw_hrs": float(df["wastage_mw"].sum()),
        "total_tx_loss_mw_hrs": float(df["tx_loss_mw"].sum()),
        "total_bdt_wasted": float(df["bdt_wasted"].sum()),
        "total_co2_kg": float(df["co2_kg_wasted"].sum()),
        "total_fuel_liters": float(df["fuel_liters_wasted"].sum()),
        "avg_daily_wastage_mw": float(df.groupby(df["timestamp"].dt.date)["wastage_mw"].sum().mean()),
        "sectors": list(SECTORS.keys()),
        "divisions": list(set(c["division"] for c in SECTORS.values())),
    }
    with open("data/summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nDone. {len(all_rows):,} rows generated.")
    print(f"Total wastage events: {summary['total_wastage_events']:,}")
    print(f"Total BDT wasted: ৳{summary['total_bdt_wasted']/1e9:.2f}B over 90 days")
    print(f"Total CO2 wasted: {summary['total_co2_kg']/1000:.0f} tonnes")

if __name__ == "__main__":
    main()
