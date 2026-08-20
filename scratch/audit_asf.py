import urllib.request
import json
import pandas as pd

url = 'https://api.daac.asf.alaska.edu/services/search/param?bbox=86.4122,23.7461,86.4247,23.7653&platform=S1&processingLevel=SLC&beamMode=IW&relativeOrbit=121&flightDirection=DESCENDING&output=json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    res = urllib.request.urlopen(req, timeout=15)
    raw = json.loads(res.read())
    items = raw[0] if isinstance(raw, list) and len(raw) > 0 and isinstance(raw[0], list) else raw
    print(f"ASF DAAC API returned {len(items)} scenes for Orbit 121 Descending.")
    
    df = pd.DataFrame(items)
    print("Platforms in ASF data:", df['platform'].value_counts().to_dict() if 'platform' in df.columns else "N/A")
    
    # Sort by startTime
    if 'startTime' in df.columns:
        df['acq_date'] = df['startTime'].str[:10]
        df = df.sort_values(by='acq_date').reset_index(drop=True)
        print("\nSample real ASF scenes:")
        print(df[['acq_date', 'platform', 'relativeOrbit', 'flightDirection', 'granuleName']].head(15).to_string(index=False))
except Exception as e:
    print(f"Error querying ASF: {e}")
