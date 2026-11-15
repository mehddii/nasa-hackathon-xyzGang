from pathlib import Path
import json

p = Path('notebooks/06_mars_process_validation.ipynb')
n = json.loads(p.read_text())

def set_cell(i, text):
    n['cells'][i]['source'] = text.splitlines(True)

set_cell(10, r'''# Translate literature statements into executable screening rules.
# A paper-defined direction/threshold and a dataset-relative prioritization
# threshold are kept separate in the exported provenance.

def direct_columns(family: str, required_tokens: tuple[str, ...] = ()) -> list[str]:
    columns = available_measurements.get(family, [])
    if required_tokens:
        columns = [c for c in columns if any(token in c.lower() for token in required_tokens)]
    return columns


def empty_screen() -> pd.DataFrame:
    return pd.DataFrame(columns=["region_index", "signal_value", "screening_score", "rule_detail"])


def screen_water_alteration(frame: pd.DataFrame) -> pd.DataFrame:
    # Bandfield (2002): 0.10 is the conservative TES detection limit. Notebook
    # 01 already converted sub-threshold values to zero and invalid spectra to NaN.
    # Sulfate/carbonate detections are rare and sheet silicate is inseparable from
    # high-Si glass here, so these are follow-up candidates, never proof of water.
    columns = [
        c for c in direct_columns("composition")
        if "detection_supported__" in c
        and any(token in c for token in ("mineral_sulfates", "mineral_carbonates", "mineral_sheet_silicates_high_si_glass"))
    ]
    if not columns:
        return empty_screen()
    signal = frame[columns].max(axis=1, skipna=True)
    usable = frame[columns].notna().any(axis=1)
    selected = usable & signal.gt(0.0)
    if not selected.any():
        return empty_screen()
    score = signal.rank(pct=True).clip(0, 1)
    return pd.DataFrame({"region_index": frame.index[selected], "signal_value": signal[selected], "screening_score": score[selected], "rule_detail": "TES alteration-related mineral component at the preparation-stage >=0.10 detection limit"})


def screen_hydrogen_candidate(frame: pd.DataFrame) -> pd.DataFrame:
    # Feldman et al. (2002, 2004): hydrogen moderates neutrons, so lower
    # epithermal-neutron count rates indicate more hydrogen. The paper does not
    # define one universal raw-count cutoff for this table; the within-latitude
    # 10th percentile is therefore only a prioritization threshold.
    columns = [c for c in direct_columns("hydrogen_sensitive") if "epithermal" in c.lower()]
    if not columns:
        return empty_screen()
    column = columns[0]
    signal = pd.to_numeric(frame[column], errors="coerce")
    latitude = pd.to_numeric(frame["centroid_latitude"], errors="coerce")
    latitude_band = pd.cut(latitude, bins=np.arange(-90, 111, 20), include_lowest=True)
    valid = signal.notna() & latitude.notna()
    thresholds = pd.Series(np.nan, index=frame.index, dtype=float)
    if valid.any():
        grouped = frame.loc[valid].assign(_signal=signal[valid], _band=latitude_band[valid]).groupby("_band", observed=True)["_signal"]
        band_q10 = grouped.transform(lambda s: s.quantile(0.10) if len(s) >= 4 else np.nan)
        thresholds.loc[band_q10.index] = band_q10
        thresholds = thresholds.fillna(float(signal[valid].quantile(0.10)))
    selected = valid & signal.le(thresholds)
    if not selected.any():
        return empty_screen()
    inverse_score = signal[valid].rank(pct=True, ascending=False)
    score = pd.Series(np.nan, index=frame.index, dtype=float); score.loc[inverse_score.index] = inverse_score
    detail = pd.Series("low epithermal-neutron flux: <= within-latitude-band 10th percentile", index=frame.index)
    detail.loc[selected & latitude.abs().ge(60)] += "; polar context consistent with Feldman et al."
    return pd.DataFrame({"region_index": frame.index[selected], "signal_value": signal[selected], "screening_score": score[selected], "rule_detail": detail[selected]})


def screen_dust_mantling(frame: pd.DataFrame) -> pd.DataFrame:
    # Ruff & Christensen (2002) use albedo >=0.2 for bright terrain and show
    # surface-obscuring dust is more direct than albedo/thermal inertia alone.
    # The dust q75 is a dataset-relative prioritization threshold.
    dust_columns = [c for c in direct_columns("dust") if "surface_dust" in c.lower()]
    albedo_columns = [c for c in direct_columns("albedo") if c.endswith("albedo_mean")]
    if not dust_columns or not albedo_columns:
        return empty_screen()
    dust = pd.to_numeric(frame[dust_columns[0]], errors="coerce")
    albedo = pd.to_numeric(frame[albedo_columns[0]], errors="coerce")
    valid = dust.notna() & albedo.notna()
    if not valid.any():
        return empty_screen()
    dust_q75 = float(dust[valid].quantile(0.75))
    selected = valid & dust.ge(dust_q75) & albedo.ge(0.20)
    if not selected.any():
        return empty_screen()
    score = dust.rank(pct=True).clip(0, 1)
    return pd.DataFrame({"region_index": frame.index[selected], "signal_value": dust[selected], "screening_score": score[selected], "rule_detail": f"dust >= dataset q75 ({dust_q75:.4g}) and paper-defined bright-terrain albedo >=0.20"})


SCREENING_RECIPES = {
    "water_driven_mineral_alteration": {
        "function": screen_water_alteration,
        "paper_rule": "TES mineral components are screenable only at or above the conservative 0.10 detection limit; sulfate/carbonate and sheet-silicate interpretations remain ambiguous.",
        "threshold_origin": "paper_defined_detection_limit_applied_in_notebook_01",
        "citation": "Bandfield 2002, doi:10.1029/2001JE001510",
        "missing_for_validation": "high-resolution mineral validation and geological/morphological association",
    },
    "near_surface_ice_or_ground_ice": {
        "function": screen_hydrogen_candidate,
        "paper_rule": "Lower epithermal-neutron flux indicates more near-surface hydrogen; it does not uniquely identify water ice.",
        "threshold_origin": "paper_defined_direction_plus_dataset_relative_latitude_band_q10",
        "citation": "Feldman et al. 2002, doi:10.1126/science.1073541; Feldman et al. 2004, doi:10.1029/2003JE002160",
        "missing_for_validation": "water-equivalent-hydrogen calibration, temperature stability, radar or diagnostic morphology",
    },
    "regolith_mantling_or_dust_cover": {
        "function": screen_dust_mantling,
        "paper_rule": "Bright terrain uses albedo >=0.20; strong surface-obscuring dust is required because albedo and thermal inertia alone are non-unique.",
        "threshold_origin": "paper_defined_albedo_plus_dataset_relative_dust_q75",
        "citation": "Ruff and Christensen 2002, doi:10.1029/2001JE001580",
        "missing_for_validation": "resolved mantling morphology, grain-size constraints and atmospheric/depositional context",
    },
}

screening_rule_rows = []
queue_frames = []
for process in PROCESS_REGISTRY:
    process_id = process["process_id"]
    recipe = SCREENING_RECIPES.get(process_id)
    if recipe is None:
        screening_rule_rows.append({"process_id": process_id, "implemented": False, "reason": "Current global products lack the morphology, repeat-change, radar, or other diagnostic evidence required for a defensible screen."})
        continue
    screened = recipe["function"](regions_work)
    screening_rule_rows.append({"process_id": process_id, "implemented": True, "reason": recipe["paper_rule"], "threshold_origin": recipe["threshold_origin"], "citation": recipe["citation"]})
    if screened.empty:
        continue
    selected = regions_work.loc[screened["region_index"]].copy()
    selected = selected.assign(
        process_id=process_id,
        signal_value=screened.set_index("region_index").loc[selected.index, "signal_value"],
        screening_score=screened.set_index("region_index").loc[selected.index, "screening_score"],
        rule_detail=screened.set_index("region_index").loc[selected.index, "rule_detail"],
        threshold_origin=recipe["threshold_origin"],
        rule_citation=recipe["citation"],
        missing_for_validation=recipe["missing_for_validation"],
        status="screening_candidate_not_validated",
    )
    selected = selected.sort_values(["screening_score", "follow_up_priority"], ascending=False).head(50)
    queue_frames.append(selected)

if queue_frames:
    screened_regions = pd.concat(queue_frames, ignore_index=True)
    export_columns = [c for c in ["process_id", "region_id", "neutral_type", "scale", "analysis_cohort", "centroid_latitude", "centroid_longitude", "signal_value", "screening_score", "follow_up_priority", "rule_detail", "threshold_origin", "rule_citation", "missing_for_validation", "status"] if c in screened_regions]
    process_review_queue_df = screened_regions[export_columns]
else:
    process_review_queue_df = pd.DataFrame(columns=["process_id", "region_id", "screening_score", "status"])
process_screening_rules_df = pd.DataFrame(screening_rule_rows)
display(process_screening_rules_df)
display(process_review_queue_df.head(30))
print(f"Signal-tested process candidates: {len(process_review_queue_df):,}")
''')

