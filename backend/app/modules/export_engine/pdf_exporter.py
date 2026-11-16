from typing import Any

from playwright.sync_api import sync_playwright

from backend.app.modules.export_engine.html_renderer import HtmlRenderer
from backend.app.modules.export_engine.matrix import CompatibilityTracker


class PdfExporter:
    @classmethod
    def export(
        cls, doc_title: str, doc_content: dict[str, Any], tracker: CompatibilityTracker
    ) -> bytes:
        html_content = HtmlRenderer.render_to_html(
            doc_title=doc_title,
            doc_content=doc_content,
            tracker=tracker,
            is_preview=False,
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )
            try:
                page = browser.new_page()
                page.set_content(html_content, wait_until="load")
                pdf_bytes = page.pdf(
                    format="A4",
                    print_background=True,
                    margin={
                        "top": "2.5cm",
                        "bottom": "2.5cm",
                        "left": "2cm",
                        "right": "2cm",
                    },
                )
                return pdf_bytes
            finally:
                browser.close()
