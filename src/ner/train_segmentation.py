import os
import sys
import random
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import torch
import torch.nn as nn
import torch.optim as optim

from src.ner.config import Config
from src.ner.dataset import get_dataloader
from src.ner.unet import UNet


def set_seed(seed=Config.SEED):
    """Set random seeds for complete reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


class DiceLoss(nn.Module):
    """Soft Dice Loss for binary semantic segmentation."""
    def __init__(self, smooth=1e-6):
        super().__init__()
        self.smooth = smooth

    def forward(self, logits, targets):
        probs = torch.sigmoid(logits)
        probs_flat = probs.view(-1)
        targets_flat = targets.view(-1)
        
        intersection = (probs_flat * targets_flat).sum()
        total = probs_flat.sum() + targets_flat.sum()
        
        dice = (2.0 * intersection + self.smooth) / (total + self.smooth)
        return 1.0 - dice


class CombinedLoss(nn.Module):
    """
    Combined BCE with Logits (Weighted) + Soft Dice Loss.
    Designed specifically to handle severe class imbalance (95.5% background vs 4.5% landslide pixels).
    """
    def __init__(self, pos_weight=8.0, dice_weight=Config.DICE_WEIGHT, bce_weight=Config.BCE_WEIGHT):
        super().__init__()
        self.dice_loss = DiceLoss()
        pos_weight_tensor = torch.tensor([pos_weight])
        self.bce_loss = nn.BCEWithLogitsLoss(pos_weight=pos_weight_tensor)
        self.dice_weight = dice_weight
        self.bce_weight = bce_weight

    def forward(self, logits, targets):
        if self.bce_loss.pos_weight.device != logits.device:
            self.bce_loss.pos_weight = self.bce_loss.pos_weight.to(logits.device)
            
        bce = self.bce_loss(logits, targets)
        dice = self.dice_loss(logits, targets)
        return self.bce_weight * bce + self.dice_weight * dice


def calculate_batch_metrics(logits, targets, threshold=0.5, smooth=1e-6):
    """Computes IoU, Dice/F1, Precision, and Recall for binary predictions."""
    probs = torch.sigmoid(logits)
    preds = (probs > threshold).float()
    
    preds_flat = preds.view(-1)
    targets_flat = targets.view(-1)
    
    tp = (preds_flat * targets_flat).sum().item()
    fp = (preds_flat * (1 - targets_flat)).sum().item()
    fn = ((1 - preds_flat) * targets_flat).sum().item()
    tn = ((1 - preds_flat) * (1 - targets_flat)).sum().item()
    
    iou = (tp + smooth) / (tp + fp + fn + smooth)
    dice = (2.0 * tp + smooth) / (2.0 * tp + fp + fn + smooth)
    precision = (tp + smooth) / (tp + fp + smooth)
    recall = (tp + smooth) / (tp + fn + smooth)
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    
    return {
        "iou": iou,
        "dice": dice,
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn
    }


def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    metrics_sum = {"iou": 0.0, "dice": 0.0, "precision": 0.0, "recall": 0.0, "accuracy": 0.0}
    total_batches = len(dataloader)
    
    for images, masks, _ in dataloader:
        images = images.to(device)
        masks = masks.to(device)
        
        optimizer.zero_grad()
        logits = model(images)
        loss = criterion(logits, masks)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        batch_m = calculate_batch_metrics(logits, masks)
        for k in metrics_sum:
            metrics_sum[k] += batch_m[k]

    avg_loss = running_loss / total_batches
    avg_metrics = {k: v / total_batches for k, v in metrics_sum.items()}
    return avg_loss, avg_metrics


@torch.no_grad()
def evaluate_epoch(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    metrics_sum = {"iou": 0.0, "dice": 0.0, "precision": 0.0, "recall": 0.0, "accuracy": 0.0}
    total_batches = len(dataloader)
    
    for images, masks, _ in dataloader:
        images = images.to(device)
        masks = masks.to(device)
        
        logits = model(images)
        loss = criterion(logits, masks)
        
        running_loss += loss.item()
        batch_m = calculate_batch_metrics(logits, masks)
        for k in metrics_sum:
            metrics_sum[k] += batch_m[k]

    avg_loss = running_loss / total_batches
    avg_metrics = {k: v / total_batches for k, v in metrics_sum.items()}
    return avg_loss, avg_metrics


def train_segmentation():
    set_seed(Config.SEED)
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device for training: {device}")
    
    # Dataloaders
    print("Loading datasets...")
    train_loader = get_dataloader(Config.TRAIN_DIR, batch_size=Config.BATCH_SIZE, shuffle=True, transform=True)
    val_loader = get_dataloader(Config.VAL_DIR, batch_size=Config.BATCH_SIZE, shuffle=False, transform=False)
    
    print(f"Train split batches: {len(train_loader)} ({len(train_loader.dataset)} images)")
    print(f"Val split batches:   {len(val_loader)} ({len(val_loader.dataset)} images)")
    
    # Model, Loss, Optimizer, Scheduler
    model = UNet(in_channels=Config.IN_CHANNELS, num_classes=Config.NUM_CLASSES).to(device)
    criterion = CombinedLoss(pos_weight=8.0)
    optimizer = optim.AdamW(model.parameters(), lr=Config.LEARNING_RATE, weight_decay=Config.WEIGHT_DECAY)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=4)
    
    best_val_dice = 0.0
    epochs_no_improve = 0
    history = []
    
    print(f"\nStarting U-Net Training for {Config.NUM_EPOCHS} Epochs (Early Stopping Patience: {Config.PATIENCE})...")
    start_time = time.time()
    
    for epoch in range(1, Config.NUM_EPOCHS + 1):
        t0 = time.time()
        train_loss, train_m = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_m = evaluate_epoch(model, val_loader, criterion, device)
        
        epoch_time = time.time() - t0
        
        # Step LR scheduler based on validation Dice score
        scheduler.step(val_m["dice"])
        
        record = {
            "epoch": epoch,
            "train_loss": train_loss,
            "train_dice": train_m["dice"],
            "train_iou": train_m["iou"],
            "val_loss": val_loss,
            "val_dice": val_m["dice"],
            "val_iou": val_m["iou"],
            "val_precision": val_m["precision"],
            "val_recall": val_m["recall"],
            "val_accuracy": val_m["accuracy"],
            "epoch_time_s": epoch_time
        }
        history.append(record)
        
        print(f"Epoch {epoch:02d}/{Config.NUM_EPOCHS:02d} [{epoch_time:.1f}s] - "
              f"Train Loss: {train_loss:.4f} | Train Dice: {train_m['dice']:.4f} | "
              f"Val Loss: {val_loss:.4f} | Val Dice: {val_m['dice']:.4f} | Val IoU: {val_m['iou']:.4f}")
        
        # Check for model improvement
        if val_m["dice"] > best_val_dice:
            best_val_dice = val_m["dice"]
            epochs_no_improve = 0
            torch.save(model.state_dict(), Config.MODEL_CHECKPOINT_PATH)
            print(f"  >>> Improved Best Val Dice to {best_val_dice:.4f}! Saved checkpoint to {Config.MODEL_CHECKPOINT_PATH}")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= Config.PATIENCE:
                print(f"\nEarly stopping triggered after {epoch} epochs (No val Dice improvement for {Config.PATIENCE} consecutive epochs).")
                break

    total_training_time = time.time() - start_time
    print(f"\nTraining Complete in {total_training_time/60:.2f} minutes.")
    print(f"Best Validation Dice Score: {best_val_dice:.4f}")
    
    # Save training history CSV
    df_hist = pd.DataFrame(history)
    df_hist.to_csv(Config.HISTORY_CSV_PATH, index=False)
    print(f"Saved training history to {Config.HISTORY_CSV_PATH}")
    
    # Plot training metrics
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(df_hist["epoch"], df_hist["train_loss"], label="Train Loss", color="blue", linewidth=2)
    plt.plot(df_hist["epoch"], df_hist["val_loss"], label="Val Loss", color="red", linestyle="--", linewidth=2)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("U-Net Training & Validation Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    plt.plot(df_hist["epoch"], df_hist["train_dice"], label="Train Dice", color="green", linewidth=2)
    plt.plot(df_hist["epoch"], df_hist["val_dice"], label="Val Dice", color="orange", linewidth=2)
    plt.plot(df_hist["epoch"], df_hist["val_iou"], label="Val IoU", color="purple", linestyle="--", linewidth=2)
    plt.xlabel("Epoch")
    plt.ylabel("Score")
    plt.title("U-Net Segmentation Performance (Dice & IoU)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(Config.HISTORY_PLOT_PATH, dpi=200)
    plt.close()
    print(f"Saved training curve plot to {Config.HISTORY_PLOT_PATH}")
    
    return best_val_dice


if __name__ == "__main__":
    train_segmentation()
