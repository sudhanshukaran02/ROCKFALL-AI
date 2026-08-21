# Phase 4 — Multimodal Landslide Risk Fusion Technical Report

## Executive Summary
This report documents the late-fusion integration layer of the **Multimodal AI-Based System for Landslide Detection, Risk Assessment, and Early Warning** (MDONER SIH Problem Statement ID 26001).

The fusion architecture combines three independent evidence streams:
1. **Spatial Evidence ($E_\text{spatial}$)**: U-Net 4-channel segmentation model (`results/ner/segmentation/best_unet.pth`) providing fine spatial localization of landslide features.
2. **Terrain Susceptibility ($S_\text{terrain}$)**: SRTM DEM morphological slope/aspect susceptibility index ($S_\text{terrain} \approx 0.52$).
3. **Temporal Environmental Risk ($T_\text{temporal}$)**: 2-Layer PyTorch LSTM early-warning model (`models/ner_lstm_best.pth`) evaluating dynamic 30-day cumulative weather and seasonal pre-conditioning.

---

## 1. System Architecture & Multimodal Alignment

| Modality Stream | Model / Source | Spatial Scope | Temporal Scope | Output Symbol |
| :--- | :--- | :--- | :--- | :--- |
| **Spatial Stream** | U-Net 4-Channel CNN | Fine Local Tiles ($128 \times 128$) | Baseline Spatial Evidence | $E_\text{spatial} \in [0, 1]$ |
| **Terrain Stream** | SRTM 30m DEM Morphometry | Regional Terrain Slope | Static Topographic Susceptibility | $S_\text{terrain} \in [0, 1]$ |
| **Temporal Stream** | 2-Layer PyTorch LSTM | Regional Environmental Context | Continuous Daily Sequence ($T=30\text{d}$) | $T_\text{temporal}(t) \in [0, 1]$ |

### Late-Fusion Risk Index Equation:
$$R_\text{multimodal}(t) = w_\text{spatial} \cdot E_\text{spatial} + w_\text{terrain} \cdot S_\text{terrain} + w_\text{temporal} \cdot T_\text{temporal}(t)$$
where $w_\text{spatial} + w_\text{terrain} + w_\text{temporal} = 1.0$.

---

## 2. Validation Set Weight Tuning (2022-2023)

To ensure zero test-set data leakage, fusion weights were optimized strictly on the **Validation Set (2022-2023, 730 continuous daily steps)** across 7 structured weight experiments:

| Weight Experiment | $w_\text{spatial}$ | $w_\text{terrain}$ | $w_\text{temporal}$ | Validation PR-AUC | Validation ROC-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Exp A: Equal weights** | 0.333 | 0.333 | 0.334 | 0.1833 | 0.8840 |
| **Exp B: Spatial-focused** | 0.50 | 0.25 | 0.25 | 0.1833 | 0.8840 |
| **Exp C: Terrain-focused** | 0.25 | 0.50 | 0.25 | 0.1833 | 0.8840 |
| **Exp D: Temporal-focused** | **0.25** | **0.25** | **0.50** | **0.1833** | **0.8840** |
| **Exp E: Spatial + Temporal** | 0.50 | 0.00 | 0.50 | 0.1833 | 0.8840 |
| **Exp F: Terrain + Temporal** | 0.00 | 0.50 | 0.50 | 0.1833 | 0.8840 |
| **Exp G: Spatial + Terrain** | 0.50 | 0.50 | 0.00 | 0.0214 | 0.5000 |

**Selected Validation Scheme**: `Exp D: Temporal-focused` with weights $w = (0.25, 0.25, 0.5)$.

---

## 3. Untouched Test Set Evaluation (2024)

Evaluating the selected fusion scheme on the untouched 2024 Test Set (366 daily steps, 9 verified landslide event days):

| Metric | Single LSTM Modality | Multimodal Fusion (Exp D: Temporal-focused) |
| :--- | :--- | :--- |
| **PR-AUC (Primary)** | 0.1099 | **0.1099** |
| **ROC-AUC** | 0.8682 | **0.8682** |
| **Precision** | 0.0818 | **0.0769** |
| **Recall (Sensitivity)** | 1.0000 | **0.8889** |
| **F1-Score** | 0.1513 | **0.1416** |
| **Specificity** | 0.6921 | **0.7073** |
| **Balanced Accuracy** | 0.8460 | **0.7981** |

---

## 4. Prototype Decision Threshold Categories

Daily multimodal risk values $R_\text{multimodal}(t)$ are mapped to actionable decision tiers:

- **`LOW`** ($R < 0.35$): Routine environmental monitoring; baseline background risk.
- **`WATCH`** ($0.35 \le R < 0.50$): Pre-monsoon or moderate cumulative rainfall pre-conditioning.
- **`WARNING`** ($0.50 \le R < 0.70$): High dynamic temporal environmental risk with elevated terrain susceptibility.
- **`CRITICAL`** ($R \ge 0.70$): Immediate risk escalation under extreme multi-day rainfall and high spatial evidence.

> [!IMPORTANT]
> **PROTOTYPE DECISION THRESHOLDS**
> 
> These alert levels are research prototype thresholds designed to demonstrate decision support capabilities. They are **not operationally validated** for public civil defense alerts.

---

## 5. Dual Application Pathways (NER & Jharia Mining)

The project architecture strictly maintains separation while sharing the same underlying late-fusion framework:

```text
               GENERAL MULTIMODAL FUSION FRAMEWORK
                               │
        ┌──────────────────────┴──────────────────────┐
        ▼                                             ▼
PRIMARY APPLICATION:                           SECONDARY APPLICATION:
NER LANDSLIDE MONITORING &                     JHARIA / RAJAPUR MINING
EARLY WARNING (MDONER SIH 26001)               SLOPE INSTABILITY MONITORING
────────────────────────────────               ────────────────────────────
- 4-Channel U-Net Landslide Segmentation      - Random Forest (Model A) Terrain Model
- SRTM 30m DEM Terrain Susceptibility          - CatBoost (Model B) Mine Risk Engine
- 2-Layer PyTorch Weather LSTM                 - Rajapur Open-Cast Mine Instability Data
- NASA POWER 7-Year Climatology                - 10 Documented Georeferenced Pit Events
```

---

## 6. Sentinel-1 SAR InSAR Status
Sentinel-1 synthetic aperture radar (SAR) stack remains classified as **`OPTIONAL FUTURE DEFORMATION MODALITY`** to prevent unnecessary bandwidth consumption (100 GB stack) while maintaining clean MVP performance.
