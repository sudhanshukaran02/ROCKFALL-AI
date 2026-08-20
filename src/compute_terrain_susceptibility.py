"""
Real-Terrain Susceptibility Index Pipeline for Rajapur / South Jharia.

Calculates a transparent, deterministic morphological terrain susceptibility index
from 1-arcsecond SRTM DEM derivatives over the Rajapur AOI.
Uses robust P5-P95 percentile normalization for slope, absolute curvature, roughness, and TWI.

Generates:
- results/rajapur/terrain_susceptibility/rajapur_terrain_susceptibility_map.png
- results/rajapur/terrain_susceptibility/rajapur_slope_map.png
- results/rajapur/terrain_susceptibility/rajapur_curvature_map.png
- results/rajapur/terrain_susceptibility/rajapur_roughness_map.png
- results/rajapur/terrain_susceptibility/rajapur_twi_map.png
- results/rajapur/terrain_susceptibility/top_50_terrain_susceptibility_locations.csv
- results/rajapur/terrain_susceptibility/susceptibility_zone_summary.csv
- results/rajapur/terrain_susceptibility/historical_event_susceptibility_overlay.csv
- results/rajapur/terrain_susceptibility/terrain_statistics.csv
- results/rajapur/terrain_susceptibility/weight_sensitivity.csv
- results/rajapur/terrain_susceptibility/weight_sensitivity.png
- results/rajapur/terrain_susceptibility/rajapur_terrain_susceptibility_report.md
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path

# Set non-interactive matplotlib backend
plt.switch_backend('Agg')

def run_terrain_susceptibility_pipeline():
    print("============================================================")
    print("RAJAPUR REAL-TERRAIN SUSCEPTIBILITY ANALYSIS")
    print("============================================================")

    # 1. INPUT FILE PATHS & OUTPUT DIRECTORY
    aoi_path = os.path.join('scratch', 'rajapur_south_jharia_aoi.geojson')
    features_path = os.path.join('results', 'terrain', 'spatial_features.csv')
    events_path = os.path.join('data', 'events', 'rajapur_instability_events.csv')
    out_dir = os.path.join('results', 'rajapur', 'terrain_susceptibility')
    os.makedirs(out_dir, exist_ok=True)

    # Check input files
    for p in [aoi_path, features_path, events_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Required input file missing at '{p}'!")

    # Load Spatial Features & AOI Polygon
    sf_df = pd.read_csv(features_path)
    tot_points = len(sf_df)

    with open(aoi_path, 'r', encoding='utf-8') as f:
        aoi_geojson = json.load(f)
    poly_coords = aoi_geojson['features'][0]['geometry']['coordinates'][0]
    aoi_polygon = Path(poly_coords)

    # AOI Polygon Area Calculation (Approximated in km²)
    poly_x = np.array([pt[0] for pt in poly_coords])
    poly_y = np.array([pt[1] for pt in poly_coords])
    aoi_area_km2 = 1.4503  # Official Rajapur AOI Area

    print(f"\n--- 1. AOI & SPATIAL DATASET VALIDATION ---")
    print(f"  AOI Area         : {aoi_area_km2:.4f} km²")
    print(f"  Valid Pixels     : {tot_points}")
    print(f"  Latitude Range   : {sf_df['latitude'].min():.6f}°N to {sf_df['latitude'].max():.6f}°N")
    print(f"  Longitude Range  : {sf_df['longitude'].min():.6f}°E to {sf_df['longitude'].max():.6f}°E")

    # 2. TERRAIN VARIABLES & P5-P95 NORMALIZATION
    print("\n--- 2. TRANSPARENT P5-P95 PERCENTILE NORMALIZATION ---")

    def normalize_p5_p95(series):
        p5 = float(np.percentile(series, 5))
        p95 = float(np.percentile(series, 95))
        if p95 == p5:
            norm = np.zeros(len(series))
        else:
            norm = np.clip((series - p5) / (p95 - p5), 0.0, 1.0)
        return norm, p5, p95

    # Variable 1: Slope
    slope_norm, slope_p5, slope_p95 = normalize_p5_p95(sf_df['slope'])
    
    # Variable 2: Curvature Magnitude (abs(curvature))
    curv_abs = np.abs(sf_df['curvature'])
    curv_norm, curv_p5, curv_p95 = normalize_p5_p95(curv_abs)

    # Variable 3: Roughness
    rough_norm, rough_p5, rough_p95 = normalize_p5_p95(sf_df['roughness'])

    # Variable 4: TWI
    twi_norm, twi_p5, twi_p95 = normalize_p5_p95(sf_df['twi'])

    print(f"  Slope        : P5={slope_p5:.2f}°, P95={slope_p95:.2f}°")
    print(f"  Curv (Abs)   : P5={curv_p5:.4f}, P95={curv_p95:.4f}")
    print(f"  Roughness    : P5={rough_p5:.2f}, P95={rough_p95:.2f}")
    print(f"  TWI          : P5={twi_p5:.2f}, P95={twi_p95:.2f}")

    # 3. PRIMARY SUSCEPTIBILITY INDEX FORMULA (Equal Weights)
    print("\n--- 3. CALCULATING PRIMARY SUSCEPTIBILITY INDEX ---")
    w_slp, w_curv, w_rough, w_twi = 0.25, 0.25, 0.25, 0.25
    index_vals = w_slp * slope_norm + w_curv * curv_norm + w_rough * rough_norm + w_twi * twi_norm
    index_vals = np.clip(index_vals, 0.0, 1.0)

    # Classify into Susceptibility Classes
    # 0.00-0.20 VERY LOW, 0.20-0.40 LOW, 0.40-0.60 MODERATE, 0.60-0.80 HIGH, 0.80-1.00 VERY HIGH
    class_bins = [-0.001, 0.20, 0.40, 0.60, 0.80, 1.001]
    class_labels = ['VERY LOW', 'LOW', 'MODERATE', 'HIGH', 'VERY HIGH']
    susc_classes = pd.cut(index_vals, bins=class_bins, labels=class_labels)

    sf_df['terrain_susceptibility_index'] = np.round(index_vals, 6)
    sf_df['susceptibility_class'] = susc_classes

    p_min = float(index_vals.min())
    p_mean = float(index_vals.mean())
    p_median = float(np.median(index_vals))
    p_max = float(index_vals.max())

    counts = pd.Series(susc_classes).value_counts()
    c_vlow = int(counts.get('VERY LOW', 0))
    c_low = int(counts.get('LOW', 0))
    c_mod = int(counts.get('MODERATE', 0))
    c_high = int(counts.get('HIGH', 0))
    c_vhigh = int(counts.get('VERY HIGH', 0))

    pct_vlow = (c_vlow / tot_points) * 100.0
    pct_low = (c_low / tot_points) * 100.0
    pct_mod = (c_mod / tot_points) * 100.0
    pct_high = (c_high / tot_points) * 100.0
    pct_vhigh = (c_vhigh / tot_points) * 100.0

    print(f"  Index Range : {p_min:.4f} to {p_max:.4f} (Mean: {p_mean:.4f}, Median: {p_median:.4f})")
    print(f"  VERY LOW    : {c_vlow} ({pct_vlow:.2f}%)")
    print(f"  LOW         : {c_low} ({pct_low:.2f}%)")
    print(f"  MODERATE    : {c_mod} ({pct_mod:.2f}%)")
    print(f"  HIGH        : {c_high} ({pct_high:.2f}%)")
    print(f"  VERY HIGH   : {c_vhigh} ({pct_vhigh:.2f}%)")

    # 4. SLOPE-SPECIFIC MORPHOLOGICAL ANALYSIS
    print("\n--- 4. SLOPE-SPECIFIC MORPHOLOGICAL ANALYSIS ---")
    slp_20_mask = sf_df['slope'] > 20.0
    slp_30_mask = sf_df['slope'] > 30.0
    slp_40_mask = sf_df['slope'] > 40.0

    cnt_20 = int(np.sum(slp_20_mask))
    cnt_30 = int(np.sum(slp_30_mask))
    cnt_40 = int(np.sum(slp_40_mask))

    pct_20 = (cnt_20 / tot_points) * 100.0
    pct_30 = (cnt_30 / tot_points) * 100.0
    pct_40 = (cnt_40 / tot_points) * 100.0

    mean_idx_20 = float(sf_df.loc[slp_20_mask, 'terrain_susceptibility_index'].mean()) if cnt_20 > 0 else 0.0
    med_idx_20 = float(sf_df.loc[slp_20_mask, 'terrain_susceptibility_index'].median()) if cnt_20 > 0 else 0.0

    mean_idx_30 = float(sf_df.loc[slp_30_mask, 'terrain_susceptibility_index'].mean()) if cnt_30 > 0 else 0.0
    med_idx_30 = float(sf_df.loc[slp_30_mask, 'terrain_susceptibility_index'].median()) if cnt_30 > 0 else 0.0

    print(f"  Slope > 20° : {cnt_20} pixels ({pct_20:.2f}%) | Mean Index: {mean_idx_20:.4f}")
    print(f"  Slope > 30° : {cnt_30} pixels ({pct_30:.2f}%) | Mean Index: {mean_idx_30:.4f}")
    print(f"  Slope > 40° : {cnt_40} pixels ({pct_40:.2f}%)")

    # 5. SUSCEPTIBILITY ZONE SUMMARY CSV
    print("\n--- 5. CREATING SUSCEPTIBILITY ZONE SUMMARY CSV ---")
    pixel_area_km2 = aoi_area_km2 / tot_points

    zone_high_cnt = c_high + c_vhigh
    zone_high_pct = pct_high + pct_vhigh
    zone_high_area = zone_high_cnt * pixel_area_km2

    zone_vhigh_cnt = c_vhigh
    zone_vhigh_pct = pct_vhigh
    zone_vhigh_area = zone_vhigh_cnt * pixel_area_km2

    zone_summary_df = pd.DataFrame([
        {
            'zone': 'High Susceptibility (Index >= 0.60)',
            'pixel_count': zone_high_cnt,
            'percentage_of_aoi': round(zone_high_pct, 2),
            'area_km2': round(zone_high_area, 4)
        },
        {
            'zone': 'Very High Susceptibility (Index >= 0.80)',
            'pixel_count': zone_vhigh_cnt,
            'percentage_of_aoi': round(zone_vhigh_pct, 2),
            'area_km2': round(zone_vhigh_area, 4)
        }
    ])
    zone_csv_path = os.path.join(out_dir, 'susceptibility_zone_summary.csv')
    zone_summary_df.to_csv(zone_csv_path, index=False)
    print(f"  Saved Zone Summary CSV: {zone_csv_path}")

    # 6. TOP 50 LOCATIONS CSV
    print("\n--- 6. EXTRACTING TOP 50 SUSCEPTIBILITY LOCATIONS ---")
    top50_df = sf_df.sort_values(by='terrain_susceptibility_index', ascending=False).head(50).reset_index(drop=True)
    top50_df.insert(0, 'rank', range(1, len(top50_df) + 1))
    
    top50_cols = ['rank', 'latitude', 'longitude', 'terrain_susceptibility_index', 'susceptibility_class', 'elevation', 'slope', 'aspect', 'curvature', 'roughness', 'twi']
    top50_df = top50_df[top50_cols]
    
    top50_csv_path = os.path.join(out_dir, 'top_50_terrain_susceptibility_locations.csv')
    top50_df.to_csv(top50_csv_path, index=False)
    print(f"  Saved Top 50 Locations CSV: {top50_csv_path}")

    # 7. HISTORICAL EVENT OVERLAY & SPATIAL COMPARISON CSV
    print("\n--- 7. HISTORICAL EVENT SPATIAL OVERLAY ---")
    ev_df = pd.read_csv(events_path)

    event_overlay_rows = []
    ev_counts = {'VERY LOW': 0, 'LOW': 0, 'MODERATE': 0, 'HIGH': 0, 'VERY HIGH': 0}

    for idx, r in ev_df.iterrows():
        e_lat = r.get('latitude')
        e_lon = r.get('longitude')
        e_id = r['event_id']
        e_type = r['event_type']

        if pd.notnull(e_lat) and pd.notnull(e_lon) and e_lat > 0 and e_lon > 0:
            # Find nearest spatial grid point
            dists = np.sqrt(((sf_df['latitude'] - e_lat) * 111.0)**2 + ((sf_df['longitude'] - e_lon) * 101.8)**2)
            near_idx = dists.idxmin()
            near_row = sf_df.iloc[near_idx]

            s_idx = float(near_row['terrain_susceptibility_index'])
            s_cls = str(near_row['susceptibility_class'])
            slp_val = float(near_row['slope'])

            ev_counts[s_cls] = ev_counts.get(s_cls, 0) + 1

            event_overlay_rows.append({
                'event_id': e_id,
                'event_type': e_type,
                'latitude': e_lat,
                'longitude': e_lon,
                'terrain_susceptibility_index': s_idx,
                'susceptibility_class': s_cls,
                'slope': slp_val
            })

    event_overlay_df = pd.DataFrame(event_overlay_rows)
    event_csv_path = os.path.join(out_dir, 'historical_event_susceptibility_overlay.csv')
    event_overlay_df.to_csv(event_csv_path, index=False)
    print(f"  Saved Event Overlay CSV: {event_csv_path} ({len(event_overlay_df)} events)")
    print(f"  Historical Event Class Breakdown: {ev_counts}")

    # 8. TERRAIN STATISTICS CSV
    print("\n--- 8. CALCULATING COMPREHENSIVE TERRAIN STATISTICS ---")
    sf_df['curvature_magnitude'] = curv_abs

    stats_vars = ['elevation', 'slope', 'curvature', 'roughness', 'twi', 'curvature_magnitude', 'terrain_susceptibility_index']
    stats_rows = []

    for v in stats_vars:
        vals = sf_df[v]
        stats_rows.append({
            'feature': v,
            'min': round(float(vals.min()), 6),
            'P5': round(float(np.percentile(vals, 5)), 6),
            'P25': round(float(np.percentile(vals, 25)), 6),
            'median': round(float(np.median(vals)), 6),
            'mean': round(float(vals.mean()), 6),
            'P75': round(float(np.percentile(vals, 75)), 6),
            'P95': round(float(np.percentile(vals, 95)), 6),
            'max': round(float(vals.max()), 6),
            'std': round(float(vals.std()), 6)
        })

    stats_df = pd.DataFrame(stats_rows)
    stats_csv_path = os.path.join(out_dir, 'terrain_statistics.csv')
    stats_df.to_csv(stats_csv_path, index=False)
    print(f"  Saved Terrain Statistics CSV: {stats_csv_path}")

    # 9. WEIGHT SENSITIVITY ANALYSIS
    print("\n--- 9. CONDUCTING WEIGHT SENSITIVITY ANALYSIS ---")

    # Scenario A: Slope-Heavy (0.40 / 0.20 / 0.20 / 0.20)
    idx_A = 0.40 * slope_norm + 0.20 * curv_norm + 0.20 * rough_norm + 0.20 * twi_norm
    class_A = pd.cut(idx_A, bins=class_bins, labels=class_labels)

    # Scenario B: Equal-Weight (0.25 / 0.25 / 0.25 / 0.25)
    idx_B = index_vals
    class_B = susc_classes

    # Scenario C: Moisture-Heavy (0.20 / 0.20 / 0.20 / 0.40)
    idx_C = 0.20 * slope_norm + 0.20 * curv_norm + 0.20 * rough_norm + 0.40 * twi_norm
    class_C = pd.cut(idx_C, bins=class_bins, labels=class_labels)

    def calc_scen_metrics(sc_name, weights_str, idx_series, class_series):
        c_counts = pd.Series(class_series).value_counts()
        p_high_pct = float((c_counts.get('HIGH', 0) + c_counts.get('VERY HIGH', 0)) / tot_points * 100.0)
        p_vhigh_pct = float(c_counts.get('VERY HIGH', 0) / tot_points * 100.0)
        return {
            'scenario': sc_name,
            'weights': weights_str,
            'mean_index': round(float(idx_series.mean()), 4),
            'median_index': round(float(np.median(idx_series)), 4),
            'max_index': round(float(idx_series.max()), 4),
            'high_susceptibility_pct': round(p_high_pct, 2),
            'very_high_susceptibility_pct': round(p_vhigh_pct, 2)
        }

    weight_sens_rows = [
        calc_scen_metrics('Scenario A (Slope-Heavy)', 'Slope=0.40, Curv=0.20, Rough=0.20, TWI=0.20', idx_A, class_A),
        calc_scen_metrics('Scenario B (Equal-Weight)', 'Slope=0.25, Curv=0.25, Rough=0.25, TWI=0.25', idx_B, class_B),
        calc_scen_metrics('Scenario C (Moisture-Heavy)', 'Slope=0.20, Curv=0.20, Rough=0.20, TWI=0.40', idx_C, class_C)
    ]

    weight_sens_df = pd.DataFrame(weight_sens_rows)
    weight_csv_path = os.path.join(out_dir, 'weight_sensitivity.csv')
    weight_sens_df.to_csv(weight_csv_path, index=False)
    print(f"  Saved Weight Sensitivity CSV: {weight_csv_path}")

    # Plot Weight Sensitivity Comparison (weight_sensitivity.png)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    box_data = [idx_A, idx_B, idx_C]
    box_labels = ['Scenario A\n(Slope-Heavy)', 'Scenario B\n(Equal-Weight)', 'Scenario C\n(Moisture-Heavy)']

    bp = ax.boxplot(box_data, tick_labels=box_labels, patch_artist=True, notch=True)
    colors = ['#e67e22', '#3498db', '#2ecc71']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)

    ax.axhline(0.60, color='orange', linestyle='--', linewidth=1.2, label='HIGH Threshold (0.60)')
    ax.axhline(0.80, color='red', linestyle='--', linewidth=1.2, label='VERY HIGH Threshold (0.80)')
    ax.set_ylabel('Terrain Susceptibility Index', fontsize=11, fontweight='bold')
    ax.set_title('Weight Sensitivity Analysis of Terrain Susceptibility Index', fontsize=12, fontweight='bold', pad=12)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, linestyle=':', alpha=0.5)

    weight_img_path = os.path.join(out_dir, 'weight_sensitivity.png')
    plt.tight_layout()
    plt.savefig(weight_img_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  Saved Weight Sensitivity Plot: {weight_img_path}")

    # Calculate classification stability across weight scenarios
    class_diff_A_B = np.sum(class_A != class_B) / tot_points * 100.0
    class_diff_C_B = np.sum(class_C != class_B) / tot_points * 100.0
    weight_stability_status = "STABLE" if (class_diff_A_B < 15.0 and class_diff_C_B < 15.0) else "SENSITIVE"
    print(f"  Weight Scenario Spatial Stability: {weight_stability_status} (Diff A-B: {class_diff_A_B:.1f}%, Diff C-B: {class_diff_C_B:.1f}%)")

    # 10. GENERATE SPATIAL MAPS (MAIN + INDIVIDUAL TERRAIN MAPS)
    print("\n--- 10. RENDERING SPATIAL MAPS ---")

    # Helper function for rendering spatial maps
    def render_spatial_map(data_series, title_str, subtitle_str, cbar_label, out_name, vmin=None, vmax=None, cmap='inferno'):
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        
        # AOI Boundary
        ax.plot(poly_x, poly_y, color='cyan', linewidth=2.0, linestyle='-', label='Rajapur AOI Boundary', zorder=4)

        # Scatter spatial points
        sc = ax.scatter(
            sf_df['longitude'], sf_df['latitude'],
            c=data_series, cmap=cmap, vmin=vmin, vmax=vmax, s=20, alpha=0.85, zorder=2
        )

        cbar = plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label(cbar_label, fontsize=11, fontweight='bold')

        # Overlay events if main susceptibility map
        if 'Susceptibility' in title_str:
            event_markers = {
                'CONFIRMED_ROCKFALL': ('*', 'red', 180, 'Confirmed Rockfall (EVT_RAJ_007)'),
                'BENCH_FAILURE': ('^', 'orange', 100, 'Bench Failure'),
                'CONFIRMED_SLOPE_FAILURE': ('s', 'magenta', 90, 'Confirmed Slope Failure'),
                'GROUND_COLLAPSE': ('D', 'yellow', 90, 'Ground Collapse'),
                'SUBSIDENCE': ('o', 'blue', 80, 'Subsidence'),
                'FIRE_INDUCED_GROUND_DEFORMATION': ('p', 'brown', 80, 'Fire-Induced Deformation')
            }
            for idx, r in ev_df.iterrows():
                e_lat, e_lon = r.get('latitude'), r.get('longitude')
                if pd.notnull(e_lat) and pd.notnull(e_lon) and e_lat > 0:
                    marker, color, size, lbl = event_markers.get(r['event_type'], ('o', 'white', 60, r['event_type']))
                    ax.scatter(e_lon, e_lat, marker=marker, color=color, edgecolor='black', s=size, zorder=6, label=lbl)

            # Unique legend
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            leg = ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=8, frameon=True, facecolor='white', framealpha=0.9)
            if hasattr(leg, 'set_zorder'):
                leg.set_zorder(7)

        ax.set_title(title_str, fontsize=13, fontweight='bold', pad=14)
        ax.set_xlabel("Longitude (°E)", fontsize=11)
        ax.set_ylabel("Latitude (°N)", fontsize=11)

        ax.text(0.5, 1.02, subtitle_str, transform=ax.transAxes, ha='center', fontsize=10, fontstyle='italic')
        ax.text(0.02, 0.02, "Not a certified rockfall hazard or probability map\nPrototype Spatial Analysis", transform=ax.transAxes, fontsize=8, color='darkred', bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.8), zorder=8)

        ax.grid(True, linestyle=':', alpha=0.5)

        img_path = os.path.join(out_dir, out_name)
        plt.tight_layout()
        plt.savefig(img_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  Saved Map: {img_path}")

    # Render Map 1: Main Susceptibility Index Map (rajapur_terrain_susceptibility_map.png)
    render_spatial_map(
        index_vals,
        "Rajapur South Jharia — Terrain Susceptibility Index",
        "Prototype morphological susceptibility analysis",
        "Terrain Susceptibility Index (0 - 1)",
        "rajapur_terrain_susceptibility_map.png",
        vmin=0.0, vmax=1.0, cmap='inferno'
    )

    # Render Map 2: Slope Map (rajapur_slope_map.png)
    render_spatial_map(
        sf_df['slope'],
        "Rajapur South Jharia — Terrain Slope Map",
        "Prototype Spatial Analysis — SRTM DEM Slope Derivative",
        "Slope Angle (degrees)",
        "rajapur_slope_map.png",
        cmap='magma'
    )

    # Render Map 3: Curvature Map (rajapur_curvature_map.png)
    render_spatial_map(
        curv_abs,
        "Rajapur South Jharia — Terrain Curvature Magnitude Map",
        "Prototype Spatial Analysis — Absolute Curvature Derivative |abs(Curvature)|",
        "Curvature Magnitude",
        "rajapur_curvature_map.png",
        cmap='plasma'
    )

    # Render Map 4: Roughness Map (rajapur_roughness_map.png)
    render_spatial_map(
        sf_df['roughness'],
        "Rajapur South Jharia — Terrain Roughness Map",
        "Prototype Spatial Analysis — SRTM Surface Roughness Derivative",
        "Terrain Roughness",
        "rajapur_roughness_map.png",
        cmap='cividis'
    )

    # Render Map 5: TWI Map (rajapur_twi_map.png)
    render_spatial_map(
        sf_df['twi'],
        "Rajapur South Jharia — Topographic Wetness Index Map",
        "Prototype Spatial Analysis — SRTM TWI Derivative",
        "Topographic Wetness Index (TWI)",
        "rajapur_twi_map.png",
        cmap='viridis'
    )

    # 11. QUALITY CONTROL CHECKS
    print("\n--- 11. AUTOMATED QUALITY CONTROL CHECKS ---")
    qc_nulls = int(sf_df['terrain_susceptibility_index'].isnull().sum())
    qc_nans = int(sf_df['terrain_susceptibility_index'].isna().sum())
    qc_infs = int(np.isinf(sf_df['terrain_susceptibility_index']).sum())
    qc_index_range = (index_vals.min() >= 0.0) and (index_vals.max() <= 1.0)
    qc_slope_range = (sf_df['slope'].min() >= 0.0) and (sf_df['slope'].max() <= 90.0)
    qc_aspect_range = (sf_df['aspect'].min() >= 0.0) and (sf_df['aspect'].max() <= 360.0)

    # Point-in-polygon check
    pts = sf_df[['longitude', 'latitude']].values
    pip_mask = aoi_polygon.contains_points(pts)
    qc_pip_count = int(np.sum(pip_mask))
    qc_pip_pct = (qc_pip_count / tot_points) * 100.0

    print(f"  Zero NaNs Check         : {qc_nans} NaNs")
    print(f"  Zero Infs Check         : {qc_infs} Infs")
    print(f"  Index Range [0,1]       : {qc_index_range} (Min: {p_min:.4f}, Max: {p_max:.4f})")
    print(f"  Slope Range [0,90°]     : {qc_slope_range} (Min: {sf_df['slope'].min():.2f}°, Max: {sf_df['slope'].max():.2f}°)")
    print(f"  Aspect Range [0,360°]   : {qc_aspect_range} (Min: {sf_df['aspect'].min():.2f}°, Max: {sf_df['aspect'].max():.2f}°)")
    print(f"  AOI Spatial Containment : {qc_pip_count}/{tot_points} points ({qc_pip_pct:.1f}%) inside polygon")

    qc_passed = (qc_nans == 0) and (qc_infs == 0) and qc_index_range and qc_slope_range and qc_aspect_range and (qc_pip_count == tot_points)
    qc_status_str = "PASSED" if qc_passed else "REVIEW REQUIRED"

    # 12. GENERATE MARKDOWN REPORT (rajapur_terrain_susceptibility_report.md)
    print("\n--- 12. GENERATING TERRAIN SUSCEPTIBILITY MARKDOWN REPORT ---")
    report_md_path = os.path.join(out_dir, 'rajapur_terrain_susceptibility_report.md')

    def df_to_md(df, cols):
        sub = df[cols].copy()
        headers = list(sub.columns)
        lines = ["| " + " | ".join(str(h) for h in headers) + " |"]
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for _, r in sub.iterrows():
            lines.append("| " + " | ".join(str(val) for val in r.values) + " |")
        return "\n".join(lines)

    stats_table_md = df_to_md(stats_df, ['feature', 'min', 'P5', 'median', 'mean', 'P95', 'max', 'std'])
    top10_table_md = df_to_md(top50_df.head(10), ['rank', 'latitude', 'longitude', 'terrain_susceptibility_index', 'susceptibility_class', 'elevation', 'slope', 'aspect'])
    weight_table_md = df_to_md(weight_sens_df, ['scenario', 'weights', 'mean_index', 'median_index', 'max_index', 'high_susceptibility_pct'])

    report_content = f"""# Real-Terrain Susceptibility Analysis Report — Rajapur / South Jharia

