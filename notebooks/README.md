# Notebooks

The previous feasibility notebook was removed. It added a separate decision stage where normal data-loading checks were enough and could incorrectly interpret PDS Search indexing gaps as unavailable scientific data.

The implementation order is now:

| Order | Notebook | Purpose |
|---|---|---|
| 1 | `01_mars_data_preparation.ipynb` | Preserve Mars measurements; build 1°/10° scales; create detection-aware TES mineral evidence; contrast-normalize spectral shape; retain leading variance-preserving PCA components; export coverage cohorts, cells, masks, feature schema, transforms, and provenance |
| 2 | `02_moon_data_preparation.ipynb` | Preserve and clean Moon measurements; build global/polar and separate-scale views; normalize variables; calculate neutral features; fit PCA/embeddings; export cells, masks, transforms, and provenance |
| 3 | `03_mars_region_discovery.ipynb` | Build area-aware connected 1°/10° Mars regions, quarantine intrinsically fragmented coverage, exclude tiny fragments from model fitting and assign them transparently afterward, discover broad types from robust measurements, conditionally refine them with composition/spectral subtypes, distinguish tested candidates from applied models, reject artifact-dominated splits, compute real cluster confidence, detect reviewable anomalies, export neutral marginal/joint/spatial signatures, and audit paper-defined process evidence without assigning process labels |
| 4 | `04_moon_region_discovery.ipynb` | Merge neighboring Moon cells into multiscale connected regions; build region representations; test artifacts; cluster common types; detect anomalies; export neutral signatures; audit paper-defined evidence before any process labels |
| 5 | `05_earth_analog_matching.ipynb` | Match validated planetary process distributions to Earth measurements (only after process validation is complete) |
| 6 | `06_mars_process_validation.ipynb` | Connect Mars neutral regions to literature-defined evidence requirements; rank candidate regions for targeted follow-up; export process distributions and controls without assigning unsupported labels |
| 7 | `07_mars_candidate_validation.ipynb` | Test Mars candidates with separate thermophysical variables and targeted CRISM/SHARAD searches; preserve inconclusive cases; export a validated dust-compatible environment distribution while keeping process-based Earth matching closed |
| 8 | `08_earth_dust_environment_matching.ipynb` | Query actual Earth climatology through NASA POWER, compare it with the Mars dust-compatible distribution using rank, joint, and spatial scores, and inventory MODIS follow-up coverage through CMR |
| 9 | `09_earth_refined_validation.ipynb` | Refine the top Earth candidates on a 1° local grid, apply a real land mask, re-query NASA POWER, and inventory higher-resolution MODIS follow-up coverage through CMR |
| 11 | `11_mars_process_readiness_audit.ipynb` | Gate each proposed Mars process on actual measurements and validation evidence; unsupported processes remain inconclusive and are not Earth-matched |

Preparation notebooks stop at cell-level data. Region size, shape, internal variation, neighbors, clustering, anomaly detection, and neutral signatures belong to notebooks 3 and 4. Final process interpretation requires the later targeted validation stage described in the design document.

The post-notebook Earth package is implemented in `scripts/mars_earth_analog_pipeline.py` and configured by `configs/mars_process_specifications.json`. It requires real Mars process distributions and Earth proxy tables; it does not create fallback data. The pre-run audit is recorded in `reports/mars_workflow_audit.md`.

After the validated Kaggle run, `10_mars_final_package.ipynb` assembles the refined candidate table, top-location CSV, ranked-candidate map, run summary, and plain-language limitations report.

Only completed, runnable notebooks should be added. The table defines the implementation sequence; it is not a claim that these files already exist.
