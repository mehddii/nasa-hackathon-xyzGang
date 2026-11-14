# Data Feasibility and Coverage Study

## Status

Proposed design for the first production notebook.

## Purpose

Before downloading large planetary datasets or training clustering models, determine which Moon and Mars properties can actually be obtained, aligned, and compared at useful spatial and temporal scales.

This study answers one question:

> Do the available PDS products provide enough overlapping, scientifically meaningful measurements to support homogeneous-region discovery and process interpretation?

The study does not identify planetary processes and does not search Earth.

## Decisions this study must support

For each planet, the study must decide:

1. Which measured properties can be used.
2. Which datasets and product levels are appropriate.
3. Where the datasets overlap geographically.
4. What common analysis resolutions are scientifically defensible.
5. Which process hypotheses are feasible with the available evidence.
6. Which hypotheses must be postponed or rejected.
7. How much storage, download time, memory, and preprocessing are required.

Moon and Mars must be evaluated separately. Their measurements must not be placed into a shared feature table during this study.

## Non-goals

- Inferring processes from keyword frequency.
- Clustering planetary regions.
- Classifying individual images.
- Building Earth similarity scores.
- Downloading every PDS observation.
- Treating metadata records as scientific measurements.
- Upsampling coarse measurements and presenting them as high-resolution evidence.

## Conceptual data levels

The implementation must distinguish these levels:

1. **Catalog metadata:** product identifiers, mission, instrument, time, location, processing level, file links and provenance.
2. **Raw observations:** detector output that may require calibration.
3. **Calibrated observations:** physically meaningful radiance, reflectance, temperature, elevation, radar power or related quantities.
4. **Derived products:** mosaics, digital elevation models, mineral maps, thermal inertia, hydrogen abundance or other interpreted variables.
5. **Analysis features:** statistics calculated from calibrated or derived products for later region discovery.

Only levels 3 and 4 should normally enter the later process-discovery pipeline. Raw data should be selected only when no suitable calibrated product exists and the required calibration is understood.

## Candidate property inventory

The study begins with the following candidate measurements. Availability and suitability must be verified from product labels and documentation.

### Mars

| Property | Candidate instruments/products | Intended use |
|---|---|---|
| Visible morphology and texture | CTX, HiRISE, THEMIS VIS | Dunes, channels, craters, layers, deposits and surface change |
| Elevation and terrain derivatives | MOLA, HRSC or stereo DEM products | Elevation, slope, curvature, drainage, basin shape and roughness |
| Surface temperature and thermal behavior | THEMIS IR | Temperature, thermal inertia proxies, rock/dust differences |
| Mineral and hydration signatures | CRISM | Clays, sulfates, hydrated minerals and mafic minerals |
| Shallow subsurface structure | SHARAD | Layering and candidate buried ice |
| Atmospheric and surface dust context | MARCI, MCS | Dust storms, clouds, seasonal context and atmospheric temperature |
| Hydrogen or elemental indicators | Mars Odyssey GRS/HEND/NS products | Near-surface hydrogen and broad composition |
| Time | Repeated observations and acquisition metadata | Active change versus preserved landforms |

### Moon

| Property | Candidate instruments/products | Intended use |
|---|---|---|
| Visible morphology and texture | LROC NAC/WAC | Craters, ejecta, boulders, pits, landslides and surface change |
| Elevation and terrain derivatives | LOLA and stereo DEM products | Elevation, slope, curvature, illumination geometry and roughness |
| Surface temperature and thermal behavior | Diviner | Thermal extremes, cold-trap stability and rock abundance |
| Radar response | Mini-RF | Backscatter, polarization and roughness-sensitive evidence |
| Neutron response | LEND | Hydrogen-sensitive evidence at its native footprint |
| Ultraviolet reflectance | LAMP | Supporting evidence for surface frost or volatile-related behavior |
| Laser reflectance | LOLA | Supporting reflectance measurements |
| Illumination and shadow | LOLA-derived geometry and time-dependent illumination products | Permanent shadow and illumination availability |
| Time | Repeated observations and acquisition metadata | Surface change and measurement context |

## Notebook architecture

The notebook should be named `01_pds_data_feasibility.ipynb` and contain the following stages.

### 1. Configuration

All limits must be explicit and editable:

- Planet under study.
- Missions and instruments.
- Geographic test areas.
- Metadata page limit.
- Maximum files and bytes to download.
- Accepted processing levels.
- Cache directory.
- Request timeout and retry policy.

Internet access and free disk space must be checked before queries begin.

### 2. PDS catalog inventory

Use the PDS Search API to retrieve product and collection metadata. Capture:

- Logical and versioned identifiers.
- Planet, mission, instrument and product class.
- Processing level.
- Start and stop time.
- Spatial bounds when available.
- Map projection and coordinate convention when available.
- Pixel scale or footprint.
- File format, file size and download location.
- Parent collection and bundle.
- Product version and update time.
- PDS node and archive provenance.

The API response must be cached. Failed queries must be recorded rather than silently converted into empty results.

### 3. Collection-level documentation audit

For each candidate collection, record:

- What physical quantity is measured.
- Units.
- Calibration level.
- Valid range and fill values.
- Spatial resolution and actual footprint.
- Temporal sampling.
- Geographic coverage.
- Known artifacts and quality flags.
- Coordinate reference system.
- Recommended software or reader.
- Citation and documentation link.

This stage requires reading collection labels and instrument documentation. Field names must not be guessed from filenames.

### 4. Representative downloads

Download a small but diverse sample from each viable collection:

