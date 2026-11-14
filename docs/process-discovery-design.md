# Homogeneous-Region and Planetary Process Discovery

## Status

Proposed design for the process-spotting phase. Implementation begins only after the data feasibility study passes its exit gate.

## Purpose

Discover recurring, spatially connected planetary environments and determine which physical processes plausibly produced or currently modify them.

The system must distinguish:

- A measured property, such as temperature or reflectance.
- An environment, such as a cold, shadowed polar surface.
- A landform, such as a channel or dune.
- A process, such as aeolian transport or fluvial deposition.
- A past process from a currently active process.

Clusters are patterns in measurements. They are not automatically process labels.

## Core principles

1. Build separate Moon and Mars pipelines.
2. Use calibrated or validated derived measurements.
3. Discover connected homogeneous regions rather than treating arbitrary squares as final objects.
4. Work at multiple spatial scales.
5. Combine unsupervised discovery with literature-derived evidence rules.
6. Preserve uncertainty and missingness.
7. Require controls and alternative explanations.
8. Prefer scientifically interpretable features over opaque embeddings when both perform similarly.
9. Keep rare but important phenomena from being erased by dominant terrain classes.
10. Translate only validated planetary findings into Earth filters.

## Definition of a homogeneous region

A homogeneous region is a connected area within which selected measurements vary less than scientifically justified tolerances at a specified scale.

There is no single smallest or universal region because:

- Temperature may be uniform across an area with several mineral units.
- A coarse neutron footprint may cover many image-texture regions.
- A narrow channel may cross a broad geological unit.
- Natural boundaries may be gradual rather than sharp.

Therefore, each region must record:

- Planet.
- Boundary and area.
- Analysis scale.
- Properties used to create the boundary.
- Per-property mean, spread and distribution.
- Internal heterogeneity.
- Missing-data fraction.
- Measurement uncertainty.
- Observation dates or date range.
- Neighboring regions.
- Parent and child regions at other scales.

## Process taxonomy

The initial taxonomy organizes hypotheses without forcing labels onto clusters.

### Mars hypothesis families

- Aeolian erosion, transport and deposition.
- Dust lifting, transport and deposition.
- Fluvial erosion and sedimentation.
- Lacustrine deposition.
- Water-driven mineral alteration.
- Glacial and periglacial modification.
- Seasonal frost and ice-related activity.
- Volcanic emplacement and modification.
- Impact cratering and ejecta modification.
- Mass wasting and slope activity.

### Moon hypothesis families

- Impact cratering and ejecta emplacement.
- Regolith production and redistribution.
- Volcanic emplacement.
- Pit formation and candidate lava-tube collapse.
- Polar cold trapping and volatile retention.
- Mass wasting and slope modification.
- Thermal fatigue and rock breakdown.
- Recent impact or other observable surface change.

These families must be revised using the feasibility study and scientific review.

## Evidence recipes

Before model training, create a versioned evidence registry. Each hypothesis must specify:

- Required observations.
- Supporting observations.
- Expected spatial relationships.
- Expected temporal relationships.
- Alternative explanations.
- Disqualifying evidence.
- Confidence calculation.
- Relevant literature.
- Earth-observable translation.

### Example: past Martian fluvial-lacustrine activity

Required evidence may include:

- Channel, valley network, delta, fan or sedimentary-basin morphology.
- Topographic relationships consistent with downhill transport and a receiving basin.

Supporting evidence may include:

- Layered or sedimentary deposits.
- Hydrated or alteration minerals in a geologically consistent location.
- Closed-basin geometry or plausible paleolake level.

Alternative explanations include:

- Lava channels.
- Glacial or subglacial channels.
- Structural lineaments.
- Inverted relief modified by later erosion.

The output label must be `past fluvial-lacustrine evidence`, not `active water`.

### Example: active Martian aeolian transport

Required evidence may include:

- Aeolian morphology such as dunes or ripples.
- Co-registered repeat observations showing displacement or surface change beyond registration uncertainty.

Supporting evidence may include:

- Thermal properties compatible with unconsolidated sediment.
- Atmospheric dust or wind context.
- Orientation consistent with regional transport patterns.

Static dune morphology alone supports an aeolian landform but not current activity.

### Example: lunar polar cold trapping

Required evidence may include:

- Time-dependent temperature or modeled sublimation conditions compatible with volatile retention.
- Illumination and topographic geometry supporting persistent or sufficiently long shadow.

Supporting evidence may include:

- Hydrogen-sensitive neutron measurements.
- Spectral or ultraviolet evidence.
- Radar response.
- Reflectance anomalies.

Cold-trap conditions indicate preservation potential, not confirmed ice. Confirmation confidence must increase only when independent compositional evidence agrees.

### Example: lunar pit or candidate lava-tube system

Required evidence may include:

