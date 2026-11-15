import json
from pathlib import Path

code = r'''from pathlib import Path
import json, zipfile
import numpy as np
import pandas as pd
from IPython.display import display

ROOTS=[Path('/kaggle/working'),Path('/kaggle/input')]
def all_hits(name):
    hits=[]
    for root in ROOTS:
        if root.exists(): hits.extend(root.rglob(name))
    return hits

paths=all_hits('downloaded_measurements.parquet')
if not paths:
    raise FileNotFoundError('Attach notebook 19 output containing downloaded_measurements.parquet')
manifest=pd.read_parquet(paths[0])
rows=[]
for row in manifest.to_dict('records'):
    if not bool(row.get('downloaded')): continue
    name=Path(str(row.get('local_path',''))).name
    hits=all_hits(name)
    path=hits[0] if hits else None
    if path is None:
        rows.append({**row,'dataset':'__missing_file__','count':0})
        continue
    try:
        import h5py
        with h5py.File(path,'r') as handle:
            def visit(name,obj):
                if not hasattr(obj,'shape') or not np.issubdtype(obj.dtype,np.number) or obj.size==0: return
                values=np.asarray(obj[...],dtype='float64').ravel()
                values=values[np.isfinite(values)]
                if values.size:
                    rows.append({**row,'attached_path':str(path),'dataset':name,'shape':str(obj.shape),'count':int(values.size),'mean':float(values.mean()),'std':float(values.std()),'min':float(values.min()),'max':float(values.max())})
            handle.visititems(visit)
    except Exception as exc:
        rows.append({**row,'attached_path':str(path),'dataset':'__decode_error__','count':0,'error':f'{type(exc).__name__}: {exc}'})
features=pd.DataFrame(rows)
out=Path('/kaggle/working/earth_decoded_features'); out.mkdir(exist_ok=True)
features.to_parquet(out/'earth_decoded_numeric_features.parquet',index=False)
features.to_csv(out/'earth_decoded_numeric_features.csv',index=False)
summary={'input_files':int(len(manifest)),'decoded_rows':int(len(features)),'products':sorted(features.product.dropna().unique().tolist()) if len(features) else [],'warning':'Numeric summaries are not final process features; product-specific QA, scale factors, and spatial extraction remain required.'}
(out/'decode_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
display(features.groupby('product').size().rename('decoded_rows'))
print(json.dumps(summary,indent=2))
'''

nb={'cells':[{'cell_type':'markdown','metadata':{},'source':['# 20 — Decode direct Earth measurements\n','\n','Reads notebook 19 outputs and summarizes numeric datasets without inventing mineral or ice values.\n']},{'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}},'nbformat':4,'nbformat_minor':5}
Path('notebooks/20_decode_earth_process_data.ipynb').write_text(json.dumps(nb,indent=1),encoding='utf-8')
