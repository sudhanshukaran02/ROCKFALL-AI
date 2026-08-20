# Sentinel-1 InSAR Data Quality & Risk Assessment — Rajapur / South Jharia

## 1. Quality Control Overview
This report evaluates potential decorrelation risks, geometric distortions, atmospheric disturbances, and operational constraints for Sentinel-1 InSAR processing over the Rajapur / South Jharia mine.

---

## 2. Key Remote Sensing Risk Factors

### A. Temporal & Vegetation Decorrelation
- **Risk Level**: **MEDIUM–HIGH**
- **Impact**: Heavy monsoon vegetation growth (July–October) causes severe loss of interferometric phase coherence in un-vegetated surroundings.
- **Mitigation**: Restrict interferometric pairs to short temporal baselines (<36 days) and utilize VV co-polarization channels.

### B. Mining Excavation Surface Changes
- **Risk Level**: **HIGH**
- **Impact**: Active opencast mining continuously alters pit geometry, bench slopes, and overburden dumps. Rapid surface restructuring destroys phase coherence between SAR passes.
- **Mitigation**: Focus Persistent Scatterer (PS) analysis on stable infrastructure, highwall crests, and undisturbed pit perimeters.

### C. Atmospheric Phase Delay Artifacts
- **Risk Level**: **MEDIUM**
- **Impact**: Tropical monsoon humidity variations introduce turbulent atmospheric phase delays that mimic ground deformation.
- **Mitigation**: Apply PyAPS / ERA5 atmospheric correction models during time-series inversion in MintPy.

### D. Geometric Distortions (Layover & Shadow)
- **Risk Level**: **MEDIUM**
- **Impact**: Very steep bench faces (>35°) aligned perpendicular to the SAR look direction may experience local radar layover or shadow.
- **Mitigation**: Combine Ascending (Orbit 85) and Descending (Orbit 121) passes to resolve 2D horizontal and vertical displacement vectors.

---

## 3. DEM Resolution Limitations
- **Current Reference DEM**: SRTM 1-ArcSec (~30m resolution).
- **Limitation**: SRTM provides a static baseline (2000/2020) that does not reflect recent open-pit bench excavations.
- **Recommendation**: Ingest high-resolution UAV LiDAR or PlanetScope photogrammetric DEMs for topographic phase subtraction during co-registration.
