# Homogeneous Regions and Planetary Process Discovery

## Goal

Use the prepared Mars and Moon datasets to discover connected regions with similar measured properties, then interpret those regions using scientific evidence combinations.

Mars and Moon are processed independently. Their clusters are never mixed.

## Key distinction

- **Property:** measured value such as elevation, temperature, reflectance, or neutron count.
- **Environment:** combination such as cold, shadowed, and hydrogen-enriched terrain.
- **Landform:** visible structure such as a dune, channel, crater, or pit.
- **Process:** mechanism such as aeolian transport, fluvial deposition, impact excavation, or mass wasting.
- **Activity status:** active, recent, past, unknown, or not applicable.

Clustering discovers recurring property combinations. It does not prove their cause.

## Inputs

- `mars_cells_input.parquet` and aligned Mars rasters/masks.
- `moon_cells_input.parquet` and aligned Moon rasters/masks.
- Provenance manifests.
- Literature-backed evidence recipes.
- Known positive and negative control locations.

## Mars broad-discovery implementation

`03_mars_region_discovery.ipynb` implements the broad global stage as follows:

1. Analyse each physical scale and compatible coverage cohort separately.
2. Quantize complete science-feature groups into area-weighted property prototypes, split them into four-neighbor connected components with longitude wrapping, then merge only adjacent tiny components whose science representations are sufficiently similar.
3. Summarize every connected region with surface-area-weighted physical values, model-space values, quality context, area, perimeter, internal variation, adjacency, and parent/child scale links.
4. Remove the regularized linear effect of acquisition-quality variables from the clustering representation while preserving the original physical measurements, then compare K-means, diagonal Gaussian mixtures, and HDBSCAN using geographic-fold stability, silhouette separation, and assigned coverage.
5. Run Isolation Forest anomaly screening, coverage-only cluster prediction, and science-family ablations. Anomalies from tiny, limited-feature, or artifact-dominated regions remain recorded but are not promoted to the review shortlist.
6. Preserve neutral type identifiers, then apply four conservative screening recipes to individual connected regions: mafic igneous material, water/hydrothermal alteration, dust or loose material, and hydrogen-enriched subsurface environments. Robust map candidates require direct and independent supporting evidence and exclude artifact-dominated, single-family-only, and unresolved tiny regions.

The screening recipes explicitly retain missing confirmation evidence and alternative explanations. Broad neutral clusters are not painted as processes; recipe evidence is localized to the regions that actually satisfy it. The recipes do not establish current activity, and they do not replace targeted CTX/HiRISE, CRISM, THEMIS, SHARAD, or repeat-observation refinement.

A coverage cohort with at least two usable features may still support descriptive segmentation and neutral clustering. If those features come from only one science family, its regions and recipe results are explicitly marked `limited_feature_evidence`; they are not treated as strong multi-property process evidence.

The Mars notebook sets `earth_filter_handoff_ready` only when robust candidates exist, no partition retains more than 20% unresolved tiny regions, and at least 40% of the reference locations recover an expected broad screening category. A completed run is therefore not automatically considered scientifically ready.

## Step 1 — Multiscale homogeneous regions

A homogeneous region is a connected area whose selected properties vary within stated tolerances at a stated spatial scale.

There is no universal smallest region. A region can be thermally uniform but contain several mineral or morphology units. The pipeline therefore creates a hierarchy:

1. Start with temporary computation cells.
2. Detect strong boundaries in terrain, thermal behavior, composition, and texture.
3. Create fine connected segments.
4. Merge adjacent segments with sufficiently similar properties.
5. Repeat at several defensible scales.
6. Link fine regions to broader parent regions.

Each region stores its boundary, area, scale, property distributions, internal variation, missingness, uncertainty, neighbors, and parent/child relationships.

Candidate segmentation methods include watershed segmentation for strong raster boundaries, superpixels for image/feature patches, and a region-adjacency graph for merging neighboring segments. Methods are compared using internal homogeneity, boundary reproducibility, and stability across legitimate scales. The chosen method must enforce spatial connectivity.

