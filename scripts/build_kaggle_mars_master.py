"""Build a self-contained Kaggle notebook from the Mars workflow notebooks."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = [
    "01_mars_data_preparation.ipynb",
    "03_mars_region_discovery.ipynb",
    "06_mars_process_validation.ipynb",
    "07_mars_candidate_validation.ipynb",
    "08_earth_dust_environment_matching.ipynb",
    "09_earth_refined_validation.ipynb",
]
OUT = ROOT / "kaggle" / "mars_workflow" / "run_mars_workflow.ipynb"

cells = [{"cell_type": "markdown", "metadata": {}, "source": ["# Mars validated workflow\n", "\n", "Self-contained sequential execution of the Mars notebooks."]}]
for name in NOTEBOOKS:
    source = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    cells.append({"cell_type": "markdown", "metadata": {}, "source": [f"## BEGIN {name}\n"]})
    for cell in source["cells"]:
        if cell.get("cell_type") == "code":
            cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": cell.get("source", [])})
        elif cell.get("cell_type") == "markdown":
            cells.append({"cell_type": "markdown", "metadata": {}, "source": cell.get("source", [])})

master = {
    "cells": cells,
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python"}},
    "nbformat": 4,
    "nbformat_minor": 5,
}
OUT.write_text(json.dumps(master, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"Built {OUT} with {len(cells)} cells")
