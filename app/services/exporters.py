from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from app.config import settings


def safe_text(value: str) -> str:

    return (
        value
        .encode(
            "latin-1",
            "replace"
        )
        .decode("latin-1")
    )


def save_pdf(
    layout,
    title: str = "ComicCraft Comic"
) -> Path:

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    pdf_path = (
        settings.exports_dir /
        f"comiccraft_{timestamp}.pdf"
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    for panel in layout:

        pdf.add_page()

        # Panel title

        pdf.set_font(
            "Helvetica",
            "B",
            18
        )

        pdf.cell(
            0,
            12,
            safe_text(
                f"Panel "
                f"{panel['panel_number']}: "
                f"{panel['title']}"
            ),
            new_x="LMARGIN",
            new_y="NEXT"
        )

        # Image

        image_path = Path(
            panel["image_path"]
        )

        if image_path.exists():

            pdf.image(
                str(image_path),
                x=20,
                y=30,
                w=170,
                h=170
            )

        # Scene description

        pdf.set_y(205)

        pdf.set_font(
            "Helvetica",
            "I",
            10
        )

        pdf.multi_cell(
            0,
            6,
            safe_text(
                panel["scene_description"]
            )
        )

        # Caption

        pdf.ln(3)

        pdf.set_font(
            "Helvetica",
            "B",
            11
        )

        pdf.multi_cell(
            0,
            6,
            "Caption"
        )

        pdf.set_font(
            "Helvetica",
            "",
            11
        )

        pdf.multi_cell(
            0,
            6,
            safe_text(
                panel["caption"]
            )
        )

        # Narration

        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "B",
            11
        )

        pdf.multi_cell(
            0,
            6,
            "Narration"
        )

        pdf.set_font(
            "Helvetica",
            "",
            11
        )

        pdf.multi_cell(
            0,
            6,
            safe_text(
                panel["narration"]
            )
        )

        # Dialogue

        if panel.get("dialogue"):

            pdf.ln(2)

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                0,
                6,
                "Dialogue"
            )

            pdf.set_font(
                "Helvetica",
                "",
                11
            )

            pdf.multi_cell(
                0,
                6,
                safe_text(
                    panel["dialogue"]
                )
            )

    pdf.output(
        str(pdf_path)
    )

    return pdf_path