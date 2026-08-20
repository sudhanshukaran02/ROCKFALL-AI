"""
Spatial Feature Dataset Creation Script for Rockfall AI.

Extracts spatially aligned tabular terrain features (latitude, longitude, elevation,
slope, aspect, curvature, roughness, twi) from real SRTM DEM and derived rasters.
Supports optional AOI GeoJSON polygon masking and subsampling for testing.
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask as rasterio_mask
from rasterio.warp import transform_geom

def extract_geojson_shapes(geojson_path, target_crs='EPSG:4326'):
    """Reads GeoJSON file and extracts shapes, reprojecting to target_crs if needed."""
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Determine input CRS from GeoJSON metadata if present
    src_crs = 'EPSG:4326'
    if 'crs' in data and isinstance(data['crs'], dict):
        properties = data['crs'].get('properties', {})
        name = properties.get('name', '')
        if '32645' in name or 'UTM' in name.upper():
            src_crs = 'EPSG:32645'
        elif '4326' in name or 'CRS84' in name:
            src_crs = 'EPSG:4326'
            
    # Extract raw geometry objects
    raw_shapes = []
    if data.get('type') == 'FeatureCollection':
        for feat in data.get('features', []):
            if 'geometry' in feat and feat['geometry']:
                raw_shapes.append(feat['geometry'])
    elif data.get('type') == 'Feature':
        if 'geometry' in data and data['geometry']:
            raw_shapes.append(data['geometry'])
    elif data.get('type') in ['Polygon', 'MultiPolygon']:
        raw_shapes.append(data)
    else:
        raise ValueError(f"Unsupported GeoJSON format at '{geojson_path}'.")
        
    if len(raw_shapes) == 0:
        raise ValueError(f"No valid geometries found in GeoJSON '{geojson_path}'.")
        
    # Reproject geometry if src_crs differs from target_crs
    if src_crs != target_crs:
        reprojected_shapes = [transform_geom(src_crs, target_crs, geom) for geom in raw_shapes]
        return reprojected_shapes
    else:
        return raw_shapes

def process_spatial_features(dem_path='data/mine_dem.tif',
                             terrain_dir='results/terrain/real',
                             aoi_path=None,
                             max_samples=None,
                             output_csv='results/terrain/spatial_features.csv',
                             output_summary='results/terrain/spatial_feature_summary.md'):
    """
    Verifies rasters, extracts spatially aligned features with coordinates,
    handles NoData/NaN/Inf values, crops to AOI if provided, and exports CSV + MD.
    """
    print("==========================================================")
    print("SPATIAL TERRAIN FEATURE DATASET EXTRACTION")
    print("==========================================================")
    
    # 1. Verify existence of required rasters
    layer_names = ['elevation', 'slope', 'aspect', 'curvature', 'roughness', 'twi']
    raster_paths = {'dem': dem_path}
    for name in layer_names:
        p = os.path.join(terrain_dir, f"{name}.tif")
        if not os.path.exists(p):
            raise FileNotFoundError(f"Required terrain layer missing: '{p}'.")
        raster_paths[name] = p
        
    # 2. Open DEM to check reference metadata
    with rasterio.open(dem_path) as ref_src:
        ref_crs = ref_src.crs
        ref_shape = (ref_src.height, ref_src.width)
        ref_transform = ref_src.transform
        ref_bounds = ref_src.bounds
        ref_res = ref_src.res
        dem_nodata = ref_src.nodata
        
    print(f"  Reference DEM : '{dem_path}'")
    print(f"  Raster Size   : {ref_shape[1]} x {ref_shape[0]} pixels")
    print(f"  CRS           : {ref_crs}")
    print(f"  Resolution    : {ref_res[0]:.10f}° x {ref_res[1]:.10f}°")
    print(f"  Bounds        : West={ref_bounds.left:.6f}°, South={ref_bounds.bottom:.6f}°, East={ref_bounds.right:.6f}°, North={ref_bounds.top:.6f}°")
    
    # 3. Verify spatial alignment across all derived rasters
    for name in layer_names:
        with rasterio.open(raster_paths[name]) as src:
            if (src.height, src.width) != ref_shape:
                raise ValueError(f"Dimension mismatch in {name}.tif: {(src.width, src.height)} vs {ref_shape}")
            if src.crs != ref_crs:
                raise ValueError(f"CRS mismatch in {name}.tif: {src.crs} vs {ref_crs}")
            if src.transform != ref_transform:
                raise ValueError(f"Transform mismatch in {name}.tif: {src.transform} vs {ref_transform}")
    print("  QC Alignment  : All 7 rasters have identical dimensions, CRS, transform, and bounds. (PASSED)")

    # 4. Load or crop rasters
    dataset_label = "Full-Tile Dataset (Testing / Unclipped)"
    shapes = None
    if aoi_path and os.path.exists(aoi_path):
        print(f"\n  AOI Masking   : Loading AOI GeoJSON from '{aoi_path}'...")
        shapes = extract_geojson_shapes(aoi_path, target_crs=str(ref_crs))
        dataset_label = f"Mine AOI Clipped Dataset (AOI: {os.path.basename(aoi_path)})"
    elif aoi_path:
        raise FileNotFoundError(f"Specified AOI GeoJSON file not found at '{aoi_path}'.")
    else:
        print("\n  AOI Masking   : No AOI specified. Processing full-tile raster dataset.")

    raster_arrays = {}
    effective_transform = ref_transform
    
    for name in ['dem'] + layer_names:
        with rasterio.open(raster_paths[name]) as src:
            if shapes:
                out_img, out_trans = rasterio_mask(src, shapes, crop=True, nodata=-9999.0)
                raster_arrays[name] = out_img[0].astype(np.float64)
                effective_transform = out_trans
            else:
                raster_arrays[name] = src.read(1).astype(np.float64)

    # 5. Coordinate calculation for pixel centers
    height, width = raster_arrays['dem'].shape
    cols, rows = np.meshgrid(np.arange(width), np.arange(height))
    longitudes = effective_transform.c + (cols + 0.5) * effective_transform.a
    latitudes = effective_transform.f + (rows + 0.5) * effective_transform.e
    
    total_pixels = height * width
    
    # 6. Build valid pixel mask
    valid_mask = np.ones((height, width), dtype=bool)
    
    # Exclude NoData / NaN / Inf across all layers
    for name, arr in raster_arrays.items():
        valid_mask &= (arr != -9999.0)
        if dem_nodata is not None and not np.isnan(dem_nodata):
            valid_mask &= (arr != dem_nodata)
        valid_mask &= ~np.isnan(arr)
        valid_mask &= ~np.isinf(arr)

    # Physical domain filters
    valid_mask &= (raster_arrays['slope'] >= 0.0) & (raster_arrays['slope'] <= 90.0)
    valid_mask &= (raster_arrays['aspect'] >= 0.0) & (raster_arrays['aspect'] <= 360.0)
    valid_mask &= (raster_arrays['elevation'] >= -500.0) & (raster_arrays['elevation'] <= 9000.0)
    
    valid_count = int(np.sum(valid_mask))
    excluded_count = int(total_pixels - valid_count)
    
    print(f"  Total Pixels  : {total_pixels:,}")
    print(f"  Valid Pixels  : {valid_count:,}")
    print(f"  Excluded      : {excluded_count:,}")
    
    if valid_count == 0:
        raise ValueError("No valid pixels found after AOI cropping and NoData filtering!")

    # 7. Extract tabular data
    flat_lats = latitudes[valid_mask]
    flat_lons = longitudes[valid_mask]
    
    feature_dict = {
        'latitude': flat_lats,
        'longitude': flat_lons,
        'elevation': raster_arrays['dem'][valid_mask],
        'slope': raster_arrays['slope'][valid_mask],
        'aspect': raster_arrays['aspect'][valid_mask],
        'curvature': raster_arrays['curvature'][valid_mask],
        'roughness': raster_arrays['roughness'][valid_mask],
        'twi': raster_arrays['twi'][valid_mask]
    }
    
    df = pd.DataFrame(feature_dict)
    
    # 8. Apply max_samples capping if specified
    if max_samples and len(df) > max_samples:
        print(f"\n  Subsampling   : Capping {len(df):,} valid pixels to max_samples={max_samples:,} for testing.")
        df = df.sample(n=max_samples, random_state=42).sort_index().reset_index(drop=True)
        sampled_note = f"Subsampled {max_samples:,} pixels from {valid_count:,} total valid pixels."
    else:
        sampled_note = f"Full extraction of all {valid_count:,} valid pixels."

    # 9. Save CSV output
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"  Saved CSV     : '{output_csv}' ({len(df):,} rows, {len(df.columns)} columns)")

    # 10. Generate Markdown Summary Report
    stats_rows = []
    for col in df.columns:
        vals = df[col]
        stats_rows.append({
            "Feature": col,
            "Min": round(float(vals.min()), 6),
            "Max": round(float(vals.max()), 6),
            "Mean": round(float(vals.mean()), 6),
            "Median": round(float(vals.median()), 6),
            "Std": round(float(vals.std()), 6)
        })
    df_summary_stats = pd.DataFrame(stats_rows)

    lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
    lon_min, lon_max = df['longitude'].min(), df['longitude'].max()
    
    summary_md = f"""# Spatial Terrain Feature Dataset Summary

