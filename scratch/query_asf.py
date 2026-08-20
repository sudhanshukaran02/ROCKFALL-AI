import urllib.request
import json
import pandas as pd

url = 'https://api.daac.asf.alaska.edu/services/search/param?bbox=86.412,23.746,86.425,23.766&platform=S1&processingLevel=SLC&beamMode=IW&output=json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    res = urllib.request.urlopen(req)
    raw = json.loads(res.read())
    print(f"Raw response type: {type(raw)}, length: {len(raw)}")
    
    # Flatten if data is wrapped in a list of lists
    items = raw[0] if isinstance(raw, list) and len(raw) > 0 and isinstance(raw[0], list) else raw
    print(f"Total acquisition items: {len(items)}")
    
    records = []
    for item in items:
        if not isinstance(item, dict):
            continue
        start_time = item.get('startTime', '')
        acq_date = start_time[:10] if start_time else 'UNKNOWN'
        sat = item.get('platform', 'SENTINEL-1')
        flight_dir = item.get('flightDirection', 'UNKNOWN')
        rel_orbit = item.get('relativeOrbit', 'UNKNOWN')
        prod_type = item.get('processingLevel', 'SLC')
        mode = item.get('beamMode', 'IW')
        pol = item.get('polarization', 'VV+VH')
        granule = item.get('granuleName', '')
        url_download = item.get('downloadUrl', f"https://datapool.asf.alaska.edu/SLC/SA/{granule}.zip")
        
        records.append({
            'acquisition_date': acq_date,
            'satellite': sat,
            'orbit_direction': flight_dir,
            'relative_orbit': rel_orbit,
            'product_type': prod_type,
            'mode': mode,
            'polarization': pol,
            'footprint_intersects_aoi': True,
            'source': 'ASF DAAC / NASA Earthdata',
            'source_url': url_download,
            'product_id': granule,
            'notes': f"Sentinel-1 {sat} IW SLC scene covering Rajapur AOI (Orbit {rel_orbit}, {flight_dir})"
        })
        
    df = pd.DataFrame(records)
    print(f"Parsed {len(df)} acquisitions.")
    if len(df) > 0:
        print("\nFirst 10 acquisitions:")
        print(df[['acquisition_date', 'satellite', 'orbit_direction', 'relative_orbit', 'polarization', 'product_id']].head(10).to_string(index=False))
except Exception as e:
    print(f"Error: {e}")
