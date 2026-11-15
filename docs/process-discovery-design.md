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
- Literature-backed evidence requirements.
- Known positive and negative control locations.

## Mars broad-discovery implementation

`03_mars_region_discovery.ipynb` implements the broad global stage as follows:

1. Analyse each physical scale and compatible coverage cohort separately.
2. Retain individually well-covered features from each science family, quantize them into area-weighted property prototypes, split them into four-neighbor connected components with longitude wrapping, then merge only adjacent tiny components whose science representations are sufficiently similar. A cohort whose valid support is intrinsically fragmented into tiny islands is preserved as descriptive-only evidence rather than forced into geological regions.
3. Summarize every connected region with surface-area-weighted physical values, model-space values, quality context, area, perimeter, internal variation, adjacency, and parent/child scale links.
4. Run hierarchical neutral clustering. The broad round uses terrain, reflectance, thermophysical measurements where available, and hydrogen-sensitive measurements only at their coarse scale. Broad clusters with fewer than five substantive regions are retained as `rare_broad_type` candidates, not treated as recurring environments or split into subtypes. Within each remaining broad type, a second round may add composition, spectral shape, and surface-dust measurements.
5. Exclude below-minimum-size fragments from imputation, acquisition-quality correction, model fitting, validation, artifact testing, ablations, and anomaly-threshold estimation. After the model is fixed, assign these fragments to a type using the chosen K-means/Gaussian model or the nearest non-noise HDBSCAN type, lower their confidence accordingly, and export them as `posthoc_tiny`. Readiness depends on the affected cell/area fraction, not the fraction of region records, so numerous one-cell fragments cannot dominate a model or falsely fail an otherwise representative partition.
6. Remove the regularized linear effect of relevant acquisition-quality variables while preserving the original physical measurements. Compare K-means, diagonal Gaussian mixtures, and HDBSCAN using geographic-fold stability, silhouette separation, assigned coverage, and coverage-only predictability. A subtype must have at least 40 substantive training regions, at least 10 regions per resulting cluster, spatial stability ARI ≥ 0.60, silhouette ≥ 0.20, assigned fraction ≥ 0.60, and a passing artifact test. The comparison report separates `best_candidate` from `applied_to_output`; a rich subtype rejected for weak separation, instability, low coverage, or artifact risk remains visible as a tested candidate but is never presented as an applied result.
7. Run Isolation Forest anomaly screening, coverage-only cluster prediction, and science-family ablations. Anomalies from tiny, limited-feature, fragmented-coverage, untested-artifact, or artifact-dominated regions remain recorded but are not promoted to the review shortlist.
8. Preserve neutral type identifiers and export their marginal distributions, feature dependencies, missingness, and spatial summaries. K-means confidence is a nearest-versus-second-nearest distance margin rather than a constant placeholder.
9. Audit literature-defined process hypotheses against the evidence present in the global products. The notebook records missing evidence but does not assign a process label from heuristic percentile thresholds.

Broad neutral clusters are not painted as processes. Mafic minerals remain compositional evidence, dust remains material/environment evidence, and neutron counts remain hydrogen-sensitive evidence. None alone establishes volcanism, active transport, or ice-related modification. Targeted CTX/HiRISE, CRISM, THEMIS, SHARAD, or repeat-observation refinement supplies the missing morphology, geological context, material discrimination, or timing.

A coverage cohort with at least two usable features may still support descriptive segmentation and neutral clustering. If those features come from only one science family, its regions are explicitly marked `limited_feature_evidence`; they cannot define a validated multivariate process signature.

The Mars notebook intentionally sets `earth_filter_handoff_ready` to false because its outputs are neutral distributions, not independently validated process distributions. A later validation stage may set that gate only after multiple positive examples, relevant negative controls, and the paper-required evidence are available.

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

Use two rounds inside each compatible cohort:

1. Discover broad types from consistently available terrain, reflectance, thermal, and scale-appropriate resource-sensitive measurements.
2. Within a broad type, test whether composition, spectral shape, or other locally rich measurements support a stable subtype.

The second round is accepted only when enough regions are available and acquisition-quality metadata cannot reproduce the split. This lets rich measurements refine a broad environment without allowing their footprint to define the environment.

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

## Step 3 — Literature evidence requirements

Each process interpretation requires a versioned evidence specification derived from NASA documentation and peer-reviewed studies. It contains required evidence, supporting evidence, disqualifying evidence, alternative causes, time requirements, scale requirements, and Earth-observable variables.

Papers define the scientific logic, not arbitrary dataset percentiles. A percentile may describe how unusual a measurement is within Mars, but it is not a scientific process threshold unless the cited study explicitly validates it as one.

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

