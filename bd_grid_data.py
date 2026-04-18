"""
GridHaat — Bangladesh National Grid Database
Realistic grid zones, substation names, incharge assignments.
Based on BPDB zone structure and published substation data.
"""

GRID_ZONES = {
    "Narayanganj Industrial Zone": {
        "lat": 23.615, "lon": 90.498,
        "division": "Dhaka", "district": "Narayanganj",
        "grid_line": "NR-07", "substation": "Narayanganj 33/11kV SS",
        "zone_code": "BPDB-DK-03",
        "incharge_name": "Md. Rafiqul Islam",
        "incharge_title": "Assistant Engineer, BPDB Zone 3",
        "wastage_type": "industrial_motor",
        "base_mw": 420, "icon_color": "#EF4444",
    },
    "Gulshan Commercial District": {
        "lat": 23.793, "lon": 90.414,
        "division": "Dhaka", "district": "Dhaka North",
        "grid_line": "GL-12", "substation": "Gulshan 33/11kV SS",
        "zone_code": "DESCO-DK-12",
        "incharge_name": "Engr. Shahnaz Begum",
        "incharge_title": "Senior Engineer, DESCO Zone 12",
        "wastage_type": "ac_overnight",
        "base_mw": 180, "icon_color": "#F59E0B",
    },
    "Chittagong Port Industrial": {
        "lat": 22.331, "lon": 91.832,
        "division": "Chittagong", "district": "Chittagong",
        "grid_line": "CT-04", "substation": "Patenga 132/33kV SS",
        "zone_code": "BPDB-CT-04",
        "incharge_name": "Md. Kamal Hossain",
        "incharge_title": "Executive Engineer, BPDB Ctg South",
        "wastage_type": "industrial_motor",
        "base_mw": 310, "icon_color": "#EF4444",
    },
    "Sylhet Urban Grid": {
        "lat": 24.892, "lon": 91.872,
        "division": "Sylhet", "district": "Sylhet Sadar",
        "grid_line": "SY-03", "substation": "Sylhet 33/11kV SS",
        "zone_code": "BPDB-SY-03",
        "incharge_name": "Md. Nurul Amin",
        "incharge_title": "Assistant Engineer, BPDB Sylhet",
        "wastage_type": "residential_phantom",
        "base_mw": 95, "icon_color": "#3B8BD4",
    },
    "Rajshahi Commercial Zone": {
        "lat": 24.374, "lon": 88.601,
        "division": "Rajshahi", "district": "Rajshahi Sadar",
        "grid_line": "RJ-02", "substation": "Rajshahi 33/11kV SS",
        "zone_code": "BPDB-RJ-02",
        "incharge_name": "Engr. Farhana Akter",
        "incharge_title": "Sub-Divisional Engineer, BPDB Rajshahi",
        "wastage_type": "ac_overnight",
        "base_mw": 110, "icon_color": "#F59E0B",
    },
    "Khulna Industrial Zone": {
        "lat": 22.812, "lon": 89.553,
        "division": "Khulna", "district": "Khulna Sadar",
        "grid_line": "KL-05", "substation": "Khulna 132/33kV SS",
        "zone_code": "BPDB-KL-05",
        "incharge_name": "Md. Jahirul Islam",
        "incharge_title": "Executive Engineer, BPDB Khulna",
        "wastage_type": "industrial_motor",
        "base_mw": 140, "icon_color": "#EF4444",
    },
    "Rangpur Rural-Urban Grid": {
        "lat": 25.743, "lon": 89.251,
        "division": "Rangpur", "district": "Rangpur Sadar",
        "grid_line": "RP-01", "substation": "Rangpur 33/11kV SS",
        "zone_code": "BPDB-RP-01",
        "incharge_name": "Md. Habibur Rahman",
        "incharge_title": "Assistant Engineer, BPDB Rangpur",
        "wastage_type": "pump_motor",
        "base_mw": 75, "icon_color": "#22C55E",
    },
    "Barishal Urban Zone": {
        "lat": 22.701, "lon": 90.360,
        "division": "Barishal", "district": "Barishal Sadar",
        "grid_line": "BS-02", "substation": "Barishal 33/11kV SS",
        "zone_code": "BPDB-BS-02",
        "incharge_name": "Engr. Rokeya Khanam",
        "incharge_title": "Sub-Divisional Engineer, BPDB Barishal",
        "wastage_type": "residential_phantom",
        "base_mw": 60, "icon_color": "#3B8BD4",
    },
    "Mymensingh Mixed Zone": {
        "lat": 24.751, "lon": 90.407,
        "division": "Mymensingh", "district": "Mymensingh Sadar",
        "grid_line": "MY-03", "substation": "Mymensingh 33/11kV SS",
        "zone_code": "BPDB-MY-03",
        "incharge_name": "Md. Alamgir Kabir",
        "incharge_title": "Assistant Engineer, BPDB Mymensingh",
        "wastage_type": "pump_motor",
        "base_mw": 85, "icon_color": "#22C55E",
    },
}

# National waste constants (based on BPDB Annual Report 2022-23)
NATIONAL_WASTE_MW_PER_DAY   = 6400       # estimated combined system loss
NATIONAL_WASTE_MW_PER_SEC   = NATIONAL_WASTE_MW_PER_DAY / 86400  # 0.074 MW/s
BDT_PER_KWH                 = 8.5
CO2_KG_PER_KWH              = 0.58
FUEL_LITERS_PER_KWH         = 0.28

# Wastage type display labels
WASTAGE_LABELS = {
    "industrial_motor":   "Industrial motor over-run",
    "ac_overnight":       "AC/HVAC left running overnight",
    "pump_motor":         "Irrigation pump over-run",
    "residential_phantom":"Residential phantom load",
}
