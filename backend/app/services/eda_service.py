"""Exploratory Data Analysis helpers."""
import numpy as np
import pandas as pd
from app.services.data_service import sanitize_json


def summary_stats(df: pd.DataFrame) -> dict:
    numeric_df = df.select_dtypes(include=[np.number])
    desc = numeric_df.describe().transpose()
    desc_dict = {}
    for col in desc.index:
        row = desc.loc[col].to_dict()
        desc_dict[str(col)] = {k: (None if pd.isna(v) else float(v)) for k, v in row.items()}

    categorical_df = df.select_dtypes(exclude=[np.number])
    cat_summary = {}
    for col in categorical_df.columns:
        vc = df[col].value_counts(dropna=True).head(10)
        cat_summary[str(col)] = {str(k): int(v) for k, v in vc.items()}

    return sanitize_json({
        "numeric_summary": desc_dict,
        "categorical_summary": cat_summary,
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "dtypes": {str(c): str(df[c].dtype) for c in df.columns},
        "missing_total": int(df.isna().sum().sum()),
    })


def correlation_matrix(df: pd.DataFrame, method="pearson") -> dict:
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return {"columns": [], "matrix": []}
    corr = numeric_df.corr(method=method)
    return sanitize_json({
        "columns": [str(c) for c in corr.columns],
        "matrix": corr.values.tolist(),
    })


def distribution(df: pd.DataFrame, column: str, bins: int = 20) -> dict:
    if column not in df.columns:
        raise ValueError("Column not found")
    series = df[column].dropna()
    if pd.api.types.is_numeric_dtype(series):
        counts, edges = np.histogram(series, bins=bins)
        return sanitize_json({
            "type": "numeric",
            "counts": counts.tolist(),
            "bin_edges": edges.tolist(),
            "mean": float(series.mean()) if len(series) else None,
            "median": float(series.median()) if len(series) else None,
            "std": float(series.std()) if len(series) else None,
        })
    else:
        vc = series.value_counts().head(30)
        return sanitize_json({
            "type": "categorical",
            "categories": [str(k) for k in vc.index],
            "counts": vc.values.tolist(),
        })


def full_eda_report(df: pd.DataFrame) -> dict:
    return {
        "summary": summary_stats(df),
        "correlation": correlation_matrix(df),
        "quality": {
            "duplicate_rows": int(df.duplicated().sum()),
            "missing_total": int(df.isna().sum().sum()),
        },
    }
