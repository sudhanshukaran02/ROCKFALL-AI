# NER Landslide Risk Assessment Report

## Executive Summary
This report presents the **Phase 2 Multimodal Landslide Risk Assessment System** for the North Eastern Region (NER) platform. 

The system integrates spatial detection evidence, physical terrain susceptibility proxies, and real daily/cumulative precipitation triggers into a transparent **Multi-Criteria Evaluation (MCE) Risk Index**.

> [!IMPORTANT]
> **SCIENTIFIC DISTINCTION & BOUNDARY**
> This risk assessment answers the question:
> **"WHERE is the terrain/environmental condition currently susceptible to landslide risk?"**
>
> It does **NOT** claim to forecast future initiation timing (*"WHEN will a landslide occur?"*). Temporal forecasting is reserved for the Phase 3 LSTM module.

---

## 1. Real Data Sources & Feature Engineering

1. **Spatial Detection Evidence ($E_{\text{spatial}}$)**:
   - Source: U-Net Model Checkpoint (`results/ner/segmentation/best_unet.pth`).
   - Derived Metric: $E_{\text{spatial}} = 0.5 \cdot \bar{P}_{\text{unet}} + 0.5 \cdot P_{\text{max}}$.
2. **Terrain Susceptibility ($S_{\text{terrain}}$)**:
   - Source: Spatial gradient & surface roughness proxies derived from satellite tiles and 30m GeoTIFF DEM.
   - Derived Metric: Composite spatial gradient magnitude + reflectance variance index.
3. **Environmental Triggers ($T_{\text{env}}$)**:
   - Source: NASA POWER Agroclimatology API 365-day series (`data/environment/rainfall.csv`).
   - Derived Metric: $T_{\text{env}} = \min\left(1.0, 0.4 \cdot \frac{R_t}{50.0} + 0.6 \cdot \frac{CR_7}{150.0}\right)$.
   - *Note*: Soil moisture and humidity are explicitly declared unavailable in `rainfall.csv` and are not fabricated.

---

## 2. Multi-Criteria Risk Index Formula

$$\text{Risk Index } (R) = 0.40 \cdot E_{\text{spatial}} + 0.35 \cdot S_{\text{terrain}} + 0.25 \cdot T_{\text{env}}$$

### Risk Zonation Thresholds:
- **LOW** ($0.00 \le R < 0.25$): Normal monitoring status.
- **MODERATE** ($0.25 \le R < 0.45$): Advisory alert; monitor slope stability.
- **HIGH** ($0.45 \le R < 0.65$): High risk trigger; spatial evidence + heavy precipitation present.
- **CRITICAL** ($0.65 \le R \le 1.00$): Severe hazard; imminent instability conditions.

---

## 3. Risk Assessment Summary (199 Test Tiles Evaluated)

| Risk Class | Tile Count | Proportion (%) | Description |
| :--- | :--- | :--- | :--- |
| **LOW** | 0 | 0.0% | Low spatial probability & low rainfall trigger |
| **MODERATE** | 199 | 100.0% | Moderate terrain steepness or background rain |
| **HIGH** | 0 | 0.0% | High U-Net detection & significant rainfall |
| **CRITICAL** | 0 | 0.0% | Extreme spatial detection + monsoon saturation |

---

## 4. Supervised Training Justification

> [!NOTE]
> **Why Supervised Learning is NOT Used for Risk Scoring**:
> The Landslide4Sense dataset provides binary segmentation masks ($0$ vs $255$), but lacks multi-class operational risk labels or continuous risk score ground-truth. Fitting a supervised classifier without authentic ground-truth labels would introduce severe bias. A transparent MCE Risk Index is mathematically rigorous and scientifically defensible.

---

## 5. Preservation of Secondary Mining Application (Jharia)

The existing Jharia / Rajapur open-cast mine slope instability work (`models/model_A_best.pkl`, `models/model_B_best.pkl`, `data/mine_dem.tif`, `data/events/rajapur_instability_events.csv`) remains completely untouched as Application 2 (Mining Slope Instability Monitoring).
