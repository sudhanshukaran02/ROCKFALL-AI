"""
Explainability module for the Prototype Risk-Fusion System.

IMPORTANT DISCLAIMER:
Feature importances and contribution scores represent model-derived correlations
and sensitivity weights. They are explicitly labeled as "Model-derived contributing factors"
and do NOT prove physical causation.
"""

import numpy as np
import pandas as pd

def get_model_feature_importances(pipeline, feature_names):
    """
    Extracts feature importances or coefficients from a fitted scikit-learn Pipeline.
    
    Parameters:
        pipeline: Trained scikit-learn Pipeline containing ('preprocessor', 'classifier')
        feature_names: List of input feature names
        
    Returns:
        pd.DataFrame with 'Feature' and 'Importance'
    """
    classifier = pipeline.named_steps.get('classifier', None)
    
    if classifier is None:
        raise ValueError("Pipeline does not contain a step named 'classifier'.")
        
    if hasattr(classifier, 'feature_importances_'):
        importances = classifier.feature_importances_
    elif hasattr(classifier, 'coef_'):
        # For multi-class or binary LogisticRegression
        coefs = np.abs(classifier.coef_)
        importances = np.mean(coefs, axis=0) if coefs.ndim > 1 else coefs[0]
    else:
        # Fallback equal importances
        importances = np.ones(len(feature_names)) / len(feature_names)
        
    df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False).reset_index(drop=True)
    
    # Normalize importances to sum to 1.0
    if df['Importance'].sum() > 0:
        df['Importance'] = df['Importance'] / df['Importance'].sum()
        
    return df

def get_sample_top_risk_factors(input_dict, pipeline, feature_names, top_n=3):
    """
    Computes model-derived contributing factors for a single input instance.
    Calculated as: Feature Importance * Normalized Relative Feature Value.
    
    Parameters:
        input_dict: Dictionary of feature_name -> numeric_value
        pipeline: Trained Pipeline
        feature_names: List of feature names
        top_n: Number of top factors to return
        
    Returns:
        List of strings detailing top contributing factors.
    """
    imp_df = get_model_feature_importances(pipeline, feature_names)
    imp_dict = dict(zip(imp_df['Feature'], imp_df['Importance']))
    
    contributions = []
    for feat in feature_names:
        val = float(input_dict.get(feat, 0.0))
        weight = imp_dict.get(feat, 0.0)
        # Use magnitude of contribution
        score = abs(val) * weight
        contributions.append({
            'Feature': feat,
            'Value': val,
            'Model_Weight': weight,
            'Contribution_Score': score
        })
        
    contrib_df = pd.DataFrame(contributions).sort_values(by='Contribution_Score', ascending=False)
    
    top_factors = []
    for idx, row in contrib_df.head(top_n).iterrows():
        feat = row['Feature']
        val = row['Value']
        top_factors.append(f"{feat} (value: {val:.2f})")
        
    return top_factors
