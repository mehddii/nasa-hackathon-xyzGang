# NASA Hackathon — Moon, Mars, and Earth Analogs

## Project workflow

1. [Planetary data preparation](docs/data-preparation-design.md) — build separate, aligned Mars and Moon feature datasets from curated PDS products.
2. [Process discovery](docs/process-discovery-design.md) — create homogeneous regions, discover recurring region types, and interpret them with scientific evidence recipes.
3. Earth filtering — translate validated planetary evidence into measurable Earth variables and rank terrestrial regions.

Implemented notebooks:

- [`01_mars_data_preparation.ipynb`](notebooks/01_mars_data_preparation.ipynb)
- [`03_mars_region_discovery.ipynb`](notebooks/03_mars_region_discovery.ipynb)

The NASA PDS API documentation is tracked as a Git submodule under `ressources/pds-api`.
