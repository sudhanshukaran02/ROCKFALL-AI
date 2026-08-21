# NER Landslide Spatial Segmentation Report: U-Net Model

## Executive Summary
This report presents the quantitative evaluation of the **4-Channel U-Net Landslide Segmentation Model** trained on the benchmark landslide dataset for the North Eastern Region (NER) early warning platform.

> [!IMPORTANT]
> **CRITICAL SCIENTIFIC DISTINCTION**
> This spatial segmentation model answers the question:
> **"WHERE do satellite optical/multispectral signatures indicate active or past landslide pixels?"**
>
> It does **NOT** answer *"WHEN will a landslide occur?"*. The temporal triggering kinetics will be handled by the upcoming environmental LSTM module.

---

## 1. Dataset & Split Specifications

| Split | Number of Images | Number of Masks | Role |
| :--- | :--- | :--- | :--- |
| **Train** | 1,385 | 1,385 | Model optimization & gradient updates |
| **Validation** | 396 | 396 | Hyperparameter tuning & early stopping |
| **Test** | 199 | 199 | **100% Untouched final evaluation** |

---

## 2. Test Set Quantitative Evaluation Results

| Metric | Score | Percentage |
| :--- | :--- | :--- |
| **Intersection over Union (IoU)** | **0.2595** | **25.95%** |
| **Dice Coefficient / F1-Score** | **0.4121** | **41.21%** |
| **Precision** | **0.2660** | **26.60%** |
| **Recall** | **0.9141** | **91.41%** |
| **Pixel Accuracy** | **0.8794** | **87.94%** |

---

## 3. Pixel Confusion Matrix (Test Split - 3,260,416 total pixels)

| | Predicted Background | Predicted Landslide |
| :--- | :--- | :--- |
| **Actual Background** | **TN = 2,729,222** (83.71%) | **FP = 380,373** (11.67%) |
| **Actual Landslide** | **FN = 12,963** (0.40%) | **TP = 137,858** (4.23%) |

---

## 4. Class-Specific Breakdown

- **Landslide Class (Positive Target)**:
  - IoU: `0.2595`
  - F1 / Dice: `0.4121`
  - Precision: `0.2660`
  - Recall: `0.9141`
- **Background Class**:
  - IoU: `0.8740`
  - F1 / Dice: `0.9328`
  - Precision: `0.9953`
  - Recall: `0.8777`

---

## 5. Sample Prediction Visualizations

Sample qualitative outputs on unseen test image tiles are saved at:
[`sample_predictions.png`](file:///C:\Users\Sudhanshu Karan\Desktop\rockfall ai\results\ner\segmentation\sample_predictions.png)
