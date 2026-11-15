import json
from pathlib import Path

code = r'''from pathlib import Path
import json, numpy as np, pandas as pd
from IPython.display import display

ROOTS=[Path('/kaggle/working'),Path('/kaggle/input')]
def find(name):
    for root in ROOTS:
        if root.exists():
            hits=list(root.rglob(name))
            if hits:return hits[0]
    raise FileNotFoundError(f'{name}: attach Notebook 21 and Mars 06 outputs')

earth=pd.read_parquet(find('earth_process_feature_evidence.parquet'))
out=Path('/kaggle/working/earth_process_matching'); out.mkdir(exist_ok=True)
mars_paths=[]
for root in ROOTS:
    if root.exists(): mars_paths.extend(root.rglob('mars_neutral_type_measurement_distributions.parquet'))
if not mars_paths:
    raise FileNotFoundError('mars_neutral_type_measurement_distributions.parquet')
mars=pd.read_parquet(mars_paths[0])

# Match only by explicit shared feature names. No proxy is silently renamed into a mineral/ice measurement.
shared=[]
# Explicit mapping: both values are metres above each body's datum. This is
# a terrain comparison, not evidence of the same geological process.
mars_elevation='raw_mean__elevation_mean_m'
if mars_elevation+'__q50' in mars.columns:
    for e in earth['dataset'].astype(str).unique():
        if e.lower().endswith('.hgt'):
            shared.append((e,mars_elevation))
rows=[]
for family in sorted(earth.feature_family.dropna().unique()) if 'feature_family' in earth else []:
    f=earth[earth.feature_family==family]
    names=set(f.dataset.astype(str))
    matched=[x for x in shared if x[0] in names]
    rows.append({'feature_family':family,'earth_variables':len(names),'shared_mars_variables':len(matched),'status':'scorable' if matched else 'blocked_no_shared_measurements','note':'Elevation is mapped in metres; SMAP freeze/thaw is retained as Earth evidence but has no Mars counterpart here.'})
status=pd.DataFrame(rows)
status.to_csv(out/'matching_readiness.csv',index=False)
if len(shared):
    # Robust distance to Mars median using Mars q10/q50/q90 and Earth summary mean.
    scores=[]
    for e,m in shared:
        er=earth[earth.dataset.astype(str)==e]
        med=pd.to_numeric(mars[m+'__q50'],errors='coerce').median() if m+'__q50' in mars else np.nan
        scale=(pd.to_numeric(mars[m+'__q90'],errors='coerce').median()-pd.to_numeric(mars[m+'__q10'],errors='coerce').median()) if m+'__q90' in mars and m+'__q10' in mars else np.nan
        val=pd.to_numeric(er['mean'],errors='coerce').median()
        scores.append({'earth_dataset':e,'mars_feature':m,'earth_value':val,'mars_median':med,'mars_q10_q90_width':scale,'z_like_distance':abs(val-med)/max(abs(scale),1e-12) if np.isfinite(val+med+scale) else np.nan})
    pd.DataFrame(scores).to_csv(out/'shared_variable_similarity.csv',index=False)
summary={'earth_feature_rows':int(len(earth)),'mars_distribution_rows':int(len(mars)),'shared_variables':int(len(shared)),'status':'scoring_ready_for_shared_variables' if shared else 'blocked_no_shared_measurements','warning':'No similarity score is produced when Earth and Mars variables are not explicitly shared with compatible units.'}
(out/'matching_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
display(status)
print(json.dumps(summary,indent=2))
'''
nb={'cells':[{'cell_type':'markdown','metadata':{},'source':['# 22 — Process-specific Mars–Earth matching\n','\n','Computes similarity only for explicitly shared variables with compatible units. It never treats a climate or terrain proxy as direct mineral evidence.\n']},{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}},'nbformat':4,'nbformat_minor':5}
Path('notebooks/22_process_matching.ipynb').write_text(json.dumps(nb,indent=1),encoding='utf-8')
