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

## Four-notebook contract

| Notebook | Owns | Does not own |
|---|---|---|
| `01_mars_data_preparation.ipynb` | Mars download, cleaning, multiscale grids, normalization, neutral features, PCA/embeddings, cell-level export | Regions, clustering, anomalies, process labels |
| `02_moon_data_preparation.ipynb` | Moon download, cleaning, multiscale grids, normalization, neutral features, PCA/embeddings, cell-level export | Regions, clustering, anomalies, process labels |
| `03_mars_region_discovery.ipynb` | Connected Mars regions, region summaries, clustering, anomaly detection, artifact tests, scientific interpretation | Source-data calibration |
| `04_moon_region_discovery.ipynb` | Connected Moon regions, region summaries, clustering, anomaly detection, artifact tests, scientific interpretation | Source-data calibration |

The preparation notebooks export temporary geographic cells. A cell is only a numerical support area. It is not yet a homogeneous scientific region.

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

`mars_cells_input.parquet` contains one row per temporary analysis cell and scale:

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

`moon_cells_input.parquet` contains one row per temporary analysis cell and scale:

- Cell identifier and geometry.
- Elevation.
- Slope, curvature, relief, and roughness at multiple scales.
- Temperature-cycle and extreme-temperature variables.
- LROC WAC texture/albedo variables.
- LEND values with native-footprint information.
- Mini-RF variables where coverage exists.
- Illumination/shadow variables where calculated.
- Missing flags, source resolution, acquisition context, and provenance.

## Neutral clustering representations

Preparation preserves the original downloaded products and creates cluster-friendly representations without encoding process labels such as volcano, river, or ice.

### Direct physical variables

Keep understandable measurements in their documented units, including elevation, temperature, reflectance, hydrogen-sensitive measurements, radar values, and validated mineral indicators.

### Neutral derived variables

Calculate general properties useful across many possible processes:

- Slope, curvature, relief, and roughness from elevation.
- Mean, spread, range, and gradients of physical measurements.
- Temperature variation when observations support it.
- Image texture, edge density, and directional texture.
- Observation count, missingness, source resolution, and uncertainty.

These describe the surface without assigning a process.

### Numeric scaling

Store unscaled values and a separate model-ready version. Fit scaling parameters on the training geography only. Candidate methods are robust scaling for variables with outliers and standard scaling for approximately symmetric variables. Scaling parameters are saved and reused; they are not recomputed on evaluation regions.

### Spectral compression

Use PCA first for high-dimensional mineral spectra because its components and explained variance can be inspected. Select the component count from reconstruction/explained-variance results rather than a fixed guess. Preserve the original quality-masked spectra outside the clustering table.

An autoencoder is considered only if PCA reconstruction removes important spectral structure. It must be compared with PCA using held-out reconstruction, stability of downstream clusters, and interpretability. An autoencoder is not automatically preferred because GPUs are available.

### Image representation

Do not place every raw image pixel into the clustering table. Create patch-level texture summaries and image embeddings using a documented encoder. Store patch location, ground resolution, illumination/acquisition metadata, and the encoder version. Compare embeddings with simpler texture features so an opaque representation is retained only when it provides stable additional information.

### Multiple resolutions

Create separate coarse, medium, and fine feature views. Do not copy a coarse hydrogen or neutron value into thousands of fine image cells and count those cells as independent measurements.

- Coarse view: broad regional measurements such as hydrogen-sensitive maps and global context.
- Medium view: terrain, thermal behavior, composition, and global imagery.
- Fine view: targeted detailed imagery and local products used later for refinement.

Each row records the source footprint or parent coarse cell. Cross-scale evidence is combined during region interpretation, not by pretending all measurements have the same resolution.

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
3. Preserve source files, labels, checksums, and provenance.
4. Read documented measurements and apply quality/fill-value masks.
5. Correct documented acquisition effects and retain acquisition metadata.
6. Build separate coarse and medium Mars grids; reserve fine products for regional refinement.
7. Reproject and aggregate without exceeding effective source resolution.
8. Calculate neutral terrain, thermal, statistical, and texture features.
9. Normalize numeric features and fit PCA for spectra; benchmark image embeddings against simple texture features.
10. Export rasters, masks, fitted transforms, provenance, and `mars_cells_input.parquet`.
11. Show coverage, missingness, resolution, and value-distribution diagnostics.

### `02_moon_data_preparation.ipynb`

1. Resolve the curated Moon manifest.
2. Download global core layers.
3. Preserve source files, labels, checksums, and provenance.
4. Read documented measurements and apply quality/fill-value masks.
5. Correct documented acquisition effects and retain acquisition metadata.
6. Build separate global, polar, coarse, and medium views; reserve fine products for regional refinement.
7. Reproject and aggregate without exceeding effective source resolution.
8. Calculate neutral terrain, thermal, illumination, statistical, and texture features.
9. Normalize numeric features and fit PCA/embeddings where dimensionality requires them.
10. Export rasters, masks, fitted transforms, provenance, and `moon_cells_input.parquet`.
11. Show coverage, missingness, resolution, and value-distribution diagnostics.

### Regional download modules

Regional high-resolution retrieval should be reusable Python code called by later notebooks, not duplicated in exploratory cells. Inputs are planet, region geometry, instrument/product type, date constraints, resolution, and byte limit. Outputs include files plus a provenance manifest.

## Completion criteria

Mars preparation is complete when its core global layers align, retain provenance and uncertainty, and produce a usable cell-level feature table without false high-resolution fusion. Direct values, compressed values, scale identifiers, acquisition context, and missingness must remain distinguishable.

Moon preparation is complete when its global and polar layers align, retain provenance and uncertainty, and produce a usable cell-level feature table without treating supporting hydrogen/radar signals as proof of ice. Direct values, compressed values, scale identifiers, acquisition context, and missingness must remain distinguishable.

Process discovery begins only from these prepared outputs. There is no separate feasibility verdict stage.