After segmentation, aggregate cell-level inputs into a region representation containing:

- Robust summaries of direct physical variables.
- Distributions and internal variation, not only averages.
- Aggregated spectral PCA and image/texture representations.
- Region size, shape, and boundary strength.
- Neighboring-region context.
- Scale, source footprint, missingness, resolution, acquisition context, and uncertainty.

## Step 2 — Neutral region types

Cluster region summaries separately for each planet, scale, and compatible `analysis_cohort`. A model may combine cohorts only if it explicitly handles missing feature families and is tested against a cohort-only baseline; ordinary median filling across absent instrument coverage is not acceptable.

Compare several clustering behaviors rather than trusting one algorithm:

- HDBSCAN for irregular clusters, variable density, and explicit noise points.
- Gaussian mixture models for soft membership and overlapping region types when their assumptions are reasonable.
- Graph/community clustering when neighborhood relationships are central.
- A simple K-means baseline to expose whether complexity is actually useful.

PCA supports compression; UMAP may support visualization but is not treated as proof of real cluster separation. Model selection uses geographic stability, resampling stability, interpretability, and control-site behavior rather than a single silhouette score.

Initial labels remain neutral, such as `mars_region_type_07`. Before scientific interpretation:

- Test stability under resampling.
- Test sensitivity to spatial scale.
- Map every cluster geographically.
- Check whether clusters are explained by latitude, illumination, instrument coverage, missing data, or resolution.
- Use spatial holdouts rather than random neighboring-cell splits.
- Run anomaly detection so rare but important regions are not discarded.

Use Isolation Forest and/or representation reconstruction error as anomaly candidates. An anomaly is an unusual region, not automatically a rare process. It receives the same scientific review as a normal cluster.

### Acquisition-artifact test

Train a diagnostic model to predict cluster identity using only instrument, observation date, illumination/observation geometry, source resolution, and missingness. If those metadata strongly predict clusters, acquisition conditions may dominate the scientific measurements. The response is to correct the representation or split incompatible observation groups, not to interpret those clusters geologically.

## Step 3 — Evidence recipes

Each process interpretation requires a versioned recipe derived from NASA documentation and peer-reviewed studies. A recipe contains required evidence, supporting evidence, disqualifying evidence, alternative causes, time requirements, and Earth-observable variables.

### Mars: active aeolian transport

Required:

- Dune, ripple, or wind-streak morphology.
- Co-registered repeat observations showing change beyond registration uncertainty.

Supporting:

- Thermal behavior compatible with unconsolidated sediment.
- Atmospheric dust or wind context.
- Consistent feature orientation and regional transport pattern.

Static dune morphology supports an aeolian landform but not present activity.

### Mars: past fluvial or lacustrine activity

Required:

- Channel, valley, delta, fan, or sedimentary-basin morphology.
- Topographic relationships consistent with downhill transport and a receiving basin.

Supporting:

- Layered or sedimentary deposits.
- Hydrated/alteration minerals in a geologically consistent position.
- Closed-basin or paleolake-level geometry.

Alternatives include lava channels, glacial channels, structural features, and inverted relief. The output label is past-process evidence, not active surface water.

### Mars: glacial or periglacial modification

Required:

- A compatible landform assemblage rather than one isolated shape.
- Terrain and latitude/elevation context consistent with ice-related formation.

Supporting:

- Hydrogen enrichment.
- Radar evidence of subsurface interfaces.
- Thermal and seasonal context.

Alternative explanations must include volcanic, mass-wasting, and aeolian modification where relevant.

### Mars: water-driven mineral alteration

Required:

- Validated spectral mineral indicators with quality masks.
- Geological association showing the mineral signal belongs to the mapped unit.

Supporting:

- Fluvial/lacustrine morphology, hydrothermal context, or evaporite setting.

Mineral detections alone do not specify whether alteration was surface, subsurface, hydrothermal, or transported.

### Moon: impact and regolith modification

Required:

- Crater/ejecta morphology and topographic relationships.

Supporting:

- Roughness, block abundance, thermal behavior, and albedo differences.
- Repeat observations for a recent-impact label.