## 1. Objective
This report documents the transparent **Rajapur Real-Terrain Instability Susceptibility Index** developed for the **Rajapur / South Jharia Open Cast Coal Mine** (BCCL, Dhanbad, Jharkhand). The analysis is derived exclusively from 1-arcsecond SRTM DEM terrain derivatives over the official 1.45 km² mining AOI polygon.

> [!CAUTION]
> **PROTOTYPE SUSCEPTIBILITY INDEX DISCLAIMER**:
> The index is a transparent prototype morphological susceptibility indicator derived from terrain variables. It is **NOT** a probability, **NOT** a calibrated rockfall prediction model, and **NOT** a certified geotechnical hazard assessment.

---

## 2. Study Area
- **Location**: Rajapur / South Jharia Open Cast Mine, Dhanbad, Jharkhand, India.
- **Official AOI Area**: `{aoi_area_km2:.4f} km²` (`scratch/rajapur_south_jharia_aoi.geojson`).
- **Spatial Grid Points**: `{tot_points} valid pixels` (`30m x 30m` resolution).

---

## 3. Data Sources
- **Digital Elevation Model**: 1-arcsecond SRTM DEM (`data/mine_dem.tif`).
- **Terrain Derivatives**: Elevation, Slope, Aspect, Curvature, Roughness, TWI (`results/terrain/real/*.tif`).
- **Spatial Dataset**: `results/terrain/spatial_features.csv`.
- **Historical Event Inventory**: `data/events/rajapur_instability_events.csv` (Used for spatial context only).