**Dataset Label:** {dataset_label}  
**Input DEM:** `{dem_path}`  
**Terrain Layer Directory:** `{terrain_dir}`  
**AOI GeoJSON Path:** `{aoi_path if aoi_path else 'None (Full Tile)'}`  
**Extraction Note:** {sampled_note}  

---

## 1. Spatial & Dataset Overview

| Parameter | Value |
| :--- | :--- |
| **Dataset Type** | {dataset_label} |
| **CRS** | `{ref_crs}` |
| **Pixel Resolution** | `{ref_res[0]:.10f}° x {ref_res[1]:.10f}°` (approx 28.4m lon x 30.9m lat) |
| **Geographic Bounds (Data)** | Latitude: [{lat_min:.6f}°, {lat_max:.6f}°], Longitude: [{lon_min:.6f}°, {lon_max:.6f}°] |
| **Exported Rows (Pixels)** | **{len(df):,}** |
| **Total Area Pixels** | {total_pixels:,} |
| **Valid Pixels Found** | {valid_count:,} |
| **Excluded / NoData Pixels** | {excluded_count:,} |

---

## 2. Feature Statistics

The extracted tabular dataset contains **{len(df.columns)} features**: `latitude`, `longitude`, `elevation`, `slope`, `aspect`, `curvature`, `roughness`, `twi`.

