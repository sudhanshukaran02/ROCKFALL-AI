import urllib.request
import json
import pandas as pd
import numpy as np

url = 'https://api.daac.asf.alaska.edu/services/search/param?bbox=86.4122,23.7461,86.4247,23.7653&platform=S1&processingLevel=SLC&beamMode=IW&relativeOrbit=121&flightDirection=DESCENDING&output=json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

res = urllib.request.urlopen(req, timeout=15)
data = json.loads(res.read())
items = data[0] if isinstance(data, list) and isinstance(data[0], list) else data

asf_df = pd.DataFrame(items)
asf_df['acq_date'] = pd.to_datetime(asf_df['startTime'].str[:10])
asf_df = asf_df.sort_values(by='acq_date').reset_index(drop=True)

manifest_df = pd.read_csv('data/insar/download_manifest.csv')
manifest_df['m_date'] = pd.to_datetime(manifest_df['acquisition_date'])

audit_records = []
for idx, row in manifest_df.iterrows():
    m_d = row['m_date']
    m_plat = 'SENTINEL-1D' if '1D' in str(row['notes']) or '1D' in str(row['product_id']) else ('SENTINEL-1B' if '1B' in str(row['notes']) else 'SENTINEL-1A')
    pid = str(row['product_id'])
    
    # Find closest real ASF acquisition date
    diffs = np.abs((asf_df['acq_date'] - m_d).dt.days)
    closest_idx = diffs.idxmin()
    closest_row = asf_df.iloc[closest_idx]
    
    v_date = closest_row['acq_date'].strftime('%Y-%m-%d')
    v_plat = str(closest_row['platform']).upper()
    v_granule = str(closest_row['granuleName'])
    v_url = str(closest_row['downloadUrl'])
    
    plat_match = (m_plat.replace('-', '').upper() == v_plat.replace('-', '').upper())
    date_match = (row['acquisition_date'] == v_date)
    id_match = pid.startswith('S1') and (pid == v_granule)
    
    overall_match = plat_match and date_match and id_match
    
    notes = []
    if not plat_match:
        notes.append(f"Platform Mismatch: Manifest lists {m_plat}, but actual ASF DAAC platform is {v_plat}.")
    if not date_match:
        notes.append(f"Date Offset: Manifest date {row['acquisition_date']} vs nearest actual ASF date {v_date}.")
    if not id_match:
        notes.append(f"Granule ID Mismatch: Manifest product_id '{pid}' vs actual ASF granule '{v_granule}'.")
    
    audit_records.append({
        'scene_id': row['scene_id'],
        'manifest_date': row['acquisition_date'],
        'verified_date': v_date,
        'manifest_platform': m_plat,
        'verified_platform': v_plat,
        'relative_orbit': '121',
        'flight_direction': 'DESCENDING',
        'mode': 'IW',
        'product_type': 'SLC',
        'polarization': 'VV+VH',
        'product_id': pid,
        'verified_product_id': v_granule,
        'verified_download_url': v_url,
        'metadata_match': 'MATCH' if overall_match else 'MISMATCH',
        'notes': " | ".join(notes) if notes else "Metadata matches ASF DAAC record."
    })

audit_df = pd.DataFrame(audit_records)
print("Audit summary:")
print(f"Total scenes: {len(audit_df)}")
print(f"Metadata matches: {np.sum(audit_df['metadata_match'] == 'MATCH')}")
print(f"Metadata mismatches: {np.sum(audit_df['metadata_match'] == 'MISMATCH')}")

print("\nSample audit records with mismatches:")
print(audit_df[audit_df['metadata_match'] == 'MISMATCH'][['scene_id', 'manifest_date', 'verified_date', 'manifest_platform', 'verified_platform', 'metadata_match', 'notes']].head(10).to_string(index=False))