- One ordinary mid-latitude observation.
- One high-latitude observation where applicable.
- One observation from a known geological target.
- Repeated observations where temporal analysis is proposed.
- At least one product containing missing or low-quality data.

Enforce byte limits before downloading. Verify checksums when provided.

### 5. File and measurement validation

For every downloaded product, test:

- The file can be opened programmatically.
- Shape, data type, band count and units are understood.
- No-data values and quality masks are applied.
- Coordinates map to the documented location.
- Value ranges are physically plausible.
- A quick-look visualization matches the browse product when available.
- Metadata and data files remain linked by product identifier.

### 6. Coverage analysis

Represent every usable observation as a geographic footprint. Produce separate Moon and Mars coverage maps showing:

- Total coverage by property.
- Number of repeat observations.
- Effective resolution.
- Missing-data fraction.
- Overlap between required property combinations.

Coverage must be area-weighted. Counting products is not a substitute for measuring covered surface area.

### 7. Resolution and scale analysis

Create a resolution matrix for every property. Determine:

- Native resolution.
- Effective footprint or point-spread scale.
- Candidate analysis resolutions.
- Whether aggregation is required.
- Whether a measurement is too coarse for a proposed process.

Fine products may be aggregated to a coarser analysis scale. Coarse products must not be treated as if they reveal fine structures after interpolation.

### 8. Overlap and missingness analysis

For each proposed evidence combination, calculate:

- Surface area with all required measurements.
- Surface area with supporting measurements.
- Missingness pattern.
- Geographic and latitude bias.
- Mission-targeting bias.
- Temporal mismatch between observations.

Missingness must be stored as information. It must not be filled with zero, because zero may represent a real physical measurement.

### 9. Compute and storage estimate

Estimate for a pilot and a scaled run:

- Number of source products.
- Compressed and expanded bytes.
- Download duration.
- Reprojection time.
- Expected raster dimensions.
- CPU memory and GPU memory requirements.
- Cache and intermediate-storage requirements.

The estimate should target Kaggle constraints and identify work that requires offline preprocessing or cloud object storage.

### 10. Feasibility decision

Produce a decision table for every candidate property and process hypothesis:

| Decision | Meaning |
|---|---|
| Accept | Required measurements exist with sufficient overlap and documented quality |
| Pilot only | Evidence exists, but coverage or scale restricts it to selected regions |
| Supporting only | Measurement may support an interpretation but cannot establish it |
| Reject | Required data, overlap, resolution or validation is insufficient |

Every decision must include a reason and supporting collection identifiers.

## Geographic test strategy

The feasibility study should not begin globally. Use test regions selected for methodological coverage, not only famous positive examples:

1. A known positive region for a candidate process.
2. A plausible negative or control region.
3. A region with strong multi-instrument overlap.
4. A region with sparse or mismatched coverage.
5. A polar region where applicable.

Known positives confirm that the pipeline can recover expected measurements. Controls expose false positives. Sparse regions reveal how the method fails.

## Output files

The notebook must create:

- `catalog_inventory.parquet`
- `collection_audit.csv`
- `product_footprints.geoparquet`
- `property_coverage_summary.csv`
- `resolution_matrix.csv`
- `evidence_overlap_summary.csv`
- `download_manifest.csv`
- `feasibility_decisions.csv`
- `compute_storage_estimate.json`
- `feasibility_report.md`

The report must summarize Moon and Mars separately.

## Quality controls

- Preserve PDS identifiers and versions through every transformation.
- Record every query and download failure.
- Check coordinate longitude conventions and latitude definitions.
- Detect footprints crossing the longitude seam.
- Use area-correct calculations on planetary bodies.
- Compare a sample against official viewers or browse products.
- Verify units before combining variables.
- Keep raw, calibrated and derived products distinguishable.
- Store checksums and acquisition dates.
- Make all sampling deterministic with recorded random seeds.

## Known risks

### Catalog incompleteness

The federated search API may not expose all archived products or consistent spatial fields. Mitigation: use collection-specific archives or PDS node services when required, while preserving PDS identifiers.

### Targeting bias

High-resolution instruments often observe already-interesting locations. Mitigation: map observation density and avoid treating the observed sample as a random sample of the planet.

### Resolution incompatibility

Some measurements represent metres and others kilometres. Mitigation: define separate analysis scales and prohibit false high-resolution fusion.

### Temporal incompatibility

Measurements may be separated by years or seasons. Mitigation: store acquisition time and define allowed temporal windows per hypothesis.

### Format complexity

PDS products may require specialized readers and label interpretation. Mitigation: validate representative files before planning bulk downloads.

### Kaggle limits

Global high-resolution processing may exceed notebook disk and runtime. Mitigation: use the notebook for inventories and pilots, then precompute stable intermediate products where necessary.

## Acceptance criteria

The feasibility phase is complete only when:

1. Every proposed input property has an identified collection and physical meaning.
2. Representative files open successfully and pass coordinate and value checks.
3. Spatial coverage and overlap are measured by area.
4. Resolutions and temporal sampling are documented.
5. Missingness and targeting bias are quantified.
6. At least one positive and one control region are tested per accepted hypothesis family.
7. Compute and storage estimates fit an explicit execution environment.
8. Every candidate hypothesis has an Accept, Pilot only, Supporting only or Reject decision.
9. The process-discovery design is updated to use only feasible measurements.

## Exit gate

Do not begin large-scale segmentation or clustering until the acceptance criteria pass. If no useful multi-property overlap exists globally, the next phase must operate on several well-covered regional studies rather than claim global process discovery.

