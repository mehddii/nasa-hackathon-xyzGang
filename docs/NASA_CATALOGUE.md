# Verified NASA Earthdata collection inventory

**55 unique collections · audited against NASA CMR on 2026-11-15**

This is a discovery list for the later Earth stage. It is **not** a ready-made feature schema and does not prove that every product is relevant to our Mars/Moon analogue search.

The teammate contribution contained valid collection identifiers, but its generated processing advice mixed metadata with science variables and included unsafe generalizations. Those recipes were removed. Before using a collection, we must check its official product guide for measurements, units, scale factors, quality flags, resolution, and access method.

The machine-readable version is [`nasa_catalogue.json`](nasa_catalogue.json).

## How to verify one entry

No package is required for metadata lookup:

```python
import json, urllib.request

concept_id = "C2327962326-LPCLOUD"
url = f"https://cmr.earthdata.nasa.gov/search/concepts/{concept_id}.umm_json"
with urllib.request.urlopen(url) as response:
    metadata = json.load(response)
```

## Land Cover / Vegetation / NDVI / Crops

Topic: Land Surface

| Short name | Version | Level | Provider | Time | CMR |
|---|---:|---:|---|---|---|
| `MOD13A3` | 061 | 3 | LPCLOUD | 2000-02-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2327962326-LPCLOUD) |
| `MOD13A2` | 061 | 3 | LPCLOUD | 2000-02-18 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2565788905-LPCLOUD) |
| `MOD13Q1` | 061 | 3 | LPCLOUD | 2000-02-18 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C1748066515-LPCLOUD) |
| `VNP13A1` | 002 | 3 | LPCLOUD | 2012-01-17 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2519127224-LPCLOUD) |
| `HLSL30` | 2.0 | 3 | LPCLOUD | 2013-04-11 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2021957657-LPCLOUD) |
| `HLSS30` | 2.0 | 3 | LPCLOUD | 2015-11-28 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2021957295-LPCLOUD) |
| `MCD12Q1` | 061 | 3 | LPCLOUD | 2001-01-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2484079608-LPCLOUD) |
| `MYD13A2` | 061 | 3 | LPCLOUD | 2002-07-04 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2565794049-LPCLOUD) |

## Active Fires / Burned Area / Wildfire Risk

Topic: Fire & Burned Area

| Short name | Version | Level | Provider | Time | CMR |
|---|---:|---:|---|---|---|
| `MOD14A2` | 061 | 3 | LPCLOUD | 2000-02-18 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2565791018-LPCLOUD) |
| `MCD64A1` | 061 | 3 | LPCLOUD | 2000-11-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2565786756-LPCLOUD) |
| `VNP64A1` | 002 | 4 | LPCLOUD | 2012-03-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2847928673-LPCLOUD) |
| `MCD14DL` | 6.1NRT | 2 | LANCEMODIS | 2019-12-15 → — | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2105705664-LANCEMODIS) |

## Precipitation / Floods / Drought / Soil Moisture

Topic: Hydrology

| Short name | Version | Level | Provider | Time | CMR |
|---|---:|---:|---|---|---|
| `GPM_3IMERGDF` | 07 | 3 | GES_DISC | 1998-01-01 → 2025-09-30 | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2723754864-GES_DISC) |
| `GPM_3IMERGHH` | 07 | 3 | GES_DISC | 1998-01-01 → 2025-09-30 | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2723754847-GES_DISC) |
| `SPL3SMP` | 009 | 3 | NSIDC_CPRD | 2015-03-31 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2938664585-NSIDC_CPRD) |
| `SPL4SMGP` | 008 | 4 | NSIDC_CPRD | 2015-03-31 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3480440870-NSIDC_CPRD) |
| `TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4` | RL06.3Mv04 | 3 | POCLOUD | 2002-04-04 → — | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3195527175-POCLOUD) |
| `TELLUS_GRFO_L3_CSR_RL06.3_LND_v04` | RL06.3v04 | 3 | POCLOUD | 2018-05-22 → — | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3193285193-POCLOUD) |

## Temperature / Land Surface / Climate Reanalysis

Topic: Temperature & Climate

| Short name | Version | Level | Provider | Time | CMR |
|---|---:|---:|---|---|---|
| `M2T1NXSLV` | 5.12.4 | 4 | GES_DISC | 1980-01-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C1276812863-GES_DISC) |
| `M2SDNXSLV` | 5.12.4 | 4 | GES_DISC | 1980-01-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C1276812843-GES_DISC) |
| `GLDAS_NOAH025_3H` | 2.1 | 4 | GES_DISC | 2000-01-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C1342986035-GES_DISC) |
| `GLDAS_NOAH025_M` | 2.1 | 4 | GES_DISC | 2000-01-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C1342986036-GES_DISC) |

## Air Quality / Aerosols / Atmospheric Composition

Topic: Atmosphere

