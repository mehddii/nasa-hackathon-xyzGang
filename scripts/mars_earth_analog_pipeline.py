"""Transparent Mars-process to Earth similarity ranking.

The script never creates Mars or Earth data. It consumes documented process
distributions and Earth feature tables and exports explainable scores.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Iterable
import numpy as np
import pandas as pd

def _read(path: Path) -> pd.DataFrame:
    if not path.exists(): raise FileNotFoundError(f"Required input is missing: {path}")
    return pd.read_parquet(path) if path.suffix.lower() == ".parquet" else pd.read_csv(path)

def _feature_columns(mars: pd.DataFrame, earth: pd.DataFrame, requested: Iterable[str] | None) -> list[str]:
    cols = list(requested or [c for c in mars.columns if c in earth.columns and pd.api.types.is_numeric_dtype(mars[c])])
    cols = [c for c in cols if c in mars.columns and c in earth.columns and pd.api.types.is_numeric_dtype(mars[c]) and pd.api.types.is_numeric_dtype(earth[c])]
    if len(cols) < 2: raise ValueError("At least two shared numeric feature columns are required")
    return cols

def _scores(mars: pd.DataFrame, earth: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    m, e = mars[features].apply(pd.to_numeric, errors="coerce"), earth[features].apply(pd.to_numeric, errors="coerce")
    med, iqr = m.median(), (m.quantile(.75) - m.quantile(.25)).replace(0, np.nan)
    iqr = iqr.fillna(m.std().replace(0, np.nan)).fillna(1.0)
    ez = (e - med) / iqr
    q05, q95 = m.quantile(.05), m.quantile(.95)
    marginal = (1 - ((e.sub(q05).clip(lower=0) + e.sub(q95).clip(upper=0).abs()) / (q95 - q05).replace(0, 1)).mean(axis=1).clip(0, 1)).fillna(0)
    joint = (1 / (1 + np.sqrt(((ez - ((m - med) / iqr).median()) ** 2).mean(axis=1)))).fillna(0)
    missing = e.isna().mean(axis=1)
    result = earth.copy()
    result["marginal_score"], result["joint_score"], result["missing_penalty"] = marginal, joint, missing
    result["spatial_coherence"] = 0.0
    result["analog_score"] = (marginal / 3 + joint / 3) * (1 - missing)
    return result

def _coherence(frame: pd.DataFrame) -> pd.Series:
    if not {"latitude", "longitude"}.issubset(frame.columns): return pd.Series(0.0, index=frame.index)
    lat, lon, score = frame.latitude.to_numpy(), frame.longitude.to_numpy(), frame.analog_score.to_numpy()
    out = np.zeros(len(frame))
    for i in range(len(frame)):
        d = np.sqrt((lat - lat[i]) ** 2 + (np.cos(np.deg2rad(lat[i])) * (lon - lon[i])) ** 2)
        n = (d > 0) & (d <= 2.5)
        out[i] = float(np.mean(score[n])) if n.any() else 0.0
    return pd.Series(out, index=frame.index)

def run(mars_path: Path, earth_path: Path, output: Path, process_id: str, features: list[str] | None = None) -> dict:
    mars, earth = _read(mars_path), _read(earth_path)
    cols = _feature_columns(mars, earth, features); output.mkdir(parents=True, exist_ok=True)
    ranked = _scores(mars, earth, cols); ranked["spatial_coherence"] = _coherence(ranked)
    ranked["analog_score"] = (ranked.marginal_score + ranked.joint_score + ranked.spatial_coherence) / 3 * (1 - ranked.missing_penalty)
    ranked = ranked.sort_values("analog_score", ascending=False).reset_index(drop=True); ranked.insert(0, "rank", np.arange(1, len(ranked)+1)); ranked.insert(1, "process_id", process_id)
    ranked.to_parquet(output / f"{process_id}_earth_candidates.parquet", index=False); ranked.to_csv(output / f"{process_id}_earth_candidates.csv", index=False)
    sensitivity = []
    for name, w in {"equal":(1/3,1/3,1/3),"marginal_heavy":(.5,.25,.25),"joint_heavy":(.25,.5,.25),"spatial_heavy":(.25,.25,.5)}.items():
        x = _scores(mars, earth, cols); x["spatial_coherence"] = _coherence(x); x["score"] = (x.marginal_score*w[0] + x.joint_score*w[1] + x.spatial_coherence*w[2]) * (1-x.missing_penalty); sensitivity.append(x.score.rename(name))
    pd.concat(sensitivity, axis=1).to_csv(output / f"{process_id}_sensitivity.csv", index=False)
    keep = [c for c in ["rank","latitude","longitude","analog_score","marginal_score","joint_score","spatial_coherence","missing_penalty"] if c in ranked]
    summary = {"process_id":process_id,"mars_rows":len(mars),"earth_rows":len(earth),"features":cols,"weights":{"marginal":1/3,"joint":1/3,"spatial":1/3},"missingness_mean":float(ranked.missing_penalty.mean()),"top_candidates":ranked.head(20)[keep].to_dict("records"),"claim":"Compatible with the tested Mars process signature under the measured variables; not proof of the same active process."}
    (output / f"{process_id}_run_summary.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")
    return summary

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--mars",type=Path,required=True); p.add_argument("--earth",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--process-id",required=True); p.add_argument("--features",nargs="*"); a=p.parse_args(); print(json.dumps(run(a.mars,a.earth,a.output,a.process_id,a.features),indent=2,default=float))

if __name__ == "__main__": main()
