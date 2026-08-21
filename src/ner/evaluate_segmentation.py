import os
import sys
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import torch

from src.ner.config import Config
from src.ner.dataset import get_dataloader
from src.ner.unet import UNet


@torch.no_grad()
def evaluate_segmentation():
    """
    Evaluates the trained U-Net checkpoint on the completely untouched TEST split (199 samples).
    Calculates pixel-level metrics, generates test predictions, sample overlay visualizations, and markdown report.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluating U-Net model on device: {device}")
    
    if not os.path.exists(Config.MODEL_CHECKPOINT_PATH):
        raise FileNotFoundError(f"Model checkpoint not found at {Config.MODEL_CHECKPOINT_PATH}. Run training first.")
        
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(Config.TEST_PREDS_DIR, exist_ok=True)
    
    # Load model
    model = UNet(in_channels=Config.IN_CHANNELS, num_classes=Config.NUM_CLASSES).to(device)
    model.load_state_dict(torch.load(Config.MODEL_CHECKPOINT_PATH, map_location=device))
    model.eval()
    print(f"Successfully loaded best checkpoint from {Config.MODEL_CHECKPOINT_PATH}")
    
    # Load test dataloader
    test_loader = get_dataloader(Config.TEST_DIR, batch_size=1, shuffle=False, transform=False)
    print(f"Test split samples to evaluate: {len(test_loader.dataset)}")
    
    total_tp, total_fp, total_fn, total_tn = 0, 0, 0, 0
    sample_visuals = []
    
    for idx, (image, mask, filename) in enumerate(test_loader):
        image = image.to(device)
        mask = mask.to(device)
        filename_str = filename[0]
        
        logits = model(image)
        probs = torch.sigmoid(logits)
        preds = (probs > 0.5).float()
        
        # Flatten tensors for confusion matrix
        pred_flat = preds.cpu().numpy().squeeze()
        mask_flat = mask.cpu().numpy().squeeze()
        
        tp = np.sum((pred_flat == 1.0) & (mask_flat == 1.0))
        fp = np.sum((pred_flat == 1.0) & (mask_flat == 0.0))
        fn = np.sum((pred_flat == 0.0) & (mask_flat == 1.0))
        tn = np.sum((pred_flat == 0.0) & (mask_flat == 0.0))
        
        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_tn += tn
        
        # Store first 6 samples for visualization
        if idx < 6:
            # Image for visualization (channels 0, 1, 2 = RGB)
            img_vis = image.cpu().numpy().squeeze().transpose(1, 2, 0)[:, :, :3]
            sample_visuals.append({
                "filename": filename_str,
                "image": img_vis,
                "target": mask_flat,
                "prediction": pred_flat,
                "prob": probs.cpu().numpy().squeeze()
            })

    # Overall dataset metrics (micro-averaged across all pixels)
    total_pixels = total_tp + total_fp + total_fn + total_tn
    iou = total_tp / (total_tp + total_fp + total_fn + 1e-8)
    dice = (2.0 * total_tp) / (2.0 * total_tp + total_fp + total_fn + 1e-8)
    precision = total_tp / (total_tp + total_fp + 1e-8)
    recall = total_tp / (total_tp + total_fn + 1e-8)
    pixel_accuracy = (total_tp + total_tn) / (total_pixels + 1e-8)
    
    # Class-specific metrics
    # Landslide Class (Positive)
    landslide_precision = precision
    landslide_recall = recall
    landslide_f1 = dice
    landslide_iou = iou
    
    # Background Class (Negative)
    bg_precision = total_tn / (total_tn + total_fn + 1e-8)
    bg_recall = total_tn / (total_tn + total_fp + 1e-8)
    bg_f1 = (2.0 * total_tn) / (2.0 * total_tn + total_fp + total_fn + 1e-8)
    bg_iou = total_tn / (total_tn + total_fp + total_fn + 1e-8)
    
    metrics_dict = {
        "metric": [
            "Intersection over Union (IoU)", "Dice Coefficient (F1)", "Precision", "Recall", "Pixel Accuracy",
            "True Positives (TP)", "False Positives (FP)", "False Negatives (FN)", "True Negatives (TN)",
            "Landslide Class IoU", "Landslide Class F1", "Landslide Class Precision", "Landslide Class Recall",
            "Background Class IoU", "Background Class F1", "Background Class Precision", "Background Class Recall"
        ],
        "value": [
            iou, dice, precision, recall, pixel_accuracy,
            total_tp, total_fp, total_fn, total_tn,
            landslide_iou, landslide_f1, landslide_precision, landslide_recall,
            bg_iou, bg_f1, bg_precision, bg_recall
        ]
    }
    df_metrics = pd.DataFrame(metrics_dict)
    df_metrics.to_csv(Config.TEST_METRICS_PATH, index=False)
    print(f"Saved test metrics to {Config.TEST_METRICS_PATH}")
    
    # Print Test Evaluation Results
    print("\n" + "="*60)
    print("NER LANDSLIDE SEGMENTATION TEST EVALUATION RESULTS")
    print("="*60)
    print(f"Test IoU (Jaccard)     : {iou:.4f} ({iou*100:.2f}%)")
    print(f"Test Dice / F1         : {dice:.4f} ({dice*100:.2f}%)")
    print(f"Test Precision         : {precision:.4f} ({precision*100:.2f}%)")
    print(f"Test Recall            : {recall:.4f} ({recall*100:.2f}%)")
    print(f"Test Pixel Accuracy    : {pixel_accuracy:.4f} ({pixel_accuracy*100:.2f}%)")
    print(f"True Positives (Landslide pixels): {total_tp:,}")
    print(f"False Positives        : {total_fp:,}")
    print(f"False Negatives        : {total_fn:,}")
    print(f"True Negatives (BG)    : {total_tn:,}")
    print("="*60)
    
    # Generate Sample Visualizations Grid (6 samples x 4 columns)
    fig, axes = plt.subplots(len(sample_visuals), 4, figsize=(16, 4 * len(sample_visuals)))
    if len(sample_visuals) == 1:
        axes = np.expand_dims(axes, axis=0)
        
    for i, item in enumerate(sample_visuals):
        img_rgb = item["image"]
        gt_mask = item["target"]
        pred_mask = item["prediction"]
        
        # Overlay ground truth (red contour) and prediction (yellow fill)
        overlay = img_rgb.copy()
        # Highlight predicted landslide pixels in translucent red/yellow
        overlay[pred_mask == 1, 0] = np.clip(overlay[pred_mask == 1, 0] + 0.5, 0, 1)
        overlay[pred_mask == 1, 1] = np.clip(overlay[pred_mask == 1, 1] * 0.5, 0, 1)
        
        # Column 1: Original Image
        axes[i, 0].imshow(img_rgb)
        axes[i, 0].set_title(f"Sample {i+1}: {item['filename']}\nOriginal Image (RGB)", fontsize=10)
        axes[i, 0].axis("off")
        
        # Column 2: Ground Truth Mask
        axes[i, 1].imshow(gt_mask, cmap="gist_gray")
        axes[i, 1].set_title("Ground Truth Mask", fontsize=10)
        axes[i, 1].axis("off")
        
        # Column 3: Predicted Mask
        axes[i, 2].imshow(pred_mask, cmap="magma")
        axes[i, 2].set_title("U-Net Predicted Mask", fontsize=10)
        axes[i, 2].axis("off")
        
        # Column 4: Overlay
        axes[i, 3].imshow(overlay)
        axes[i, 3].set_title("Landslide Detection Overlay", fontsize=10)
        axes[i, 3].axis("off")
        
    plt.tight_layout()
    plt.savefig(Config.SAMPLE_PREDS_PLOT_PATH, dpi=200)
    plt.close()
    print(f"Saved sample predictions plot to {Config.SAMPLE_PREDS_PLOT_PATH}")

    # Generate Markdown Report
    report_content = f"""# NER Landslide Spatial Segmentation Report: U-Net Model

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
| **Intersection over Union (IoU)** | **{iou:.4f}** | **{iou*100:.2f}%** |
| **Dice Coefficient / F1-Score** | **{dice:.4f}** | **{dice*100:.2f}%** |
| **Precision** | **{precision:.4f}** | **{precision*100:.2f}%** |
| **Recall** | **{recall:.4f}** | **{recall*100:.2f}%** |
| **Pixel Accuracy** | **{pixel_accuracy:.4f}** | **{pixel_accuracy*100:.2f}%** |

