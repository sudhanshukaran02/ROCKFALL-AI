import os

class Config:
    # Project paths
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    DATA_DIR = os.path.join(BASE_DIR, "data", "dataset")
    TRAIN_DIR = os.path.join(DATA_DIR, "train")
    VAL_DIR = os.path.join(DATA_DIR, "validation")
    TEST_DIR = os.path.join(DATA_DIR, "test")
    
    # Output paths
    OUTPUT_DIR = os.path.join(BASE_DIR, "results", "ner", "segmentation")
    MODEL_CHECKPOINT_PATH = os.path.join(OUTPUT_DIR, "best_unet.pth")
    HISTORY_CSV_PATH = os.path.join(OUTPUT_DIR, "training_history.csv")
    HISTORY_PLOT_PATH = os.path.join(OUTPUT_DIR, "training_history.png")
    TEST_METRICS_PATH = os.path.join(OUTPUT_DIR, "test_metrics.csv")
    TEST_PREDS_DIR = os.path.join(OUTPUT_DIR, "test_predictions")
    SAMPLE_PREDS_PLOT_PATH = os.path.join(OUTPUT_DIR, "sample_predictions.png")
    REPORT_PATH = os.path.join(OUTPUT_DIR, "segmentation_report.md")

    # Data hyperparameters
    IMAGE_SIZE = (128, 128)
    IN_CHANNELS = 4
    NUM_CLASSES = 1
    
    # Training hyperparameters
    BATCH_SIZE = 32
    LEARNING_RATE = 1e-3
    WEIGHT_DECAY = 1e-4
    NUM_EPOCHS = 35
    PATIENCE = 10
    SEED = 42
    NUM_WORKERS = 0  # 0 for main-thread loading on Windows
    
    # Loss hyperparameter weights
    DICE_WEIGHT = 0.5
    BCE_WEIGHT = 0.5