- Pit morphology and shadow geometry consistent with an opening or collapse.
- Volcanic geological context.

Supporting evidence may include:

- Aligned collapse features.
- Subsurface-sensitive evidence where available.
- Thermal behavior consistent with a cavity, interpreted cautiously.

A pit must not be called a lava tube without evidence beyond a circular depression.

## End-to-end architecture

### Stage 1 — Planet-specific analysis layers

For each planet, construct versioned layers containing:

- Physical values and units.
- Native resolution.
- Effective footprint.
- Observation time.
- Quality mask.
- Uncertainty.
- Provenance.

Layers remain separate until a justified feature-extraction step combines them.

### Stage 2 — Common computational grids

Use temporary grids for numerical processing. A grid is not the final scientific region.

Requirements:

- Planet-appropriate coordinate reference systems.
- Area-aware geometry.
- Multiple resolutions chosen from the feasibility study.
- Aggregation of fine data using documented statistics.
- No false sharpening of coarse data.
- Explicit flags where a coarse footprint crosses several fine cells.

### Stage 3 — Feature extraction

Compute interpretable features at each scale.

#### Terrain

- Elevation.
- Slope and aspect.
- Curvature.
- Local relief.
- Roughness at multiple window sizes.
- Drainage and basin metrics where physically relevant.

#### Spectral and compositional

- Validated mineral indices or abundance products.
- Spectral shape summaries.
- Hydration indicators.
- Mafic or felsic indicators where supported.
- Quality and atmospheric-correction flags.

#### Thermal

- Day and night temperature summaries.
- Seasonal or local-time variation.
- Thermal inertia or validated proxy.
- Extreme and persistence statistics.
- Rock-abundance products where available.

#### Radar and neutron

- Backscatter and polarization summaries.
- Radar texture.
- Neutron count or hydrogen-product values.
- Native-footprint uncertainty and spatial support.

#### Image morphology

- Edge and line structure.
- Directional texture.
- Repeating ridge or dune patterns.
- Layering indicators.
- Crater, channel, pit and boulder candidates.
- Learned image embeddings only when their behavior is audited against lighting and resolution.

#### Temporal

- Change magnitude after accurate co-registration.
- Direction and rate where measurable.
- Seasonal phase.
- Number and spacing of observations.
- Detection threshold and registration uncertainty.

### Stage 4 — Boundary detection and region formation

Use a multiscale segmentation approach:

1. Detect strong property boundaries.
2. Produce fine candidate segments using spatially constrained segmentation.
3. Merge adjacent segments when property differences fall below validated thresholds.
4. Preserve narrow or rare structures through shape-aware rules.
5. Build a hierarchy linking fine regions to broader parent regions.
6. Calculate internal heterogeneity and reject regions that are not sufficiently homogeneous.

Candidate methods may include watershed segmentation, superpixels, region adjacency graphs and hierarchical agglomeration. Method selection must be based on validation performance, not visual preference.

### Stage 5 — Region representation

Represent each region using:

- Robust property statistics.
- Within-region distributions.
- Shape and area.
- Boundary strength.
- Neighborhood composition.
- Parent and child context.
- Temporal behavior.
- Missingness pattern.
- Uncertainty.

Features must be normalized within each planet and instrument context. Missing values must use masks or models designed for missing data, never zero filling by default.

### Stage 6 — Unsupervised discovery

Cluster regions separately by planet and scale.

Requirements:

- Compare more than one clustering family.
- Avoid selecting cluster count only from one internal metric.
- Test stability under resampling and feature perturbation.
- Map clusters back to geography.
- Measure whether clusters correspond to latitude, lighting, mission coverage or missingness.
- Include rare-region or anomaly discovery in addition to dominant clustering.

Initial outputs use neutral identifiers such as `mars_region_type_07`.

### Stage 7 — Scientific interpretation

For every discovered region type:

1. Summarize defining properties.
2. Inspect geographic examples.
3. Compare with evidence recipes.
4. Test alternative explanations.
5. Examine positive and negative controls.
6. Assign a label only when evidence thresholds pass.
7. Retain ambiguous types as unresolved rather than forcing a process.

### Stage 8 — Confidence and status

Every interpreted region receives separate fields:

- `interpretation`: process, environment, landform or operational condition.
- `activity_status`: active, recent, past, unknown or not applicable.
- `evidence_confidence`: strength of the evidence combination.
- `data_confidence`: coverage, quality and uncertainty of measurements.
- `alternative_explanations`: competing interpretations.
- `earth_transferability`: whether comparable Earth measurements exist.

Confidence must not be reduced to one unexplained probability.

### Stage 9 — Earth-filter specification

For each validated planetary interpretation, create an Earth-filter record containing:

- Planet and process/environment.
- Planetary evidence.
- Earth-observable variables.
- Expected Earth ranges or relationships.
- Required and optional Earth datasets.
- Scale requirements.
- Known analogy failures.
- Scientific and operational uses.

