from pathlib import Path
import json, shutil
import pandas as pd

src=Path('/tmp/k09full/earth_refined_validation')
out=Path('deliverable/marscope_dust_analog'); fig=out/'figures'; fig.mkdir(parents=True,exist_ok=True)
df=pd.read_parquet(src/'refined_earth_matches.parquet').sort_values('rank')
df.to_csv(out/'ranked_earth_candidates.csv',index=False); df.head(10).to_csv(out/'top_10_candidates.csv',index=False)
shutil.copy2(src/'refined_earth_matches.parquet',out/'refined_earth_matches.parquet')

def svg(name,body,w=1200,h=700,title=''):
    text=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<rect width="100%" height="100%" fill="#f8fafc"/><text x="40" y="45" font-family="Arial" font-size="25" font-weight="bold" fill="#0f172a">{title}</text>{body}</svg>'''
    (fig/name).write_text(text,encoding='utf-8')

def xmap(x): return 70+(x+125)/30*1080
def ymap(y): return 640-(y-25)/17*570
points=[]
for _,r in df.iterrows():
    color='#7c2d12' if r['rank']<=10 else '#f59e0b'
    points.append(f'<circle cx="{xmap(r.longitude):.1f}" cy="{ymap(r.latitude):.1f}" r="{7 if r["rank"]<=10 else 4}" fill="{color}" opacity=".78"/>')
for _,r in df.head(3).iterrows():
    points.append(f'<text x="{xmap(r.longitude)+8:.1f}" y="{ymap(r.latitude)-8:.1f}" font-family="Arial" font-size="15" fill="#0f172a">#{int(r["rank"])}</text>')
body=''.join(points)+'<path d="M70 640H1150M70 640V70" stroke="#334155"/><text x="560" y="680" font-family="Arial" font-size="16">Longitude (°)</text><text x="15" y="360" transform="rotate(-90 15 360)" font-family="Arial" font-size="16">Latitude (°)</text><text x="850" y="95" font-family="Arial" font-size="16" fill="#7c2d12">Top 10</text><text x="850" y="120" font-family="Arial" font-size="16" fill="#f59e0b">Other refined cells</text>'
svg('01_ranked_candidates_map.svg',body,title='MarsCOPE: Earth candidates compatible with a Mars dust/regolith signature')

bars=[]; top=df.head(10).iloc[::-1]
for i,(_,r) in enumerate(top.iterrows()):
    y=100+i*50
    for j,(col,color) in enumerate([('marginal_similarity','#f4a261'),('joint_similarity','#e76f51'),('spatial_coherence','#2a9d8f')]):
        bars.append(f'<rect x="{250+j*290}" y="{y}" width="{240*float(r[col]):.1f}" height="12" fill="{color}"/><text x="{250+j*290+245}" y="{y+11}" font-family="Arial" font-size="12">{float(r[col]):.3f}</text>')
        bars.append(f'<text x="55" y="{y+12}" font-family="Arial" font-size="14">#{int(r["rank"])} {r.latitude:.0f}°, {r.longitude:.0f}°</text>')
body=''.join(bars)+'<text x="250" y="75" font-family="Arial" font-size="14">Marginal</text><text x="540" y="75" font-family="Arial" font-size="14">Joint</text><text x="830" y="75" font-family="Arial" font-size="14">Spatial</text>'
svg('02_score_components.svg',body,title='Why the leading candidates rank highly')

best=df.iloc[0]
summary={'candidate_count':int(len(df)),'top_location':{'latitude':float(best.latitude),'longitude':float(best.longitude),'rank':int(best['rank']),'analog_score':float(best.analog_score)},'top10_mean_score':float(df.head(10).analog_score.mean()),'process':'regolith_mantling_or_dust_cover','excluded_context_sites':True}
(out/'result_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
readme=f'''# MarsCOPE — strongest result: dust/regolith analog

The unsupervised Earth search returned {len(df)} refined land cells. The highest-ranked cell is approximately {best.latitude:.0f}°N, {abs(best.longitude):.0f}°W (rank 1; score {best.analog_score:.3f}). The candidates form a coherent southwestern United States cluster. The challenge's named example sites were excluded from the reported result.

The ranking is based on a Mars dust/regolith-compatible process distribution, not visual resemblance. Earth cells are compared using annual surface albedo, precipitation-derived aridity, wind, temperature range, elevation, and spatial coherence. Each variable is converted to a percentile before comparison.

The score combines marginal similarity, joint similarity, and spatial coherence. The top cell has analog score {best.analog_score:.3f}, marginal similarity {best.marginal_similarity:.3f}, joint similarity {best.joint_similarity:.3f}, and spatial coherence {best.spatial_coherence:.3f}.

## Why it matches

- dry, particulate-friendly conditions represented by aridity and wind;
- surface-brightness behavior represented by albedo;
- terrain context represented by elevation;
- a coherent cluster rather than an isolated pixel.

## Where it differs

Earth has a dense atmosphere, liquid water, Earth gravity, and no Mars-like radiation environment. These variables are process proxies and do not prove active Mars-equivalent dust transport. This is a test-site shortlist, not a claim that Mars dust storms occur on Earth.

## Mission value

The cluster can support testing of dust-sensitive optics, contamination procedures, rover mobility and navigation, sampling workflows, terrain mapping, and environmental monitoring. Higher-resolution wind, aerosol, geology, and field measurements are required before selecting a physical test site.

The figures are SVG and require no extra software to view. The ranked CSV preserves every score component.
'''
(out/'README.md').write_text(readme,encoding='utf-8'); (out/'scientific_interpretation.md').write_text(readme,encoding='utf-8')
(out/'data_provenance.json').write_text(json.dumps({'mars_reference':'NASA PDS-derived Mars process distributions from notebooks 01, 03, and 06','earth_screening':'NASA POWER and land-mask refinement from notebooks 08 and 09','process_registry':'Literature-backed Mars process registry in notebook 06','method':'percentile-normalized marginal and joint similarity plus spatial coherence','context_sites_used_as_reported_results':False},indent=2),encoding='utf-8')