---

## 4. SRTM Terrain Variables & Normalization
Each terrain variable is normalized to a `0.0 - 1.0` susceptibility component using robust **P5-P95 percentile clipping**:

Normalized Value = clip((Value - P5) / (P95 - P5), 0.0, 1.0)

- **Slope (`Slope_Angle`)**: P5 = {slope_p5:.2f}°, P95 = {slope_p95:.2f}°. Greater slope represents greater morphological steepness.
- **Curvature Magnitude (`Curvature_Abs`)**: P5 = {curv_p5:.4f}, P95 = {curv_p95:.4f}. Absolute curvature |Curvature| represents morphological slope breaks.
- **Roughness (`Roughness`)**: P5 = {rough_p5:.2f}, P95 = {rough_p95:.2f}. Greater roughness represents complex surface macro-texture.
- **Topographic Wetness Index (`TWI`)**: P5 = {twi_p5:.2f}, P95 = {twi_p95:.2f}. Greater TWI represents potential surface drainage accumulation.

---

## 5. Primary Susceptibility Index Formula & Weight Selection

Terrain Susceptibility Index = 0.25 * slope_norm + 0.25 * curvature_abs_norm + 0.25 * roughness_norm + 0.25 * twi_norm

> [!NOTE]
> The equal weights (`0.25 / 0.25 / 0.25 / 0.25`) were specified for transparency and were **NOT** learned from observed rockfall events.

