# NASA Space Apps Challenge 2026
## *Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![NASA Space Apps](https://img.shields.io/badge/NASA-Space%20Apps%20Challenge-orange.svg)](https://www.spaceappschallenge.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Autonomous AI-Driven Multi-Criteria Decision Framework for Planetary-to-Terrestrial Analog Site Recommendation**

---

### 📖 Master Documentation
For the complete, in-depth technical specification, data inventory, mathematical formulations (PSI + TOPSIS), scientific discoveries (including Morocco space analogs), and hackathon criteria, please consult:
👉 **[PROJECT_MASTER_BRIEF.md](PROJECT_MASTER_BRIEF.md)**

---

### 🚀 Pipeline Overview

Our repository delivers an end-to-end, scientifically verified data science and machine learning pipeline across 5 fully executed notebooks:

| Order | Notebook | Purpose & Outputs | Status |
| :---: | :--- | :--- | :---: |
| **01** | [`01_mars_data_preparation.ipynb`](notebooks/01_mars_data_preparation.ipynb) | Ingests global Mars orbital data (MOLA topography, TES thermal inertia/albedo, 13 mineral endmembers, Odyssey GRS neutrons). Generates multiscale grids (1° medium, 10° coarse), variance-preserving PCA, and `processed/mars_cells_input.parquet`. | ✅ Verified (0 Err) |
| **02** | [`02_moon_data_preparation.ipynb`](notebooks/02_moon_data_preparation.ipynb) | Calibrates LRO datasets (LOLA altimetry, Diviner $T_{\text{max}} < 110\text{ K}$ cold traps, LEND neutrons, Mini-RF CPR). Generates South Polar Stereographic grids (80°S–90°S) and `processed/moon_cells_input.parquet`. | ✅ Verified (0 Err) |
| **03** | [`03_mars_region_discovery.ipynb`](notebooks/03_mars_region_discovery.ipynb) | DisjointSet connected component segmentation, spatial holdout clustering (K-Means, GMM, HDBSCAN), Isolation Forest anomaly detection, process recipes, and `processed/mars_regions.parquet`. | ✅ Verified (0 Err) |
| **04** | [`04_moon_region_discovery.ipynb`](notebooks/04_moon_region_discovery.ipynb) | Fast connected component clustering with 360° longitude wrapping, benchmarking positive control sites (Shackleton, Malapert, Haworth, Marius Hills), and `processed/moon_regions.parquet`. | ✅ Verified (0 Err) |
| **05** | [`05_earth_analog_matching.ipynb`](notebooks/05_earth_analog_matching.ipynb) | **Core Recommender Engine**: Two-Stage Planetary Similarity Index (PSI) & TOPSIS Multi-Criteria Decision Analysis matching 7 NASA exploration targets to 315 global terrestrial candidates. Validates NASA benchmarks and discovers novel North African analogs. | ✅ Verified (0 Err) |

---

### 🗺️ Visual Artifacts & Interactive Satellite Maps

- **Interactive Leaflet Satellite Map**: Open [`reports/interactive_earth_analogs_map.html`](reports/interactive_earth_analogs_map.html) in your browser for an interactive Esri satellite map with fidelity metrics and direct Google Maps buttons.
- **Global Portfolio Map**: [`reports/earth_analog_global_map.png`](reports/earth_analog_global_map.png)
- **Multi-Axis Radar Profiles**: [`reports/earth_analog_radar_profiles.png`](reports/earth_analog_radar_profiles.png)
- **Cross-Mission Compatibility Heatmap**: [`reports/earth_analog_cross_compatibility_matrix.png`](reports/earth_analog_cross_compatibility_matrix.png)

---

### 🛠️ Quickstart

```powershell
# Clone the repository
git clone git@github.com:mehddii/nasa-hackathon-xyzGang.git
cd nasa-hackathon-xyzGang

# Install dependencies
pip install numpy scipy pandas scikit-learn matplotlib seaborn pyarrow pds4_tools rasterio streamlit

# Explore the interactive analog map in your browser
start reports/interactive_earth_analogs_map.html
```

---
*Developed for the NASA International Space Apps Challenge 2026 by Team xyzGang.*