Earth filters must use measurable properties, not labels such as “Mars-like.”

## Validation design

### Positive controls

Use published examples of each feasible hypothesis to test whether the pipeline produces appropriate regions and evidence.

### Negative controls

Use locations that resemble the target visually but have a different origin, as well as ordinary terrain lacking the process.

### Spatial cross-validation

Hold out entire geographic areas rather than random neighboring cells. Random cell splits would leak nearly identical spatial information between training and evaluation.

### Temporal validation

For active processes, hold out observation dates and require changes to exceed co-registration and sensor uncertainty.

### Resolution sensitivity

Repeat segmentation and interpretation at multiple defensible resolutions. Record which conclusions remain stable.

### Expert and literature review

Compare outputs with published maps and interpretations. Disagreement is recorded and investigated rather than hidden.

## Metrics

No single metric is sufficient. Track:

- Region internal homogeneity.
- Boundary reproducibility.
- Cluster stability.
- Geographic generalization.
- Positive-control recovery.
- Negative-control false-positive rate.
- Sensitivity to missing layers.
- Sensitivity to resolution and season.
- Fraction of surface assigned confidently.
- Fraction retained as unresolved.
- Earth-transferability coverage.

## Major failure modes and mitigations

### Instrument and illumination clusters

The model may group observations by sensor, incidence angle or resolution. Mitigation: normalize acquisition effects, include them in diagnostics and test whether cluster identity can be predicted from instrument metadata.

### Coverage clusters

Missing-data patterns may dominate. Mitigation: model missingness explicitly, cluster only compatible feature sets and audit cluster membership against coverage.

### Equifinality

Different processes can create similar landforms. Mitigation: require independent evidence types and retain competing explanations.

### Spatial autocorrelation

Neighboring samples are not independent. Mitigation: geographic holdouts and region-level evaluation.

### Scale dependence

Segmentation changes with resolution. Mitigation: hierarchical regions and scale-sensitivity reporting.

### Rare-process loss

Dominant terrain may absorb small important features. Mitigation: anomaly detection, stratified sampling and preservation rules for narrow or high-contrast structures.

### False activity claims

Static morphology may be mistaken for current activity. Mitigation: require repeat observations and uncertainty-aware change detection for active labels.

### False compositional certainty

Radar, neutron or temperature anomalies may be treated as direct composition measurements. Mitigation: classify them as supporting evidence unless independent compositional observations agree.

### Targeting bias

Published high-resolution coverage favors known interesting sites. Mitigation: report the inference domain and avoid global prevalence claims from targeted samples.

### Earth analogy overreach

Earth may match geology while failing in gravity, atmosphere, radiation or vacuum. Mitigation: score analogy dimensions separately and state failures explicitly.

## Expected outputs

Separate outputs are required for Moon and Mars:

- Versioned analysis-layer manifest.
- Multiscale region polygons in GeoParquet.
- Region feature tables in Parquet.
- Region hierarchy and adjacency graph.
- Neutral cluster assignments.
- Cluster stability report.
- Evidence-recipe registry.
- Interpreted region catalog.
- Positive and negative control evaluation.
- Ambiguity and alternative-explanation report.
- Earth-filter specifications in JSON and tabular form.
- Reproducible maps and representative examples.

## Implementation sequence

1. Implement one Mars regional pilot with strong multi-instrument coverage.
2. Validate segmentation, missingness handling and one past plus one active hypothesis.
3. Implement one lunar polar pilot to validate temperature, illumination and coarse supporting measurements.
4. Implement one lunar non-polar pilot for impact, volcanic or slope processes.
5. Compare algorithms and freeze the region schema.
6. Scale to all feasible well-covered regions.
7. Add rare-region discovery.
8. Produce Earth-filter specifications.
9. Begin the separate Earth search pipeline.

## Acceptance criteria

The process-discovery phase is successful only when:

1. Moon and Mars are processed independently.
2. Regions are spatially connected, multiscale and accompanied by uncertainty.
3. Clusters remain stable under reasonable resampling and scale changes.
4. Instrument, lighting and missingness do not explain the main clusters.
5. Every process label satisfies a documented evidence recipe.
6. Active-process labels include temporal evidence.
7. Past-process labels state that the evidence is preserved rather than current.
8. Positive controls are recovered at an agreed rate.
9. Negative-control false positives remain below an agreed threshold.
10. Ambiguous regions remain explicitly unresolved.
11. Every Earth filter maps to available Earth-observation variables.
12. Known analogy failures are included in the output.

## Exit gate

Earth-scale filtering begins only after at least one Mars and one Moon pilot pass the acceptance criteria. If a hypothesis lacks independent supporting measurements, it may remain an environment or landform detector but must not be presented as a confirmed process detector.