## Step 4 — Scientific validation

For candidate regions selected from neutral types or anomalies:

1. Summarize the defining measurements.
2. Inspect representative and boundary cases.
3. Compare with every relevant literature evidence specification.
4. Test alternative explanations.
5. Evaluate multiple known positive controls.
6. Evaluate geographically and visually plausible negative controls.
7. Obtain the targeted observations needed for morphology, geological setting, material identification, or temporal change.
8. Assign a process/environment label only when all required evidence passes.
9. Preserve ambiguous types as unresolved.

Every interpreted region has separate fields for interpretation, activity status, evidence confidence, data confidence, alternative explanations, and Earth transferability.

Evidence requirements are defined before final labels are assigned, even though they are applied after neutral clustering. This prevents post-hoc selection of whichever paper makes a cluster appear convincing. A known location may validate its inspected region; it does not automatically label every region in the same broad cluster.

## Step 5 — Regional refinement

After broad discovery, request high-resolution observations intersecting the candidate region:

- Mars: CTX, HiRISE, CRISM, THEMIS, SHARAD, MARCI/MCS as appropriate.
- Moon: LROC NAC, detailed LOLA/stereo terrain, Diviner polar products, Mini-RF, LEND, and LAMP as appropriate.

Regional evidence may confirm, reject, split, or leave a candidate unresolved. Targeted coverage cannot be used to claim global prevalence.

## Step 6 — Build validated process distributions

After several examples pass the same evidence specification, represent the process using:

- Marginal distributions: robust quantiles, spread, tails, and missingness for each comparable feature.
- Joint structure: covariance, correlation, or a multivariate density/embedding so feature relationships are preserved.
- Spatial structure: region size and shape, adjacency, gradients, texture, and scale.
- Observation uncertainty and differences in sensor resolution.
- Subtypes when one process has meaningfully different expressions.

This is a conditional signature such as `P(features, spatial structure | process, planet, scale)`, not a list of exact values. Matching each feature histogram separately is insufficient because different processes can share the same marginal values while arranging them differently.

## Step 7 — Earth-filter translation and matching

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

Earth features must first be harmonized with the planetary descriptors. Use common physical units when genuinely comparable and within-planet robust ranks or standardized relationships when absolute values cannot transfer because of atmosphere, gravity, sensor, or resolution differences.

Earth matching compares joint distributions and spatial organization, using an explicit distance or likelihood such as Wasserstein distance, energy distance, maximum mean discrepancy, or a validated multivariate model. The result is an analog score with uncertainty and documented analogy failures—not proof that the exact same process occurred on Earth.

## Main safeguards

- Do not confuse static landforms with active processes.
- Do not confuse environmental suitability with confirmed material presence.
- Do not let missing-data patterns define clusters.
- Do not sharpen coarse measurements into independent fine pixels.
- Do not evaluate with random neighboring-cell splits.
- Do not combine Moon and Mars clusters.
- Do not force every cluster to receive a process label.
- Do not use hand-chosen percentiles as paper-backed process thresholds.
- Do not treat separate matching feature histograms as a joint-distribution match.
- Do not build a process distribution from one famous location.
- Do not use targeted high-resolution coverage to infer planetary prevalence.
- Do not hide competing explanations.

## Outputs

For each planet:

- Multiscale homogeneous-region polygons.
- Region hierarchy and adjacency graph.
- Region feature table.
- Neutral cluster assignments and stability report.
- Region-level and neutral-type marginal distributions, feature dependencies, and spatial summaries.
- Literature evidence-requirement registry and current-data availability audit.
- Validated interpreted-region catalog after regional refinement.
- Positive/negative control evaluation after regional refinement.
- Alternative-explanation report.
- Regional-refinement manifest.
- Validated process-signature and Earth-filter specification after regional refinement.

## Completion criteria

The process-discovery stage passes when:

1. Regions are connected, multiscale, and uncertainty-aware.
2. Main clusters are not explained by coverage, resolution, or acquisition artifacts.
3. Process labels satisfy explicit literature evidence requirements rather than heuristic thresholds.
4. Active labels include temporal evidence.
5. Past labels are clearly marked as preserved evidence.
6. Multiple positive controls are recovered and negative controls constrain false positives.
7. Process signatures preserve marginal distributions, joint dependencies, spatial structure, scale, missingness, and uncertainty.
8. Ambiguous regions remain unresolved.
9. Earth translations use variables that can actually be measured globally or regionally.
10. Earth analog scores compare harmonized distributions and explicitly report where the analogy fails.
