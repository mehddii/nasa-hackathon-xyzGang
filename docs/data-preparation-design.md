# Planetary Data Preparation Design

## Goal

Build two clean, analysis-ready datasets:

1. A Mars dataset for discovering homogeneous surface regions.
2. A Moon dataset for discovering homogeneous surface regions.

This is not a separate feasibility study. Dataset checks happen while each layer is loaded. If a file cannot be opened, geolocated, or interpreted, that layer fails immediately with a clear error.

## Why preparation is necessary

NASA PDS is an archive, not one combined table. Different instruments produce separate files with different projections, resolutions, units, coverage, and dates. We need to convert selected products into aligned layers before any segmentation or clustering is scientifically meaningful.

Preparation means:

- Downloading a small, curated set of suitable products.
- Reading their documented physical values.
- Reprojecting them onto a planet-specific grid.
- Aggregating fine data to the chosen analysis scale.
- Preserving masks, dates, resolution, and provenance.
- Exporting one feature table per planet.

It does not mean independently proving that NASA calibrated its instruments correctly.

## Access strategy

Use each service for the job it performs well:

| Service | Role |
|---|---|
| PDS Search API | Resolve known product/collection identifiers, labels, versions, file references, and provenance |
| PDS Geosciences Node | Download documented mission products and Software Interface Specifications |
| Orbital Data Explorer (ODE) | Search orbital observations by instrument and geography, especially for regional refinement |
| Instrument archives | Obtain products not consistently indexed by the federated API |

The pipeline must not depend on guessed PDS instrument identifiers. Known collection identifiers are stored in a versioned manifest. API queries resolve and verify those identifiers rather than trying to rediscover the scientific dataset on every run.

Official entry points:

- [PDS Search API](https://pds.nasa.gov/api/search/1/)
- [PDS Orbital Data Explorer](https://ode.rsl.wustl.edu/)
- [PDS MRO archive](https://pds-geosciences.wustl.edu/missions/mro/)
- [PDS MOLA archive](https://pds-geosciences.wustl.edu/missions/mgs/mola.html)
- [PDS LRO archive](https://pds-geosciences.wustl.edu/missions/lro/)

## Two-stage spatial strategy

### Stage A: broad discovery

Use global or near-global derived products at a defensible common scale. This prevents targeted high-resolution observations from defining the global clusters.

### Stage B: candidate refinement

After broad regions are discovered, retrieve higher-resolution observations that intersect those regions. These products validate landforms, boundaries, and alternative explanations.

High-resolution targeted data must not be used to estimate how common a process is across an entire planet.

## Mars preparation

### Broad-discovery layers

| Property | Primary product | Use |
|---|---|---|
| Elevation | MOLA Mission Experiment Gridded Data Record (MEGDR), preferably the maintained PDS4 topography-derived bundle | Elevation, slope, curvature, relief, basins, and drainage context |
| Thermal behavior | MGS TES derived thermal-inertia maps; THEMIS global products may supplement where their product definition is appropriate | Particle-size/rockiness proxy and thermal surface behavior |
| Surface composition | CRISM multispectral map or MRDR products with documented correction and quality masks | Broad mineral and hydration indicators |
| Hydrogen | Mars Odyssey GRS/HEND/Neutron Spectrometer derived maps | Coarse near-surface hydrogen evidence |
| Base morphology | A documented global controlled mosaic suitable for regional texture at its native effective resolution | Broad morphology and context only |

The MOLA MEGDR is a global topographic map derived from mission altimetry. The final product uses the IAU 2000 coordinate system. The loader must record the exact product version and coordinate definition.

### Regional-refinement layers

| Property | Instruments/products | Use |
|---|---|---|
| Detailed morphology | CTX calibrated/map-projected products | Dunes, channels, layers, craters, deposits, and boundaries |
| Very high-resolution morphology and change | HiRISE RDR and repeat observations | Small landforms and active surface change |
| Detailed mineralogy | CRISM TRDR and suitable derived products | Mineral associations and alteration evidence |
| Thermal detail | THEMIS IR products | Local thermal behavior |
| Subsurface | SHARAD radargrams and derived products | Subsurface layering and candidate buried ice |
| Atmospheric context | MARCI/MCS products | Dust and seasonal atmospheric context |

These products are searched geographically through Mars ODE or their mission archive after broad candidate regions exist.

### Mars output

`mars_regions_input.parquet` contains one row per temporary analysis cell:

- Cell identifier and geometry.
- Elevation.
- Slope, curvature, relief, and roughness at multiple scales.
- Thermal variables.
- Mineral/composition variables.
- Hydrogen variables at their true effective footprint.
- Base-image texture features.
- Per-property missing flags.
- Per-property source resolution.
- Product identifiers and versions.

Raster layers and masks are also retained separately so region boundaries can be reconstructed.

## Moon preparation

### Broad-discovery layers

| Property | Primary product | Use |
|---|---|---|
| Elevation | LOLA gridded digital elevation products from the calibrated/derived archive | Elevation, slope, curvature, relief, crater geometry, and illumination modeling |
| Base morphology | LROC WAC controlled/global mosaics | Broad morphology, albedo, and texture |
| Thermal behavior | Diviner GDR, global cumulative products, and polar resource products where applicable | Temperature cycles, thermal extremes, rock abundance, and cold-trap conditions |
| Hydrogen | LEND derived/gridded products | Coarse supporting evidence for hydrogen enrichment |
| Radar | Mini-RF global map-projected mosaics | Radar backscatter and polarization-sensitive surface information |

Official archive identifiers and versions must be resolved from the current LRO archive. Examples of maintained PDS4 bundles include `urn:nasa:pds:lro_lola_rdr`, `urn:nasa:pds:lro_lend`, and the Diviner derived bundles. Exact collection members are selected from their labels, not inferred from filenames.

### Regional-refinement layers

| Property | Instruments/products | Use |
|---|---|---|
| Detailed morphology | LROC NAC observations | Pits, blocks, ejecta, small craters, and slope features |
| Detailed topography | LOLA profiles and stereo-derived terrain products | Local terrain and shadow geometry |
| Polar thermal behavior | Diviner polar and high-resolution products | Temperature persistence and volatile-stability conditions |
| Volatile-related evidence | LEND, LAMP, LOLA reflectance, and Mini-RF | Independent supporting observations; no single layer confirms ice |
| Surface change | Co-registered repeat LROC observations | New impacts or slope change |

These products are searched geographically through Lunar ODE, the Planetary Image Atlas, or the instrument archive after broad candidate regions exist.

### Moon output

`moon_regions_input.parquet` contains:

- Cell identifier and geometry.
- Elevation.
- Slope, curvature, relief, and roughness at multiple scales.
- Temperature-cycle and extreme-temperature variables.
- LROC WAC texture/albedo variables.
- LEND values with native-footprint information.
- Mini-RF variables where coverage exists.
- Illumination/shadow variables where calculated.
- Missing flags, source resolution, acquisition context, and provenance.

## Grid and resolution rules

Mars and Moon use separate coordinate systems and grids.

1. Choose the broad analysis resolution from the coarsest required core layer, not the sharpest image.
2. Aggregate fine products using documented statistics.
3. Never sharpen coarse LEND, GRS, or radar measurements and treat the interpolated pixels as independent evidence.
4. Store each layer's native and effective resolution.
5. Run later region discovery at several legitimate scales rather than claiming one universal smallest region.
6. Keep polar projections separate when a global cylindrical grid produces severe distortion.

## Required loader checks

Each loader performs only checks needed to prevent corrupted analysis:

- HTTP request succeeded and checksum matches when provided.
- File and label can be opened.
- Product identifier and version match the manifest.
- Units and fill values are known.
- Valid-range and quality masks are applied.
- Coordinate system and longitude convention are explicit.
- Values fall within documented ranges.
- Reprojection preserves location and masks.
- Output resolution does not exceed the source's effective resolution.

A failed check stops that layer. It does not produce a global verdict that the instrument or archive is unusable.

## Provenance manifest

Every prepared layer must have a manifest entry containing:

- Planet.
- Property name.
- Mission and instrument.
- PDS bundle, collection, and product identifiers.
- Product version.
- Product level: raw, calibrated, or derived.
- Source URL.
- Checksum.
- Units.
- Native and effective resolution.
- Coordinate reference and longitude convention.
- Acquisition date or time range.
- Processing steps.
- Output path.

## Notebook organization

### `01_mars_data_preparation.ipynb`

1. Resolve the curated Mars manifest through PDS.
2. Download global core layers under explicit limits.
3. Read and mask products.
4. Reproject and aggregate them.
5. Calculate Mars terrain and texture features.
6. Export Mars rasters, masks, provenance, and `mars_regions_input.parquet`.
7. Show coverage and missingness maps.

### `02_moon_data_preparation.ipynb`

1. Resolve the curated Moon manifest.
2. Download global core layers.
3. Read and mask products.
4. Build global and polar grids.
5. Calculate terrain, thermal, illumination, and texture features.
6. Export Moon rasters, masks, provenance, and `moon_regions_input.parquet`.
7. Show coverage and missingness maps.

### Regional download modules

Regional high-resolution retrieval should be reusable Python code called by later notebooks, not duplicated in exploratory cells. Inputs are planet, region geometry, instrument/product type, date constraints, resolution, and byte limit. Outputs include files plus a provenance manifest.

## Completion criteria

Mars preparation is complete when its core global layers align, retain provenance and uncertainty, and produce a usable feature table without false high-resolution fusion.

Moon preparation is complete when its global and polar layers align, retain provenance and uncertainty, and produce a usable feature table without treating supporting hydrogen/radar signals as proof of ice.

Process discovery begins only from these prepared outputs. There is no separate feasibility verdict stage.