set_cell(12, r'''fig, axes = plt.subplots(1, 2, figsize=(18, 6), constrained_layout=True)
plot_df = evidence_availability_df.sort_values("co_located_region_fraction")
axes[0].barh(plot_df["process_id"], plot_df["co_located_region_fraction"], color="#2563EB")
axes[0].set_xlim(0, 1.05); axes[0].set_xlabel("Fraction of regions containing the necessary measurement families")
axes[0].set_title("Measurement availability — not process confidence", loc="left", fontweight="bold")
if len(process_review_queue_df):
    process_codes, process_names = pd.factorize(process_review_queue_df["process_id"], sort=True)
    points = axes[1].scatter(process_review_queue_df["centroid_longitude"], process_review_queue_df["centroid_latitude"], c=process_codes, cmap="tab10", s=18 + 45 * process_review_queue_df["screening_score"], alpha=0.80)
    axes[1].set_title("Literature-rule screening candidates", loc="left", fontweight="bold"); axes[1].set_xlabel("Longitude"); axes[1].set_ylabel("Latitude")
    axes[1].set_xlim(-180, 180); axes[1].set_ylim(-90, 90)
    handles = [plt.Line2D([0], [0], marker="o", linestyle="", color=plt.cm.tab10(i / max(1, len(process_names) - 1)), label=name) for i, name in enumerate(process_names)]
    axes[1].legend(handles=handles, loc="lower left", fontsize=8)
else:
    axes[1].text(0.5, 0.5, "No process candidates passed the implemented signal rules", ha="center", va="center"); axes[1].set_axis_off()
plt.show()
''')

