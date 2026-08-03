"""
Converts a generic chart request (chart_type + field mappings) into
data ready to be plotted by Plotly.js on the frontend. Aggregation and
filtering happen here so the frontend just renders whatever comes back.
"""
import numpy as np
import pandas as pd
from app.services.data_service import sanitize_json

AGG_FUNCS = {
    "sum": "sum", "avg": "mean", "mean": "mean", "count": "count",
    "min": "min", "max": "max", "median": "median",
}


def apply_filters(df: pd.DataFrame, filters) -> pd.DataFrame:
    if not filters:
        return df
    for f in filters:
        col, op, val = f.get("column"), f.get("operator", "eq"), f.get("value")
        if col not in df.columns:
            continue
        if op == "eq":
            df = df[df[col] == val]
        elif op == "neq":
            df = df[df[col] != val]
        elif op == "in":
            df = df[df[col].isin(val if isinstance(val, list) else [val])]
        elif op == "not_in":
            df = df[~df[col].isin(val if isinstance(val, list) else [val])]
        elif op == "gt":
            df = df[df[col] > val]
        elif op == "gte":
            df = df[df[col] >= val]
        elif op == "lt":
            df = df[df[col] < val]
        elif op == "lte":
            df = df[df[col] <= val]
        elif op == "contains":
            df = df[df[col].astype(str).str.contains(str(val), case=False, na=False)]
    return df


def _agg(df, group_col, value_cols, agg):
    func = AGG_FUNCS.get(agg, "sum")
    grouped = df.groupby(group_col)[value_cols].agg(func).reset_index()
    return grouped


