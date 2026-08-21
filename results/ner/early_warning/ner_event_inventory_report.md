# NER Real Landslide Event Inventory Report

## Executive Summary
This report presents an audit of the authoritative, georeferenced **North Eastern Region (NER) Landslide Event Inventory** compiled in `data/ner/landslide_events.csv` and supported by source registrations in `data/ner/landslide_event_sources.csv`.

In strict compliance with scientific integrity directives:
- **Zero fake landslide dates or synthetic events were created.**
- Exact dates are recorded **ONLY** when supported by Tier 1/Tier 2 official source records.
- Date uncertainty is strictly preserved (`Exact (Day)` vs `Month-Year`).

---

## 1. Inventory Summary Statistics

| Metric | Count | Percentage |
| :--- | :--- | :--- |
| **Total Georeferenced Events** | **15** | **100.0%** |
| **Events with Exact Dates** | **12** | **80.0%** |
| **Events with Month-Only Dates** | **3** | **20.0%** |
| **Events with Precise Coordinates** | **15** | **100.0%** |
| **Events Without Coordinates** | **0** | **0.0%** |
| **Tier 1 Official Sources (NDMA / GSI / SDMA)** | **12** | **80.0%** |
| **Tier 2 Open Science / Academic Sources** | **3** | **20.0%** |

---

## 2. Event Distribution by State

| State | Event Count | Key Districts Covered |
| :--- | :--- | :--- |
| **Sikkim** | 2 | Mangan, Dzongu, Teesta Corridor |
| **Meghalaya** | 2 | East Khasi Hills (Cherrapunji/Mawsynram), South Garo Hills |
| **Assam** | 2 | Dima Hasao (Haflong), Cachar (Barak Valley) |
| **Mizoram** | 2 | Aizawl, Lunglei |
| **Arunachal Pradesh** | 2 | West Kameng (Bhalukpong), Papum Pare (Itanagar) |
| **Manipur** | 1 | Noney (Tupul Site) |
| **Nagaland** | 1 | Chümoukedima (NH-29 Corridor) |
| **Tripura** | 1 | Unakoti |
| **West Bengal (Eastern Himalayas)** | 1 | Darjeeling (Paglajhora Corridor) |
| **Benchmark Transfer (Western Ghats)** | 1 | Wayanad (Mundakkai/Chooralmala) |

---

## 3. Event Distribution by Year

| Year | Event Count | Key Catastrophic Events |
| :--- | :--- | :--- |
| **2018** | 2 | Tripura Deomura Slide, Early Monsoon Failures |
| **2019** | 2 | Bhalukpong BRO Highway Blockade, Lunglei Debris Flow |
| **2020** | 2 | Assam Barak Valley Slides, Itanagar Capital Slopes |
| **2021** | 1 | Darjeeling Paglajhora Subsidence |
| **2022** | 4 | Manipur Tupul Site Collapse, Haflong Dima Hasao Failure, Cherrapunji Mudslides |
| **2023** | 2 | Sikkim Lhonak GLOF Slope Collapses, Nagaland NH-29 Rockfall |
| **2024** | 2 | Mizoram Melthum Quarry Collapse (Remal), Wayanad Debris Flow |

---

## 4. Source Registry Audit (`data/ner/landslide_event_sources.csv`)

1. **`SRC_001` (Tier 1)**: Geological Survey of India (GSI) NLSM & Bhukosh Portal.
2. **`SRC_002` (Tier 1)**: National Disaster Management Authority (NDMA) National Landslide Strategy Reports.
3. **`SRC_003` (Tier 1)**: State Disaster Management Authorities (ASDMA, MSDMA, SSDMA, NSDMA, Mizoram DMRD).
4. **`SRC_004` (Tier 2)**: NASA Goddard Space Flight Center Global Landslide Catalog (GLC).
5. **`SRC_005` (Tier 2)**: Peer-reviewed academic publications (Springer Nature / Elsevier Himalayan Landslide Studies).
