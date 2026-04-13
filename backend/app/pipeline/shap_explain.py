import shap
import pandas as pd
import numpy as np


def get_shap_values(model, features: dict, feature_cols: list) -> list:
    X = pd.DataFrame([features])[feature_cols]
    explainer = shap.TreeExplainer(model)
    raw = explainer.shap_values(X)

    # Newer SHAP returns 3D ndarray (n_samples, n_features, n_classes)
    # Older SHAP returns list of arrays, one per class: [(n_samples, n_features), ...]
    if isinstance(raw, np.ndarray) and raw.ndim == 3:
        # shape: (1, n_features, n_classes) — pick class with highest total |shap|
        shap_3d = raw[0]  # (n_features, n_classes)
        class_totals = np.abs(shap_3d).sum(axis=0)
        best_class = int(np.argmax(class_totals))
        class_shap = shap_3d[:, best_class]
    elif isinstance(raw, list):
        # Old format: list of (n_samples, n_features) per class
        class_totals = [np.abs(raw[i][0]).sum() for i in range(len(raw))]
        best_class = int(np.argmax(class_totals))
        class_shap = raw[best_class][0]
    else:
        # Fallback: 2D array (n_samples, n_features) — binary or direct
        class_shap = raw[0] if raw.ndim == 2 else raw

    shap_df = pd.DataFrame({
        'feature': feature_cols,
        'shap_value': class_shap,
        'abs_shap': np.abs(class_shap)
    }).sort_values('abs_shap', ascending=False).head(8)

    return shap_df[['feature', 'shap_value']].to_dict(orient='records')
