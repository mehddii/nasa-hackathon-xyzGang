# Notebooks

The previous feasibility notebook was removed. It added a separate decision stage where normal data-loading checks were enough and could incorrectly interpret PDS Search indexing gaps as unavailable scientific data.

The implementation order is now:

| Order | Notebook | Purpose |
|---|---|---|
| 1 | `01_mars_data_preparation.ipynb` | Preserve and clean Mars measurements; build separate scales; normalize direct variables; calculate neutral terrain/texture features; fit PCA and image representations; export cells, masks, transforms, and provenance |
| 2 | `02_moon_data_preparation.ipynb` | Preserve and clean Moon measurements; build global/polar and separate-scale views; normalize variables; calculate neutral features; fit PCA/embeddings; export cells, masks, transforms, and provenance |
| 3 | `03_mars_region_discovery.ipynb` | Merge neighboring Mars cells into multiscale connected regions; build region representations; test artifacts; cluster common types; detect anomalies; interpret with evidence recipes |
| 4 | `04_moon_region_discovery.ipynb` | Merge neighboring Moon cells into multiscale connected regions; build region representations; test artifacts; cluster common types; detect anomalies; interpret with evidence recipes |

Preparation notebooks stop at cell-level data. Region size, shape, internal variation, neighbors, clustering, anomaly detection, and process interpretation belong only to notebooks 3 and 4.

Only completed, runnable notebooks should be added. The table defines the implementation sequence; it is not a claim that these files already exist.
