# Next steps and handoff

This document is for continuing the project after notebook 08. The current
Earth result is a **coarse candidate ranking**, not a final claim that a place
has active Martian-style dust transport.

## Current state

- Notebooks 01 and 03 prepare and organize Mars data.
- Notebook 06 discovers and validates Mars region/process evidence.
- Notebook 07 keeps the Mars regions that pass the dust-compatible evidence
  checks.
- Notebook 08 queries NASA POWER and ranks Earth grid cells against those Mars
  regions using albedo, temperature range, precipitation, wind, and elevation.
- Notebook 08 uses percentile similarity, joint distance to Mars regions, and
  spatial coherence. Its output is a ranked list, not a binary match.
- The current global screen uses a 15-degree grid and retains 102 positive-
  elevation cells. This is useful for narrowing the search, but too coarse for
  site selection.

## Immediate priority: stages 1 and 2

### 1. Improve the Earth screen

Do this incrementally rather than downloading a complete high-resolution Earth
archive.

1. Start with the top 10–20 cells from notebook 08.
2. Replace each coarse cell with a local grid (for example 0.1–0.25 degrees).
3. Apply a real land/ice mask. Do not use elevation alone as a land mask:
   below-sea-level land can be valid, and positive-elevation ocean artefacts can
   occur at coarse resolution.
4. Add variables in groups, checking each group separately:
   - terrain: elevation, slope, roughness (DEM);
   - climate: temperature extremes, precipitation, wind;
   - surface/process: aerosol or dust indicators;
   - geology/minerals and ice/water where a documented open product exists.
5. Keep the original variables and record missingness, source, resolution,
   date range, and units for every new variable.

Do not silently treat a proxy as the physical process. For example, dry and
windy conditions support a dust-transport hypothesis but do not prove dust
movement.

### 2. Validate the Mars-to-Earth match

For each refined candidate:

- verify that it is land, and record its actual terrain and climate values;
- query higher-resolution Earthdata products through CMR (MODIS or another
  documented product) for follow-up imagery/measurements;
- compare the candidate with nearby cells, not only the single best cell;
- check whether the ranking survives reasonable changes to feature weights;
- record evidence for and against the interpretation.

The validation output should contain one row per candidate with its coordinates,
source products, values, score, uncertainty, and a plain-language conclusion.

## Later stages

### 3. Repeat for other planetary processes

Use the same matching framework for separately defined Mars and Moon processes,
such as erosion, sediment transport, volcanic terrain, ice dynamics, or water-
related alteration. Each process needs its own evidence recipe and proxy map;
do not combine Moon and Mars distributions into one target.

### 4. Run the Moon workflow

Use notebooks 02 and 04 to prepare Moon regions, then validate Moon process
evidence before matching it to Earth. The Moon and Mars pipelines must remain
separate because their gravity, atmosphere, thermal environment, and surface
processes differ.

### 5. Produce the final deliverable

Create a map and a short table of candidate locations. For every location show:

- the planetary process it may help study;
- the Earth measurements that support the analogy;
- the supporting source products and dates;
- confidence and uncertainty;
- where the analogy breaks down;
- what field, instrument, or additional dataset should be used next.

## What happens after the first Earth filtering

The first filter is only a broad candidate generator. After higher-resolution
validation, apply a second, process-specific filter to the survivors:

1. Keep the validated planetary process distributions and their uncertainty
   ranges.
2. Compute a separate Earth score for each process using its required
   variables, rather than one universal score.
3. Add practical constraints such as accessibility, protected areas, season,
   infrastructure, and field safety when the challenge requires a usable test
   site.
4. Rank the remaining locations and report the evidence behind every score.

This should initially be a transparent weighted/rule-based model with
sensitivity tests. A machine-learning classifier should only be introduced if
we obtain labeled examples of successful and unsuccessful analog sites; without
labels it would create confident-looking but unsupported classifications.

## Rules for continuation

- Preserve raw downloads and provenance; derived tables are not replacements.
- Use documented NASA APIs and cite the product/collection IDs.
- Keep Mars and Moon analyses separate.
- Prefer a smaller, well-validated candidate set over a large unverified map.
- Never describe a statistical similarity as proof of a physical process.
- Keep credentials in Kaggle Secrets or environment variables; never commit
  tokens to notebooks or Git.
