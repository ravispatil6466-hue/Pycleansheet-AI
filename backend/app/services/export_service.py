"""Export helpers for CSV, Excel, JSON, and PDF report generation."""
import io
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    return buf.getvalue()


def to_json_bytes(df: pd.DataFrame) -> bytes:
    return df.to_json(orient="records", date_format="iso").encode("utf-8")


def build_pdf_report(title: str, quality: dict, summary: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleX", parent=styles["Title"], textColor=colors.HexColor("#0F3D5C"))
    elements = [Paragraph(title, title_style), Spacer(1, 12)]

    elements.append(Paragraph("Data Quality Overview", styles["Heading2"]))
    qdata = [["Metric", "Value"]]
    qdata.append(["Total Rows", quality.get("total_rows", "-")])
    qdata.append(["Total Columns", quality.get("total_columns", "-")])
    qdata.append(["Duplicate Rows", quality.get("duplicate_rows", "-")])
    qdata.append(["Missing Cells", quality.get("total_missing_cells", "-")])
    t = Table(qdata, colWidths=[8 * cm, 8 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F3D5C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("Column Summary", styles["Heading2"]))
    cdata = [["Column", "Dtype", "Missing", "Missing %", "Unique"]]
    for col in quality.get("columns", [])[:40]:
        cdata.append([col["name"], col["dtype"], col["missing"], f"{col['missing_pct']}%", col["unique"]])
    t2 = Table(cdata, colWidths=[5 * cm, 3 * cm, 3 * cm, 3 * cm, 3 * cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E7A6F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    elements.append(t2)

    doc.build(elements)
    return buf.getvalue()