def build_chart_data(df: pd.DataFrame, req) -> dict:
    df = apply_filters(df, req.filters)
    ctype = req.chart_type

    if ctype in ("bar", "column", "line", "area"):
        y_cols = req.y or []
        if req.x and y_cols:
            grouped = _agg(df, req.x, y_cols, req.aggregation)
            if req.top_n:
                grouped = grouped.sort_values(y_cols[0], ascending=False).head(req.top_n)
            return sanitize_json({
                "type": ctype,
                "x": grouped[req.x].astype(str).tolist(),
                "series": [{"name": y, "values": grouped[y].tolist()} for y in y_cols],
            })
        return {"type": ctype, "x": [], "series": []}

    if ctype in ("pie", "donut", "funnel"):
        names_col = req.names or req.x
        values_col = req.values or (req.y[0] if req.y else None)
        if names_col and values_col:
            grouped = df.groupby(names_col)[values_col].agg(AGG_FUNCS.get(req.aggregation, "sum")).reset_index()
            grouped = grouped.sort_values(values_col, ascending=False)
            if req.top_n:
                grouped = grouped.head(req.top_n)
            return sanitize_json({
                "type": ctype,
                "labels": grouped[names_col].astype(str).tolist(),
                "values": grouped[values_col].tolist(),
            })
        return {"type": ctype, "labels": [], "values": []}

    if ctype == "scatter" or ctype == "bubble":
        x_col, y_cols = req.x, req.y or []
        y_col = y_cols[0] if y_cols else None
        if x_col and y_col:
            sub = df[[c for c in [x_col, y_col, req.color, req.size] if c]].dropna()
            result = {
                "type": ctype,
                "x": sub[x_col].tolist(),
                "y": sub[y_col].tolist(),
            }
            if req.color and req.color in sub.columns:
                result["color"] = sub[req.color].astype(str).tolist()
            if req.size and req.size in sub.columns:
                result["size"] = sub[req.size].tolist()
            return sanitize_json(result)
        return {"type": ctype, "x": [], "y": []}

    if ctype == "histogram":
        x_col = req.x
        if x_col:
            vals = df[x_col].dropna().tolist()
            return sanitize_json({"type": "histogram", "values": vals})
        return {"type": "histogram", "values": []}

    if ctype in ("box", "violin"):
        y_cols = req.y or ([req.x] if req.x else [])
        group_col = req.color
        if group_col and group_col in df.columns:
            groups = {}
            for g, sub in df.groupby(group_col):
                groups[str(g)] = sub[y_cols[0]].dropna().tolist() if y_cols else []
            return sanitize_json({"type": ctype, "grouped": True, "groups": groups})
        series = {y: df[y].dropna().tolist() for y in y_cols if y in df.columns}
        return sanitize_json({"type": ctype, "grouped": False, "series": series})

    if ctype == "heatmap" or ctype == "correlation":
        numeric_df = df.select_dtypes(include=[np.number])
        corr = numeric_df.corr()
        return sanitize_json({
            "type": "heatmap",
            "columns": [str(c) for c in corr.columns],
            "matrix": corr.values.tolist(),
        })

    if ctype == "treemap" or ctype == "sunburst":
        path_cols = req.path or ([req.x] if req.x else [])
        value_col = req.values or (req.y[0] if req.y else None)
        if path_cols and value_col:
            grouped = df.groupby(path_cols)[value_col].sum().reset_index()
            return sanitize_json({
                "type": ctype,
                "path_columns": path_cols,
                "records": grouped.to_dict(orient="records"),
                "value_column": value_col,
            })
        return {"type": ctype, "records": []}

    if ctype == "waterfall":
        x_col, y_cols = req.x, req.y or []
        if x_col and y_cols:
            grouped = _agg(df, x_col, y_cols, req.aggregation)
            return sanitize_json({
                "type": "waterfall",
                "x": grouped[x_col].astype(str).tolist(),
                "y": grouped[y_cols[0]].tolist(),
            })
        return {"type": "waterfall", "x": [], "y": []}

    if ctype in ("radar", "polar"):
        theta_col = req.theta or req.x
        r_col = req.r or (req.y[0] if req.y else None)
        if theta_col and r_col:
            grouped = df.groupby(theta_col)[r_col].agg(AGG_FUNCS.get(req.aggregation, "sum")).reset_index()
            return sanitize_json({
                "type": ctype,
                "theta": grouped[theta_col].astype(str).tolist(),
                "r": grouped[r_col].tolist(),
            })
        return {"type": ctype, "theta": [], "r": []}

    if ctype == "parallel":
        dims = req.dimensions or df.select_dtypes(include=[np.number]).columns.tolist()[:6]
        sub = df[dims].dropna()
        return sanitize_json({
            "type": "parallel",
            "dimensions": dims,
            "data": {d: sub[d].tolist() for d in dims},
        })

    if ctype == "pairplot":
        dims = req.dimensions or df.select_dtypes(include=[np.number]).columns.tolist()[:5]
        sub = df[dims].dropna()
        return sanitize_json({
            "type": "pairplot",
            "dimensions": dims,
            "data": {d: sub[d].tolist() for d in dims},
        })

    if ctype == "gauge":
        value_col = req.values or (req.y[0] if req.y else None)
        if value_col:
            val = df[value_col].agg(AGG_FUNCS.get(req.aggregation, "mean"))
            return sanitize_json({
                "type": "gauge",
                "value": float(val),
                "max": float(df[value_col].max()),
                "min": float(df[value_col].min()),
            })
        return {"type": "gauge", "value": 0, "max": 100, "min": 0}

    if ctype == "kpi":
        value_col = req.values or (req.y[0] if req.y else None)
        if value_col:
            val = df[value_col].agg(AGG_FUNCS.get(req.aggregation, "sum"))
            return sanitize_json({"type": "kpi", "value": float(val), "label": value_col})
        return {"type": "kpi", "value": 0, "label": ""}

    if ctype in ("table", "matrix"):
        cols = (req.dimensions or []) + (req.y or [])
        cols = cols or df.columns.tolist()[:10]
        sub = df[[c for c in cols if c in df.columns]].head(500)
        return sanitize_json({
            "type": ctype,
            "columns": [str(c) for c in sub.columns],
            "rows": sub.to_dict(orient="records"),
        })

    return {"type": ctype, "error": "Unsupported chart type"}
