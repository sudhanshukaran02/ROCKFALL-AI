import joblib
import pickle
import pandas as pd

with open('models/model_A_best.pkl', 'rb') as f:
    model_A = pickle.load(f)

print("Model A type:", type(model_A))
if hasattr(model_A, 'feature_names_in_'):
    print("Feature names in:", list(model_A.feature_names_in_))
elif hasattr(model_A, 'n_features_in_'):
    print("Num features in:", model_A.n_features_in_)

sf = pd.read_csv('results/terrain/spatial_features.csv')
print("\nSpatial features CSV columns:")
print(list(sf.columns))
print(f"Total rows in spatial_features.csv: {len(sf)}")
