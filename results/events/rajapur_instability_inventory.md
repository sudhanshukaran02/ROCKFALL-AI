# Historical Instability Event Inventory Report — Rajapur / South Jharia Coal Mine

## 1. Objective
This report compiles an evidence-based historical instability event inventory for the **Rajapur / South Jharia Open Cast Project (OCP)**, Dhanbad, Jharkhand (Bharat Coking Coal Limited - BCCL). The objective is to systematically document observed geotechnical failures, slope collapses, ground fractures, mine seam fire deformations, and subsidence events to evaluate dataset readiness for Machine Learning (ML) rockfall susceptibility modeling.

---

## 2. Study Area Context
- **Location**: Rajapur / South Jharia Open Cast Project, Jharia Coalfield, Dhanbad, Jharkhand.
- **Operator**: Bharat Coking Coal Limited (BCCL).
- **Geology**: Gondwana coal measures comprising jointed sandstone, shale, and coal seams (VIII/IX, V/VI) with shallow overburden depths (~50–60 m).
- **Operational Challenges**: Multi-bench opencast mining over legacy underground bord-and-pillar workings, active underground seam fires, steep bench geometries (>35°), and monsoon water seepage.

---

## 3. Sources Searched
Search efforts covered Tier 1 Government/Official documents (BCCL, DGMS, Coal Controller, MoEFCC/PARIVESH), Tier 2 Peer-Reviewed Academic Literature (IIT-ISM Dhanbad, IIT Bombay), and Tier 3 Industry Reports.

### Source Register Summary
| source_id | source_title | source_type | organization | publication_date |
| --- | --- | --- | --- | --- |
| SRC_001 | Stability Analysis of Highwall Slopes in Open Cast Mine, Jharia Coalfield | Tier 2 Academic Literature | IIT-ISM Dhanbad / IIT Bombay | 2015-09 |
| SRC_002 | Geomechanical Characterization and Slope Stability Assessment in Jharia Coalfield Mines | Tier 2 Academic Literature | ResearchGate / Mining Engineering Journal | 2016-11 |
| SRC_003 | Investigation of Underground Mine Fires and Surface Cracking in Bastacolla-Rajapur Region | Tier 1 Government/Official | BCCL / CIMFR Dhanbad | 2018-05 |
| SRC_004 | BCCL Environmental Clearance and Mine Safety Status Report — Bastacolla Area | Tier 1 Government/Official | Ministry of Environment, Forest & Climate Change (MoEFCC) | 2019-10 |
| SRC_005 | Annual Environmental Monitoring and Dump Stability Audit of Rajapur OCP | Tier 1 Government/Official | Coal Controller Organization (CCO) | 2021-12 |
| SRC_006 | DGMS Safety Notice and Fire Stabilization Program in Jharia Coalfield | Tier 1 Government/Official | Directorate General of Mines Safety (DGMS) | 2022-12 |
| SRC_007 | Highwall Stability and Rockfall Hazard Assessment in Open Pit Coal Mining | Tier 2 Academic Literature | Journal of Rock Mechanics & Geotechnical Engineering | 2023-06 |
| SRC_008 | Historical Coal Mining Disasters and Safety Records in Jharia Field | Tier 1 Government/Official | Directorate General of Mines Safety (DGMS) | 2014-01 |
| SRC_009 | Haul Road and Highwall Slope Stability Review at Rajapur OCP | Tier 1 Government/Official | Bharat Coking Coal Limited (BCCL Safety Wing) | 2020-09 |
| SRC_010 | Implementation of Highwall Mining Technology at Rajapur OCP — Geotechnical Report | Tier 1 Government/Official | Central Mine Planning & Design Institute (CMPDI) | 2024-03 |

---

## 4. Source Hierarchy & Data Integrity Protocol
- **Tier 1 (Government / Regulatory)**: High reliability for administrative, safety notices, and mine plan boundaries.
- **Tier 2 (Academic / Geotechnical Studies)**: High precision for site-specific slope stability, SMR ratings, joint kinematics, and bench failure mechanics.
- **Tier 3 (Industry Reports)**: Supporting context only.
- **Strict Anti-Manufacturing Protocol**: Event labels are assigned strictly according to explicit source evidence. Absence of documented event data is NEVER interpreted as proof of stability.

---

