import sys
import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Add workspace root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import (
    MODEL_A_FEATURES, MODEL_B_FEATURES, MODEL_B_CLASS_NAMES,
    INSTABILITY_THRESHOLDS, RISK_MATRIX, PROTOTYPE_DISCLAIMER
)
from src.risk_fusion_engine import RiskFusionEngine
from src.explainability import get_model_feature_importances

# Page Config
st.set_page_config(
    page_title="Rockfall AI - Rajapur Terrain & Risk Prototype",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 20px;
    }
    .card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eef2f5;
        margin-bottom: 20px;
    }
    .risk-badge {
        font-size: 1.6rem;
        font-weight: 800;
        padding: 10px 24px;
        border-radius: 30px;
        color: white;
        display: inline-block;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    .badge-LOW { background: linear-gradient(135deg, #27ae60, #2ecc71); }
    .badge-MODERATE { background: linear-gradient(135deg, #f39c12, #f1c40f); color: #2c3e50; }
    .badge-HIGH { background: linear-gradient(135deg, #d35400, #e67e22); }
    .badge-CRITICAL { background: linear-gradient(135deg, #c0392b, #e74c3c); }
    .disclaimer-box {
        background-color: #fff8e7;
        border-left: 5px solid #f39c12;
        padding: 15px;
        border-radius: 6px;
        font-size: 0.88rem;
        color: #7f8c8d;
        margin-top: 15px;
    }
    .warning-box {
        background-color: #fdf2e9;
        border-left: 5px solid #e67e22;
        padding: 15px;
        border-radius: 6px;
        font-size: 0.90rem;
        color: #7e5109;
        margin-bottom: 20px;
    }
    .flow-diagram {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        font-weight: 600;
        font-size: 0.95rem;
        color: #2c3e50;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Engine
@st.cache_resource
def load_fusion_engine():
    return RiskFusionEngine()

try:
    engine = load_fusion_engine()
except Exception as e:
    st.error(f"Error loading models: {e}. Please ensure models/model_A_best.pkl and models/model_B_best.pkl exist.")
    st.stop()

# Header
st.markdown('<div class="main-header">⛰️ ROCKFALL AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Real-Terrain Morphological Susceptibility & Risk Fusion System (Rajapur / South Jharia)</div>', unsafe_allow_html=True)

# Navigation Mode Selector in Sidebar
st.sidebar.title("🧭 Dashboard Mode")
app_mode = st.sidebar.radio(
    "Select View Mode:",
    ["🗺️ Rajapur Spatial Analysis", "🧪 Interactive Risk Simulator"]
)

# ==============================================================================
# MODE 1: RAJAPUR SPATIAL ANALYSIS (REAL SRTM TERRAIN SUSCEPTIBILITY INDEX)
# ==============================================================================
if app_mode == "🗺️ Rajapur Spatial Analysis":
    st.markdown("## 🗺️ Rajapur South Jharia — Terrain Susceptibility Analysis")
    st.caption("Prototype terrain-based morphological susceptibility derived from 1-arcsecond SRTM DEM derivatives")

    # 1. SCIENTIFIC DISCLAIMER WARNING BOX (Top of Page)
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ IMPORTANT SCIENTIFIC LIMITATION:</strong><br>
        This is a prototype terrain-based morphological susceptibility index. It is <strong>NOT</strong> a probability of rockfall, <strong>NOT</strong> a calibrated machine-learning prediction, and <strong>NOT</strong> a certified geotechnical hazard assessment.<br><br>
        The index weights (0.25 / 0.25 / 0.25 / 0.25) were specified transparently and were <strong>not learned</strong> from observed rockfall events.<br>
        Historical instability events are shown for spatial context only and are <strong>not sufficient for statistical model validation</strong>.
    </div>
    """, unsafe_allow_html=True)

    # Output file paths
    ts_dir = os.path.join('results', 'rajapur', 'terrain_susceptibility')
    
    map_index_img = os.path.join(ts_dir, 'rajapur_terrain_susceptibility_map.png')
    map_slope_img = os.path.join(ts_dir, 'rajapur_slope_map.png')
    map_curv_img = os.path.join(ts_dir, 'rajapur_curvature_map.png')
    map_rough_img = os.path.join(ts_dir, 'rajapur_roughness_map.png')
    map_twi_img = os.path.join(ts_dir, 'rajapur_twi_map.png')
    weight_img = os.path.join(ts_dir, 'weight_sensitivity.png')

    top50_path = os.path.join(ts_dir, 'top_50_terrain_susceptibility_locations.csv')
    zone_path = os.path.join(ts_dir, 'susceptibility_zone_summary.csv')
    events_path = os.path.join(ts_dir, 'historical_event_susceptibility_overlay.csv')
    stats_path = os.path.join(ts_dir, 'terrain_statistics.csv')
    weight_path = os.path.join(ts_dir, 'weight_sensitivity.csv')

    # Load data files if present
    df_top50 = pd.read_csv(top50_path) if os.path.exists(top50_path) else None
    df_events = pd.read_csv(events_path) if os.path.exists(events_path) else None
    df_stats = pd.read_csv(stats_path) if os.path.exists(stats_path) else None
    df_weight = pd.read_csv(weight_path) if os.path.exists(weight_path) else None

    # 2. MODEL STATUS & PROJECT SUMMARY WORKFLOW
    col_stat, col_flow = st.columns([1, 1.3])

    with col_stat:
        st.markdown("#### 🔬 ML Model Status Panel")
        st.info("""
        - **Model A**: Synthetic benchmark — **NOT** used for Rajapur terrain index
        - **Model B**: Synthetic benchmark — **NOT** used for Rajapur terrain index
        - **Terrain Susceptibility**: Real SRTM-derived terrain analysis
        - **Sentinel-1 SAR**: Not used
        - **InSAR Processing**: Not performed
        - **ML Retraining**: No
        """)

    with col_flow:
        st.markdown("#### 🔄 How This System Works")
        st.markdown("""
        <div class="flow-diagram">
            SRTM DEM (1-Arcsecond)<br>
            ↓<br>
            Terrain Derivatives (Slope, Curvature, Roughness, TWI)<br>
            ↓<br>
            Robust P5–P95 Percentile Normalization<br>
            ↓<br>
            Transparent Equal-Weight Susceptibility Index (0.25 x 4)<br>
            ↓<br>
            Rajapur Susceptibility Map & Historical Event Overlay
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. KEY METRICS CARDS (Section 4)
    st.markdown("### 📊 Key Terrain Metrics")
    km1, km2, km3, km4, km5 = st.columns(5)
    km1.metric("Study Area", "1.4503 km²")
    km2.metric("Valid Spatial Points", "1,665")
    km3.metric("Mean Index", "0.3161")
    km4.metric("Max Index", "0.7632")
    km5.metric("High Susceptibility (≥0.60)", "6.01%")

    km6, km7, km8, km9 = st.columns(4)
    km6.metric("Very High Susceptibility (≥0.80)", "0.00%")
    km7.metric("Slope > 20°", "5.59% (93 pts)")
    km8.metric("Slope > 30°", "0.96% (16 pts)")
    km9.metric("Slope > 40°", "0.00% (0 pts)")

    st.markdown("---")

    # 4. TERRAIN LAYER SELECTOR (Section 6)
    st.markdown("### 🗺️ Terrain Spatial Layers")
    layer_selected = st.selectbox(
        "Select Terrain Layer to Display:",
        [
            "Susceptibility Index Map",
            "Slope Map",
            "Curvature Magnitude Map",
            "Roughness Map",
            "Topographic Wetness Index (TWI) Map"
        ]
    )

    layer_map_dict = {
        "Susceptibility Index Map": (map_index_img, "Rajapur Terrain Susceptibility Index Map (0 - 1)"),
        "Slope Map": (map_slope_img, "SRTM DEM Slope Angle Map (degrees)"),
        "Curvature Magnitude Map": (map_curv_img, "SRTM Absolute Curvature Map"),
        "Roughness Map": (map_rough_img, "SRTM Surface Roughness Map"),
        "Topographic Wetness Index (TWI) Map": (map_twi_img, "SRTM Topographic Wetness Index Map")
    }

    selected_img, selected_cap = layer_map_dict[layer_selected]
    if os.path.exists(selected_img):
        st.image(selected_img, use_container_width=True, caption=selected_cap)
    else:
        st.warning(f"Image layer missing at '{selected_img}'. Run `python src/compute_terrain_susceptibility.py`.")

    st.caption("The map shows a transparent terrain-based susceptibility index derived from SRTM terrain morphology. It is not a probability of rockfall and is not a certified geotechnical hazard map.")

    st.markdown("---")

    # 5. TABS FOR DETAILED ANALYSIS
    tab_dist, tab_top, tab_events, tab_sens = st.tabs([
        "📊 Susceptibility Distribution",
        "📍 Top 50 Locations & Inspector",
        "📜 Historical Events Spatial Overlay",
        "⚖️ Weight Sensitivity Analysis"
    ])

    with tab_dist:
        st.subheader("Baseline Susceptibility Class Distribution")
        
        dist_df = pd.DataFrame([
            {'Class': 'VERY LOW (0.00 - 0.20)', 'Pixel Count': 227, 'Percentage': '13.63%'},
            {'Class': 'LOW (0.20 - 0.40)', 'Pixel Count': 1097, 'Percentage': '65.89%'},
            {'Class': 'MODERATE (0.40 - 0.60)', 'Pixel Count': 241, 'Percentage': '14.47%'},
            {'Class': 'HIGH (0.60 - 0.80)', 'Pixel Count': 100, 'Percentage': '6.01%'},
            {'Class': 'VERY HIGH (0.80 - 1.00)', 'Pixel Count': 0, 'Percentage': '0.00%'}
        ])
        st.table(dist_df)

        if df_stats is not None:
            st.markdown("#### Comprehensive Terrain Statistics")
            st.dataframe(df_stats, use_container_width=True)

    with tab_top:
        st.subheader("Top 50 High-Susceptibility Locations")
        if df_top50 is not None:
            st.dataframe(df_top50, use_container_width=True)
            
            st.download_button(
                label="📥 Download Top 50 Locations CSV",
                data=df_top50.to_csv(index=False),
                file_name="top_50_terrain_susceptibility_locations.csv",
                mime="text/csv"
            )

            st.markdown("---")
            st.markdown("#### 🔍 Location Inspector")
            selected_rank = st.selectbox("Select Location Rank to Inspect:", df_top50['rank'].tolist())
            loc_row = df_top50[df_top50['rank'] == selected_rank].iloc[0]

            lic1, lic2, lic3 = st.columns(3)
            lic1.metric("Latitude", f"{loc_row['latitude']:.6f}°N")
            lic1.metric("Longitude", f"{loc_row['longitude']:.6f}°E")
            lic2.metric("Susceptibility Index", f"{loc_row['terrain_susceptibility_index']:.4f}")
            lic2.metric("Susceptibility Class", f"{loc_row['susceptibility_class']}")
            lic3.metric("Slope Angle", f"{loc_row['slope']:.2f}°")
            lic3.metric("Elevation", f"{loc_row['elevation']:.1f} m")

            st.caption(f"Curvature: {loc_row['curvature']:.4f} | Roughness: {loc_row['roughness']:.2f} | TWI: {loc_row['twi']:.2f} | Aspect: {loc_row['aspect']:.1f}°")

    with tab_events:
        st.subheader("Historical Event Spatial Comparison")
        st.caption("The historical event inventory is used for spatial context only. The current inventory contains too few confirmed rockfall events to support statistical model validation.")

        if df_events is not None:
            st.dataframe(df_events, use_container_width=True)

            # Observation for EVT_RAJ_007
            evt_007 = df_events[df_events['event_id'] == 'EVT_RAJ_007']
            if len(evt_007) > 0:
                e_row = evt_007.iloc[0]
                st.success(f"📌 **Key Spatial Observation**: {e_row['event_id']} ({e_row['event_type']}, April 2023) is located within a **{e_row['susceptibility_class']}** susceptibility cell (Index = {e_row['terrain_susceptibility_index']:.4f}, Slope = {e_row['slope']:.1f}°).")

    with tab_sens:
        st.subheader("Index Weight Sensitivity Analysis")
        st.caption("Testing how susceptibility predictions change across alternative expert weighting scenarios")

        st.markdown("#### Weight Scenario Stability: **SENSITIVE**")
        st.warning("The susceptibility pattern changes when the relative weights assigned to terrain variables are changed. Therefore the index should be treated as a transparent prototype indicator rather than a fixed hazard probability.")

        if os.path.exists(weight_img):
            st.image(weight_img, use_container_width=True, caption="Weight Sensitivity Comparison Across Scenarios A, B, and C")

        if df_weight is not None:
            st.dataframe(df_weight, use_container_width=True)

# ==============================================================================
# MODE 2: INTERACTIVE RISK SIMULATOR (EXISTING FUNCTIONALITY 100% PRESERVED)
# ==============================================================================
else:
    st.sidebar.header("🧪 Test Preset Scenarios")
    preset = st.sidebar.selectbox(
        "Select a pre-configured test scenario:",
        ["Custom Inputs", "Baseline Safe", "Heavy Rainfall Event", "Seismic Trigger Event", "Extreme Combined Hazard", "Drought / Arid"]
    )

    default_vals = {
        "Rainfall_mm": 120.0, "Slope_Angle": 25.0, "Soil_Saturation": 0.40,
        "Vegetation_Cover": 0.60, "Earthquake_Activity": 1.5, "Proximity_to_Water": 1.2,
        "Soil_Type": "Gravel", "Temperature": 22, "Humidity": 55, "Precipitation": 40,
        "Soil_Moisture": 35, "Elevation": 350
    }

    if preset == "Baseline Safe":
        default_vals.update({"Rainfall_mm": 60.0, "Slope_Angle": 12.0, "Soil_Saturation": 0.15, "Vegetation_Cover": 0.85, "Earthquake_Activity": 0.2, "Proximity_to_Water": 1.8, "Soil_Type": "Gravel", "Temperature": 20, "Humidity": 40, "Precipitation": 10, "Soil_Moisture": 25, "Elevation": 200})
    elif preset == "Heavy Rainfall Event":
        default_vals.update({"Rainfall_mm": 260.0, "Slope_Angle": 42.0, "Soil_Saturation": 0.88, "Vegetation_Cover": 0.25, "Earthquake_Activity": 2.1, "Proximity_to_Water": 0.2, "Soil_Type": "Silt", "Temperature": 18, "Humidity": 88, "Precipitation": 210, "Soil_Moisture": 82, "Elevation": 650})
    elif preset == "Seismic Trigger Event":
        default_vals.update({"Rainfall_mm": 180.0, "Slope_Angle": 52.0, "Soil_Saturation": 0.65, "Vegetation_Cover": 0.20, "Earthquake_Activity": 5.8, "Proximity_to_Water": 0.5, "Soil_Type": "Sand", "Temperature": 24, "Humidity": 60, "Precipitation": 80, "Soil_Moisture": 50, "Elevation": 800})
    elif preset == "Extreme Combined Hazard":
        default_vals.update({"Rainfall_mm": 290.0, "Slope_Angle": 58.0, "Soil_Saturation": 0.95, "Vegetation_Cover": 0.12, "Earthquake_Activity": 6.2, "Proximity_to_Water": 0.1, "Soil_Type": "Silt", "Temperature": 32, "Humidity": 92, "Precipitation": 240, "Soil_Moisture": 88, "Elevation": 950})
    elif preset == "Drought / Arid":
        default_vals.update({"Rainfall_mm": 52.0, "Slope_Angle": 15.0, "Soil_Saturation": 0.05, "Vegetation_Cover": 0.30, "Earthquake_Activity": 0.5, "Proximity_to_Water": 1.9, "Soil_Type": "Sand", "Temperature": 34, "Humidity": 32, "Precipitation": 5, "Soil_Moisture": 22, "Elevation": 150})

    col_in1, col_in2 = st.columns(2)

    with col_in1:
        st.subheader("⛰️ Geotechnical Parameters (Model A)")
        rf = st.slider("Rainfall (mm)", 50.0, 300.0, float(default_vals["Rainfall_mm"]), 1.0)
        slope = st.slider("Slope Angle (degrees)", 5.0, 60.0, float(default_vals["Slope_Angle"]), 0.5)
        sat = st.slider("Soil Saturation (Ratio)", 0.0, 1.0, float(default_vals["Soil_Saturation"]), 0.01)
        veg = st.slider("Vegetation Cover (Ratio)", 0.1, 1.0, float(default_vals["Vegetation_Cover"]), 0.01)
        eq = st.slider("Earthquake Activity (Richter)", 0.0, 6.5, float(default_vals["Earthquake_Activity"]), 0.1)
        prox = st.slider("Proximity to Water (km)", 0.0, 2.0, float(default_vals["Proximity_to_Water"]), 0.05)
        soil_type = st.selectbox("Soil Type Category", ["Gravel", "Sand", "Silt", "Bedrock / Clay (Unlisted Base)"],
                                 index=["Gravel", "Sand", "Silt", "Bedrock / Clay (Unlisted Base)"].index(default_vals["Soil_Type"]) if default_vals["Soil_Type"] in ["Gravel", "Sand", "Silt"] else 0)

    with col_in2:
        st.subheader("🌧️ Meteorological Parameters (Model B)")
        temp = st.slider("Temperature (°C)", 15, 35, int(default_vals["Temperature"]))
        hum = st.slider("Humidity (%)", 30, 95, int(default_vals["Humidity"]))
        precip = st.slider("Precipitation (mm)", 0, 250, int(default_vals["Precipitation"]))
        moist = st.slider("Soil Moisture (%)", 20, 90, int(default_vals["Soil_Moisture"]))
        elev = st.slider("Elevation (m)", 0, 1000, int(default_vals["Elevation"]))

    soil_gravel = 1 if soil_type == "Gravel" else 0
    soil_sand = 1 if soil_type == "Sand" else 0
    soil_silt = 1 if soil_type == "Silt" else 0

    inputs_A = {
        'Rainfall_mm': rf, 'Slope_Angle': slope, 'Soil_Saturation': sat,
        'Vegetation_Cover': veg, 'Earthquake_Activity': eq, 'Proximity_to_Water': prox,
        'Soil_Type_Gravel': soil_gravel, 'Soil_Type_Sand': soil_sand, 'Soil_Type_Silt': soil_silt
    }

    inputs_B = {
        'Temperature (°C)': temp, 'Humidity (%)': hum, 'Precipitation (mm)': precip,
        'Soil Moisture (%)': moist, 'Elevation (m)': elev
    }

    out = engine.predict(inputs_A, inputs_B)

    st.markdown("---")
    st.header("🎯 Assessment Results & Hazard Output")

    m_col1, m_col2, m_col3 = st.columns([1, 1, 1.2])

    with m_col1:
        st.markdown("#### Model A: Ground Instability")
        st.metric(label="Instability Probability", value=f"{out['instability_probability']*100:.1f}%")
        st.progress(float(out['instability_probability']))
        st.caption(f"Instability Class: **{out['instability_class']}**")

    with m_col2:
        st.markdown("#### Model B: Weather Risk")
        st.metric(label="Meteorological Risk Tier", value=out['weather_risk'])
        prob_df = pd.DataFrame(list(out['weather_probabilities'].items()), columns=['Tier', 'Probability'])
        st.caption("Class Probabilities:")
        st.dataframe(prob_df, use_container_width=True, hide_index=True)

    with m_col3:
        st.markdown("#### Integrated Risk Fusion")
        badge_class = f"badge-{out['final_risk_level']}"
        st.markdown(f'<div class="risk-badge {badge_class}">{out["final_risk_level"]} RISK</div>', unsafe_allow_html=True)
        st.write("")
        st.metric(label="Rockfall Hazard Index (0-100)", value=f"{out['risk_score']} / 100")

    st.markdown("### 📢 Prototype Advisory")
    st.info(out['advisory'])

    st.markdown("""
    <div class="disclaimer-box">
        <strong>⚠️ PROTOTYPE SYSTEM NOTICE:</strong> All risk scores, hazard index values, and advisories generated by this application are experimental heuristics based on proxy datasets. They do not constitute operational safety instructions or certified geotechnical risk assessments.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        st.subheader("🔍 Model-Derived Contributing Factors")
        st.write("Top factors contributing to this prediction:")
        for factor in out['top_risk_factors']:
            st.markdown(f"- **{factor}**")
        st.caption("*Note: Contributing factors reflect model-derived sensitivity weights, not proven physical causation.*")

    with exp_col2:
        st.subheader("📊 Active 2D Risk Matrix Mapping")
        matrix_df = pd.DataFrame(RISK_MATRIX).T
        st.write(f"Current Matrix Cell: **Instability ({out['instability_class']})** × **Weather ({out['weather_risk']})** ➔ **{out['final_risk_level']}**")
        st.dataframe(matrix_df, use_container_width=True)

    st.markdown("---")

    st.subheader("📈 Model-Derived Feature Importance Comparison")
    tab1, tab2 = st.tabs(["Model A (Ground Instability)", "Model B (Meteorological)"])

    with tab1:
        imp_A = get_model_feature_importances(engine.model_A, engine.features_A)
        fig_a, ax_a = plt.subplots(figsize=(8, 4))
        sns.barplot(data=imp_A, x='Importance', y='Feature', palette='Blues_r', ax=ax_a)
        ax_a.set_title("Model A Derived Feature Importance")
        st.pyplot(fig_a)

    with tab2:
        imp_B = get_model_feature_importances(engine.model_B, engine.features_B)
        fig_b, ax_b = plt.subplots(figsize=(8, 4))
        sns.barplot(data=imp_B, x='Importance', y='Feature', palette='Oranges_r', ax=ax_b)
        ax_b.set_title("Model B Derived Feature Importance")
        st.pyplot(fig_b)
