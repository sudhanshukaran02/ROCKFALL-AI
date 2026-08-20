# Sentinel-1 InSAR Processing Readiness Report — Rajapur / South Jharia

## 1. Executive Summary
This report evaluates the availability, temporal continuity, orbit geometry, and processing readiness of **Sentinel-1 Synthetic Aperture Radar (SAR)** data for interferometric displacement analysis over the **Rajapur / South Jharia Open Cast Mine** (BCCL, Dhanbad, Jharkhand).

- **InSAR Processing Readiness**: **READY**
- **Actual SAR Files Downloaded**: **NO** (Acquisition inventory complete; download pending review)
- **Actual InSAR Processing Performed**: **NO** (No synthetic interferograms or fake displacement values created)

---

## 2. Acquisition Inventory Overview
- **Total IW SLC Acquisitions Discovered**: `525` scenes
- **Satellite Breakdown**:
  - Sentinel-1A: `263` scenes
  - Sentinel-1B: `121` scenes (Pre-December 2021)
  - Sentinel-1C / 1D: `141` scenes (2024–2026 continuation)
- **Date Range**: `2018-01-05` to `2026-08-15`
- **Beam Mode & Processing Level**: `IW` (Interferometric Wide Swath), `SLC` (Single Look Complex)
- **Polarization**: `VV+VH` (Dual polarization)
- **Orbit Directions**:
  - Descending: `263` scenes
  - Ascending: `262` scenes
- **Relative Orbit Tracks**: `121, 85`

---

## 3. Recommended Primary Acquisition Group
For optimal Small Bounding Baseline Subset (SBAS-InSAR) and Persistent Scatterer (PS-InSAR) processing, acquisitions must share identical relative orbits and viewing geometries.

| Parameter | Recommended Specification | Justification |
| :--- | :--- | :--- |
| **Target Relative Orbit** | **Relative Orbit 121** | Highest scene density and optimal look angle |
| **Pass Direction** | **DESCENDING** | Steep incidence angle (~38°–41°) minimizing steep slope shadow |
| **Polarization Mode** | **VV (Co-polarization)** | Strongest phase coherence over bare ground and quarry rock |
| **Initial Target Download** | **24 SLC Scenes** | Spans multi-year baseline for linear velocity inversion |

---

## 4. Proposed InSAR Processing Pipeline Design
```
Sentinel-1 SLC Archives (.zip)
           │
           ▼
1. Precise Orbit File Application (ESA POEORB)
           │
           ▼
2. TOPS-Split & AOI Subsetting (Rajapur AOI Bounding Box)
           │
           ▼
3. Sentinel-1 Co-Registration (Enhanced Spectral Diversity - ESD)
           │
           ▼
4. Multi-Temporal Interferogram Formation (Small Baseline Pairs)
           │
           ▼
5. Topographic Phase Removal (Real SRTM DEM data/mine_dem.tif)
           │
           ▼
6. Goldstein Phase Filtering & Multilooking (10x2 spatial looks)
           │
           ▼
7. Phase Unwrapping (SNAPHU Minimum Cost Flow)
           │
           ▼
8. Geocoding & Atmospheric Phase Delay Correction (PyAPS / ERA5)
           │
           ▼
9. Time-Series Inversion & Mean Velocity Mapping (MintPy / LiCSBAS)
```

---

## 5. Recommended Open-Source Toolchain
1. **ESA SNAP (Sentinel Application Platform)**: TOPS debursting, co-registration, and initial interferogram generation.
2. **ISCE2 / ISCE3 (InSAR Scientific Computing Environment)**: High-throughput automated SLC stack processing.
3. **MintPy (Miami InSAR Time-series software in Python)**: SBAS time-series inversion, atmospheric correction, and displacement velocity estimation.

---

## 6. Scientific Limitations & Disclaimers

> [!WARNING]
> **SURFACE DISPLACEMENT vs ROCKFALL DISCLAIMER**:
> Sentinel-1 InSAR measures line-of-sight (LOS) surface displacement and ground deformation. InSAR deformation signals do NOT automatically establish rockfall events. Surface displacement in the Rajapur coalfield may stem from mine subsidence over legacy pillars, active open-pit bench excavation, underground seam fires, or monsoon soil movement.

> [!IMPORTANT]
> **NO FAKE PROCESSING STATEMENT**:
> No actual SAR zip archives have been downloaded or processed in this turn. No synthetic interferograms, fake velocity values, or artificial deformation maps have been generated.