## 5. Event Classification Methodology
Events are categorized into 11 distinct geomechanical failure types:
1. `CONFIRMED_ROCKFALL` (Detachment and free fall/roll of rock blocks from steep slopes)
2. `CONFIRMED_SLOPE_FAILURE` (Rotational/translational slope slump in soil or waste dumps)
3. `WEDGE_FAILURE` (Failure along intersecting joint planes in rock mass)
4. `BENCH_FAILURE` (Localized bench face spalling or slope collapse)
5. `GROUND_COLLAPSE` (Surface skin collapse into underground voids)
6. `SUBSIDENCE` (Gradual or rapid ground sinking over mined-out pillars)
7. `GROUND_FRACTURE` (Tension cracking along pit crest or haul road)
8. `FIRE_INDUCED_GROUND_DEFORMATION` (Thermal fracturing and gas fissure formation)
9. `ROOF_COLLAPSE` (Underground gallery roof fall)
10. `OTHER_INSTABILITY` (Uncategorized structural movement)
11. `UNKNOWN` (Unspecified failure mode)

### Rockfall Label Assignment Rules
- `rockfall_label = 1`: Confirmed rockfall event (detachment of boulders/rock blocks from highwall/bench).
- `rockfall_label = 0`: Confirmed non-rockfall instability (e.g., roof collapse, waste dump slump, floor subsidence).
- `rockfall_label = -1`: Unknown / insufficient evidence or non-rockfall slope mechanics (e.g., fire-induced cracking).

---

## 6. Documented Historical Event Inventory
The table below lists all 10 documented historical instability events for the Rajapur / South Jharia project area:

| event_id | event_year | event_type | mine_name | latitude | longitude | rockfall_label | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EVT_RAJ_001 | 2015 | BENCH_FAILURE | Rajapur OCP | 23.753889 | 86.416111 | 0 | HIGH |
| EVT_RAJ_002 | 2016 | WEDGE_FAILURE | Rajapur OCP | 23.755556 | 86.414444 | 0 | HIGH |
| EVT_RAJ_003 | 2018 | FIRE_INDUCED_GROUND_DEFORMATION | Rajapur OCP | 23.756389 | 86.414167 | -1 | HIGH |
| EVT_RAJ_004 | 2019 | SUBSIDENCE | Rajapur OCP / South Jharia | 23.753611 | 86.416944 | 0 | HIGH |
| EVT_RAJ_005 | 2021 | CONFIRMED_SLOPE_FAILURE | Rajapur OCP | 23.761822 | 86.417415 | 0 | HIGH |
| EVT_RAJ_006 | 2022 | GROUND_COLLAPSE | South Jharia / Rajapur OC | 23.749222 | 86.41498 | 0 | HIGH |
| EVT_RAJ_007 | 2023 | CONFIRMED_ROCKFALL | Rajapur OCP | 23.753611 | 86.416667 | 1 | HIGH |
| EVT_RAJ_008 | 2014 | ROOF_COLLAPSE | Rajapur Colliery (Underground) | NaN | NaN | 0 | MEDIUM |
| EVT_RAJ_009 | 2020 | GROUND_FRACTURE | Rajapur OCP | 23.764043 | 86.412249 | -1 | HIGH |
| EVT_RAJ_010 | 2024 | BENCH_FAILURE | Rajapur OCP | 23.757831 | 86.419891 | 0 | HIGH |

---

## 7. Confirmed Rockfall Events
- **Total Count**: **1 Event** (`EVT_RAJ_007`)
- **Event Summary**: In April 2023, blast vibrations triggered the detachment of weathered sandstone boulders from upper highwall Bench 2 at Rajapur OCP (`Lat: 23.753611°N`, `Lon: 86.416667°E`), resulting in localized rockfall into the pit bottom.
- **Source**: *Highwall Stability and Rockfall Hazard Assessment in Open Pit Coal Mining* (Journal of Rock Mechanics & Geotechnical Engineering, 2023).

---

## 8. Confirmed Slope Failures (Waste Dumps & Benches)
- **Bench Failures**: 2 Events (`EVT_RAJ_001`, `EVT_RAJ_010`) — Localized bench slope spalling and seepage-induced highwall slope failures along jointed sandstone faces.
- **Dump Slope Failures**: 1 Event (`EVT_RAJ_005`) — Rainfall infiltration caused rotational slumping on the northern external overburden dump in July 2021.

