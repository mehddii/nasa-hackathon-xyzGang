# Mars preparation run summary

- Status: **complete**
- Sources: **9 products**, 0.0 MiB on disk
- Rows: **64,800 medium cells** and **648 coarse cells**
- TES emissivity archive: **73 bands → 1 PCA components**, preserving 99.99% of normalized-shape training variance
- Default spectral model: **1 leading PCA components**, preserving 99.99%
- Held-out spectral reconstruction: **99.99% retained by the archive view** and **99.99% by the default model view**
- Default clustering features: **13 medium-scale** and **16 coarse-scale**
- Official checksums: **0/0 verified** where the archive supplied MD5 values
- Terrain coverage: **100.0%**
- Thermal coverage: **61.1%**
- Quality-passing mineral coverage: **100.0%** (100.0% of all medium cells)
- Emissivity coverage: **100.0%**

## Interpretation limits

1. Neutron measurements are evidence sensitive to hydrogen, not proof of ice.
2. MOLA observation coverage must accompany topography because empty bins were interpolated.
3. TES mineral values are model results; default clustering receives only quality-passing concentrations at or above 0.10.
4. Slope and curvature are masked poleward of 88°; polar candidates need a polar-projected refinement.
5. The 1° and 10° rows represent different physical scales and should be analysed separately.
6. Coverage cohorts must be analysed separately or by an explicitly missing-aware method.
7. Quality, coverage, coordinates, and resolution are validation context, not default clustering inputs.
8. This notebook prepared measurements only. Region creation and process interpretation belong to notebook 03.
