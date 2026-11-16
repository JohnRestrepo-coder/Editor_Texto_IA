import csv
import io
import os

import openpyxl
from docx import Document as DocxDocument
from pypdf import PdfReader


class SourceExtractor:
    """
    Extractor multi-formato para procesar documentos de referencia (fuentes)
    y suministrar contexto fidedigno a los modelos de lenguaje.
    """

    MAX_CHARS_PER_SOURCE = 50000

    @classmethod
    def extract_text(
        cls, filename: str, content_bytes: bytes
    ) -> tuple[str, str, int, bool, str | None]:
        """
        Extrae texto según la extensión del archivo.
        Retorna (texto_extraido, tipo_archivo, cantidad_caracteres, exito, error).
        """
        ext = os.path.splitext(filename)[1].lower()

        try:
            if ext == ".pdf":
                text = cls._extract_pdf(content_bytes)
                file_type = "pdf"
            elif ext == ".docx":
                text = cls._extract_docx(content_bytes)
                file_type = "docx"
            elif ext in (".xlsx", ".xls"):
                text = cls._extract_excel(content_bytes)
                file_type = "excel"
            elif ext == ".csv":
                text = cls._extract_csv(content_bytes)
                file_type = "csv"
            elif ext in (".txt", ".md", ".json", ".log"):
                text = cls._extract_text_plain(content_bytes)
                file_type = "text"
            else:
                return (
                    "",
                    ext.replace(".", ""),
                    0,
                    False,
                    f"Tipo de archivo '{ext}' no soportado. Formatos admitidos: PDF, DOCX, XLSX, XLS, CSV, TXT.",
                )

            # Control de tamaño máximo para no sobrecargar el prompt
            if len(text) > cls.MAX_CHARS_PER_SOURCE:
                text = (
                    text[: cls.MAX_CHARS_PER_SOURCE]
                    + "\n\n[... CONTENIDO TRUNCADO POR LÍMITE DE TAMAÑO ...]"
                )

            return text.strip(), file_type, len(text.strip()), True, None

        except (ValueError, KeyError, OSError, TypeError, RuntimeError) as e:
            return (
                "",
                ext.replace(".", ""),
                0,
                False,
                f"Error al procesar el archivo: {e!s}",
            )

    @classmethod
    def _extract_pdf(cls, content_bytes: bytes) -> str:
        reader = PdfReader(io.BytesIO(content_bytes))
        pages_text: list[str] = []
        for idx, page in enumerate(reader.pages):
            page_content = page.extract_text() or ""
            if page_content.strip():
                pages_text.append(f"--- Página {idx + 1} ---\n{page_content.strip()}")
        return "\n\n".join(pages_text)

    @classmethod
    def _extract_docx(cls, content_bytes: bytes) -> str:
        doc = DocxDocument(io.BytesIO(content_bytes))
        paragraphs: list[str] = []
        for p in doc.paragraphs:
            if p.text.strip():
                paragraphs.append(p.text.strip())

        # Extraer también contenido de tablas si existen
        for table in doc.tables:
            for row in table.rows:
                row_cells = [
                    cell.text.strip() for cell in row.cells if cell.text.strip()
                ]
                if row_cells:
                    paragraphs.append(" | ".join(row_cells))

        return "\n\n".join(paragraphs)

    @classmethod
    def _extract_excel(cls, content_bytes: bytes) -> str:
        wb = openpyxl.load_workbook(io.BytesIO(content_bytes), data_only=True)
        sheets_text: list[str] = []

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            rows_data: list[str] = []
            for row in ws.iter_rows(values_only=True):
                # Filtrar celdas no vacías
                row_str = [
                    str(val).strip()
                    for val in row
                    if val is not None and str(val).strip()
                ]
                if row_str:
                    rows_data.append(" | ".join(row_str))

            if rows_data:
                sheets_text.append(
                    f"--- Hoja: {sheet_name} ---\n" + "\n".join(rows_data[:500])
                )

        return "\n\n".join(sheets_text)

    @classmethod
    def _extract_csv(cls, content_bytes: bytes) -> str:
        text_content = cls._extract_text_plain(content_bytes)
        reader = csv.reader(io.StringIO(text_content))
        lines: list[str] = []
        for idx, row in enumerate(reader):
            if idx >= 500:  # Máximo 500 filas
                lines.append("[... Filas adicionales omitidas ...]")
                break
            if any(cell.strip() for cell in row):
                lines.append(" | ".join([cell.strip() for cell in row]))
        return "\n".join(lines)

    @classmethod
    def _extract_text_plain(cls, content_bytes: bytes) -> str:
        try:
            return content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return content_bytes.decode("latin-1")
            except UnicodeDecodeError:
                return content_bytes.decode("utf-8", errors="replace")