---

## 3. Pixel Confusion Matrix (Test Split - {total_pixels:,} total pixels)

| | Predicted Background | Predicted Landslide |
| :--- | :--- | :--- |
| **Actual Background** | **TN = {total_tn:,}** ({(total_tn/total_pixels)*100:.2f}%) | **FP = {total_fp:,}** ({(total_fp/total_pixels)*100:.2f}%) |
| **Actual Landslide** | **FN = {total_fn:,}** ({(total_fn/total_pixels)*100:.2f}%) | **TP = {total_tp:,}** ({(total_tp/total_pixels)*100:.2f}%) |

---

## 4. Class-Specific Breakdown

- **Landslide Class (Positive Target)**:
  - IoU: `{landslide_iou:.4f}`
  - F1 / Dice: `{landslide_f1:.4f}`
  - Precision: `{landslide_precision:.4f}`
  - Recall: `{landslide_recall:.4f}`
- **Background Class**:
  - IoU: `{bg_iou:.4f}`
  - F1 / Dice: `{bg_f1:.4f}`
  - Precision: `{bg_precision:.4f}`
  - Recall: `{bg_recall:.4f}`

---

## 5. Sample Prediction Visualizations

Sample qualitative outputs on unseen test image tiles are saved at:
[`sample_predictions.png`](file:///{Config.SAMPLE_PREDS_PLOT_PATH.replace('\\\\', '/')})
"""
    with open(Config.REPORT_PATH, "w") as f:
        f.write(report_content)
    print(f"Saved segmentation report to {Config.REPORT_PATH}")
    
    return {
        "iou": iou,
        "dice": dice,
        "precision": precision,
        "recall": recall,
        "pixel_accuracy": pixel_accuracy
    }


if __name__ == "__main__":
    evaluate_segmentation()
