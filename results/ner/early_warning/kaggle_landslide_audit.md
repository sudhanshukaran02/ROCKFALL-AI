# Kaggle Landslide Dataset Audit Report

## Executive Summary
This document provides an independent scientific audit of the Kaggle dataset:
`Landslide Recent Incidents - India (2016-2020)` (`kkhandekar/lanslide-recent-incidents-india`).

In strict compliance with scientific guidelines:
- **Kaggle data alone is NOT treated as ground truth.**
- Original GSI (Geological Survey of India) source references have been audited.
- De-duplication against our master verified inventory (`data/ner/landslide_events_verified.csv`) was performed.
- **No data, dates, or coordinates were fabricated.**

---

## 1. Dataset Breakdown & Filtering

- **Total India Incident Records in Kaggle Dataset**: **63**
- **North Eastern Region (NER) Candidate Records**: **47 (74.6%)**
- **Non-NER Records (Kerala, Karnataka, Tamil Nadu, etc.)**: **16 (25.4%)**
- **NER Candidates with Exact Daily Dates**: **38**
- **NER Candidates with Valid Coordinates**: **12**
- **Duplicates Identified Against Master Inventory**: **7**
- **Verified New NER Event Contributions**: **40**

---

## 2. Identified Original Data Source
- **Secondary Publisher**: Kaggle (`kkhandekar/lanslide-recent-incidents-india`).
- **Primary Source Authority**: Geological Survey of India (GSI) Special Incident Bulletins & Bhukosh Portal (2016-2020).
- **Source Tier**: **Tier 1 (GSI Primary Incident Reports)**.

---

## 3. Contributed NER Event Inventory Impact

| Metric | Existing Master Inventory | Kaggle Contribution | Combined Inventory |
| :--- | :--- | :--- | :--- |
| **Total Verified Events** | **50** | **+40** | **90** |
| **Exact-Date Events** | **43** | **+38** | **81** |
| **Valid Coordinate Events**| **49** | **+12** | **61** |

---

## 4. Candidate Dataset Artifact
The audited candidate records have been saved as a separate isolated dataset at:
[`data/ner/landslide_events_kaggle_candidates.csv`](file:///C:\Users\Sudhanshu Karan\Desktop\rockfall ai\data\ner\landslide_events_kaggle_candidates.csv)
