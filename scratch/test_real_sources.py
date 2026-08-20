import urllib.request
import json
import pandas as pd
import numpy as np

lat, lon = 23.7536, 86.4167

print("=== TESTING REAL DATA API SOURCES FOR RAJAPUR (23.7536°N, 86.4167°E) ===")

# 1. NASA POWER API for Rainfall
print("\n1. Testing NASA POWER API (Precipitation)...")
try:
    url_rain = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR&community=RE&longitude={lon}&latitude={lat}&start=20230101&end=20231231&format=JSON"
    req = urllib.request.Request(url_rain, headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req, timeout=10)
    data_rain = json.loads(res.read())
    precip_dict = data_rain['properties']['parameter']['PRECTOTCORR']
    precip_vals = [v for k, v in precip_dict.items() if v >= 0]
    print(f"  NASA POWER API Success: Returned {len(precip_vals)} daily rainfall records for 2023.")
    print(f"  2023 Annual Rainfall Sum: {sum(precip_vals):.1f} mm | Max Daily: {max(precip_vals):.1f} mm | Mean Daily: {np.mean(precip_vals):.2f} mm")
except Exception as e:
    print(f"  NASA POWER API Error: {e}")

# 2. ISRIC SoilGrids API for Soil Composition
print("\n2. Testing ISRIC SoilGrids API (Sand/Silt/Clay/Coarse)...")
try:
    url_soil = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=sand&property=silt&property=clay&depths=0-5cm&values=mean"
    req = urllib.request.Request(url_soil, headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req, timeout=10)
    data_soil = json.loads(res.read())
    layers = data_soil['properties']['layers']
    soil_dict = {}
    for layer in layers:
        name = layer['name']
        val = layer['depths'][0]['values']['mean'] / 10.0 # SoilGrids returns g/kg -> %
        soil_dict[name] = val
    print(f"  ISRIC SoilGrids Success (0-5cm depth):")
    print(f"  Sand: {soil_dict.get('sand', 0):.1f}% | Silt: {soil_dict.get('silt', 0):.1f}% | Clay: {soil_dict.get('clay', 0):.1f}%")
except Exception as e:
    print(f"  ISRIC SoilGrids Error: {e}")

# 3. USGS Earthquake API
print("\n3. Testing USGS Earthquake API (200km radius around Dhanbad)...")
try:
    url_eq = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&latitude={lat}&longitude={lon}&maxradiuskm=200&starttime=2000-01-01"
    req = urllib.request.Request(url_eq, headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req, timeout=10)
    data_eq = json.loads(res.read())
    count = data_eq['metadata']['count']
    events = data_eq['features']
    print(f"  USGS Seismicity Success: {count} historical earthquakes (M>=1.0) recorded within 200km of Rajapur since 2000.")
    if count > 0:
        mags = [e['properties']['mag'] for e in events if e['properties']['mag'] is not None]
        print(f"  Max Magnitude: {max(mags):.1f} Richter | Mean Magnitude: {np.mean(mags):.1f} Richter")
except Exception as e:
    print(f"  USGS Earthquake API Error: {e}")

# 4. OpenStreetMap Overpass API for Hydrography / Water Features
print("\n4. Testing OpenStreetMap Overpass API (Water features near Rajapur)...")
try:
    overpass_query = f"""
    [out:json];
    (
      way["natural"="water"]({lat-0.03},{lon-0.03},{lat+0.03},{lon+0.03});
      way["waterway"]({lat-0.03},{lon-0.03},{lat+0.03},{lon+0.03});
      relation["waterway"]({lat-0.03},{lon-0.03},{lat+0.03},{lon+0.03});
    );
    out geom;
    """
    url_osm = "https://overpass-api.de/api/interpreter"
    req = urllib.request.Request(url_osm, data=overpass_query.encode('utf-8'), headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'})
    res = urllib.request.urlopen(req, timeout=12)
    data_osm = json.loads(res.read())
    elements = data_osm.get('elements', [])
    print(f"  OSM Overpass Hydrography Success: {len(elements)} mapped water features / streams found in Rajapur vicinity.")
except Exception as e:
    print(f"  OSM Overpass API Error: {e}")
