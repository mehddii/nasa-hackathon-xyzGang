import json
from pathlib import Path

intro = '''# 19 — Direct Earth measurements for process matching

This notebook searches the top Earth candidates and downloads a bounded sample of actual measurement files. It does not pretend that precipitation or temperature are mineral or ice measurements. The files are preserved with checksums for product-specific decoding in the next step.
'''
code = '''from pathlib import Path
import hashlib, json, os, zipfile, requests, pandas as pd
from IPython.display import display

ROOTS = [Path('/kaggle/working'), Path('/kaggle/input')]
def find(name):
    for root in ROOTS:
        if root.exists():
            hits = list(root.rglob(name))
            if hits: return hits[0]
    raise FileNotFoundError(name)

matches = pd.read_parquet(find('refined_earth_matches.parquet')).sort_values('rank').head(20)
OUT = Path('/kaggle/working/earth_direct_measurements'); OUT.mkdir(exist_ok=True)
token = os.environ.get('EARTHDATA_TOKEN')
secret_error = None
try:
    from kaggle_secrets import UserSecretsClient
    token = UserSecretsClient().get_secret('EARTHDATA_TOKEN')
except Exception as exc:
    secret_error = f'{type(exc).__name__}: {exc}'
if not token:
    print('WARNING: EARTHDATA_TOKEN is unavailable; CMR metadata may work, protected downloads may fail.')
    if secret_error: print('Secret lookup:', secret_error)
headers = {'Authorization': f'Bearer {token}'} if token else {}
collections = {
    'EMITL2ARFL': 'C4079844428-LPCLOUD',
    'MOD10CM': 'C3050353608-NSIDC_CPRD',
    'SPL3SMP': 'C2938664585-NSIDC_CPRD',
    'NASADEM_HGT': 'C2763264762-LPCLOUD',
}
rows = []
for cell in matches.itertuples():
    for product, cid in collections.items():
        bbox = f'{cell.longitude-0.5},{cell.latitude-0.5},{cell.longitude+0.5},{cell.latitude+0.5}'
        query = {'collection_concept_id': cid, 'page_size': 3, 'downloadable': 'true', 'bounding_box': bbox}
        try:
            response = requests.get('https://cmr.earthdata.nasa.gov/search/granules.json', params=query, headers=headers, timeout=45)
            response.raise_for_status()
            entries = response.json().get('feed', {}).get('entry', [])
            for entry in entries:
                links = [x.get('href') for x in entry.get('links', []) if x.get('href') and ('data' in x.get('rel', '') or x.get('title', '').lower() in ('download', 'direct download'))]
                rows.append({'rank': cell.rank, 'latitude': cell.latitude, 'longitude': cell.longitude, 'product': product, 'granule_id': entry.get('id'), 'time_start': entry.get('time_start'), 'download_url': links[0] if links else None, 'metadata_only': True})
        except Exception as exc:
            rows.append({'rank': cell.rank, 'latitude': cell.latitude, 'longitude': cell.longitude, 'product': product, 'granule_id': None, 'time_start': None, 'download_url': None, 'metadata_only': True, 'error': f'{type(exc).__name__}: {exc}'})
manifest = pd.DataFrame(rows)
manifest.to_csv(OUT/'direct_measurement_manifest.csv', index=False)
manifest.to_parquet(OUT/'direct_measurement_manifest.parquet', index=False)

download_dir = OUT/'files'; download_dir.mkdir(exist_ok=True)
download_rows = []
for product, group in manifest.dropna(subset=['download_url']).groupby('product', sort=False):
    row = group.iloc[0].to_dict(); url = row['download_url']
    target = download_dir/(product + '_' + Path(url.split('?')[0]).name)
    try:
        total = 0; digest = hashlib.sha256()
        with requests.get(url, headers=headers, stream=True, timeout=90, allow_redirects=True) as response:
            response.raise_for_status()
            with target.open('wb') as handle:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if not chunk: continue
                    total += len(chunk)
                    if total > 200*1024*1024: raise RuntimeError('download exceeded 200 MiB safety limit')
                    handle.write(chunk); digest.update(chunk)
        row.update({'downloaded': True, 'local_path': str(target), 'bytes': total, 'sha256': digest.hexdigest(), 'download_error': None})
    except Exception as exc:
        if target.exists(): target.unlink()
        row.update({'downloaded': False, 'local_path': None, 'bytes': 0, 'sha256': None, 'download_error': f'{type(exc).__name__}: {exc}'})
    download_rows.append(row)
downloads = pd.DataFrame(download_rows)
downloads.to_csv(OUT/'downloaded_measurements.csv', index=False)
downloads.to_parquet(OUT/'downloaded_measurements.parquet', index=False)
archive = OUT/'earth_measurement_files.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
    for p in download_dir.iterdir():
        if p.is_file(): bundle.write(p, arcname=p.name)
decoded_rows = []
try:
    import numpy as np, h5py
    for row in downloads[downloads.downloaded].to_dict('records'):
        path = Path(row['local_path'])
        if path.suffix.lower() not in ('.h5', '.hdf5', '.nc', '.he5'): continue
        with h5py.File(path, 'r') as handle:
            def visit(name, obj):
                if not hasattr(obj, 'shape') or not np.issubdtype(obj.dtype, np.number) or obj.size == 0: return
                values = np.asarray(obj[...], dtype='float64').ravel()
                values = values[np.isfinite(values)]
                if values.size:
                    decoded_rows.append({'product': row['product'], 'dataset': name, 'shape': str(obj.shape), 'count': int(values.size), 'mean': float(values.mean()), 'std': float(values.std()), 'min': float(values.min()), 'max': float(values.max())})
            handle.visititems(visit)
except Exception as exc:
    decoded_rows.append({'product': '__decoder__', 'dataset': '__decode_error__', 'error': f'{type(exc).__name__}: {exc}'})
decoded = pd.DataFrame(decoded_rows)
decoded.to_csv(OUT/'decoded_numeric_features.csv', index=False)
decoded.to_parquet(OUT/'decoded_numeric_features.parquet', index=False)
summary = {
    'candidate_cells': int(len(matches)), 'products': collections,
    'earthdata_token_available': bool(token), 'secret_error': secret_error,
    'granules_found': int(manifest.granule_id.notna().sum()),
    'download_attempts': int(len(downloads)),
    'downloaded_files': int(downloads.downloaded.sum()) if len(downloads) else 0,
    'archive': str(archive),
    'decoded_numeric_rows': int(len(decoded)),
    'note': 'Downloaded files are raw product files; product-specific decoding and QA masking are required before process scores.'
}
(OUT/'manifest_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
display(manifest.groupby('product').size().rename('granules'))
display(downloads[['product','downloaded','bytes','download_error']] if len(downloads) else downloads)
print(json.dumps(summary, indent=2))
'''
nb = {'cells': [
    {'cell_type': 'markdown', 'metadata': {}, 'source': intro.splitlines(True)},
    {'cell_type': 'code', 'execution_count': None, 'metadata': {}, 'outputs': [], 'source': code.splitlines(True)},
], 'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python', 'version': '3.11'}}, 'nbformat': 4, 'nbformat_minor': 5}
Path('notebooks/19_earth_process_data_extraction.ipynb').write_text(json.dumps(nb, indent=1), encoding='utf-8')
