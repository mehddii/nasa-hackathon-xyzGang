# Notebooks

The previous feasibility notebook was removed. It added a separate decision stage where normal data-loading checks were enough and could incorrectly interpret PDS Search indexing gaps as unavailable scientific data.

The implementation order is now:

| Order | Notebook | Purpose |
|---|---|---|
| 1 | `01_mars_data_preparation.ipynb` | Download curated global Mars layers, align them, calculate features, and export the Mars process-discovery input |
| 2 | `02_moon_data_preparation.ipynb` | Download curated global and polar Moon layers, align them, calculate features, and export the Moon process-discovery input |
| 3 | `03_mars_region_discovery.ipynb` | Create and interpret multiscale homogeneous Mars regions |
| 4 | `04_moon_region_discovery.ipynb` | Create and interpret multiscale homogeneous Moon regions |

Only completed, runnable notebooks should be added. The table defines the implementation sequence; it is not a claim that these files already exist.
