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
    raise FileNotFoundError(f'{name}: attach Notebook 19 output')

decoded=pd.read_parquet(find('decoded_numeric_features.parquet'))
if decoded.empty:
    raise ValueError('Notebook 19 produced no decoded numeric datasets')
decoded['dataset_lower']=decoded['dataset'].astype(str).str.lower()

rules={
 'snow_ice': {'products':['MOD10CM'], 'terms':['snow','albedo','fraction','qa']},
 'soil_freeze_thaw': {'products':['SPL3SMP'], 'terms':['soil','freeze','thaw','moisture','quality','retrieval']},
 'terrain': {'products':['NASADEM_HGT'], 'terms':['elevation','height','dem','slope','aspect','roughness']},
}
rows=[]
for family,rule in rules.items():
    part=decoded[decoded['product'].isin(rule['products'])].copy()
    if family=='terrain' and len(part) and not part.dataset_lower.str.contains('|'.join(rule['terms']),regex=True).any():
        selected=part.head(20).copy()
    else:
        selected=part[part.dataset_lower.str.contains('|'.join(rule['terms']),regex=True)].copy()
    for row in selected.to_dict('records'):
        rows.append({**row,'feature_family':family,'evidence_status':'decoded_numeric_summary'})
features=pd.DataFrame(rows)
if features.empty:
    features=pd.DataFrame(columns=list(decoded.columns)+['feature_family','evidence_status'])
OUT=Path('/kaggle/working/earth_process_features'); OUT.mkdir(exist_ok=True)
features.to_parquet(OUT/'earth_process_feature_evidence.parquet',index=False)
features.to_csv(OUT/'earth_process_feature_evidence.csv',index=False)

readiness=pd.DataFrame([
 {'process_id':'regolith_mantling_or_dust_cover','status':'available_from_existing_pipeline','evidence':'Mars dust/regolith distribution + existing Earth dust candidates'},
 {'process_id':'near_surface_ice_or_ground_ice','status':'earth_evidence_available_for_screening','evidence':'MOD10CM snow/albedo + SMAP freeze/thaw/soil moisture summaries'},
 {'process_id':'terrain_and_operations','status':'earth_evidence_available_for_screening','evidence':'NASADEM granule and decoded terrain datasets'},
 {'process_id':'water_driven_mineral_alteration','status':'blocked_missing_direct_mineral_measurement','evidence':'EMIT download exceeded safety limit; no mineral inference made'},
])
readiness.to_csv(OUT/'process_feature_readiness.csv',index=False)
summary={'decoded_input_rows':int(len(decoded)),'selected_feature_rows':int(len(features)),'feature_families':sorted(features.feature_family.unique().tolist()) if len(features) else [],'limitations':['Current Notebook 19 downloaded one granule per product, so these are evidence summaries, not a complete 20-cell Earth map.','Product-specific QA and scale-factor interpretation must be checked against product guides before final scoring.','EMIT/mineral alteration remains blocked.']}
(OUT/'feature_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
display(readiness)
display(features.groupby(['feature_family','product']).size().rename('variables') if len(features) else features)
print(json.dumps(summary,indent=2))
'''
nb={'cells':[{'cell_type':'markdown','metadata':{},'source':['# 21 — Earth process feature evidence\n','\n','Selects direct decoded measurements from Notebook 19 into process evidence families. It does not convert proxies into minerals or subsurface ice.\n']},{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}},'nbformat':4,'nbformat_minor':5}
Path('notebooks/21_earth_process_feature_evidence.ipynb').write_text(json.dumps(nb,indent=1),encoding='utf-8')
