import shap
import pandas as pd
import numpy as np


def get_shap_values(model, features: dict, feature_cols: list) -> list:
    X = pd.DataFrame([features])[feature_cols]
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    pred_idx = int(np.argmax([abs(shap_values[i][0]).sum() for i in range(len(shap_values))]))
    class_shap = shap_values[pred_idx][0]
    shap_df = pd.DataFrame({
        'feature': feature_cols,
        'shap_value': class_shap,
        'abs_shap': np.abs(class_shap)
    }).sort_values('abs_shap', ascending=False).head(8)
    return shap_df[['feature', 'shap_value']].to_dict(orient='records')
