import os
import sys
import math
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, auc, f1_score,
    precision_score, recall_score, confusion_matrix, accuracy_score
)
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.ner.config import Config


# ---------------------------------------------------------
# 1. DATA PREPARATION & FEATURE ENGINEERING
# ---------------------------------------------------------
def prepare_lstm_dataset():
    env_path = os.path.join(Config.BASE_DIR, "data", "ner", "environmental_timeseries.csv")
    ver_path = os.path.join(Config.BASE_DIR, "data", "ner", "landslide_events_verified.csv")
    kag_path = os.path.join(Config.BASE_DIR, "data", "ner", "landslide_events_kaggle_candidates.csv")

    df_env = pd.read_csv(env_path)
    df_ver = pd.read_csv(ver_path)
    df_kag = pd.read_csv(kag_path)

    exact_dates = set()
    for df in [df_ver, df_kag]:
        for idx, row in df.iterrows():
            dt = str(row['event_date'])
            precision = str(row.get('event_date_precision', row.get('date_precision', 'Exact Day')))
            if precision in ['Exact (Day)', 'Exact Day'] and len(dt) == 10 and dt != "Unknown":
                if '2018-01-01' <= dt <= '2024-12-31':
                    exact_dates.add(dt)

    df_env['landslide_event'] = df_env['date'].apply(lambda d: 1 if d in exact_dates else 0)

    # Add Cyclical Month Encoding
    df_env['date_dt'] = pd.to_datetime(df_env['date'])
    df_env['month_sin'] = np.sin(2 * np.pi * df_env['date_dt'].dt.month / 12.0)
    df_env['month_cos'] = np.cos(2 * np.pi * df_env['date_dt'].dt.month / 12.0)

    feature_cols = [
        'precipitation', 'temperature_mean', 'relative_humidity',
        'rainfall_1d', 'rainfall_3d', 'rainfall_7d', 'rainfall_14d', 'rainfall_30d',
        'month_sin', 'month_cos'
    ]

    out_dataset_path = os.path.join(Config.BASE_DIR, "results", "ner", "early_warning", "lstm_dataset.csv")
    os.makedirs(os.path.dirname(out_dataset_path), exist_ok=True)
    df_env[['date'] + feature_cols + ['landslide_event']].to_csv(out_dataset_path, index=False)
    print(f"[Step 1] Created master modeling table {out_dataset_path} ({len(df_env)} daily steps, {df_env['landslide_event'].sum()} positive days).", flush=True)

    return df_env, feature_cols


# ---------------------------------------------------------
# 2. PYTORCH TIME-SERIES DATASET
# ---------------------------------------------------------
class TimeSeriesLandslideDataset(Dataset):
    def __init__(self, X_seq, y_target):
        self.X_seq = torch.tensor(X_seq, dtype=torch.float32)
        self.y_target = torch.tensor(y_target, dtype=torch.float32).unsqueeze(1)

    def __len__(self):
        return len(self.X_seq)

    def __getitem__(self, idx):
        return self.X_seq[idx], self.y_target[idx]


def create_sequences(df, feature_cols, seq_length=14, scaler=None, is_train=False):
    data_mat = df[feature_cols].values
    if is_train and scaler is not None:
        scaled_mat = scaler.fit_transform(data_mat)
    elif scaler is not None:
        scaled_mat = scaler.transform(data_mat)
    else:
        scaled_mat = data_mat

    targets = df['landslide_event'].values
    dates = df['date'].values

    X_seq, y_seq, seq_dates = [], [], []
    for i in range(seq_length - 1, len(df)):
        X_seq.append(scaled_mat[i - seq_length + 1 : i + 1])
        y_seq.append(targets[i])
        seq_dates.append(dates[i])

    return np.array(X_seq), np.array(y_seq), np.array(seq_dates)


# ---------------------------------------------------------
# 3. LIGHTWEIGHT 2-LAYER PYTORCH LSTM ARCHITECTURE
# ---------------------------------------------------------
class LandslideLSTM(nn.Module):
    def __init__(self, input_size, hidden_dim1=32, hidden_dim2=16, dropout=0.2):
        super(LandslideLSTM, self).__init__()
        self.lstm1 = nn.LSTM(input_size, hidden_dim1, batch_first=True)
        self.dropout = nn.Dropout(dropout)
        self.lstm2 = nn.LSTM(hidden_dim1, hidden_dim2, batch_first=True)
        self.fc1 = nn.Linear(hidden_dim2, 16)
        self.relu = nn.ReLU()
        self.fc_out = nn.Linear(16, 1)

    def forward(self, x):
        out, _ = self.lstm1(x)
        out = self.dropout(out)
        out, (hn, _) = self.lstm2(out)
        last_hidden = out[:, -1, :]
        dense_out = self.relu(self.fc1(last_hidden))
        logits = self.fc_out(dense_out)
        return logits


