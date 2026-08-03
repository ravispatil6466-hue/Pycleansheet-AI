"""Data cleaning & preprocessing operations, all operating on pandas DataFrames."""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder


def handle_missing(df: pd.DataFrame, columns, strategy, constant_value=None) -> pd.DataFrame:
    df = df.copy()
    cols = columns or df.columns.tolist()
    if strategy == "drop_rows":
        return df.dropna(subset=cols)
    for col in cols:
        if col not in df.columns:
            continue
        if strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].mean())
        elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        elif strategy == "mode":
            mode_val = df[col].mode()
            if len(mode_val):
                df[col] = df[col].fillna(mode_val.iloc[0])
        elif strategy == "constant":
            df[col] = df[col].fillna(constant_value)
        elif strategy == "ffill":
            df[col] = df[col].ffill()
        elif strategy == "bfill":
            df[col] = df[col].bfill()
    return df


def remove_duplicates(df: pd.DataFrame, subset=None, keep="first") -> pd.DataFrame:
    keep_val = False if keep == "none" else keep
    return df.drop_duplicates(subset=subset, keep=keep_val).reset_index(drop=True)


def handle_outliers(df: pd.DataFrame, columns, method="iqr", action="remove", threshold=1.5) -> pd.DataFrame:
    df = df.copy()
    mask = pd.Series(True, index=df.index)
    for col in columns:
        if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
            continue
        if method == "iqr":
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - threshold * iqr, q3 + threshold * iqr
        else:  # zscore
            mean, std = df[col].mean(), df[col].std()
            lower, upper = mean - threshold * std, mean + threshold * std
        if action == "remove":
            mask &= df[col].between(lower, upper) | df[col].isna()
        elif action == "cap":
            df[col] = df[col].clip(lower, upper)
    if action == "remove":
        df = df[mask].reset_index(drop=True)
    return df


def convert_type(df: pd.DataFrame, column: str, target_type: str) -> pd.DataFrame:
    df = df.copy()
    if column not in df.columns:
        return df
    try:
        if target_type == "int":
            df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")
        elif target_type == "float":
            df[column] = pd.to_numeric(df[column], errors="coerce")
        elif target_type == "string":
            df[column] = df[column].astype(str)
        elif target_type == "datetime":
            df[column] = pd.to_datetime(df[column], errors="coerce")
        elif target_type == "category":
            df[column] = df[column].astype("category")
        elif target_type == "bool":
            df[column] = df[column].astype(bool)
    except Exception as e:
        raise ValueError(f"Type conversion failed: {e}")
    return df


def rename_columns(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    return df.rename(columns=mapping)


def normalize_columns(df: pd.DataFrame, columns, method="standard") -> pd.DataFrame:
    df = df.copy()
    scaler = {"standard": StandardScaler, "minmax": MinMaxScaler, "robust": RobustScaler}.get(method, StandardScaler)()
    valid_cols = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    if valid_cols:
        df[valid_cols] = scaler.fit_transform(df[valid_cols].fillna(0))
    return df


def encode_columns(df: pd.DataFrame, columns, method="onehot") -> pd.DataFrame:
    df = df.copy()
    valid_cols = [c for c in columns if c in df.columns]
    if method == "onehot":
        df = pd.get_dummies(df, columns=valid_cols, prefix=valid_cols)
    else:
        for c in valid_cols:
            le = LabelEncoder()
            df[c] = le.fit_transform(df[c].astype(str))
    return df


def quality_report(df: pd.DataFrame) -> dict:
    total_rows = len(df)
    report = {
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "total_missing_cells": int(df.isna().sum().sum()),
        "columns": [],
    }
    for col in df.columns:
        missing = int(df[col].isna().sum())
        report["columns"].append({
            "name": str(col),
            "dtype": str(df[col].dtype),
            "missing": missing,
            "missing_pct": round((missing / total_rows) * 100, 2) if total_rows else 0,
            "unique": int(df[col].nunique(dropna=True)),
        })
    return report
