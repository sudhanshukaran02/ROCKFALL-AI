# Landslide Dataset Audit: Landslide4Sense / Kaggle Landslide Divided

## Executive Summary
This document provides a comprehensive technical audit of the benchmark landslide dataset located at `data/dataset/`. The dataset is structured for spatial semantic segmentation of landslides from multi-channel remote sensing satellite imagery.

---

## 1. Dataset Directory & File Organization

```
data/dataset/
├── train/
│   ├── images/  (1,385 PNG files: image_0.png ... image_3795.png)
│   └── masks/   (1,385 PNG files: mask_0.png ... mask_3795.png)
├── validation/
│   ├── images/  (396 PNG files: image_1013.png ... image_3787.png)
│   └── masks/   (396 PNG files: mask_1013.png ... mask_3787.png)
└── test/
    ├── images/  (199 PNG files: image_100.png ... image_3700.png)
    └── masks/   (199 PNG files: mask_100.png ... mask_3700.png)
```

---

## 2. Sample Breakdown & Split Ratios

| Dataset Split | Number of Images | Number of Masks | Proportion | Positive Image Ratio | Positive Pixel Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Train** | 1,385 | 1,385 | 69.95% | 99.8% (1,382 / 1,385) | 4.50% |
| **Validation** | 396 | 396 | 20.00% | 100.0% (396 / 396) | 4.03% |
| **Test** | 199 | 199 | 10.05% | 100.0% (199 / 199) | 4.63% |
| **Total** | **1,980** | **1,980** | **100.00%** | **99.8%** | **4.46%** |

---

## 3. Data Specification & Format

- **Image Dimensions**: 128 x 128 pixels
- **Image Channels**: 4 channels (`RGBA`, 8-bit unsigned integer `uint8`)
- **Image File Format**: Portable Network Graphics (`.png`)
- **Average Image File Size**: ~28.1 KB per file
- **Mask Dimensions**: 128 x 128 pixels
- **Mask Channels**: 4 channels (`RGBA`, 8-bit unsigned integer `uint8`)
- **Mask File Format**: Portable Network Graphics (`.png`)
- **Average Mask File Size**: ~775 bytes per file
- **Class Labels**:
  - `0`: Background (Non-landslide pixel)
  - `255`: Landslide pixel
- **Pixel Class Imbalance**: ~95.5% background vs ~4.5% landslide pixels across tiles.

---

## 4. Crucial Analytical Distinction: Spatial vs Temporal Data

> [!IMPORTANT]
> **SPATIAL DATA vs TEMPORAL DATA DISTINCTION**
>
> 1. **Spatial Data Characteristics**:
>    - Each sample is a static 128 x 128 x 4 multi-spectral patch of terrain.
>    - Captures surface reflectance, vegetation loss, soil exposure, and scarp boundaries.
>    - Ideal for pixel-level semantic segmentation (detecting WHERE landslides occurred).
>
> 2. **Temporal Data Characteristics**:
>    - Represents sequential time-series measurements over time (e.g. daily rainfall $R_t$, soil moisture $M_t$, cumulative 7-day precipitation $CR_7$).
>    - Captures triggering kinetics and escalation trends (detecting WHEN landslides are likely to occur).
>    - **COMPLETELY ABSENT IN THIS DATASET**: There are no timestamps, acquisition dates, revisit frequencies, or sequential tile ordering.

---

## 5. Feasibility of Training an LSTM on this Dataset

> [!CAUTION]
> **LSTM FEASIBILITY: IMPOSSIBLE ON THIS DATASET ALONE**
>
> An image segmentation dataset composed of un-indexed static spatial tiles **CANNOT** be used to train a Long Short-Term Memory (LSTM) network.
>
> **Why?**
> 1. LSTMs require sequential temporal ordering with timestamped steps.
> 2. The images in `data/dataset/` are independent spatial snapshots without temporal continuity.
> 3. Forcing static image patches into an LSTM would result in meaningless temporal gradient updates and false predictive claims.

---

## 6. Correct Architectural Assignment

To address the SIH NER Problem Statement 26001 scientifically:

1. **Spatial Module (Landslide Detection)**:
   - Input: 128 x 128 x 4 satellite optical image.
   - Model: **U-Net / U-Net++ with ResNet/EfficientNet backbone**.
   - Output: Pixel-level binary landslide segmentation mask + Spatial probability map + Landslide area ($m^2$).

2. **Temporal Module (Early Warning LSTM)**:
   - Input: 7-day or 14-day sequence of environmental variables for NER regions (Daily Rainfall, Cumulative Rainfall, Soil Moisture, Humidity).
   - Data Source: NASA POWER / ERA5 daily agroclimatology API for North Eastern Region (e.g. Wayanad, Guwahati, Sikkim, Imphal).
   - Model: **Many-to-One 2-Layer LSTM Network**.
   - Output: Temporal escalation score & 24h-72h future landslide probability.
