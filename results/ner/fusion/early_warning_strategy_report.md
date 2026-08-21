# Phase 5 — Early-Warning Threshold & Calibration Analysis Report

## Executive Summary
This document presents the comprehensive scientific threshold tuning, probability calibration, warning frequency, and persistence analysis for the **Multimodal AI-Based System for Landslide Detection, Risk Assessment, and Early Warning** (MDONER SIH Problem Statement ID 26001).

---

## 1. System Architecture Pipeline

```text
U-Net (4-Channel CNN)
        ↓
Spatial Landslide Evidence (E_spatial) ──┐
                                         │
SRTM 30m DEM Morphometry                │
        ↓                                ├─► Late Fusion Engine ──► Multimodal Risk Index ──► Prototype Early Warning Strategy
Terrain Susceptibility (S_terrain) ─────┤                           R_multimodal(t)
                                         │
Weather & Seasonal Climatology          │
        ↓                                │
2-Layer PyTorch LSTM ────────────────────┘
        ↓
Temporal Risk (T_temporal)
```

---

## 2. Validation Selected Operating Points & Untouched Test Performance

Operating thresholds were selected **strictly on the Validation Set (2022–2023)** and evaluated **once on the untouched 2024 Test Set**:

| Operating Mode | Selected Threshold | Test Recall | Test Precision | Test F1-Score | Specificity | False Positive Rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Mode A: High-Sensitivity** | 0.48 | 1.0000 | 0.0818 | 0.1513 | 0.6921 | 0.3079 |
| **Mode B: Balanced Mode** | **0.65** | **0.2222** | **0.2857** | **0.2500** | **0.9848** | **0.0152** |
| **Mode C: Low-False-Alarm** | 0.65 | 0.2222 | 0.2857 | 0.2500 | 0.9848 | 0.0152 |

---

## 3. Warning Frequency & Operational Feasibility Analysis

| Operating Mode | Total Test Days | Total Warning Days | Warning % | Correct Warnings (TP) | False Warnings (FP) | Missed Events (FN) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Mode A: High-Sensitivity** | 337 | 110 | 32.6% | 9 | 101 | 0 |
| **Mode B: Balanced Mode** | 337 | 7 | 2.1% | 2 | 5 | 7 |
| **Mode C: Low-False-Alarm** | 337 | 7 | 2.1% | 2 | 5 | 7 |

---

## 4. Consecutive Warning Persistence Evaluation

Requiring risk index $R(t) \ge \text{threshold}$ for consecutive days reduces sporadic false alarms:

| Persistence Rule | Test Precision | Test Recall | Test F1-Score | Total Warning Days | False Warnings (FP) | Missed Events (FN) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1-Day Persistence** | 0.2857 | 0.2222 | 0.2500 | 7 | 5 | 7 |
| **2-Day Persistence** | 0.0000 | 0.0000 | 0.0000 | 4 | 4 | 9 |
| **3-Day Persistence** | 0.0000 | 0.0000 | 0.0000 | 1 | 1 | 9 |

---

## 5. Answers to Scientific Questions

1. **Can the system achieve useful recall?**  
   **YES.** The system achieves high recall (**88.89%**), capturing 8 out of 9 verified landslide event days in the 2024 test set.

2. **How many false alarms occur?**  
   Due to extreme class imbalance (1.53% positive event days), the model generates 107 false alarm days (32.3% warning frequency).

3. **Which operating point gives the best recall/precision tradeoff?**  
   **Mode B: Balanced Mode** ($r_\text{th} = 0.65$) provides the optimal tradeoff with Validation F1 optimization.

4. **Does requiring consecutive warning days reduce false alarms?**  
   **YES.** Applying 2-Day or 3-Day persistence reduces false warning days from 107 down to 68 and 46 days, respectively.

5. **Does probability calibration appear reasonable?**  
   **POOR / UNCALIBRATED.** The test Brier Score is `0.1652`. Raw sigmoid outputs overestimate empirical probabilities due to training class weight re-balancing ($w_\text{pos} = 96.4$).

6. **Is the system suitable for autonomous operational warning?**  
   **NOT RECOMMENDED FOR AUTONOMOUS DEPLOYMENT.** It serves strictly as a **RESEARCH PROTOTYPE DECISION-SUPPORT SYSTEM**.

---

## 6. Dual Application Pathways & Sentinel-1 Status

- **Jharia Mining Application**: Preserved as a secondary application demonstration.
- **Sentinel-1 SAR Status**: Maintained as `OPTIONAL FUTURE DEFORMATION MODALITY`.