### Moon: volcanic terrain and candidate lava tubes

Required:

- Volcanic geological context.
- Pit, collapse-chain, channel, or flow morphology appropriate to the interpretation.

Supporting:

- Topographic continuity.
- Thermal or radar behavior consistent with, but not proof of, a cavity.

A circular pit alone is not labelled a lava tube.

### Moon: polar cold trapping and volatile evidence

Required for a cold-trap environment:

- Temperature history or modeled sublimation conditions allowing volatile retention.
- Topographic/illumination geometry consistent with sufficient shadow.

Supporting evidence for possible ice:

- Hydrogen-sensitive neutron measurement.
- Spectral or ultraviolet evidence.
- Radar response.
- Reflectance evidence.

Cold conditions show preservation potential. Hydrogen, radar, or temperature alone does not confirm water ice.

### Moon: mass wasting

Required:

- Slope-related morphology and material movement pattern.
- Topographic context.

Active/recent status additionally requires repeat-image change or another time-constrained observation.

## Step 4 — Scientific interpretation

For each neutral region type:

1. Summarize the defining measurements.
2. Inspect representative and boundary cases.
3. Compare with every relevant evidence recipe.
4. Test alternative explanations.
5. Evaluate known positive controls.
6. Evaluate visually similar negative controls.
7. Assign a process/environment label only if its evidence threshold passes.
8. Preserve ambiguous types as unresolved.

Every interpreted region has separate fields for interpretation, activity status, evidence confidence, data confidence, alternative explanations, and Earth transferability.

Evidence recipes are defined before final labels are assigned, even though they are applied after neutral clustering. This prevents post-hoc selection of whichever paper makes a cluster appear convincing.

## Step 5 — Regional refinement

After broad discovery, request high-resolution observations intersecting the candidate region:

- Mars: CTX, HiRISE, CRISM, THEMIS, SHARAD, MARCI/MCS as appropriate.
- Moon: LROC NAC, detailed LOLA/stereo terrain, Diviner polar products, Mini-RF, LEND, and LAMP as appropriate.

Regional evidence may confirm, reject, split, or leave a candidate unresolved. Targeted coverage cannot be used to claim global prevalence.

## Step 6 — Earth-filter translation

Only validated interpretations become Earth filters. Each filter contains:

- Planet and interpretation.
- Required planetary evidence.
- Earth-observable variables.
- Scale and resolution requirements.
- Expected relationships among variables.
- Available Earth datasets.
- Known analogy failures.
- Scientific and operational uses.

Example:

```text
Mars active aeolian region
→ aridity + exposed sediment + dune morphology
  + wind regime + observed surface change + low vegetation
```

Earth filters describe measurable characteristics. They do not use a vague “Mars-like” score.

## Main safeguards

- Do not confuse static landforms with active processes.
- Do not confuse environmental suitability with confirmed material presence.
- Do not let missing-data patterns define clusters.
- Do not sharpen coarse measurements into independent fine pixels.
- Do not evaluate with random neighboring-cell splits.
- Do not combine Moon and Mars clusters.
- Do not force every cluster to receive a process label.
- Do not use targeted high-resolution coverage to infer planetary prevalence.
- Do not hide competing explanations.

## Outputs

For each planet:

- Multiscale homogeneous-region polygons.
- Region hierarchy and adjacency graph.
- Region feature table.
- Neutral cluster assignments and stability report.
- Evidence-recipe registry.
- Interpreted-region catalog.
- Positive/negative control evaluation.
- Alternative-explanation report.
- Regional-refinement manifest.
- Earth-filter specification JSON.

## Completion criteria

The process-discovery stage passes when:

1. Regions are connected, multiscale, and uncertainty-aware.
2. Main clusters are not explained by coverage, resolution, or acquisition artifacts.
3. Process labels satisfy explicit evidence recipes.
4. Active labels include temporal evidence.
5. Past labels are clearly marked as preserved evidence.
6. Positive controls are recovered and negative controls constrain false positives.
7. Ambiguous regions remain unresolved.
8. Earth translations use variables that can actually be measured globally or regionally.