src = ''.join(n['cells'][14]['source'])
src = src.replace('evidence_availability_df.to_csv(OUTPUT_ROOT / "mars_process_evidence_availability.csv", index=False)', 'evidence_availability_df.to_csv(OUTPUT_ROOT / "mars_process_evidence_availability.csv", index=False)\nprocess_screening_rules_df.to_csv(OUTPUT_ROOT / "mars_process_screening_rules.csv", index=False)')
src = src.replace('"candidate_region_count":int(len(candidate_regions_df)), "review_queue_rows":int(len(process_review_queue_df)),', '"candidate_region_count":int(len(candidate_regions_df)), "screened_process_candidate_count":int(process_review_queue_df["region_id"].nunique()) if len(process_review_queue_df) else 0, "review_queue_rows":int(len(process_review_queue_df)),')
src = src.replace("- Process-specific review rows: **{summary['review_queue_rows']:,}**", "- Signal-tested process candidates: **{summary['review_queue_rows']:,}**")
src = src.replace("The notebook creates evidence requirements and a targeted review queue. It does not convert neutral clusters into process labels.", "The notebook applies cited screening rules to measured values and creates a targeted review queue. Screening candidates are not validated process labels.")
n['cells'][14]['source'] = src.splitlines(True)

p.write_text(json.dumps(n, indent=1), encoding='utf-8')
