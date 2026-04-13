import shap
import pandas as pd
import numpy as np


def _extract_base_model(model):
    """
    CalibratedClassifierCV wraps the base estimator and shap.TreeExplainer
    cannot work on the wrapper directly — it needs the raw tree model.

    For a CalibratedClassifierCV fitted with cv=3, the structure is:
        model.calibrated_classifiers_[i].estimator  →  the base LightGBM

    We use the first fold's estimator (index 0) since all folds share the
    same architecture and produce equivalent SHAP feature importance patterns.
    """
    if hasattr(model, 'calibrated_classifiers_'):
        return model.calibrated_classifiers_[0].estimator
    return model


def get_shap_values(model, features: dict, feature_cols: list) -> list:
    X = pd.DataFrame([features])[feature_cols]

    # Extract base LightGBM estimator if wrapped in CalibratedClassifierCV
    base_model = _extract_base_model(model)

    explainer = shap.TreeExplainer(base_model)
    raw = explainer.shap_values(X)

    # Newer SHAP (0.4x+) returns 3D ndarray: (n_samples, n_features, n_classes)
    # Older SHAP returns a list of arrays: [(n_samples, n_features)] × n_classes
    if isinstance(raw, np.ndarray) and raw.ndim == 3:
        shap_3d = raw[0]  # (n_features, n_classes)
        class_totals = np.abs(shap_3d).sum(axis=0)
        best_class = int(np.argmax(class_totals))
        class_shap = shap_3d[:, best_class]
    elif isinstance(raw, list):
        class_totals = [np.abs(raw[i][0]).sum() for i in range(len(raw))]
        best_class = int(np.argmax(class_totals))
        class_shap = raw[best_class][0]
    else:
        class_shap = raw[0] if raw.ndim == 2 else raw

    shap_df = pd.DataFrame({
        'feature': feature_cols,
        'shap_value': class_shap,
        'abs_shap': np.abs(class_shap)
    }).sort_values('abs_shap', ascending=False).head(8)

    return shap_df[['feature', 'shap_value']].to_dict(orient='records')