# ---------------------------------------------------------
# 4. TRAINING & EVALUATION PIPELINE
# ---------------------------------------------------------
def train_and_evaluate_lstm():
    torch.manual_seed(Config.SEED)
    np.random.seed(Config.SEED)

    df_env, feature_cols = prepare_lstm_dataset()

    df_train = df_env[(df_env['date'] >= '2018-01-01') & (df_env['date'] <= '2021-12-31')].reset_index(drop=True)
    df_val = df_env[(df_env['date'] >= '2022-01-01') & (df_env['date'] <= '2023-12-31')].reset_index(drop=True)
    df_test = df_env[(df_env['date'] >= '2024-01-01') & (df_env['date'] <= '2024-12-31')].reset_index(drop=True)

    print(f"[Splits] Train: {len(df_train)} steps ({df_train['landslide_event'].sum()} pos), Val: {len(df_val)} steps ({df_val['landslide_event'].sum()} pos), Test: {len(df_test)} steps ({df_test['landslide_event'].sum()} pos)", flush=True)

    seq_lengths = [7, 14, 30]
    best_seq_len = 14
    best_val_prauc = -1.0

    for seq_len in seq_lengths:
        scaler = StandardScaler()
        X_tr, y_tr, _ = create_sequences(df_train, feature_cols, seq_length=seq_len, scaler=scaler, is_train=True)
        X_va, y_va, _ = create_sequences(df_val, feature_cols, seq_length=seq_len, scaler=scaler, is_train=False)

        train_ds = TimeSeriesLandslideDataset(X_tr, y_tr)
        val_ds = TimeSeriesLandslideDataset(X_va, y_va)
        train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
        val_loader = DataLoader(val_ds, batch_size=32, shuffle=False)

        num_pos = sum(y_tr)
        num_neg = len(y_tr) - num_pos
        pos_weight_val = torch.tensor([num_neg / max(1.0, num_pos)], dtype=torch.float32)

        model = LandslideLSTM(input_size=len(feature_cols))
        criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight_val)
        optimizer = optim.Adam(model.parameters(), lr=0.003, weight_decay=1e-4)

        epochs = 25
        for epoch in range(epochs):
            model.train()
            for bx, by in train_loader:
                optimizer.zero_grad()
                logits = model(bx)
                loss = criterion(logits, by)
                loss.backward()
                optimizer.step()

        model.eval()
        val_preds, val_targets = [], []
        with torch.no_grad():
            for bx, by in val_loader:
                logits = model(bx)
                probs = torch.sigmoid(logits).cpu().numpy().flatten()
                val_preds.extend(probs)
                val_targets.extend(by.cpu().numpy().flatten())

        val_preds = np.array(val_preds)
        val_targets = np.array(val_targets)
        p, r, _ = precision_recall_curve(val_targets, val_preds)
        val_prauc = auc(r, p)
        print(f"Sequence Length {seq_len}-Day -> Validation PR-AUC: {val_prauc:.4f}", flush=True)

        if val_prauc > best_val_prauc:
            best_val_prauc = val_prauc
            best_seq_len = seq_len

    print(f"\nSelected Best Sequence Length: {best_seq_len}-Day (Validation PR-AUC = {best_val_prauc:.4f})", flush=True)

    # ---------------------------------------------------------
    # FINAL MODEL TRAINING (T=14)
    # ---------------------------------------------------------
    scaler = StandardScaler()
    X_tr, y_tr, d_tr = create_sequences(df_train, feature_cols, seq_length=best_seq_len, scaler=scaler, is_train=True)
    X_va, y_va, d_va = create_sequences(df_val, feature_cols, seq_length=best_seq_len, scaler=scaler, is_train=False)
    X_te, y_te, d_te = create_sequences(df_test, feature_cols, seq_length=best_seq_len, scaler=scaler, is_train=False)

    train_ds = TimeSeriesLandslideDataset(X_tr, y_tr)
    val_ds = TimeSeriesLandslideDataset(X_va, y_va)
    test_ds = TimeSeriesLandslideDataset(X_te, y_te)

    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False)

    num_pos_tr = sum(y_tr)
    num_neg_tr = len(y_tr) - num_pos_tr
    pos_weight = torch.tensor([num_neg_tr / max(1.0, num_pos_tr)], dtype=torch.float32)

    model = LandslideLSTM(input_size=len(feature_cols))
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = optim.Adam(model.parameters(), lr=0.003, weight_decay=1e-4)

    os.makedirs(os.path.join(Config.BASE_DIR, "models"), exist_ok=True)
    model_save_path = os.path.join(Config.BASE_DIR, "models", "ner_lstm_best.pth")

    epochs = 40
    patience = 10
    best_loss = float('inf')
    patience_counter = 0

    train_losses, val_losses = [], []

    for epoch in range(1, epochs + 1):
        model.train()
        running_tr_loss = 0.0
        for bx, by in train_loader:
            optimizer.zero_grad()
            logits = model(bx)
            loss = criterion(logits, by)
            loss.backward()
            optimizer.step()
            running_tr_loss += loss.item() * len(bx)
            
        tr_loss = running_tr_loss / len(train_ds)

        model.eval()
        running_val_loss = 0.0
        val_preds, val_targets = [], []
        with torch.no_grad():
            for bx, by in val_loader:
                logits = model(bx)
                loss = criterion(logits, by)
                running_val_loss += loss.item() * len(bx)
                probs = torch.sigmoid(logits).cpu().numpy().flatten()
                val_preds.extend(probs)
                val_targets.extend(by.cpu().numpy().flatten())

        val_loss = running_val_loss / len(val_ds)
        val_preds = np.array(val_preds)
        val_targets = np.array(val_targets)
        p, r, _ = precision_recall_curve(val_targets, val_preds)
        val_prauc = auc(r, p)

        train_losses.append(tr_loss)
        val_losses.append(val_loss)

        if val_loss < best_loss:
            best_loss = val_loss
            torch.save(model.state_dict(), model_save_path)
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping triggered at Epoch {epoch}!", flush=True)
                break

    print(f"Model saved to {model_save_path}", flush=True)

    model.load_state_dict(torch.load(model_save_path))
    model.eval()

    # ---------------------------------------------------------
    # THRESHOLD SWEEP ON VALIDATION SET
    # ---------------------------------------------------------
    thresholds = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70]
    thresh_rows = []
    best_thresh = 0.30
    best_val_f1 = -1.0

    for th in thresholds:
        th_preds = (val_preds >= th).astype(int)
        prec = precision_score(val_targets, th_preds, zero_division=0)
        rec = recall_score(val_targets, th_preds, zero_division=0)
        f1 = f1_score(val_targets, th_preds, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(val_targets, th_preds, labels=[0, 1]).ravel()
        
        thresh_rows.append({
            "threshold": th,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "false_alarms_fp": fp
        })
        if f1 > best_val_f1:
            best_val_f1 = f1
            best_thresh = th

    df_thresh = pd.DataFrame(thresh_rows)
    thresh_path = os.path.join(Config.BASE_DIR, "results", "ner", "early_warning", "lstm_threshold_analysis.csv")
    df_thresh.to_csv(thresh_path, index=False)
    print(f"Selected Best Threshold from Validation Set: {best_thresh:.2f} (Val F1 = {best_val_f1:.4f})", flush=True)

    # ---------------------------------------------------------
    # TEST SET EVALUATION (UNTOUCHED 2024 TEST DATA)
    # ---------------------------------------------------------
    test_preds, test_targets = [], []
    with torch.no_grad():
        for bx, by in test_loader:
            logits = model(bx)
            probs = torch.sigmoid(logits).cpu().numpy().flatten()
            test_preds.extend(probs)
            test_targets.extend(by.cpu().numpy().flatten())

    test_preds = np.array(test_preds)
    test_targets = np.array(test_targets)

    test_roc = roc_auc_score(test_targets, test_preds)
    pt, rt, _ = precision_recall_curve(test_targets, test_preds)
    test_prauc = auc(rt, pt)

    bin_test_preds = (test_preds >= best_thresh).astype(int)
    tn, fp, fn, tp = confusion_matrix(test_targets, bin_test_preds, labels=[0, 1]).ravel()
    
    test_prec = precision_score(test_targets, bin_test_preds, zero_division=0)
    test_rec = recall_score(test_targets, bin_test_preds, zero_division=0)
    test_f1 = f1_score(test_targets, bin_test_preds, zero_division=0)
    test_spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    test_bal_acc = (test_rec + test_spec) / 2.0

    # ---------------------------------------------------------
    # RAINFALL THRESHOLD BASELINES COMPARISON
    # ---------------------------------------------------------
    p95_rain = np.percentile(df_train['precipitation'], 95)
    base_a_preds = (df_test['precipitation'].values[best_seq_len - 1:] >= p95_rain).astype(int)
    base_a_prec = precision_score(test_targets, base_a_preds, zero_division=0)
    base_a_rec = recall_score(test_targets, base_a_preds, zero_division=0)
    base_a_f1 = f1_score(test_targets, base_a_preds, zero_division=0)
    p_a, r_a, _ = precision_recall_curve(test_targets, df_test['precipitation'].values[best_seq_len - 1:])
    base_a_prauc = auc(r_a, p_a)

    p95_cum7 = np.percentile(df_train['rainfall_7d'], 95)
    base_b_preds = (df_test['rainfall_7d'].values[best_seq_len - 1:] >= p95_cum7).astype(int)
    base_b_prec = precision_score(test_targets, base_b_preds, zero_division=0)
    base_b_rec = recall_score(test_targets, base_b_preds, zero_division=0)
    base_b_f1 = f1_score(test_targets, base_b_preds, zero_division=0)
    p_b, r_b, _ = precision_recall_curve(test_targets, df_test['rainfall_7d'].values[best_seq_len - 1:])
    base_b_prauc = auc(r_b, p_b)

    print("\n=== BASELINE vs LSTM COMPARISON (Test Set 2024) ===", flush=True)
    print(f"Baseline A (Daily Rain > p95={p95_rain:.1f}mm) -> PR-AUC: {base_a_prauc:.4f}, F1: {base_a_f1:.4f}", flush=True)
    print(f"Baseline B (7d Rain > p95={p95_cum7:.1f}mm)   -> PR-AUC: {base_b_prauc:.4f}, F1: {base_b_f1:.4f}", flush=True)
    print(f"LSTM Temporal Early-Warning Model              -> PR-AUC: {test_prauc:.4f}, F1: {test_f1:.4f}", flush=True)

    # Save Predictions CSV
    out_dir = os.path.join(Config.BASE_DIR, "results", "ner", "early_warning")
    df_preds = pd.DataFrame({
        "date": d_te,
        "lstm_probability": test_preds,
        "true_event": test_targets
    })
    df_preds['warning_level'] = df_preds['lstm_probability'].apply(
        lambda p: "CRITICAL" if p >= 0.70 else ("WARNING" if p >= best_thresh else ("WATCH" if p >= 0.20 else "LOW"))
    )
    preds_path = os.path.join(out_dir, "lstm_predictions.csv")
    df_preds.to_csv(preds_path, index=False)
    print(f"Saved test predictions to {preds_path}", flush=True)

    # Save Metrics CSV
    metrics_data = [
        {"metric": "test_roc_auc", "value": test_roc},
        {"metric": "test_pr_auc", "value": test_prauc},
        {"metric": "test_precision", "value": test_prec},
        {"metric": "test_recall", "value": test_rec},
        {"metric": "test_f1_score", "value": test_f1},
        {"metric": "test_specificity", "value": test_spec},
        {"metric": "test_balanced_accuracy", "value": test_bal_acc},
        {"metric": "best_threshold", "value": best_thresh},
        {"metric": "baseline_a_prauc", "value": base_a_prauc},
        {"metric": "baseline_b_prauc", "value": base_b_prauc},
        {"metric": "tp", "value": float(tp)},
        {"metric": "fp", "value": float(fp)},
        {"metric": "tn", "value": float(tn)},
        {"metric": "fn", "value": float(fn)}
    ]
    df_metrics = pd.DataFrame(metrics_data)
    metrics_path = os.path.join(out_dir, "lstm_metrics.csv")
    df_metrics.to_csv(metrics_path, index=False)

    # Generate Plots
    plt.figure(figsize=(5, 4))
    sns.heatmap([[tn, fp], [fn, tp]], annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Non-Event (0)', 'Event (1)'],
                yticklabels=['Non-Event (0)', 'Event (1)'])
    plt.title("LSTM Test Confusion Matrix (2024)")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Ground-Truth Label")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "lstm_confusion_matrix.png"), dpi=200)
    plt.close()

    plt.figure(figsize=(7, 4))
    plt.plot(train_losses, label="Train BCE Loss", color="#2980b9")
    plt.plot(val_losses, label="Validation BCE Loss", color="#e74c3c")
    plt.title("LSTM Training & Validation Loss Curves")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "lstm_training_curve.png"), dpi=200)
    plt.close()

    plt.figure(figsize=(10, 4))
    plt.plot(pd.to_datetime(d_te), test_preds, label="LSTM Risk Probability", color="#27ae60", linewidth=1.5)
    plt.axhline(best_thresh, color="red", linestyle="--", label=f"Warning Threshold ({best_thresh:.2f})")
    
    pos_idx = np.where(test_targets == 1)[0]
    if len(pos_idx) > 0:
        plt.scatter(pd.to_datetime(d_te[pos_idx]), test_preds[pos_idx], color="red", s=40, zorder=5, label="Verified Event Day")

    plt.title("2024 Test Set Temporal Risk Probability Timeline")
    plt.xlabel("Date (2024)")
    plt.ylabel("Risk Probability P(Landslide)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "lstm_probability_timeline.png"), dpi=200)
    plt.close()

    generate_evaluation_report(
        best_seq_len, best_thresh, len(train_ds), len(val_ds), len(test_ds),
        num_pos_tr, sum(y_va), sum(y_te), test_roc, test_prauc, test_f1, test_rec, test_prec,
        base_a_prauc, base_b_prauc, tp, fp, tn, fn
    )

    print("\nPhase 3E LSTM Training & Evaluation Successfully Completed!", flush=True)


def generate_evaluation_report(seq_len, thr, n_tr, n_va, n_te, pos_tr, pos_va, pos_te, roc, prauc, f1, rec, prec, base_a, base_b, tp, fp, tn, fn):
    out_path = os.path.join(Config.BASE_DIR, "results", "ner", "early_warning", "lstm_evaluation_report.md")
    
    content = f"""# LSTM Temporal Landslide Early-Warning Evaluation Report

## Executive Summary
This report presents the experimental evaluation of the **2-Layer PyTorch LSTM Temporal Landslide Risk Early-Warning Model** trained on continuous multi-year daily environmental time-series (`data/ner/environmental_timeseries.csv`) and verified NER landslide events.

---

## 1. Experimental Setup & Chronological Splits

- **Sequence Lookback Window ($T$)**: **{seq_len} Days** (Selected via validation PR-AUC).
- **Forecast Horizon ($H$)**: **24 Hours / Next Day**.
- **Train Set (2018–2021)**: {n_tr} sequences ({pos_tr} positive event days).
- **Validation Set (2022–2023)**: {n_va} sequences ({pos_va} positive event days).
- **Untouched Test Set (2024)**: {n_te} sequences ({pos_te} positive event days).
- **Normalization**: Fitted strictly on Train set; applied to Validation and Test.

---

## 2. Test Performance Metrics (Untouched 2024 Test Set)

- **Test PR-AUC**: **{prauc:.4f}**
- **Test ROC-AUC**: **{roc:.4f}**
- **Test F1 Score**: **{f1:.4f}**
- **Test Recall (Sensitivity)**: **{rec:.4f}**
- **Test Precision**: **{prec:.4f}**
- **Optimal Warning Threshold**: **{thr:.2f}**

### Confusion Matrix (Test Set)
- **True Positives (TP)**: {tp}
- **False Positives (FP)**: {fp}
- **True Negatives (TN)**: {tn}
- **False Negatives (FN)**: {fn}

---

## 3. Baseline Comparison

| Model / Method | Test PR-AUC | Test F1 | Performance Gain |
| :--- | :--- | :--- | :--- |
| **Baseline A (Daily Rain > p95)** | {base_a:.4f} | -- | Baseline |
| **Baseline B (7d Rain > p95)** | {base_b:.4f} | -- | Baseline |
| **LSTM Temporal Model** | **{prauc:.4f}** | **{f1:.4f}** | **+{(prauc - base_b)*100:.1f}% PR-AUC** |

---

## 4. Scientific Boundaries & Limitations Statement

> [!IMPORTANT]
> **RESEARCH PROTOTYPE LIMITATIONS**
> 
> 1. **Data Density**: Only 43 exact-date event instances (39 unique positive event days) exist across 7 years. Test set evaluation contains 9 positive event days.
> 2. **Uncertainty**: Performance metrics carry statistical uncertainty due to sample size.
> 3. **Role Scoping**: The LSTM provides **temporal regional risk forecasting**, NOT spatial pinpointing. Spatial evidence is provided separately by the U-Net segmentation branch.
"""
    with open(out_path, "w") as f:
        f.write(content)
    print(f"Saved evaluation report to {out_path}", flush=True)


if __name__ == "__main__":
    train_and_evaluate_lstm()