---

## 9. Wedge / Structural Rock Mass Failures
- **Total Count**: 1 Event (`EVT_RAJ_002`) — Structural wedge failure along intersecting joint sets J1 and J2 in fractured sandstone overburden on the western bench of Rajapur OCP (November 2016).

---

## 10. Ground Collapse & Subsidence Events
- **Subsidence Events**: 1 Event (`EVT_RAJ_004`) — Monsoon-induced pit floor subsidence over legacy un-stowed bord-and-pillar workings in August 2019.
- **Ground Collapse**: 1 Event (`EVT_RAJ_006`) — Surface pillar skin collapse creating a 3m deep fissure in South Jharia sector in November 2022.
- **Roof Collapse**: 1 Event (`EVT_RAJ_008`) — Historical underground gallery roof fall in seam VI (2014, mine-level record).

---

## 11. Fire-Induced Ground Deformation Events
- **Fire Deformation**: 1 Event (`EVT_RAJ_003`) — Active seam VIII/IX fire thermal fracturing resulting in surface collapse vents (May 2018).
- **Ground Fracture**: 1 Event (`EVT_RAJ_009`) — Haul road tension cracking (10–15 cm width) along northwestern pit perimeter (September 2020).

---

## 12. Spatial Integrity & Location Precision
- **Events with Coordinates**: `9 / 10` (`90.0%`)
- **Events without Coordinates**: `1` (`EVT_RAJ_008`)
- **Events Inside Rajapur AOI**: `6 / 10` (`60.0%`)
- **Events Outside Rajapur AOI**: `3` (`0`)

---

## 13. Terrain Feature Extraction at Event Locations
For the 6 georeferenced events inside the AOI, terrain derivatives were extracted from real SRTM rasters:
- **Elevation Range**: `160.00 m` to `204.94 m`
- **Slope Range**: `4.45°` to `37.26°` (Highest slope associated with `EVT_RAJ_007` rockfall at `37.26°` and `EVT_RAJ_001` bench failure at `36.91°`).

---

## 14. Evidence Confidence Distribution
- **HIGH Confidence**: `9` events (`100%` supported by official DGMS/BCCL reports or peer-reviewed literature).
- **MEDIUM Confidence**: `1` events.
- **LOW Confidence**: `0` events.

---

## 15. Data Limitations

> [!WARNING]
> 1. **Under-Reporting & Reporting Bias**: Official records document major operational disruptions, accidents, and environmental compliance audits; minor bench spalling or small rockfalls are rarely recorded in regulatory literature unless they cause injury or equipment damage.
> 2. **Coarse Spatial Precision**: Most historical reports provide mine-level or bench-level text descriptions rather than sub-meter GPS points for rockfall locations.
> 3. **Distinction of Phenomena**: Mine fire collapse, pillar subsidence, and waste dump slumping follow fundamentally different geomechanical mechanisms than rockfall block detachment.

---

## 16. Suitability for Supervised ML Training
- **Confirmed Rockfall Events inside AOI**: **1 Event** (`rockfall_label = 1`)
- **Confirmed Non-Rockfall Events**: **7 Events** (`rockfall_label = 0`)
- **Uncertain / Deformation Events**: **2 Events** (`rockfall_label = -1`)
- **Audit Conclusion**: **NOT READY FOR SUPERVISED ML ROCKFALL MODELING**. 
  * A single positive rockfall sample (`N=1`) is statistically insufficient to train, cross-validate, or evaluate any supervised machine learning classifier (Model A / Model B). Attempting to train an ML model on this dataset would result in severe class imbalance, severe overfitting, and meaningless evaluation metrics.

---

## 17. Scientific Recommendations
1. **Do NOT Train Supervised ML Models**: Maintain the freeze on Model A and Model B training until a substantial, high-resolution event inventory is established.
2. **Implement Remote Sensing Event Mapping**: Utilize multi-temporal InSAR (PS-InSAR / SBAS) and high-resolution optical satellite imagery (Sentinel-2 / PlanetScope / PlanetScope LiDAR) to detect slope surface displacements over time.
3. **Establish On-Site Rockfall Logging**: Partner with BCCL safety teams to digitize daily pit inspection logs and Total Station / Prism monitoring data.
