# Mars workflow audit — 2026-11-15

This audit was performed before rerunning any notebook. The repository contains the Mars notebooks but no saved Mars preparation, region-discovery, process-validation, candidate-validation, or Earth-ranking outputs. The committed processed tables are Moon artifacts and a Moon report. Mars notebooks 01, 03, 06, 07, 08, and 09 have zero saved cell outputs.

No Mars candidate map, process distribution, Earth ranking, or top-three scientific interpretation is published by this commit. Producing those files without Mars inputs would fabricate evidence. The new runner fails closed when an input table is absent.

| Notebook | Audit result | Next run condition |
|---|---|---|
| 01 Mars preparation | Code exists; outputs absent | Run on Kaggle with PDS downloads and preserve manifest/checksums |
| 03 Mars region discovery | Code exists; outputs absent | Requires `mars_cells_input.parquet` and preparation schema |
| 06 Mars process validation | Code exists; outputs absent | Requires Mars regions and feature distributions |
| 07 Mars candidate validation | Code exists; outputs absent | Requires process review queue; validates dust-compatible environments only |
| 08 Earth dust matching | Code exists; outputs absent | Requires notebook-07 distributions and NASA POWER access |
| 09 Earth refined validation | Code exists; outputs absent | Requires notebook-08 matches; adds local land-mask and MODIS inventory |

The package defines six Mars process specifications. Only fine-particulate dust transport is currently eligible for Earth screening because the existing workflow documents a notebook-07 dust-compatible evidence gate. The other five remain explicitly inconclusive until independent Mars evidence is present.

Run notebooks 01 → 03 → 06 → 07 → 08 → 09 in Kaggle. Configure credentials through Kaggle Secrets; never print or commit `kaggle.json`, Earthdata credentials, or tokens. Then run `scripts/mars_earth_analog_pipeline.py` for each eligible process. It preserves marginal, joint, spatial, missingness, and weight-sensitivity outputs.
