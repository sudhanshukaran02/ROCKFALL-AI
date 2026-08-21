import os

class BackendConfig:
    # Base directory is workspace root
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # Data directories
    DATA_DIR = os.path.join(BASE_DIR, "data")
    NER_DATA_DIR = os.path.join(DATA_DIR, "ner")
    RESULTS_DIR = os.path.join(BASE_DIR, "results")
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    FIELD_REPORTS_DIR = os.path.join(DATA_DIR, "field_reports")

    # Important File Paths
    LANDSLIDE_EVENTS_CSV = os.path.join(NER_DATA_DIR, "landslide_events_verified.csv")
    ENVIRONMENTAL_SERIES_CSV = os.path.join(NER_DATA_DIR, "environmental_timeseries.csv")
    FIELD_REPORTS_CSV = os.path.join(FIELD_REPORTS_DIR, "field_reports.csv")

    # NER Results Paths
    LSTM_PREDICTIONS_CSV = os.path.join(RESULTS_DIR, "ner", "early_warning", "lstm_predictions.csv")
    MULTIMODAL_PREDICTIONS_CSV = os.path.join(RESULTS_DIR, "ner", "fusion", "multimodal_predictions.csv")
    THRESHOLD_ANALYSIS_CSV = os.path.join(RESULTS_DIR, "ner", "fusion", "threshold_analysis.csv")

    # Jharia Results & Data Paths
    RAJAPUR_EVENTS_CSV = os.path.join(DATA_DIR, "events", "rajapur_instability_events.csv")
    RAJAPUR_TOP50_CSV = os.path.join(RESULTS_DIR, "rajapur", "terrain_susceptibility", "top_50_terrain_susceptibility_locations.csv")
    RAJAPUR_TERRAIN_STATS_CSV = os.path.join(RESULTS_DIR, "rajapur", "terrain_susceptibility", "terrain_statistics.csv")

    # Models Paths
    UNET_CHECKPOINT = os.path.join(RESULTS_DIR, "ner", "segmentation", "best_unet.pth")
    LSTM_CHECKPOINT = os.path.join(MODELS_DIR, "ner_lstm_best.pth")
    MODEL_A_PATH = os.path.join(MODELS_DIR, "model_A_best.pkl")
    MODEL_B_PATH = os.path.join(MODELS_DIR, "model_B_best.pkl")

    # System metadata
    SYSTEM_NAME = "NER-LENS"
    SYSTEM_TITLE = "North Eastern Region Landslide Early Warning & Risk Monitoring System"
    VERSION = "1.0.0-PROTOTYPE"
    OPERATING_MODE = "RESEARCH_DECISION_SUPPORT"
    LATEST_DATA_DATE = "2024-12-31"

config = BackendConfig()