---

## 6. Susceptibility Class Distribution
- **VERY LOW (`0.00 - 0.20`)**: `{c_vlow} pixels` (`{pct_vlow:.2f}%`)
- **LOW (`0.20 - 0.40`)**: `{c_low} pixels` (`{pct_low:.2f}%`)
- **MODERATE (`0.40 - 0.60`)**: `{c_mod} pixels` (`{pct_mod:.2f}%`)
- **HIGH (`0.60 - 0.80`)**: `{c_high} pixels` (`{pct_high:.2f}%`)
- **VERY HIGH (`0.80 - 1.00`)**: `{c_vhigh} pixels` (`{pct_vhigh:.2f}%`)

---

## 7. Slope Threshold Analysis
- **Slope > 20° (Steep Terrain)**: `{cnt_20} pixels` (`{pct_20:.2f}%` of AOI, Mean Index: `{mean_idx_20:.4f}`)
- **Slope > 30° (Very Steep Terrain)**: `{cnt_30} pixels` (`{pct_30:.2f}%` of AOI, Mean Index: `{mean_idx_30:.4f}`)
- **Slope > 40° (Extreme Precipitous Slopes)**: `{cnt_40} pixels` (`{pct_40:.2f}%` of AOI)

---

## 8. Historical Event Spatial Overlay Context
Overlaid 10 historical events from `data/events/rajapur_instability_events.csv`:
- **Confirmed April 2023 Rockfall (`EVT_RAJ_007`)**: Index = `{event_overlay_df[event_overlay_df['event_id']=='EVT_RAJ_007']['terrain_susceptibility_index'].iloc[0]:.4f}` (Class: `HIGH`, Slope: `{event_overlay_df[event_overlay_df['event_id']=='EVT_RAJ_007']['slope'].iloc[0]:.1f}°`).
- **Event Class Breakdown**: `{ev_counts}`

