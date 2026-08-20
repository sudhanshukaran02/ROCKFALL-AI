"""
Terrain Analysis Module for inspecting DEM metadata and statistical summaries.
"""

import os
import numpy as np

try:
    import rasterio
except ImportError:
    rasterio = None

from src.terrain_features import TerrainFeatureExtractor

def analyze_dem_metadata(dem_path):
    """
    Inspects a DEM GeoTIFF file and extracts metadata and statistical summaries.
    
    Parameters:
        dem_path (str): Path to DEM GeoTIFF raster file
        
    Returns:
        dict containing comprehensive DEM metadata and elevation/slope statistics
    """
    if rasterio is None:
        raise ImportError("rasterio is required for DEM analysis. Install via 'pip install rasterio'")
        
    if not os.path.exists(dem_path):
        raise FileNotFoundError(f"DEM raster file not found at '{dem_path}'.")
        
    # Instantiate extractor to compute slope and clean masks
    extractor = TerrainFeatureExtractor(dem_path)
    slope_deg, _ = extractor.compute_slope_and_aspect()
    
    elev_valid = extractor.clean_elevation[extractor.mask]
    slope_valid = slope_deg[extractor.mask]
    
    stats = {
        "dem_file": os.path.basename(dem_path),
        "dimensions": {
            "width": extractor.profile["width"],
            "height": extractor.profile["height"],
            "count": extractor.profile["count"]
        },
        "crs": str(extractor.crs),
        "resolution": {
            "x_resolution": abs(extractor.res[0]),
            "y_resolution": abs(extractor.res[1])
        },
        "bounds": {
            "left": extractor.bounds.left,
            "bottom": extractor.bounds.bottom,
            "right": extractor.bounds.right,
            "top": extractor.bounds.top
        },
        "elevation_stats": {
            "min_elevation_m": round(float(np.nanmin(elev_valid)), 2),
            "max_elevation_m": round(float(np.nanmax(elev_valid)), 2),
            "mean_elevation_m": round(float(np.nanmean(elev_valid)), 2),
            "std_elevation_m": round(float(np.nanstd(elev_valid)), 2)
        },
        "slope_stats": {
            "min_slope_deg": round(float(np.nanmin(slope_valid)), 2),
            "max_slope_deg": round(float(np.nanmax(slope_valid)), 2),
            "mean_slope_deg": round(float(np.nanmean(slope_valid)), 2),
            "std_slope_deg": round(float(np.nanstd(slope_valid)), 2)
        }
    }
    
    return stats

def print_dem_summary(dem_path):
    """Prints a clean human-readable summary of DEM metadata and stats."""
    info = analyze_dem_metadata(dem_path)
    print("="*60)
    print(f"DEM RASTER ANALYSIS SUMMARY: {info['dem_file']}")
    print("="*60)
    print(f"Dimensions : {info['dimensions']['width']} x {info['dimensions']['height']} pixels ({info['dimensions']['count']} band)")
    print(f"CRS        : {info['crs']}")
    print(f"Resolution : {info['resolution']['x_resolution']}m x {info['resolution']['y_resolution']}m per pixel")
    print(f"Bounds     : West={info['bounds']['left']:.1f}, South={info['bounds']['bottom']:.1f}, East={info['bounds']['right']:.1f}, North={info['bounds']['top']:.1f}")
    print("\nElevation Statistics:")
    print(f"  Min Elevation  : {info['elevation_stats']['min_elevation_m']} m")
    print(f"  Max Elevation  : {info['elevation_stats']['max_elevation_m']} m")
    print(f"  Mean Elevation : {info['elevation_stats']['mean_elevation_m']} m (std: {info['elevation_stats']['std_elevation_m']} m)")
    print("\nSlope Statistics:")
    print(f"  Min Slope  : {info['slope_stats']['min_slope_deg']}°")
    print(f"  Max Slope  : {info['slope_stats']['max_slope_deg']}°")
    print(f"  Mean Slope : {info['slope_stats']['mean_slope_deg']}° (std: {info['slope_stats']['std_slope_deg']}°)")
    print("="*60)