| Short name | Version | Level | Provider | Time | CMR |
|---|---:|---:|---|---|---|
| `OMNO2d` | 004 | 3 | GES_DISC | 2004-10-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3333493715-GES_DISC) |
| `OMSO2G` | 003 | 2G | GES_DISC | 2004-10-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C1266136113-GES_DISC) |
| `MOD04_3K` | 6.1 | 2 | LAADS | 2000-02-24 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C1443420430-LAADS) |
| `MYD04_3K` | 6.1 | 2 | LAADS | 2002-07-04 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C1443528505-LAADS) |
| `M2T1NXAER` | 5.12.4 | 4 | GES_DISC | 1980-01-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C1276812830-GES_DISC) |
| `S5P_L2__NO2____HiR` | 2 | 2 | GES_DISC | 2018-04-30 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2089270961-GES_DISC) |
| `MCD19A2` | 061 | 2G | LPCLOUD | 2000-02-24 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2324689816-LPCLOUD) |

## Oceans / Sea Surface Temperature / Ocean Color

Topic: Ocean

| Short name | Version | Level | Provider | Time | CMR |
|---|---:|---:|---|---|---|
| `MUR-JPL-L4-GLOB-v4.1` | 4.1 | 4 | POCLOUD | 2002-05-31 → — | [record](https://cmr.earthdata.nasa.gov/search/concepts/C1996881146-POCLOUD) |
| `MUR25-JPL-L4-GLOB-v04.2` | 4.2 | 4 | POCLOUD | 2002-08-31 → — | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2036880657-POCLOUD) |
| `MODISA_L3m_CHL` | 2022.0 | 3 | OB_CLOUD | 2002-07-04 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3380709133-OB_CLOUD) |
| `SWOT_L2_LR_SSH_D` | D | 2 | POCLOUD | 2022-12-16 → — | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3233945000-POCLOUD) |
| `MODISA_L2_OC` | 2022.0 | 2 | OB_CLOUD | 2002-07-04 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3380708980-OB_CLOUD) |

## Cryosphere / Snow / Sea Ice / Ice Sheets / Glaciers

Topic: Cryosphere

| Short name | Version | Level | Provider | Time | CMR |
|---|---:|---:|---|---|---|
| `MOD10CM` | 61 | 3 | NSIDC_CPRD | 2000-03-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3050353608-NSIDC_CPRD) |
| `NSIDC-0079` | 4 | 3 | NSIDC_CPRD | 1978-11-01 → 2025-12-31 | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3177837864-NSIDC_CPRD) |
| `NSIDC-0051` | 2 | 3 | NSIDC_CPRD | 1978-10-26 → 2025-12-31 | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3177837840-NSIDC_CPRD) |
| `ATL09` | 007 | 3 | NSIDC_CPRD | 2018-10-13 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3578753623-NSIDC_CPRD) |
| `MYD10CM` | 61 | 3 | NSIDC_CPRD | 2002-07-04 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3091267534-NSIDC_CPRD) |
| `NISE` | 5 | 3 | NSIDC_CPRD | 2016-12-01 → 2026-01-16 | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3177837670-NSIDC_CPRD) |
| `ATL06` | 007 | 3 | NSIDC_CPRD | 2018-10-14 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3564876127-NSIDC_CPRD) |

## Elevation / Terrain / 3D Structure

Topic: Terrain

| Short name | Version | Level | Provider | Time | CMR |
|---|---:|---:|---|---|---|
| `SRTMGL1` | 003 | 3 | LPCLOUD | 2000-02-11 → 2000-02-21 | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2763266360-LPCLOUD) |
| `ASTGTM` | 003 | 3 | LPCLOUD | 2000-03-01 → 2013-11-30 | [record](https://cmr.earthdata.nasa.gov/search/concepts/C1711961296-LPCLOUD) |
| `NASADEM_HGT` | 001 | 3 | LPCLOUD | 2000-02-11 → 2000-02-21 | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2763264762-LPCLOUD) |
| `GEDI02_B` | 003 | 2B | LPCLOUD | 2019-04-04 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3974616135-LPCLOUD) |

## Human Dimensions / Population / Night Lights

Topic: Human Dimensions

| Short name | Version | Level | Provider | Time | CMR |
|---|---:|---:|---|---|---|
| `VNP46A1` | 2 | 3 | LAADS | 2012-01-19 → — | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2980666614-LAADS) |
| `VNP46A2` | 2 | 3 | LAADS | 2012-01-19 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3365931269-LAADS) |
| `CIESIN_SEDAC_GPWv4_POPDENS_R11` | 4.11 | 4 | ESDIS | — → — | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3540910651-ESDIS) |
| `VNP46A3` | 2 | 3 | LAADS | 2012-01-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3860061042-LAADS) |
| `VNP46A4` | 2 | 3 | LAADS | 2012-01-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3860065683-LAADS) |

## Solid Earth / Hazards / Deformation / SAR

Topic: Solid Earth

| Short name | Version | Level | Provider | Time | CMR |
|---|---:|---:|---|---|---|
| `EMITL2ARFL` | 002 | 2A | LPCLOUD | 2022-08-09 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C4079844428-LPCLOUD) |
| `OPERA_L3_DISP-S1_V1` | 1 | 3 | ASF | 2016-07-01 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C3294057315-ASF) |
| `ARIA_S1_GUNW` | 1 | 2 | ASF | 2014-06-15 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2859376221-ASF) |
| `MSVOLSO2L4` | 4 | 4 | GES_DISC | 1978-10-31 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C2027429276-GES_DISC) |
| `SENTINEL-1A_SLC` | 1 | 1 | ASF | 2014-04-03 → ongoing | [record](https://cmr.earthdata.nasa.gov/search/concepts/C1214470488-ASF) |