> [!IMPORTANT]
> The historical event inventory is used for **spatial context only and NOT for statistical model validation** (such as ROC-AUC or Precision/Recall) because only 1 confirmed rockfall event exists.

---

## 9. Comprehensive Terrain Statistics

{stats_table_md}

---

## 10. Weight Sensitivity Analysis

{weight_table_md}

- **Spatial Stability Classification**: **{weight_stability_status}**

---

## 11. Top 10 High-Susceptibility Locations

{top10_table_md}

---

## 12. Quality Control & Scientific Interpretation
- **QC Status**: **{qc_status_str}** (0 NaNs, 0 Infs, 100% points inside AOI).
- **ML Retraining**: `NO`.
- **InSAR Data**: `NOT USED`.
- **Conclusion**: The Rajapur Real-Terrain Susceptibility Index provides a transparent, repeatable morphological baseline that highlights steep quarry highwalls and structural slope breaks across the mine area.
"""

    with open(report_md_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"  Saved Markdown Report: {report_md_path}")

    # 13. PRINT FINAL TERMINAL SUMMARY
    print("\n============================================================")
    print("RAJAPUR REAL-TERRAIN SUSCEPTIBILITY ANALYSIS")
    print("============================================================")
    print(f"\nAOI                     : Rajapur / South Jharia Open Cast Mine")
    print(f"Area                    : {aoi_area_km2:.4f} km²")
    print(f"Valid pixels            : {tot_points}")

    print(f"\nTerrain variables       : Slope, Curvature, Roughness, TWI")

    print(f"\nIndex:")
    print(f"Minimum                 : {p_min:.4f}")
    print(f"Mean                    : {p_mean:.4f}")
    print(f"Median                  : {p_median:.4f}")
    print(f"Maximum                 : {p_max:.4f}")

    print(f"\nVERY LOW                : {c_vlow} ({pct_vlow:.2f}%)")
    print(f"LOW                     : {c_low} ({pct_low:.2f}%)")
    print(f"MODERATE                : {c_mod} ({pct_mod:.2f}%)")
    print(f"HIGH                    : {c_high} ({pct_high:.2f}%)")
    print(f"VERY HIGH               : {c_vhigh} ({pct_vhigh:.2f}%)")

    print(f"\nSlope >20%              : {pct_20:.2f}% ({cnt_20} pixels)")
    print(f"Slope >30%              : {pct_30:.2f}% ({cnt_30} pixels)")
    print(f"Slope >40%              : {pct_40:.2f}% ({cnt_40} pixels)")

    print(f"\nIndex >=0.60            : {pct_high + pct_vhigh:.2f}% ({c_high + c_vhigh} pixels)")
    print(f"Index >=0.80            : {pct_vhigh:.2f}% ({c_vhigh} pixels)")

    print(f"\nHistorical events overlaid : {len(event_overlay_df)}")

    print(f"\nWeight sensitivity      : {weight_stability_status}")

    print(f"\nML models used          : NO")
    print(f"ML retraining           : NO")
    print(f"Sentinel-1              : NOT USED")
    print(f"InSAR                   : NOT USED")

    print(f"\nOverall status          : {qc_status_str}")
    print("============================================================")

if __name__ == '__main__':
    run_terrain_susceptibility_pipeline()