| Feature | Min | Max | Mean | Median | Std Dev |
| :--- | :---: | :---: | :---: | :---: | :---: |
"""
    for r in stats_rows:
        summary_md += f"| **{r['Feature']}** | {r['Min']} | {r['Max']} | {r['Mean']} | {r['Median']} | {r['Std']} |\n"

    summary_md += f"""

---

## 3. Data Integrity & Alignment Verification

- **Spatial Alignment:** Verified 100% spatial transform and cell boundary alignment across all 7 input rasters.
- **Coordinate Integrity:** Derived pixel-center latitude/longitude using exact affine spatial transform matrix.
- **Null & Invalid Values:** **0** null/NaN values, **0** infinite values, and **0** NoData (-9999.0) values present in exported CSV.
- **Domain Constraints:** All slope values within [0°, 90°], aspect within [0°, 360°], elevation within valid physical range.

---

## IMPORTANT SCIENTIFIC NOTE

> [!WARNING]
> **Spatial Intelligence & Morphological Disclaimer**:
> This dataset provides spatial terrain features for geographic intelligence and susceptibility modeling.
> Do NOT interpret steep slope as automatically meaning rockfall.
> Terrain layers must later be combined with geological, environmental, structural, and sensor evidence.
> No machine learning models were trained during this step.
"""

    os.makedirs(os.path.dirname(output_summary), exist_ok=True)
    with open(output_summary, 'w', encoding='utf-8') as f:
        f.write(summary_md)
    print(f"  Saved Summary : '{output_summary}'")
    
    print("\n==========================================================")
    print("SPATIAL FEATURE EXTRACTION COMPLETE & VERIFIED")
    print("==========================================================")
    return df, df_summary_stats

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create Spatial Feature Dataset from Terrain Rasters.")
    parser.add_argument('--dem', type=str, default='data/mine_dem.tif', help='Path to DEM GeoTIFF')
    parser.add_argument('--terrain_dir', type=str, default='results/terrain/real', help='Path to derived terrain rasters directory')
    parser.add_argument('--aoi', type=str, default=None, help='Optional path to GeoJSON AOI file')
    parser.add_argument('--max_samples', type=int, default=None, help='Optional max sample cap for testing')
    parser.add_argument('--output_csv', type=str, default='results/terrain/spatial_features.csv', help='Path for output CSV')
    parser.add_argument('--output_summary', type=str, default='results/terrain/spatial_feature_summary.md', help='Path for output summary markdown')
    
    args = parser.parse_args()
    
    # If no AOI is supplied and no max_samples is supplied, default max_samples=5000 for full-tile testing safety
    if args.aoi is None and args.max_samples is None:
        print("Notice: No AOI specified. Setting default max_samples=5000 for full-tile testing safety.")
        args.max_samples = 5000
        
    process_spatial_features(
        dem_path=args.dem,
        terrain_dir=args.terrain_dir,
        aoi_path=args.aoi,
        max_samples=args.max_samples,
        output_csv=args.output_csv,
        output_summary=args.output_summary
    )
