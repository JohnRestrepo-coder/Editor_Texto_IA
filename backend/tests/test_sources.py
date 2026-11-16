import io

import openpyxl
from docx import Document as DocxDocument
from pypdf import PdfWriter

from backend.app.modules.source_mgmt.extractor import SourceExtractor


def test_extract_plain_text():
    content = "Línea 1: Diagnóstico inicial.\nLínea 2: Objetivos de mercado."
    text, file_type, char_count, success, error = SourceExtractor.extract_text(
        "notas.txt", content.encode("utf-8")
    )
    assert success is True
    assert error is None
    assert file_type == "text"
    assert "Diagnóstico inicial" in text
    assert char_count == len(content)


def test_extract_csv():
    csv_data = "Producto,Precio,Ventas\nWidget A,1500,45\nWidget B,2300,80\n"
    text, file_type, _char_count, success, error = SourceExtractor.extract_text(
        "ventas.csv", csv_data.encode("utf-8")
    )
    assert success is True
    assert error is None
    assert file_type == "csv"
    assert "Widget A | 1500 | 45" in text
    assert "Widget B | 2300 | 80" in text


def test_extract_docx():
    doc = DocxDocument()
    doc.add_heading("Estrategia 2026", level=1)
    doc.add_paragraph("Este es un informe de prueba sobre métricas trimestrales.")
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    text, file_type, _count, success, error = SourceExtractor.extract_text(
        "estrategia.docx", buf.getvalue()
    )
    assert success is True
    assert error is None
    assert file_type == "docx"
    assert "Estrategia 2026" in text
    assert "Este es un informe de prueba" in text


def test_extract_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Finanzas"
    ws.append(["Concepto", "Monto"])
    ws.append(["Ingresos", 50000])
    ws.append(["Costos", 22000])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    text, file_type, _count, success, error = SourceExtractor.extract_text(
        "reporte.xlsx", buf.getvalue()
    )
    assert success is True
    assert error is None
    assert file_type == "excel"
    assert "Concepto | Monto" in text
    assert "Ingresos | 50000" in text


def test_extract_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)

    _text, file_type, _count, success, error = SourceExtractor.extract_text(
        "documento.pdf", buf.getvalue()
    )
    assert success is True
    assert error is None
    assert file_type == "pdf"


def test_extract_unsupported_file():
    _text, _file_type, count, success, error = SourceExtractor.extract_text(
        "video.mp4", b"fake binary data"
    )
    assert success is False
    assert count == 0
    assert "no soportado" in error
