"""
charts.py
---------
Chart factory: builds a Plotly figure for any of the 14 supported chart
types given a dataframe, column mapping and a format dict from the
Format Panel. Also exposes CHART_TYPES and the field requirements for
each, used by the Dashboard Builder to render the right input widgets.
"""

import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import numpy as np

from src.components import PALETTES

CHART_TYPES = {
    "Bar Chart": {"fields": ["x", "y", "color"]},
    "Line Chart": {"fields": ["x", "y", "color"]},
    "Pie Chart": {"fields": ["names", "values"]},
    "Scatter Plot": {"fields": ["x", "y", "color", "size"]},
    "Histogram": {"fields": ["x", "color"]},
    "Heatmap": {"fields": []},  # uses full numeric correlation
    "Box Plot": {"fields": ["x", "y", "color"]},
    "Area Chart": {"fields": ["x", "y", "color"]},
    "Treemap": {"fields": ["path", "values"]},
    "Sunburst Chart": {"fields": ["path", "values"]},
    "Violin Plot": {"fields": ["x", "y", "color"]},
    "Pair Plot": {"fields": ["dimensions"]},
    "Distribution Plot": {"fields": ["x"]},
    "Correlation Matrix": {"fields": []},
}


def build_chart(chart_type: str, df: pd.DataFrame, mapping: dict, fmt: dict):
    palette = PALETTES.get(fmt.get("palette", "Vivid"), PALETTES["Vivid"])
    template = fmt.get("chart_theme", "plotly_dark")

    common_layout = dict(
        template=template,
        height=fmt.get("height", 380),
        showlegend=fmt.get("show_legend", True),
        font=dict(family=fmt.get("font_family", "Inter, sans-serif"), size=fmt.get("font_size", 13)),
        margin=dict(l=30, r=20, t=50, b=30),
    )

    x = mapping.get("x")
    y = mapping.get("y")
    color = mapping.get("color") or None
    size = mapping.get("size") or None

    if chart_type == "Bar Chart":
        fig = px.bar(df, x=x, y=y, color=color, color_discrete_sequence=palette, barmode="group")
    elif chart_type == "Line Chart":
        fig = px.line(df, x=x, y=y, color=color, color_discrete_sequence=palette, markers=True)
    elif chart_type == "Pie Chart":
        fig = px.pie(df, names=mapping.get("names"), values=mapping.get("values"), color_discrete_sequence=palette, hole=0.35)
    elif chart_type == "Scatter Plot":
        fig = px.scatter(df, x=x, y=y, color=color, size=size, color_discrete_sequence=palette)
    elif chart_type == "Histogram":
        fig = px.histogram(df, x=x, color=color, color_discrete_sequence=palette, nbins=40)
    elif chart_type == "Heatmap":
        num_df = df.select_dtypes(include=np.number)
        fig = px.imshow(num_df.corr(numeric_only=True), text_auto=".2f", color_continuous_scale="RdBu_r", aspect="auto")
    elif chart_type == "Box Plot":
        fig = px.box(df, x=x, y=y, color=color, color_discrete_sequence=palette)
    elif chart_type == "Area Chart":
        fig = px.area(df, x=x, y=y, color=color, color_discrete_sequence=palette)
    elif chart_type == "Treemap":
        path = mapping.get("path") or []
        fig = px.treemap(df, path=path, values=mapping.get("values"), color_discrete_sequence=palette)
    elif chart_type == "Sunburst Chart":
        path = mapping.get("path") or []
        fig = px.sunburst(df, path=path, values=mapping.get("values"), color_discrete_sequence=palette)
    elif chart_type == "Violin Plot":
        fig = px.violin(df, x=x, y=y, color=color, box=True, points="outliers", color_discrete_sequence=palette)
    elif chart_type == "Pair Plot":
        dims = mapping.get("dimensions") or df.select_dtypes(include=np.number).columns.tolist()[:4]
        fig = px.scatter_matrix(df, dimensions=dims, color=color, color_discrete_sequence=palette)
    elif chart_type == "Distribution Plot":
        try:
            fig = ff.create_distplot([df[x].dropna().astype(float)], [x], colors=[palette[0]])
        except Exception:
            fig = px.histogram(df, x=x, marginal="rug", color_discrete_sequence=palette)
    elif chart_type == "Correlation Matrix":
        num_df = df.select_dtypes(include=np.number)
        fig = px.imshow(num_df.corr(numeric_only=True), text_auto=".2f", color_continuous_scale="Viridis", aspect="auto")
    else:
        fig = px.scatter(df, x=x, y=y)

    fig.update_layout(**common_layout)
    if not fmt.get("show_grid", True):
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
    if not fmt.get("show_tooltips", True):
        fig.update_traces(hoverinfo="skip", hovertemplate=None)

    return fig
