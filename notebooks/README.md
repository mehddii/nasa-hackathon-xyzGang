# NASA Space Apps Challenge Notebooks

This directory contains the end-to-end scientific and machine-learning pipeline for the NASA Space Apps Challenge: **Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars**.

### Complete End-to-End Implementation Pipeline

| Order | Notebook | Purpose & Key Outputs |
| :---: | :--- | :--- |
| **01** | `01_mars_data_preparation.ipynb` | Processes global Mars measurements (MOLA altimetry, TES thermal inertia, TES albedo, TES mineral spectral unmixing, Odyssey GRS neutrons). Generates calibrated multiscale cells (1° medium, 10° coarse), robust scaling, variance-preserving spectral PCA, and exports `processed/mars_cells_input.parquet`. |
| **02** | `02_moon_data_preparation.ipynb` | Processes high-resolution Moon geophysics (LOLA topography, Diviner cryogenic thermal bands $T_{\text{max}} < 110\text{ K}$, LEND epithermal neutron flux, LROC WAC albedo, Mini-RF CPR, Artemis landing suitability). Generates circular South Polar Stereographic projections (80°S–90°S) and exports `processed/moon_cells_input.parquet`. |
| **03** | `03_mars_region_discovery.ipynb` | DisjointSet connected component segmentation, spatial holdout clustering (K-Means, GMM, HDBSCAN), Isolation Forest anomaly detection, conservative Mars process evidence recipes, control site benchmarking (Jezero, Meridiani, Gale, Syrtis Major, Utopia Planitia), and exports `processed/mars_regions.parquet` and `reports/mars_earth_filter_specifications.json`. |
| **04** | `04_moon_region_discovery.ipynb` | Fast connected component clustering with 360° longitude wrapping, spatial block validation (Fold 4), Isolation Forest anomaly detection, positive control validation (Shackleton, Malapert, Haworth, Faustini, Marius Hills), and exports `processed/moon_regions.parquet` and `reports/moon_earth_filter_specifications.json`. |
| **05** | `05_earth_analog_matching.ipynb` | **Core Recommender Deliverable**: Two-Stage Planetary Similarity Index (PSI) & TOPSIS Multi-Criteria Decision Analysis engine matching Moon Artemis and Mars targets to terrestrial analogs. Benchmarks NASA/ESA analog facilities (HI-SEAS Hawaii, Devon Island HMP, Lanzarote Pangea, McMurdo Dry Valleys, Atacama Yungay) and discovers novel high-fidelity analogs in Morocco (Anti-Atlas, Zagora, Merzouga). Exports `processed/earth_analog_rankings.parquet`, `processed/earth_analogs.geojson`, and mission dossiers. |

All notebooks are executed in-place with saved outputs and visualizations (`jupyter nbconvert --to notebook --execute --inplace`).
