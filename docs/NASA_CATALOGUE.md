# NASA Earth Science Data Catalogue for ML

**Created:** 2026-11-15  |  **Collections:** 56  |  **CMR Base:** `https://cmr.earthdata.nasa.gov/search`

*Curated NASA Earth science catalogue for ML notebooks*

## Table of Contents

1. [Authentication Guide](#authentication-guide)
2. [How to Fetch Data](#how-to-fetch-data)
3. [Spatial Helpers](#spatial-helpers)
4. [Temporal Alignment](#temporal-alignment)
5. [ML Data Prep Patterns](#ml-data-prep-patterns)
6. [Collection Catalogue](#collection-catalogue)
   - [CAT 01: Land Cover / Vegetation / NDVI / Crops](#cat-01-land-cover--vegetation--ndvi--crops)
   - [CAT 02: Active Fires / Burned Area](#cat-02-active-fires--burned-area)
   - [CAT 03: Precipitation / Floods / Drought](#cat-03-precipitation--floods--drought)
   - [CAT 04: Temperature / Climate Reanalysis](#cat-04-temperature--climate-reanalysis)
   - [CAT 05: Air Quality / Atmosphere](#cat-05-air-quality--atmosphere)
   - [CAT 06: Oceans / SST / Ocean Color](#cat-06-oceans--sst--ocean-color)
   - [CAT 07: Cryosphere](#cat-07-cryosphere)
   - [CAT 08: Elevation / Terrain / 3D Structure](#cat-08-elevation--terrain--3d-structure)
   - [CAT 09: Human Dimensions / Night Lights](#cat-09-human-dimensions--night-lights)
   - [CAT 10: Solid Earth / Hazards / SAR](#cat-10-solid-earth--hazards--sar)
7. [ML Task Decision Guide](#ml-task-decision-guide)

## Authentication Guide

**Earthdata Login:** <https://urs.earthdata.nasa.gov/>  (Free account required for all NASA EarthData downloads)

**Login Methods:**

- Environment vars: EARTHDATA_LOGIN_USERNAME, EARTHDATA_LOGIN_PASSWORD
- .netrc file: machine urs.earthdata.nasa.gov login <user> password <pass>
- earthaccess.login(strategy='interactive') — prompts once, caches token

**S3 Direct Access:** S3 direct access requires s3credentials endpoint call (auto-handled by earthaccess.open())

**Token:** earthaccess.login() returns an Auth object; bearer tokens auto-refreshed

## How to Fetch Data

```python
import earthaccess, xarray as xr

# 1. Login
earthaccess.login(strategy="environment")

# 2. Search (CMR under the hood)
results = earthaccess.search_data(
    short_name="GPM_3IMERGDF",
    temporal=("2023-06-01", "2023-06-30"),
    bounding_box=(-120, 25, -65, 50),  # CONUS: west, south, east, north
    count=10
)
print(f"Found {len(results)} granules")

# 3a. Stream (best for cloud, no local storage)
files = earthaccess.open(results)
ds = xr.open_mfdataset(files, group="Grid", engine="h5netcdf")

# 3b. Download subset
earthaccess.download(results[:2], "./tmp/")

# 4. Raw CMR query (no login needed for metadata)
import urllib.request, json
url = "https://cmr.earthdata.nasa.gov/search/collections.json?short_name=GPM_3IMERGDF&page_size=1"
with urllib.request.urlopen(url) as r:
    data = json.loads(r.read())
    print(data["feed"]["entry"][0]["id"])
```

## Spatial Helpers

**BBox format:** `(west, south, east, north) — WGS84 degrees`

**Regions:**

| Region | west | south | east | north |
|--------|------|-------|------|-------|
| CONUS | -125 | 24 | -66 | 50 |
| EUROPE | -12 | 34 | 45 | 72 |
| AMAZON | -80 | -20 | -44 | 10 |
| SAHEL | -20 | 10 | 45 | 20 |
| SE_ASIA | 90 | -10 | 145 | 30 |

**MODIS tile lookup:** https://modis-land.gsfc.nasa.gov/MODLAND_grid.html

**OPeNDAP subsetting:** Append .nc4?variable[time][lat][lon] to OPeNDAP URL for server-side subsetting

## Temporal Alignment

*All NASA products use UTC. MODIS uses maximum NDVI composite within window — clouds are suppressed but phenology may be biased*

**Product cadences:**

- **30-min:** GPM_3IMERGHH
- **daily:** MUR-JPL-L4-GLOB-v4.1, VNP46A1, MOD14A2 (8-day fire), GPM_3IMERGDF
- **8-day:** MOD09A1, MOD11A2 (LST)
- **16-day:** MOD13Q1, MOD13A2
- **monthly:** MOD13A3, MCD64A1, MODISA_L3m_CHL, VNP46A3, TELLUS_GRAC-GRFO_MASCON
- **annual:** MCD12Q1, VNP46A4

```python
# Resample example
ds.resample(time='1D').mean()  # or pd.merge_asof() for irregular timestamps
```

## ML Data Prep Patterns

### Cloud Masking

- **MODIS:** Use StateQA or QA_60 bit flags; bits 0-1 for cloud state
- **HLS_Sentinel2:** QA band bits 1-3 for cloud/shadow/snow
- **GPM:** precipitationQualityIndex > 0.9 recommended
- **VIIRS:** QF_Cloud bit in quality flags

### Normalization / Scale Factors

- **NDVI:** Already -1 to 1; no scaling needed
- **LST_MODIS:** scale_factor=0.02, subtract 273.15 for Celsius
- **reflectance_MODIS:** multiply by 0.0001
- **reflectance_HLS:** multiply by 0.0001

### Leakage Prevention

- **Spatial:** Use geographically separated folds (k-fold on grid tiles, not random pixels)
- **Temporal:** Always train on past, validate/test on future dates

```python
# Pattern: build labeled dataset from 2+ collections
# Example: Wildfire risk = NDVI + Precip + Fire labels
bbox = (-125, 32, -114, 42)  # California
dates = ("2020-06-01", "2020-09-30")
# 1. Fetch each product, resample to common 500m/8-day grid
# 2. Stack as xarray.Dataset with aligned coordinates
# 3. Apply QA masks before training
```

## Collection Catalogue

### Land Cover / Vegetation / NDVI / Crops

**Topic:** Land Surface  |  **Category ID:** `cat_01_land_vegetation`

| Short Name | Concept ID | Version | Prov | Cloud | Granules | Level | Time Range |
|------------|-----------|---------|------|-------|----------|-------|-----------|
| `MOD13A3` | `C2327962326-LPCLOUD` | 061 | LPCLOUD | ☁️ | 93,611 | 3 | 2000-02→ongoing |
| `MOD13A2` | `C2565788905-LPCLOUD` | 061 | LPCLOUD | ☁️ | 178,652 | 3 | 2000-02→ongoing |
| `MOD13Q1` | `C1748066515-LPCLOUD` | 061 | LPCLOUD | ☁️ | 178,658 | 3 | 2000-02→ongoing |
| `VNP13A1` | `C2519127224-LPCLOUD` | 002 | LPCLOUD | ☁️ | 193,117 | 3 | 2012-01→ongoing |
| `HLSL30` | `C2021957657-LPCLOUD` | 2.0 | LPCLOUD | ☁️ | 16,241,212 | 3 | 2013-04→ongoing |
| `HLSS30` | `C2021957295-LPCLOUD` | 2.0 | LPCLOUD | ☁️ | 22,280,081 | 3 | 2015-11→ongoing |
| `MCD12Q1` | `C2484079608-LPCLOUD` | 061 | LPCLOUD | ☁️ | 7,875 | 3 | 2001-01→ongoing |
| `MYD13A2` | `C2565794049-LPCLOUD` | 061 | LPCLOUD | ☁️ | 162,933 | 3 | 2002-07→ongoing |

#### `MOD13A3` — MODIS/Terra Vegetation Indices Monthly L3 Global 1km SIN Grid V061

**concept_id:** `C2327962326-LPCLOUD`  |  **DOI:** 10.5067/MODIS/MOD13A3.061

**ML Use:** Monthly NDVI/EVI for crop-type mapping, vegetation health monitoring, drought indices

*The Terra Moderate Resolution Imaging Spectroradiometer (MODIS) Vegetation Indices Monthly (MOD13A3) Version 6.1 data are provided monthly at 1 kilometer (km) spatial resolution as a gridded Level 3 p*

**Access:** HTTPS  |  **Format:** HDF-EOS2  |  **Size:** 8.6 MB  |  **Login required:** ✅

**Key Variables:** `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`, `PROCESSVERSION`, `TileID`, `NDVI1KMMONTHQCLASSPERCENTAGE`, `EVI1KMMONTHQCLASSPERCENTAGE`

**⚠️ Gotchas:**
- Monthly composites only — no sub-monthly temporal info
- MODIS tile system (sinusoidal); reproject before analysis

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MOD13A3",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MOD13A2` — MODIS/Terra Vegetation Indices 16-Day L3 Global 1km SIN Grid V061

**concept_id:** `C2565788905-LPCLOUD`  |  **DOI:** 10.5067/MODIS/MOD13A2.061

**ML Use:** 16-day NDVI time series for phenology, land cover change detection

*The MOD13A2 Version 6.1 product provides Vegetation Index (VI) values at a per pixel basis at 1 kilometer (km) spatial resolution. There are two primary vegetation layers. The first is the Normalized *

**Access:** HTTPS  |  **Format:** HDF-EOS2  |  **Size:** 8.7 MB  |  **Login required:** ✅

**Key Variables:** `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`, `PROCESSVERSION`, `TileID`, `INPUTPRODUCTRESOLUTION`, `NDVI1KM16DAYQCLASSPERCENTAGE`

**⚠️ Gotchas:**
- 16-day composite; actual acquisition date varies within window
- Max-NDVI compositing suppresses clouds but can bias phenology

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MOD13A2",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MOD13Q1` — MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061

**concept_id:** `C1748066515-LPCLOUD`  |  **DOI:** 10.5067/MODIS/MOD13Q1.061

**ML Use:** 16-day 250m NDVI for high-resolution crop mapping and vegetation analysis

*The Terra Moderate Resolution Imaging Spectroradiometer (MODIS) Vegetation Indices (MOD13Q1) Version 6.1 data are generated every 16 days at 250 meter (m) spatial resolution as a Level 3 product. The *

**Access:** HTTPS  |  **Format:** HDF-EOS2  |  **Size:** 92.6 MB  |  **Login required:** ✅

**Key Variables:** `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`, `PROCESSVERSION`, `TileID`, `INPUTPRODUCTRESOLUTION`, `NDVI250M16DAYQCLASSPERCENTAGE`

**⚠️ Gotchas:**
- 250m resolution; EVI may saturate in dense tropical forest

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MOD13Q1",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `VNP13A1` — VIIRS/NPP Vegetation Indices 16-Day L3 Global 500m SIN Grid V002

**concept_id:** `C2519127224-LPCLOUD`  |  **DOI:** 10.5067/VIIRS/VNP13A1.002

**ML Use:** VIIRS NDVI/EVI complement to MODIS for continuity in vegetation monitoring

*The delivery of all Suomi National Polar-orbiting Partnership (Suomi NPP) VIIRS science data products [ceased on November 2, 2026 (2026/306)](https://www.earthdata.nasa.gov/data/alerts-outages/reminde*

**Access:** HTTPS  |  **Format:** HDF-EOS5  |  **Size:** 42.8 MB  |  **Login required:** ✅

**Key Variables:** `identifier_product_doi`, `identifier_product_doi_authority`, `TileID`, `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`

**⚠️ Gotchas:**
- VIIRS 500m — slightly different spectral bands than MODIS; not fully interchangeable

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="VNP13A1",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `HLSL30` — HLS Landsat Operational Land Imager Surface Reflectance and TOA Brightness Daily

**concept_id:** `C2021957657-LPCLOUD`  |  **DOI:** 10.5067/HLS/HLSL30.002

**ML Use:** 30m Landsat-based surface reflectance for crop mapping, change detection, ML training labels

*The Harmonized Landsat Sentinel-2 (HLS) project provides consistent surface reflectance (SR) and top of atmosphere (TOA) brightness data from a virtual constellation of satellite sensors. The Operatio*

**Access:** HTTPS  |  **Format:** COG  |  **Size:** 20 MB  |  **Login required:** ✅

**Key Variables:** `LANDSAT_PRODUCT_ID`, `CLOUD_COVERAGE`, `SPATIAL_COVERAGE`, `SPATIAL_RESOLUTION`, `HORIZONTAL_CS_NAME`, `ULX`

**⚠️ Gotchas:**
- Landsat revisit ~16 days; cloud gaps common; check Fmask QA band bits 1-4
- 30m res requires significant storage; use spatial subsets

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="HLSL30",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `HLSS30` — HLS Sentinel-2 Multi-spectral Instrument Surface Reflectance Daily Global 30m v2

**concept_id:** `C2021957295-LPCLOUD`  |  **DOI:** 10.5067/HLS/HLSS30.002

**ML Use:** 30m Sentinel-2-based surface reflectance for crop mapping at high spatial resolution

*The Harmonized Landsat Sentinel-2 (HLS) project provides consistent surface reflectance data from the Operational Land Imager (OLI) aboard the joint NASA/USGS Landsat 8 satellite and the Multi-Spectra*

**Access:** HTTPS  |  **Format:** COG  |  **Size:** 20 MB  |  **Login required:** ✅

**Key Variables:** `CLOUD_COVERAGE`, `MGRS_TILE_ID`, `SPATIAL_COVERAGE`, `SPATIAL_RESOLUTION`, `HORIZONTAL_CS_CODE`, `HORIZONTAL_CS_NAME`

**⚠️ Gotchas:**
- Sentinel-2 MSI; band numbering differs from Landsat — check band mapping docs
- 10-day revisit but cloud contamination still common

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="HLSS30",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MCD12Q1` — MODIS/Terra+Aqua Land Cover Type Yearly L3 Global 500m SIN Grid V061

**concept_id:** `C2484079608-LPCLOUD`  |  **DOI:** 10.5067/MODIS/MCD12Q1.061

**ML Use:** Annual land cover classification labels for supervised ML and accuracy assessment

*The Terra and Aqua combined Moderate Resolution Imaging Spectroradiometer (MODIS) Land Cover Type (MCD12Q1) Version 6.1 data product provides global land cover types at yearly intervals. The MCD12Q1 V*

**Access:** HTTPS  |  **Format:** HDF-EOS2  |  **Size:** 4.6 MB  |  **Login required:** ✅

**Key Variables:** `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`, `TileID`, `PROCESSVERSION`, `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- Annual only — no within-year dynamics
- IGBP scheme has 17 classes; some regimes lump crops with mosaics

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MCD12Q1",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MYD13A2` — MODIS/Aqua Vegetation Indices 16-Day L3 Global 1km SIN Grid V061

**concept_id:** `C2565794049-LPCLOUD`  |  **DOI:** 10.5067/MODIS/MYD13A2.061

**ML Use:** Aqua MODIS 16-day NDVI, complementary to Terra (MOD13A2) for gap-filling

*The Aqua Moderate Resolution Imaging Spectroradiometer (MODIS) Vegetation Indices 16-Day (MYD13A2) Version 6.1 product provides Vegetation Index (VI) values at a per pixel basis at 1 kilometer (km) sp*

**Access:** HTTPS  |  **Format:** HDF-EOS2  |  **Size:** 8.8 MB  |  **Login required:** ✅

**Key Variables:** `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`, `PROCESSVERSION`, `TileID`, `INPUTPRODUCTRESOLUTION`, `NDVI1KM16DAYQCLASSPERCENTAGE`

**⚠️ Gotchas:**
- Aqua crosses equator at ~1:30 PM local — different view angle than Terra

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MYD13A2",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

### Active Fires / Burned Area / Wildfire Risk

**Topic:** Fire & Burned Area  |  **Category ID:** `cat_02_active_fires`

| Short Name | Concept ID | Version | Prov | Cloud | Granules | Level | Time Range |
|------------|-----------|---------|------|-------|----------|-------|-----------|
| `MOD14A2` | `C2565791018-LPCLOUD` | 061 | LPCLOUD | ☁️ | 360,813 | 3 | 2000-02→ongoing |
| `MCD64A1` | `C2565786756-LPCLOUD` | 061 | LPCLOUD | ☁️ | 83,336 | 3 | 2000-11→ongoing |
| `VNP64A1` | `C2847928673-LPCLOUD` | 002 | LPCLOUD | ☁️ | 50,050 | 4 | 2012-03→ongoing |
| `MCD14DL` | `C2105705664-LANCEMODIS` | 6.1NRT | LANCEMODIS | 🖥️ | 7 | 2 | 2019-12→ongoing |

#### `MOD14A2` — MODIS/Terra Thermal Anomalies/Fire 8-Day L3 Global 1km SIN Grid V061

**concept_id:** `C2565791018-LPCLOUD`  |  **DOI:** 10.5067/MODIS/MOD14A2.061

**ML Use:** Fire hotspot detection labels for wildfire risk models; temporal fire tracking

*The Terra Moderate Resolution Imaging Spectroradiometer (MODIS) Thermal Anomalies and Fire 8-Day (MOD14A2) Version 6.1 data are generated at 1 kilometer (km) spatial resolution as a Level 3 product. T*

**Access:** HTTPS  |  **Format:** HDF-EOS2  |  **Size:** 0.3 MB  |  **Login required:** ✅

**Key Variables:** `FIREPIXELS`, `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`, `NUMBERGRIDCELLSCONTAININGFIRE`, `PROCESSVERSION`, `TileID`

**⚠️ Gotchas:**
- 8-day composite; individual fire timing lost
- Commission errors possible in hot desert/industrial areas

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MOD14A2",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MCD64A1` — MODIS/Terra+Aqua Direct Broadcast Burned Area Monthly L3 Global 500m SIN Grid V0

**concept_id:** `C2565786756-LPCLOUD`  |  **DOI:** 10.5067/MODIS/MCD64A1.061

**ML Use:** Monthly burned area ground truth for fire severity classification and risk mapping

*The Terra and Aqua combined MCD64A1 Version 6.1 Burned Area data product is a monthly, global gridded 500 meter (m) product containing per-pixel burned-area and quality information. The MCD64A1 burned*

**Access:** HTTPS  |  **Format:** HDF-EOS2  |  **Size:** 1.8 MB  |  **Login required:** ✅

**Key Variables:** `PROCESSVERSION`, `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`, `TileID`, `INPUTFILERESOLUTION`, `identifier_product_doi`

**⚠️ Gotchas:**
- Monthly burned area; misses small fires <100ha
- Algorithm differs from active fire — use both for training

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MCD64A1",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `VNP64A1` — VIIRS/NPP Burned Area Monthly L4 Global 500m SIN Grid V002

**concept_id:** `C2847928673-LPCLOUD`  |  **DOI:** 10.5067/VIIRS/VNP64A1.002

**ML Use:** VIIRS burned area monthly for fire ML continuity beyond MODIS era

*The delivery of all Suomi National Polar-orbiting Partnership (Suomi NPP) VIIRS science data products [ceased on November 2, 2026 (2026/306)](https://www.earthdata.nasa.gov/data/alerts-outages/reminde*

**Access:** HTTPS  |  **Format:** HDF-EOS5  |  **Size:** 1.8 MB  |  **Login required:** ✅

**Key Variables:** `identifier_product_doi`, `identifier_product_doi_authority`, `TileID`, `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`

**⚠️ Gotchas:**
- VIIRS successor to MCD64A1; slightly different detection characteristics

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="VNP64A1",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MCD14DL` — MODIS/Aqua Terra Thermal Anomalies/Fire locations 1km FIRMS NRT (Vector data)

**concept_id:** `C2105705664-LANCEMODIS`  |  **DOI:** 10.5067/FIRMS/MODIS/MCD14DL.NRT.0061

**ML Use:** Near-real-time active fire locations for fire response and event detection

*The MODIS/Aqua Terra Thermal Anomalies/Fire locations 1km FIRMS Near Real-Time (NRT) - Collection 61 processed by NASA's Land, Atmosphere Near real-time Capability for EOS (LANCE) Fire Information for*

**Access:** HTTPS  |  **Format:** Text File  |  **Size:** 1 MB  |  **Login required:** ✅

**Key Variables:** `Latitude`, `Longitude`, `Brightness`, `Scan`, `Track`, `Acq_Date`

**⚠️ Gotchas:**
- NRT product — preliminary quality; not for long-term climatology
- CSV/shapefile format, not gridded

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MCD14DL",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

### Precipitation / Floods / Drought / Soil Moisture

**Topic:** Hydrology  |  **Category ID:** `cat_03_precipitation`

| Short Name | Concept ID | Version | Prov | Cloud | Granules | Level | Time Range |
|------------|-----------|---------|------|-------|----------|-------|-----------|
| `GPM_3IMERGDF` | `C2723754864-GES_DISC` | 07 | GES_DISC | ☁️ | 10,135 | 3 | 1998-01→2025-09 |
| `GPM_3IMERGHH` | `C2723754847-GES_DISC` | 07 | GES_DISC | ☁️ | 486,480 | 3 | 1998-01→2025-09 |
| `SPL3SMP` | `C2938664585-NSIDC_CPRD` | 009 | NSIDC_CPRD | ☁️ | 4,166 | 3 | 2015-03→ongoing |
| `SPL4SMGP` | `C3480440870-NSIDC_CPRD` | 008 | NSIDC_CPRD | ☁️ | 33,977 | 4 | 2015-03→ongoing |
| `TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4` | `C3195527175-POCLOUD` | RL06.3Mv04 | POCLOUD | ☁️ | 1 | 3 | 2002-04→ongoing |
| `TELLUS_GRFO_L3_CSR_RL06.3_LND_v04` | `C3193285193-POCLOUD` | RL06.3v04 | POCLOUD | ☁️ | 97 | 3 | 2018-05→ongoing |

#### `GPM_3IMERGDF` — GPM IMERG Final Precipitation L3 1 day 0.1 degree x 0.1 degree V07 (GPM_3IMERGDF

**concept_id:** `C2723754864-GES_DISC`  |  **DOI:** 10.5067/GPM/IMERGDF/DAY/07

**ML Use:** Daily precipitation feature for flood prediction, drought index, crop water stress models

*
Version 07 is the current version of the data set. Older versions will no longer be available and have been superseded by Version 07.

The Integrated Multi-satellitE Retrievals for GPM (IMERG) IMERG *

**Access:** HTTPS  |  **Format:**   |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- Late-run product has ~2.5 month latency; Early-run available sooner with less accuracy
- Gauge-corrected; sparse gauge network affects quality over oceans and remote land

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="GPM_3IMERGDF",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `GPM_3IMERGHH` — GPM IMERG Final Precipitation L3 Half Hourly 0.1 degree x 0.1 degree V07 (GPM_3I

**concept_id:** `C2723754847-GES_DISC`  |  **DOI:** 10.5067/GPM/IMERG/3B-HH/07

**ML Use:** 30-min precipitation for flash flood ML, storm tracking, sub-daily hydrological models

*Version 07B is the current version of the IMERG data sets. Older versions will no longer be available and have been superseded by Version 07.

The Integrated Multi-satellitE Retrievals for GPM (IMERG)*

**Access:** HTTPS  |  **Format:**   |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- Very large dataset; use temporal/spatial subsets
- 0.1° resolution; 30-min accumulation

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="GPM_3IMERGHH",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `SPL3SMP` — SMAP L3 Radiometer Global Daily 36 km EASE-Grid Soil Moisture V009

**concept_id:** `C2938664585-NSIDC_CPRD`  |  **DOI:** 10.5067/4XXOGX0OOW1S

**ML Use:** Soil moisture input for drought monitoring, agricultural stress prediction, flood risk

*This Level-3 (L3) soil moisture product provides a composite of daily estimates of global land surface conditions retrieved by the Soil Moisture Active Passive (SMAP) passive microwave radiometer. SMA*

**Access:** HTTPS  |  **Format:** HDF5  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- Enhanced 9km product (not standard 36km) — fewer data gaps
- Radiometer can't penetrate dense vegetation canopy (>5 kg/m²)

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="SPL3SMP",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `SPL4SMGP` — SMAP L4 Global 3-hourly 9 km EASE-Grid Surface and Root Zone Soil Moisture Geoph

**concept_id:** `C3480440870-NSIDC_CPRD`  |  **DOI:** 10.5067/T5RUATAQREF8

**ML Use:** SMAP L4 3-hourly soil moisture profile for root-zone water availability, agricultural stress prediction

*SMAP Level-4 (L4) surface and root zone soil moisture (L4_SM) data are provided in three products. 

The SMAP L4 Global 3-hourly 9 km EASE-Grid Surface and Root Zone Soil Moisture Geophysical Data (SP*

**Access:** HTTPS  |  **Format:** HDF5  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- Model-assimilated product — not independent observations; correlated with GEOS-5
- 9km EASE-Grid — reproject for integration with optical data

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="SPL4SMGP",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4` — JPL GRACE and GRACE-FO Mascon Ocean, Ice, and Hydrology Equivalent Water Height 

**concept_id:** `C3195527175-POCLOUD`  |  **DOI:** 10.5067/TEMSC-3JC634

**ML Use:** GRACE/GRACE-FO terrestrial water storage anomaly for drought/flood severity and groundwater depletion ML

*This dataset contains gridded monthly global water storage/height anomalies relative to a time-mean, derived from GRACE and GRACE-FO and processed at JPL using the Mascon approach (RL06.3Mv04). A Coas*

**Access:** OPeNDAP | HTTPS  |  **Format:** netCDF-4  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `earliest_granule_start_time`, `latest_granule_end_time`, `data_latency`, `Series Name`, `Persistent ID`

**⚠️ Gotchas:**
- Monthly resolution only; gap months in 2017-2018 GRACE/GRACE-FO transition
- Mascon approach; apply land mask and CRI filter for land-only analysis

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `TELLUS_GRFO_L3_CSR_RL06.3_LND_v04` — CSR TELLUS GRACE-FO Level-3 Monthly Land Water-Equivalent-Thickness Surface Mass

**concept_id:** `C3193285193-POCLOUD`  |  **DOI:** 10.5067/GFLND-3C634

**ML Use:** GRACE-FO land water equivalent thickness for long-term water cycle trend analysis

*This data set is produced by the Center for Space Research (CSR) GRACE-FO (Gravity Recovery and Climate Experiment Follow-On) program and derives the terrestrial water storage anomaly given as equival*

**Access:** OPeNDAP | HTTPS  |  **Format:** netCDF-4  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `earliest_granule_start_time`, `latest_granule_end_time`, `Series Name`

**⚠️ Gotchas:**
- Spherical harmonics; apply de-striping and Gaussian smoothing (300km recommended)
- Independent from mascon solution — compare both for uncertainty quantification

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="TELLUS_GRFO_L3_CSR_RL06.3_LND_v04",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

### Temperature / Land Surface / Climate Reanalysis

**Topic:** Temperature & Climate  |  **Category ID:** `cat_04_temperature`

| Short Name | Concept ID | Version | Prov | Cloud | Granules | Level | Time Range |
|------------|-----------|---------|------|-------|----------|-------|-----------|
| `M2T1NXSLV` | `C1276812863-GES_DISC` | 5.12.4 | GES_DISC | ☁️ | 17,076 | 4 | 1980-01→ongoing |
| `M2SDNXSLV` | `C1276812843-GES_DISC` | 5.12.4 | GES_DISC | ☁️ | 17,076 | 4 | 1980-01→ongoing |
| `GLDAS_NOAH025_3H` | `C1342986035-GES_DISC` | 2.1 | GES_DISC | ☁️ | 77,671 | 4 | 2000-01→ongoing |
| `GLDAS_NOAH025_M` | `C1342986036-GES_DISC` | 2.1 | GES_DISC | ☁️ | 319 | 4 | 2000-01→ongoing |

#### `M2T1NXSLV` — MERRA-2 tavg1_2d_slv_Nx: 2d,1-Hourly,Time-Averaged,Single-Level,Assimilation,Sin

**concept_id:** `C1276812863-GES_DISC`  |  **DOI:** 10.5067/VJAFPLI1CSIV

**ML Use:** MERRA-2 hourly 2m air temperature, humidity, winds for climate ML and weather downscaling

*M2T1NXSLV (or  tavg1_2d_slv_Nx) is an hourly time-averaged 2-dimensional data collection in Modern-Era Retrospective analysis for Research and Applications version 2 (MERRA-2).  This collection consis*

**Access:** HTTPS  |  **Format:**   |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- Very large dataset; hourly global 0.5°×0.625° — subset spatially/temporally
- Reanalysis: not direct observations; regional biases exist especially over sparse-station areas

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="M2T1NXSLV",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `M2SDNXSLV` — MERRA-2 statD_2d_slv_Nx: 2d,Daily,Aggregated Statistics,Single-Level,Assimilatio

**concept_id:** `C1276812843-GES_DISC`  |  **DOI:** 10.5067/9SC1VNTWGWV3

**ML Use:** MERRA-2 daily statistics for extreme event detection, heat wave classification, climate trend analysis

*M2SDNXSLV (or  statD_2d_slv_Nx) is a 2-dimensional daily data collection in Modern-Era Retrospective analysis for Research and Applications version 2 (MERRA-2).  This collection consists of daily stat*

**Access:** HTTPS  |  **Format:**   |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- Daily statistics product; min/max/mean aggregated — verify which statistic before ML feature engineering

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="M2SDNXSLV",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `GLDAS_NOAH025_3H` — GLDAS Noah Land Surface Model L4 3 hourly 0.25 x 0.25 degree V2.1 (GLDAS_NOAH025

**concept_id:** `C1342986035-GES_DISC`  |  **DOI:** 10.5067/E7TYRXPJKWOQ

**ML Use:** GLDAS 3-hourly land surface model outputs for hydrological ML and soil/vegetation state estimation

*NASA Global Land Data Assimilation System Version 2 (GLDAS-2) has three components: GLDAS-2.0, GLDAS-2.1, and GLDAS-2.2.  GLDAS-2.0 is forced entirely with the Princeton meteorological forcing input d*

**Access:** HTTPS  |  **Format:**   |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- Model output, not observations — use ensemble spread for uncertainty
- 0.25° resolution; discontinuities at MODIS forcing transitions

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="GLDAS_NOAH025_3H",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `GLDAS_NOAH025_M` — GLDAS Noah Land Surface Model L4 monthly 0.25 x 0.25 degree V2.1 (GLDAS_NOAH025_

**concept_id:** `C1342986036-GES_DISC`  |  **DOI:** 10.5067/SXAVCZFAQLNO

**ML Use:** GLDAS monthly mean land surface variables for climate analysis and long-term trend detection

*NASA Global Land Data Assimilation System Version 2 (GLDAS-2) has three components: GLDAS-2.0, GLDAS-2.1, and GLDAS-2.2.  GLDAS-2.0 is forced entirely with the Princeton meteorological forcing input d*

**Access:** HTTPS  |  **Format:**   |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- Monthly only; use for climatological baselines rather than event detection

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="GLDAS_NOAH025_M",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

### Air Quality / Aerosols / Atmospheric Composition

**Topic:** Atmosphere  |  **Category ID:** `cat_05_air_quality`

| Short Name | Concept ID | Version | Prov | Cloud | Granules | Level | Time Range |
|------------|-----------|---------|------|-------|----------|-------|-----------|
| `OMNO2d` | `C3333493715-GES_DISC` | 004 | GES_DISC | ☁️ | 8,029 | 3 | 2004-10→ongoing |
| `OMSO2G` | `C1266136113-GES_DISC` | 003 | GES_DISC | ☁️ | 7,518 | 2G | 2004-10→ongoing |
| `MOD04_3K` | `C1443420430-LAADS` | 6.1 | LAADS | ☁️ | 1,491,495 | 2 | 2000-02→ongoing |
| `MYD04_3K` | `C1443528505-LAADS` | 6.1 | LAADS | ☁️ | 1,374,685 | 2 | 2002-07→ongoing |
| `M2T1NXAER` | `C1276812830-GES_DISC` | 5.12.4 | GES_DISC | ☁️ | 17,076 | 4 | 1980-01→ongoing |
| `S5P_L2__NO2____HiR` | `C2089270961-GES_DISC` | 2 | GES_DISC | ☁️ | 43,971 | 2 | 2018-04→ongoing |
| `MCD19A2` | `C2324689816-LPCLOUD` | 061 | LPCLOUD | ☁️ | 2,881,933 | 2G | 2000-02→ongoing |

#### `OMNO2d` — OMI/Aura NO2 Cloud-Screened Total and Tropospheric Column L3 Global Gridded 0.25

**concept_id:** `C3333493715-GES_DISC`  |  **DOI:** 10.5067/AURA/OMI/DATA3407

**ML Use:** Daily NO2 columns for air quality ML, pollution source attribution, urban health studies

*This is Level-3 daily global gridded (0.25x0.25 degree) Nitrogen Dioxide Product (OMNO2d). OMNO2d data product is a Level-3 Gridded Product where pixel level data of good quality are binned and "avera*

**Access:** HTTPS  |  **Format:**   |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- Daily gridded at 0.25°; cloud fraction threshold needed (apply cloud_fraction < 0.3)
- Retrieval quality degrades at high SZA (polar winter); use qa_value >= 0.75

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="OMNO2d",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `OMSO2G` — OMI/Aura Sulphur Dioxide (SO2) Total Column Daily L2 Global Gridded 0.125 degree

**concept_id:** `C1266136113-GES_DISC`  |  **DOI:** 10.5067/Aura/OMI/DATA2023

**ML Use:** Daily SO2 for volcanic eruption detection, industrial pollution monitoring, atmospheric chemistry ML

*This Level-2G daily global gridded product OMSO2G is based on the pixel level OMI Level-2 SO2 product OMSO2.  OMSO2G data product is a special Level-2 gridded product where pixel level products are bi*

**Access:** HTTPS  |  **Format:**   |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- SO2 retrieval has large uncertainty over clean ocean; mask low-signal pixels
- Multiple SO2 columns (PBL, TRL, TRM, STL) — choose appropriate altitude layer

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="OMSO2G",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MOD04_3K` — MODIS/Terra Aerosol 5-Min L2 Swath 3km

**concept_id:** `C1443420430-LAADS`  |  **DOI:** 10.5067/MODIS/MOD04_3K.061

**ML Use:** 3km MODIS aerosol optical depth for air quality, PM2.5 estimation, climate forcing ML

*The new Collection 6.1 (C61) MODIS/Terra Aerosol 5 Min L2 Swath 3km (MOD04_3K) product is an improved version based on algorithm changes in Dark Target (DT) Aerosol retrieval over urban areas and unce*

**Access:** OPeNDAP | HTTPS  |  **Format:** HDF-EOS  |  **Size:** 8 MB  |  **Login required:** ✅

**Key Variables:** `SuccessfulRetrievalPct_Ocean`, `SuccessfulRetrievalPct`, `SuccessfulRetrievalPct_Land`, `SCI_STATE`, `SCI_ABNORM`, `VeryHighConfidentClearPct`

**⚠️ Gotchas:**
- Land and ocean retrievals use different algorithms; check Land_Ocean_Quality_Flag
- High cloud contamination risk; check quality flag before ML ingestion

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MOD04_3K",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MYD04_3K` — MODIS/Aqua Aerosol 5-Min L2 Swath 3km

**concept_id:** `C1443528505-LAADS`  |  **DOI:** 10.5067/MODIS/MYD04_3K.061

**ML Use:** Aqua MODIS 3km AOD — complementary to Terra (MOD04_3K) for twice-daily coverage

*The new Collection 6.1 (C61) MODIS/Aqua Aerosol 5 Min L2 Swath 3km (MYD04_3K) product is an improved version based on algorithm changes in Dark Target (DT) Aerosol retrieval over urban areas and uncer*

**Access:** OPeNDAP | HTTPS  |  **Format:** HDF-EOS  |  **Size:** 8 MB  |  **Login required:** ✅

**Key Variables:** `SuccessCloudPhaseRtrPct_IR`, `SuccessCloudOptPropRtrPct_VIS`, `IceCloudDetectedPct_VIS`, `CloudCoverFractionPct_VIS`, `SuccessfulRetrievalPct_NIR`, `SuccessfulRetrievalPct_IR`

**⚠️ Gotchas:**
- Same caveats as MOD04_3K but Aqua equatorial crossing ~1:30pm vs Terra ~10:30am

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MYD04_3K",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `M2T1NXAER` — MERRA-2 tavg1_2d_aer_Nx: 2d,1-Hourly,Time-averaged,Single-Level,Assimilation,Aer

**concept_id:** `C1276812830-GES_DISC`  |  **DOI:** 10.5067/KLICLTZ8EM9D

**ML Use:** MERRA-2 hourly aerosol diagnostics (AOD, dust, sea salt) for air quality trend ML

*M2T1NXAER (or  tavg1_2d_aer_Nx) is an hourly time-averaged 2-dimensional data collection in Modern-Era Retrospective analysis for Research and Applications version 2 (MERRA-2).  This collection consis*

**Access:** HTTPS  |  **Format:**   |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- Reanalysis-based aerosol; model biases in emissions propagate to output
- 0.5°×0.625° grid; insufficient for urban-scale studies

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="M2T1NXAER",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `S5P_L2__NO2____HiR` — Sentinel-5P TROPOMI Tropospheric NO2 1-Orbit L2 5.5km x 3.5km V2 (S5P_L2__NO2___

**concept_id:** `C2089270961-GES_DISC`  |  **DOI:** 10.5270/S5P-9bnp8q8

**ML Use:** TROPOMI high-resolution (3.5×5.5km) tropospheric NO2 columns for urban air quality ML

*Starting from August 6th in 2019, Sentinel-5P TROPOMI along-track high spatial resolution (~5.5km at nadir) has been implemented.
For data before August 6th of 2019, please check S5P_L2__NO2____1 data*

**Access:** HTTPS  |  **Format:**   |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- Swath data — requires spatial binning to grid for ML feature stacks
- Apply qa_value >= 0.75 filter; clouds and snow cause retrieval issues

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="S5P_L2__NO2____HiR",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MCD19A2` — MODIS/Terra+Aqua Land Aerosol Optical Depth Daily L2G Global 1km SIN Grid V061

**concept_id:** `C2324689816-LPCLOUD`  |  **DOI:** 10.5067/MODIS/MCD19A2.061

**ML Use:** Multi-angle MODIS MAIAC AOD at 1km for air quality, PM2.5 estimation ML

*The MCD19A2 Version 6.1 data product is a Moderate Resolution Imaging Spectroradiometer (MODIS) Terra and Aqua combined Multi-angle Implementation of Atmospheric Correction (MAIAC) Land Aerosol Optica*

**Access:** HTTPS  |  **Format:** HDF-EOS2  |  **Size:** 6.7 MB  |  **Login required:** ✅

**Key Variables:** `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`, `TileID`, `PROCESSVERSION`, `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- MAIAC algorithm requires contiguous orbit history — gaps at orbit boundaries
- 1km AOD — finer than standard DT/DB retrievals; check urban vs rural retrieval mode

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MCD19A2",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

### Oceans / Sea Surface Temperature / Ocean Color

**Topic:** Ocean  |  **Category ID:** `cat_06_oceans`

| Short Name | Concept ID | Version | Prov | Cloud | Granules | Level | Time Range |
|------------|-----------|---------|------|-------|----------|-------|-----------|
| `MUR-JPL-L4-GLOB-v4.1` | `C1996881146-POCLOUD` | 4.1 | POCLOUD | ☁️ | 8,933 | 4 | 2002-05→ongoing |
| `MUR25-JPL-L4-GLOB-v04.2` | `C2036880657-POCLOUD` | 4.2 | POCLOUD | ☁️ | 8,841 | 4 | 2002-08→ongoing |
| `MODISA_L3m_CHL` | `C3380709133-OB_CLOUD` | 2022.0 | OB_CLOUD | ☁️ | 27,028 | 3 | 2002-07→ongoing |
| `SWOT_L2_LR_SSH_D` | `C3233945000-POCLOUD` | D | POCLOUD | ☁️ | 151,431 | 2 | 2022-12→ongoing |
| `MODISA_L2_OC` | `C3380708980-OB_CLOUD` | 2022.0 | OB_CLOUD | ☁️ | 1,713,208 | 2 | 2002-07→ongoing |

#### `MUR-JPL-L4-GLOB-v4.1` — GHRSST Level 4 MUR Global Foundation Sea Surface Temperature Analysis (v4.1)

**concept_id:** `C1996881146-POCLOUD`  |  **DOI:** 10.5067/GHGMR-4FJ04

**ML Use:** 1km daily gap-free SST for marine heatwave detection, coral bleaching risk, fisheries ML

*A Group for High Resolution Sea Surface Temperature (GHRSST) Level 4 sea surface temperature analysis produced as a retrospective dataset (four day latency) and near-real-time dataset (one day latency*

**Access:** OPeNDAP | Harmony | HTTPS  |  **Format:** netCDF-4  |  **Size:** 700 MB  |  **Login required:** ✅

**Key Variables:** `earliest_granule_start_time`, `latest_granule_end_time`, `Series Name`, `Persistent ID`

**⚠️ Gotchas:**
- Very large dataset (1km global daily); always subset spatially
- Foundation SST (not skin SST); compare to MODIS for surface vs subsurface dynamics

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MUR-JPL-L4-GLOB-v4.1",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MUR25-JPL-L4-GLOB-v04.2` — GHRSST Level 4 MUR 0.25deg Global Foundation Sea Surface Temperature Analysis (v

**concept_id:** `C2036880657-POCLOUD`  |  **DOI:** 10.5067/GHM25-4FJ42

**ML Use:** 0.25° daily SST for ENSO/PDO indices, basin-scale climate ML, operational ocean forecasting features

*A Group for High Resolution Sea Surface Temperature (GHRSST) Level 4 sea surface temperature analysis produced as a retrospective dataset  at the JPL Physical Oceanography DAAC using wavelets as basis*

**Access:** OPeNDAP | Harmony | HTTPS  |  **Format:** netCDF-4  |  **Size:** 2 MB  |  **Login required:** ✅

**Key Variables:** `earliest_granule_start_time`, `latest_granule_end_time`, `data_latency`, `Series Name`, `Persistent ID`

**⚠️ Gotchas:**
- 0.25° coarser than MUR 1km; use for large-scale climate studies only

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MUR25-JPL-L4-GLOB-v04.2",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MODISA_L3m_CHL` — Aqua MODIS Level-3 Global Mapped Chlorophyll (CHL) Data, version 2022.0

**concept_id:** `C3380709133-OB_CLOUD`  |  **DOI:** 10.5067/AQUA/MODIS/L3M/CHL/2022.0

**ML Use:** Global monthly chlorophyll-a for ocean productivity ML, harmful algal bloom prediction, biogeochemistry

*The Chlorophyll-a data suite provides global, gridded composites of surface chlorophyll-a concentration (a proxy for phytoplankton biomass). CHL supports time-series and climatologies, anomaly detecti*

**Access:** OPeNDAP | HTTPS  |  **Format:** netCDF-4  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `CompositingPeriod`, `SpatialResolution`, `Product`

**⚠️ Gotchas:**
- Cloud/ice gaps persist in monthly composites; apply valid data mask (l2_flags)
- Algorithm uncertainty high in coastal/turbid waters; use Rrs-based approaches for nearshore

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MODISA_L3m_CHL",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `SWOT_L2_LR_SSH_D` — SWOT Level 2 KaRIn Low Rate Sea Surface Height Data Product, Version D

**concept_id:** `C3233945000-POCLOUD`  |  **DOI:** 10.5067/SWOT-SSH-D

**ML Use:** SWOT wide-swath sea surface height for eddy detection, ocean current ML, inland water levels

*The SWOT Level 2 KaRIn Low Rate Sea Surface Height Data Product from the Surface Water Ocean Topography (SWOT) mission provides global sea surface height and significant wave height observations deriv*

**Access:** OPeNDAP | HTTPS  |  **Format:** netCDF-4  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `TILE`

**⚠️ Gotchas:**
- New mission (2022+); data quality still improving; check science quality flag
- 21-day repeat orbit; temporal coverage gaps between swaths

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="SWOT_L2_LR_SSH_D",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MODISA_L2_OC` — Aqua MODIS Level-2 Regional  Ocean Color (OC) Data, version 2022.0

**concept_id:** `C3380708980-OB_CLOUD`  |  **DOI:** 10.5067/AQUA/MODIS/L2/OC/2022.0

**ML Use:** MODIS Aqua L2 ocean color Rrs bands for water quality ML, sediment transport, primary productivity

*The Ocean Color (OC) data suite provides calibrated, atmospherically corrected ocean-optics measurements and derived biogeophysical products. This data suite includes the Apparent Optical Properties (*

**Access:** HTTPS  |  **Format:** netCDF-4  |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- Swath data at 1km; requires spatial binning to grid for ML
- High cloud contamination in tropics; temporal compositing needed

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MODISA_L2_OC",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

### Cryosphere / Snow / Sea Ice / Ice Sheets / Glaciers

**Topic:** Cryosphere  |  **Category ID:** `cat_07_cryosphere`

| Short Name | Concept ID | Version | Prov | Cloud | Granules | Level | Time Range |
|------------|-----------|---------|------|-------|----------|-------|-----------|
| `MOD10CM` | `C3050353608-NSIDC_CPRD` | 61 | NSIDC_CPRD | ☁️ | 315 | 3 | 2000-03→ongoing |
| `NSIDC-0079` | `C3177837864-NSIDC_CPRD` | 4 | NSIDC_CPRD | ☁️ | 35,580 | 3 | 1978-11→2025-12 |
| `NSIDC-0051` | `C3177837840-NSIDC_CPRD` | 2 | NSIDC_CPRD | ☁️ | 35,600 | 3 | 1978-10→2025-12 |
| `ATL09` | `C3578753623-NSIDC_CPRD` | 007 | NSIDC_CPRD | ☁️ | 42,670 | 3 | 2018-10→ongoing |
| `MYD10CM` | `C3091267534-NSIDC_CPRD` | 61 | NSIDC_CPRD | ☁️ | 290 | 3 | 2002-07→ongoing |
| `NISE` | `C3177837670-NSIDC_CPRD` | 5 | NSIDC_CPRD | ☁️ | 3,323 | 3 | 2016-12→2026-01 |
| `ATL06` | `C3564876127-NSIDC_CPRD` | 007 | NSIDC_CPRD | ☁️ | 448,704 | 3 | 2018-10→ongoing |

#### `MOD10CM` — MODIS/Terra Snow Cover Monthly L3 Global 0.05Deg CMG V061

**concept_id:** `C3050353608-NSIDC_CPRD`  |  **DOI:** 10.5067/MODIS/MOD10CM.061

**ML Use:** Monthly MODIS snow cover for snowmelt runoff prediction, water resource ML, climate trend analysis

*This global Level-3 (L3) data set provides monthly mean snow cover extent within 0.05° (approx. 5 km) MODIS Climate Modeling Grid (CMG) cells. This data set is derived from snow cover observations in *

**Access:** HTTPS  |  **Format:** HDF-EOS2  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `PROCESSVERSION`, `SNOWCOVERPERCENT`, `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- Monthly composited; cloud-free but temporal detail lost
- NDSI threshold may miss wet snow (spring melt)

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MOD10CM",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `NSIDC-0079` — Bootstrap Sea Ice Concentrations from Nimbus-7 SMMR and DMSP SSM/I-SSMIS V004

**concept_id:** `C3177837864-NSIDC_CPRD`  |  **DOI:** 10.5067/X5LG68MH013O

**ML Use:** Daily SSM/I passive microwave sea ice concentration for sea ice extent ML and navigation risk

*This sea ice concentration data set was derived using measurements from the Scanning Multichannel Microwave Radiometer (SMMR) on the Nimbus-7 satellite and from the Special Sensor Microwave/Imager (SS*

**Access:** HTTPS  |  **Format:** netCDF-4  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `GridResolution`, `SIPSMetGenVersion`, `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- 25km passive microwave resolution; melt pond contamination in summer reduces accuracy
- SSMI/SSMIS sensor transitions; check inter-sensor calibration before long-term trend analysis

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="NSIDC-0079",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `NSIDC-0051` — Sea Ice Concentrations from Nimbus-7 SMMR and DMSP SSM/I-SSMIS Passive Microwave

**concept_id:** `C3177837840-NSIDC_CPRD`  |  **DOI:** 10.5067/MPYG15WAA4WX

**ML Use:** SMMR/SSM/I sea ice concentration 25km for long-term cryosphere trend analysis

*This data set is generated from brightness temperature data and is designed to provide a consistent time series of sea ice concentrations spanning the coverage of several passive microwave instruments*

**Access:** HTTPS  |  **Format:** PNG  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `GridResolution`, `SIPSMetGenVersion`, `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- 25km; may underestimate sea ice in melt season due to surface melt ponds
- Data gaps before 1979 for some channels

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="NSIDC-0051",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `ATL09` — ATLAS/ICESat-2 L3A Calibrated Backscatter Profiles and Atmospheric Layer Charact

**concept_id:** `C3578753623-NSIDC_CPRD`  |  **DOI:** 10.5067/ATLAS/ATL09.007

**ML Use:** ICESat-2 ATL09 atmospheric calibrated backscatter for cloud profiling ML

*ATL09 contains calibrated, attenuated backscatter profiles (CAB), layer-integrated attenuated backscatter, blowing snow, and other parameters including cloud and aerosol layer height and atmospheric c*

**Access:** HTTPS  |  **Format:** HDF5  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- Along-track profile only — not gridded; requires spatial aggregation for area ML

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="ATL09",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MYD10CM` — MODIS/Aqua Snow Cover Monthly L3 Global 0.05Deg CMG V061

**concept_id:** `C3091267534-NSIDC_CPRD`  |  **DOI:** 10.5067/MODIS/MYD10CM.061

**ML Use:** Aqua MODIS monthly snow cover CMG for Northern Hemisphere snowpack analysis, climate ML

*This global Level-3 (L3) data set provides monthly average snow cover within 0.05° (approx. 5 km) MODIS Climate Modeling Grid (CMG) cells. Monthly averages are computed from daily snow cover observati*

**Access:** HTTPS  |  **Format:** HDF-EOS2  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `PROCESSVERSION`, `SNOWCOVERPERCENT`, `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- Monthly only; pair with MOD10CM (Terra) for double-coverage consistency check
- NDSI-based; wet snow in spring may be missed

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MYD10CM",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `NISE` — Near-Real-Time SSM/I-SSMIS EASE-Grid Daily Global Ice Concentration and Snow Ext

**concept_id:** `C3177837670-NSIDC_CPRD`  |  **DOI:** 10.5067/3KB2JPLFPK3R

**ML Use:** Near-real-time daily sea ice concentration for operational ice extent tracking and sea ice ML features

*The Near-real-time Ice and Snow Extent (NISE) data set provides daily, global maps of sea ice concentrations and snow extent. These data are not suitable for time series, anomalies, or trends analyses*

**Access:** HTTPS  |  **Format:** HDF-EOS2  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- NRT product; may have preliminary quality; not recommended for long-term climatology
- EASE-Grid projection; reproject to WGS84 for multi-sensor fusion

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="NISE",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `ATL06` — ATLAS/ICESat-2 L3A Land Ice Height V007

**concept_id:** `C3564876127-NSIDC_CPRD`  |  **DOI:** 10.5067/ATLAS/ATL06.007

**ML Use:** ICESat-2 land ice surface elevation for ice sheet mass balance ML, glaciological studies

*ATL06 contains geolocated land-ice surface heights above the WGS84 ellipsoid, plus ancillary parameters that can be used to interpret and assess the quality of the height estimates. The data were acqu*

**Access:** HTTPS  |  **Format:** HDF5  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- Along-track profile only — not gridded; requires spatial aggregation
- Strong beam vs weak beam quality differences; use only strong beams for elevation retrievals

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="ATL06",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

### Elevation / Terrain / 3D Structure

**Topic:** Terrain  |  **Category ID:** `cat_08_elevation`

| Short Name | Concept ID | Version | Prov | Cloud | Granules | Level | Time Range |
|------------|-----------|---------|------|-------|----------|-------|-----------|
| `SRTMGL1` | `C2763266360-LPCLOUD` | 003 | LPCLOUD | ☁️ | 14,297 | 3 | 2000-02→2000-02 |
| `ASTGTM` | `C1711961296-LPCLOUD` | 003 | LPCLOUD | ☁️ | 22,912 | 3 | 2000-03→2013-11 |
| `NASADEM_HGT` | `C2763264762-LPCLOUD` | 001 | LPCLOUD | ☁️ | 14,520 | 3 | 2000-02→2000-02 |
| `GEDI02_B` | `C3974616135-LPCLOUD` | 003 | LPCLOUD | ☁️ | 114,604 | 2B | 2024-04→ongoing |

#### `SRTMGL1` — NASA Shuttle Radar Topography Mission Global 1 arc second V003

**concept_id:** `C2763266360-LPCLOUD`  |  **DOI:** 10.5067/MEASURES/SRTM/SRTMGL1.003

**ML Use:** 30m global DEM for terrain features (slope, aspect, curvature) in hydrological and risk ML models

*The Land Processes Distributed Active Archive Center (LP DAAC) is responsible for the archive and distribution of the NASA Making Earth System Data Records for Use in Research Environments ([MEaSUREs]*

**Access:** HTTPS  |  **Format:** HGT  |  **Size:** 7 MB  |  **Login required:** ✅

**Key Variables:** `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- Static 2000-era snapshot; does not capture post-2000 elevation changes
- Voids over water and steep terrain; use NASADEM for void-filled version
- Trees/buildings captured in DSM — not bare-earth DTM

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="SRTMGL1",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `ASTGTM` — ASTER Global Digital Elevation Model V003

**concept_id:** `C1711961296-LPCLOUD`  |  **DOI:** 10.5067/ASTER/ASTGTM.003

**ML Use:** 30m ASTER GDEM v3 for topographic features, void-filled where SRTM has gaps

*The Terra Advanced Spaceborne Thermal Emission and Reflection Radiometer (ASTER) Global Digital Elevation Model (GDEM) Version 3 (ASTGTM) provides a global digital elevation model (DEM) of land areas *

**Access:** HTTPS  |  **Format:** COG  |  **Size:** 16.9 MB  |  **Login required:** ✅

**Key Variables:** `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- ASTER stereo-photogrammetry artifacts in cloudy regions; vertical accuracy ±17m RMSE
- Coarser accuracy than SRTM in flat areas

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="ASTGTM",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `NASADEM_HGT` — NASADEM Merged DEM Global 1 arc second V001

**concept_id:** `C2763264762-LPCLOUD`  |  **DOI:** 10.5067/MEASURES/NASADEM/NASADEM_HGT.001

**ML Use:** NASADEM improved SRTM void-filled DEM for hydrological routing, flood modeling, terrain ML

*The Land Processes Distributed Active Archive Center (LP DAAC) is responsible for the archive and distribution of the NASA Making Earth System Data Records for Use in Research Environments ([MEaSUREs]*

**Access:** HTTPS  |  **Format:** HGT  |  **Size:** 7.1 MB  |  **Login required:** ✅

**Key Variables:** `identifier_product_doi`, `identifier_product_doi_authority`

**⚠️ Gotchas:**
- Improved void-filling over SRTM but same 2000 vintage
- Still DSM not DTM; large forest canopy bias in height

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="NASADEM_HGT",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `GEDI02_B` — GEDI L2B Canopy Cover and Vertical Profile Metrics Data Global Footprint Level V

**concept_id:** `C3974616135-LPCLOUD`  |  **DOI:** 10.5067/GEDI/GEDI02_B.003

**ML Use:** GEDI 3D forest structure (canopy height, cover) for biomass estimation ML

*The Global Ecosystem Dynamics Investigation ([GEDI](https://gedi.umd.edu/)) mission aims to characterize ecosystem structure and dynamics to enable radically improved quantification and understanding *

**Access:** HTTPS  |  **Format:** HDF5  |  **Size:** 647.4 MB  |  **Login required:** ✅

**Key Variables:** `identifier_product_doi`, `identifier_product_doi_authority`, `Reference_Ground_Track`, `SEGMENT_NUMBER`

**⚠️ Gotchas:**
- Along-track footprint (~25m) data; requires spatial gridding for area analysis
- Only available between 51.6°N and 51.6°S (ISS orbit inclination)

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="GEDI02_B",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

### Human Dimensions / Population / Night Lights

**Topic:** Human Dimensions  |  **Category ID:** `cat_09_human`

| Short Name | Concept ID | Version | Prov | Cloud | Granules | Level | Time Range |
|------------|-----------|---------|------|-------|----------|-------|-----------|
| `VNP46A1` | `C2980666614-LAADS` | 2 | LAADS | ☁️ | 3,152,854 | 3 | 2012-01→ongoing |
| `VNP46A2` | `C3365931269-LAADS` | 2 | LAADS | ☁️ | 2,785,382 | 3 | 2012-01→ongoing |
| `CIESIN_SEDAC_GPWv4_POPDENS_R11` | `C3540910651-ESDIS` | 4.11 | ESDIS | 🖥️ | 54 | 4 | ?→ongoing |
| `VNP46A3` | `C3860061042-LAADS` | 2 | LAADS | ☁️ | 96,507 | 3 | 2012-01→ongoing |
| `VNP46A4` | `C3860065683-LAADS` | 2 | LAADS | ☁️ | 7,560 | 3 | 2012-01→ongoing |

#### `VNP46A1` — VIIRS/NPP Daily Gridded Day Night Band 15 arc-second Linear Lat Lon Grid Night V

**concept_id:** `C2980666614-LAADS`  |  **DOI:** 10.5067/VIIRS/VNP46A1.002


**ML Use:** Daily VIIRS nighttime light for urban growth mapping, infrastructure monitoring, power outage detection ML

*The VIIRS/NPP Daily Gridded Day Night Band 15 arc-second Linear Lat Lon Grid Night product, short-name VNP46A1 is a daily, top-of-atmosphere, at-sensor nighttime radiance product. This product is avai*

**Access:** OPeNDAP | HTTPS  |  **Format:** HDF5  |  **Size:** 40 MB  |  **Login required:** ✅

**Key Variables:** `TileId`, `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`

**⚠️ Gotchas:**
- Strongly affected by moonlight — apply lunar correction; use gap-filled VNP46A2 for monthly ML
- Annual and monthly versions also available (VNP46A3, VNP46A4)

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="VNP46A1",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `VNP46A2` — VIIRS/NPP Gap-Filled Lunar BRDF-Adjusted Nighttime Lights Daily L3 Global 15 arc

**concept_id:** `C3365931269-LAADS`  |  **DOI:** 10.5067/VIIRS/VNP46A2.002


**ML Use:** VIIRS gap-filled monthly nighttime light composites for socioeconomic proxy, urban ML, disaster impact

*The SNPP VIIRS Gap-Filled Lunar BRDF-Adjusted Nighttime Lights Daily L3 Global 15 arc-second Linear Lat Lon Grid product, short-name VNP46A2 is a daily moonlight- and atmosphere-corrected Nighttime Li*

**Access:** OPeNDAP | HTTPS  |  **Format:** HDF5  |  **Size:** 1.5 MB  |  **Login required:** ✅

**Key Variables:** `TileId`, `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`

**⚠️ Gotchas:**
- Gap-filled using temporal compositing; artifacts possible at cloud-persistent locations
- Attenuation correction applied; still not ideal in areas with persistent cloud cover

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="VNP46A2",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `CIESIN_SEDAC_GPWv4_POPDENS_R11` — Gridded Population of the World, Version 4 (GPWv4): Population Density, Revision

**concept_id:** `C3540910651-ESDIS`  |  **DOI:** 10.7927/H49C6VHW

**ML Use:** Global gridded population density v4.11 for exposure/vulnerability ML, disaster impact assessment

*The Gridded Population of the World, Version 4 (GPWv4): Population Density, Revision 11 consists of estimates of human population density (number of persons per square kilometer) based on counts consi*

**Access:** HTTPS  |  **Format:** ASCII  |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- 5-year snapshots (2000, 2005, 2010, 2015, 2020); no annual data
- 30 arc-second resolution; aggregation from census units may introduce spatial bias

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="CIESIN_SEDAC_GPWv4_POPDENS_R11",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `VNP46A3` — VIIRS/NPP Lunar BRDF-Adjusted Nighttime Lights Monthly L3 Global 15 arc second L

**concept_id:** `C3860061042-LAADS`  |  **DOI:** 10.5067/VIIRS/VNP46A3.002


**ML Use:** Monthly VIIRS nighttime light composites for urban growth tracking and economic activity ML

*The Suomi National Polar-orbiting Partnership (SNPP) Visible Infrared Imaging Radiometer Suite (VIIRS) supports a Day-Night Band (DNB) sensor that provides global daily measurements of nocturnal visib*

**Access:** HTTPS  |  **Format:** HDF5  |  **Size:** 12 MB  |  **Login required:** ✅

**Key Variables:** `TileId`, `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`

**⚠️ Gotchas:**
- Monthly gap-filled composites; seasonal variation in NTL (holiday, agricultural burning)
- Overglow/blooming effect near bright sources; not suitable for small-settlement detection

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="VNP46A3",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `VNP46A4` — VIIRS/NPP Lunar BRDF-Adjusted Nighttime Lights Yearly L3 Global 15 arc second Li

**concept_id:** `C3860065683-LAADS`  |  **DOI:** 10.5067/VIIRS/VNP46A4.002


**ML Use:** Annual VIIRS nighttime light for multi-year socioeconomic trend analysis, electrification mapping ML

*The Suomi National Polar-orbiting Partnership (SNPP) Visible Infrared Imaging Radiometer Suite (VIIRS) supports a Day-Night Band (DNB) sensor that provides global daily measurements of nocturnal visib*

**Access:** HTTPS  |  **Format:** HDF5  |  **Size:** 92 MB  |  **Login required:** ✅

**Key Variables:** `TileId`, `HORIZONTALTILENUMBER`, `VERTICALTILENUMBER`

**⚠️ Gotchas:**
- Annual averages smooth out short-term events; pair with daily VNP46A1 for event detection

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="VNP46A4",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

### Solid Earth / Hazards / Deformation / SAR

**Topic:** Solid Earth  |  **Category ID:** `cat_10_solid_earth`

| Short Name | Concept ID | Version | Prov | Cloud | Granules | Level | Time Range |
|------------|-----------|---------|------|-------|----------|-------|-----------|
| `EMITL2ARFL` | `C4079844428-LPCLOUD` | 002 | LPCLOUD | ☁️ | 135,705 | 2A | 2022-08→ongoing |
| `GEDI02_B` | `C3974616135-LPCLOUD` | 003 | LPCLOUD | ☁️ | 114,604 | 2B | 2024-04→ongoing |
| `OPERA_L3_DISP-S1_V1` | `C3294057315-ASF` | 1 | ASF | ☁️ | 205,761 | 3 | 2016-07→ongoing |
| `ARIA_S1_GUNW` | `C2859376221-ASF` | 1 | ASF | ☁️ | 470,824 | 2 | 2014-06→ongoing |
| `MSVOLSO2L4` | `C2027429276-GES_DISC` | 4 | GES_DISC | ☁️ | 1 | 4 | 1978-10→2026-05 |
| `SENTINEL-1A_SLC` | `C1214470488-ASF` | 1 | ASF | ☁️ | 2,140,803 | 1 | 2014-04→ongoing |

#### `EMITL2ARFL` — EMIT L2A Surface Reflectance and Uncertainty 60 m V002

**concept_id:** `C4079844428-LPCLOUD`  |  **DOI:** 10.5067/EMIT/EMITL2ARFL.002

**ML Use:** EMIT surface mineralogy/reflectance for geological mapping, mineral identification ML, dust source detection

*The Earth Surface Mineral Dust Source Investigation (EMIT) is an Earth Ventures-Instrument (EVI-4) Mission aboard the International Space Station (ISS). EMIT’s prime mission was designed to map surfac*

**Access:** HTTPS  |  **Format:** netCDF-4  |  **Size:** 3.8 GB  |  **Login required:** ✅

**Key Variables:** `SOFTWARE_BUILD_VERSION`, `identifier_product_doi`, `identifier_product_doi_authority`, `ORBIT`, `SCENE`, `SOLAR_ZENITH`

**⚠️ Gotchas:**
- ISS-based hyperspectral; non-uniform spatial coverage — not global gridded product
- 380 spectral bands; large file sizes; apply atmospheric correction mask before ML

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="EMITL2ARFL",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `GEDI02_B` — GEDI L2B Canopy Cover and Vertical Profile Metrics Data Global Footprint Level V

**concept_id:** `C3974616135-LPCLOUD`  |  **DOI:** 10.5067/GEDI/GEDI02_B.003

**ML Use:** GEDI 3D canopy structure for biomass estimation, forest degradation ML, carbon stock assessment

*The Global Ecosystem Dynamics Investigation ([GEDI](https://gedi.umd.edu/)) mission aims to characterize ecosystem structure and dynamics to enable radically improved quantification and understanding *

**Access:** HTTPS  |  **Format:** HDF5  |  **Size:** 647.4 MB  |  **Login required:** ✅

**Key Variables:** `identifier_product_doi`, `identifier_product_doi_authority`, `Reference_Ground_Track`, `SEGMENT_NUMBER`

**⚠️ Gotchas:**
- Along-track 25m footprint; not uniformly sampled grid; requires spatial aggregation
- Coverage limited to 51.6°N – 51.6°S (ISS orbit)

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="GEDI02_B",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `OPERA_L3_DISP-S1_V1` — OPERA Surface Displacement from Sentinel-1 validated product (Version 1)

**concept_id:** `C3294057315-ASF`  |  **DOI:** 10.5067/SNWG/OPL3DISPS1-V1

**ML Use:** OPERA Sentinel-1 surface displacement maps for subsidence detection ML, earthquake/volcano deformation monitoring

*The Level-3 OPERA Sentinel-1 Surface Displacement (DISP) product is generated through interferometric time-series analysis of Level-2 Coregistered Sentinel-1 Single Look Complex (CSLC) datasets. Using*

**Access:** HTTPS  |  **Format:** netCDF-4  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `POLARIZATION`, `PRODUCT_VERSION`, `PROCESSING_TYPE`, `FRAME_ID`, `STACK_ID`, `ASCENDING_DESCENDING`

**⚠️ Gotchas:**
- Validated product v1; check baseline date pairs for coherence
- Displacement relative to reference epoch — not absolute elevation change

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="OPERA_L3_DISP-S1_V1",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `ARIA_S1_GUNW` — ARIA Sentinel-1 Geocoded Unwrapped Interferograms

**concept_id:** `C2859376221-ASF`  |  **DOI:** 

**ML Use:** ARIA Sentinel-1 InSAR unwrapped interferograms for land deformation ML, infrastructure monitoring

*Level-2 interferometric products generated by the Jet Propulsion Lab (JPL) ARIA project. The creation, discovery, and distribution of these products support InSAR science around tectonically active re*

**Access:** HTTPS  |  **Format:** netCDF-4  |  **Size:**   |  **Login required:** ✅

**Key Variables:** `ASCENDING_DESCENDING`, `BEAM_MODE`, `POLARIZATION`, `PATH_NUMBER`, `PERPENDICULAR_BASELINE`, `VERSION`

**⚠️ Gotchas:**
- Requires phase unwrapping; atmospheric artifacts (tropospheric delay) must be corrected
- 12-day repeat; temporal decorrelation limits use in vegetated areas

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="ARIA_S1_GUNW",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `MSVOLSO2L4` — Multi-Satellite Volcanic Sulfur Dioxide L4 Long-Term Global Database V4 (MSVOLSO

**concept_id:** `C2027429276-GES_DISC`  |  **DOI:** 10.5067/MEASURES/SO2/DATA405

**ML Use:** Multi-satellite volcanic SO2 L4 for eruption detection, aviation hazard ML, atmospheric chemistry studies

*Version 4 is the current version of the data set. Older versions are no longer available and have been superseded by Version 4.

These data are a part of MEaSUREs 2012 projects. The particular project*

**Access:** HTTPS  |  **Format:**   |  **Size:**   |  **Login required:** ✅

**⚠️ Gotchas:**
- Event-based product — not uniform temporal sampling
- SO2 mass estimates uncertain for large eruptions that saturate sensors

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="MSVOLSO2L4",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

#### `SENTINEL-1A_SLC` — Sentinel-1A Single Look Complex Product

**concept_id:** `C1214470488-ASF`  |  **DOI:** 

**ML Use:** Sentinel-1A SAR SLC data for custom InSAR processing, change detection ML, flood mapping

*Sentinel-1A, the first satellite in the Sentinel-1 constellation, was launched April 3, 2014.  The Sentinel-1 satellites (Sentinel-1A, Sentinel-1B, and Sentinel-1C) are sun-synchronous polar-orbiting *

**Access:** HTTPS  |  **Format:**   |  **Size:**   |  **Login required:** ✅

**Key Variables:** `SV_POSITION_PRE`, `SV_VELOCITY_PRE`, `SV_POSITION_POST`, `SV_VELOCITY_POST`, `ASC_NODE_TIME`, `SV_START_POSITION`

**⚠️ Gotchas:**
- Raw SLC requires significant processing (focusing, coregistration, interferometry) before ML use
- Large file sizes (1-4 GB per scene); cloud processing recommended

<details>
<summary>earthaccess snippet</summary>

```python
import earthaccess
earthaccess.login(strategy="environment")
results = earthaccess.search_data(
    short_name="SENTINEL-1A_SLC",
    temporal=("2023-01-01", "2023-01-31"),
    bounding_box=(-10, 35, 10, 45),
    count=2
)
print(f"Found {len(results)} granules")
# files = earthaccess.open(results)  # stream without downloading
```

</details>

## ML Task Decision Guide

| ML Task | Primary Collection | Secondary | Join Key | Notes |
|---------|-------------------|-----------|----------|-------|
| Crop mapping / type classification | HLSL30 or HLSS30 | MCD12Q1 (labels) | lat/lon/date | 30m multi-spectral time series; apply Fmask QA; use 10+ bands |
| Vegetation health / drought monitoring | MOD13A2 (NDVI 16-day) | GPM_3IMERGDF + SPL4SMGP | lat/lon/date resampled to common grid | Anomaly detection: compare to climatology baseline |
| Wildfire risk prediction | MOD13A2 + MOD04_3K | MCD64A1 (labels) + GPM_3IMERGDF | lat/lon/week | Feature stack: NDVI, LST, precip, wind (MERRA-2), slope (SRTM) |
| Flood mapping / detection | SENTINEL-1A_SLC (SAR) | GPM_3IMERGDF + NASADEM_HGT | lat/lon/event date | SAR backscatter change detection; DEM for terrain routing |
| Air quality / PM2.5 estimation | MCD19A2 (MAIAC AOD) | M2T1NXSLV (met fields) | lat/lon/day | AOD→PM2.5 regression; add surface elevation (NASADEM) |
| Marine heatwave / coral bleaching risk | MUR-JPL-L4-GLOB-v4.1 (SST) | MODISA_L3m_CHL | lat/lon/week | SST anomaly from climatology; CHL as productivity stress proxy |
| Sea ice extent / area prediction | NSIDC-0051 (passive microwave) | M2T1NXSLV (surface temperature) | lat/lon/month | Classification or regression on ice fraction; temporal sequence for LSTM |
| Urban growth / light pollution mapping | VNP46A3 (monthly NTL) | CIESIN_SEDAC_GPWv4_POPDENS | lat/lon/year | Correlate NTL growth with population density changes |
| Land deformation / subsidence monitoring | OPERA_L3_DISP-S1_V1 (InSAR displacement) | ARIA_S1_GUNW (interferograms) | lat/lon/epoch-pair | Time-series InSAR; apply atmospheric correction; mask water |
| Glacier / ice sheet mass balance | ATL06 (ICESat-2 elevation) | TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4 (GRACE) | glacier RGI outline / monthly | Elevation differencing for mass balance; GRACE for basin-scale water loss |

---

*Generated 2026-11-15 by NASA catalogue builder. All concept_ids verified live against CMR API.*
