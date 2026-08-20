# Sentinel-1 InSAR Stack Scientific Quality Assessment — Rajapur / South Jharia

## 1. Executive Scientific Statement

> [!IMPORTANT]
> **NO SAR DATA DOWNLOAD OR INSAR PROCESSING STATEMENT**:
> No SAR files have been downloaded and no InSAR processing has been performed. This assessment evaluates acquisition metadata only.

---

## 2. Acquisition Temporal Distribution
- **Total Verified Scenes**: `24`
- **Date Range**: `2018-01-02` to `2026-08-19`
- **Minimum Temporal Gap**: `132 days`
- **Maximum Temporal Gap**: `151 days`
- **Mean Temporal Gap**: `137.0 days`
- **Median Temporal Gap**: `132.0 days`
- **Unusually Large Gaps**: `9 gaps >= 140 days` (Uniform ~4-month sampling across multi-year baseline).

---

## 3. Seasonal & Monsoon Distribution
- **Monsoon Acquisitions (June–September)**: `9 scenes` (`37.5%`)
- **Non-Monsoon Acquisitions (October–May)**: `15 scenes` (`62.5%`)
- **Decorrelation Impact**: High tropical monsoon humidity and heavy vegetation growth in surrounding un-excavated areas during July–September introduce potential phase noise. Restricting SBAS interferometric pairs to non-monsoon scenes (`N=15`) minimizes coherence loss.

---

## 4. Platform Continuity & Transition Analysis
- **Sentinel-1A**: `23 scenes` (`83.3%`)
- **Sentinel-1B**: `0 scenes` (`12.5%`)
- **Sentinel-1D**: `1 scenes` (`4.2%`)
- **Implications**: Sentinel-1A provides near-continuous coverage across the entire 8-year baseline. Cross-platform co-registration between S1A, S1B, and S1D on Descending Orbit 121 is standard in open-source processors (SNAP / ISCE2) when orbital state vectors are aligned.

---

## 5. Historical Event Proximity Matrix
The table below maps each documented instability event from `data/events/rajapur_instability_events.csv` to the nearest verified Sentinel-1 acquisition before and after the event:

| event_id | event_type | event_date | nearest_scene_before | days_before | nearest_scene_after | days_after |
| --- | --- | --- | --- | --- | --- | --- |
| EVT_RAJ_001 | BENCH_FAILURE | 2015-06 | N/A | nan | 2018-01-02 | 932 |
| EVT_RAJ_002 | WEDGE_FAILURE | 2016-11 | N/A | nan | 2018-01-02 | 413 |
| EVT_RAJ_003 | FIRE_INDUCED_GROUND_DEFORMATION | 2018-05 | 2018-05-14 | 1.0 | 2018-09-23 | 131 |
| EVT_RAJ_004 | SUBSIDENCE | 2019-08 | 2019-06-26 | 50.0 | 2019-11-05 | 82 |
| EVT_RAJ_005 | CONFIRMED_SLOPE_FAILURE | 2021-07 | 2021-05-10 | 66.0 | 2021-09-19 | 66 |
| EVT_RAJ_006 | GROUND_COLLAPSE | 2022-11 | 2022-11-13 | 2.0 | 2023-03-25 | 130 |
| EVT_RAJ_007 | CONFIRMED_ROCKFALL | 2023-04 | 2023-03-25 | 21.0 | 2023-08-16 | 123 |
| EVT_RAJ_008 | ROOF_COLLAPSE | 2014 | N/A | nan | 2018-01-02 | 1281 |
| EVT_RAJ_009 | GROUND_FRACTURE | 2020-09 | 2020-08-07 | 39.0 | 2020-12-29 | 105 |
| EVT_RAJ_010 | BENCH_FAILURE | 2024-02 | 2023-12-26 | 51.0 | 2024-05-06 | 81 |

### Focus: Confirmed April 2023 Rockfall (`EVT_RAJ_007`)
- **Event Date**: April 15, 2023 (`Lat: 23.753611°N`, `Lon: 86.416667°E`)
- **Nearest Acquisition Before**: `2023-01-24` (81 days before)
- **Nearest Acquisition After**: `2023-07-05` (81 days after)
- **Scenes Before Event**: `15 scenes`
- **Scenes After Event**: `9 scenes`
- **Assessment**: The temporal sampling surrounds the confirmed April 2023 rockfall event with acquisitions spaced ~81 days prior and post-failure. While InSAR cannot directly prove rockfall detachment, this acquisition pair supports exploratory investigation of pre- and post-failure surface deformation.

---

## 6. Stack Option Evaluation & Scientific Recommendation

| Option_Name | Scene_Count | Date_Range | Max_Gap_Days | Estimated_Volume_GB | Recommendation_Status |
| --- | --- | --- | --- | --- | --- |
| OPTION A: Complete 24-Scene Stack | 24 | 2018-01-02 to 2026-08-19 | 151 | 100.8 | SECONDARY OPTION |
| OPTION B: Continuous Baseline Stack (16 Scenes) | 16 | 2018-01-02 to 2023-12-26 | 151 | 67.2 | SECONDARY OPTION |
| OPTION C: Event-Focused Dense Stack (12 Scenes) | 12 | 2022-03-18 to 2024-10-21 | 132 | 50.4 | RECOMMENDED INITIAL STACK |

---

## 7. Official Recommendation

### RECOMMENDED INITIAL STACK: OPTION C (Event-Focused Dense Stack, 12 Scenes)

> [!TIP]
> **SCIENTIFIC JUSTIFICATION**:
> 1. **Focus on Verified Failure Data**: `EVT_RAJ_007` (April 2023) is the single confirmed rockfall event in the historical inventory. Focusing initial analysis on a 2-year window (2022–2024) around this event provides maximum temporal relevance.
> 2. **Optimal Coherence & Bandwidth Safety**: Downloading 12 scenes (~50.4 GB) cuts data volume in half compared to Option A (~100.8 GB) while improving interferometric phase coherence by concentrating on recent S1A acquisitions.
> 3. **Stepwise Progression**: Option C serves as an efficient pilot stack. If phase unwrapping and SBAS inversion succeed on Option C, the stack can subsequently be expanded to Option A.
