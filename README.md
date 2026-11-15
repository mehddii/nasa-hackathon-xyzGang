# NASA Hackathon — Moon, Mars, and Earth Analogs

## Project workflow

1. [Planetary data preparation](docs/data-preparation-design.md) — build separate, aligned Mars and Moon feature datasets from curated PDS products.
2. [Process discovery](docs/process-discovery-design.md) — create homogeneous regions, discover recurring region types, and interpret them with scientific evidence recipes.
3. Earth filtering — translate validated planetary evidence into measurable Earth variables and rank terrestrial regions.

For continuation, see the [next-steps handoff](docs/next-steps-handoff.md), which defines the five remaining stages and the immediate Earth-screening and validation work.

Implemented notebooks:

- [`01_mars_data_preparation.ipynb`](notebooks/01_mars_data_preparation.ipynb)
- [`03_mars_region_discovery.ipynb`](notebooks/03_mars_region_discovery.ipynb)
- [`06_mars_process_validation.ipynb`](notebooks/06_mars_process_validation.ipynb)
- [`07_mars_candidate_validation.ipynb`](notebooks/07_mars_candidate_validation.ipynb)
- [`08_earth_dust_environment_matching.ipynb`](notebooks/08_earth_dust_environment_matching.ipynb)
- [`09_earth_refined_validation.ipynb`](notebooks/09_earth_refined_validation.ipynb)

The NASA PDS API documentation is tracked as a Git submodule under `ressources/pds-api`.
