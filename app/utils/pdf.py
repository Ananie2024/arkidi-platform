"""
PDF Certificate and Report Generator Service using ReportLab.

Produces genuine, printable A4 canonical sacramental certificates (previously a
placeholder that returned a few raw header bytes) with:

* an ornate double border,
* the recipient, certificate number and canonical register details,
* the QR verification image (from the certificate's ``qr_code_payload``) and
* an issuance footer (date + issuing officer).

The function is intentionally dependency-light on application data: callers
pass a flat ``details`` mapping of display strings plus optional QR PNG bytes,
so the same renderer can be reused by the API download endpoint and the Celery
batch task (``app/tasks/certificates.py``).
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = A4

_BORDER_GOLD = colors.HexColor("#9B6A2F")
_BORDER_BLACK = colors.HexColor("#222222")
_ACCENT = colors.HexColor("#8B1A1A")

# Layout constants (in points; A4 = 595 x 842).
_MARGIN = 42
_OUTER = 10


def _wrap_text(
    c: canvas.Canvas, text: str, x: float, y: float, max_width: float, leading: float = 15
):
    """Greedily wrap ``text`` to fit *max_width* and draw it at ``(x, y)``.

    Returns the new baseline ``y`` after the wrapped block.
    """
    words = text.split()
    if not words:
        return y
    lines: list[str] = []
    current = ""
    for word in words:
        probe = f"{current} {word}".strip()
        if c.stringWidth(probe, "Helvetica", 10) <= max_width:
            current = probe
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    for idx, line in enumerate(lines):
        c.drawString(x, y - idx * leading, line)
    return y - len(lines) * leading


def _draw_ornate_border(c: canvas.Canvas):
    """Draw a double gold/black border frame inside the A4 page."""
    c.setStrokeColor(_BORDER_GOLD)
    c.setLineWidth(3)
    c.roundRect(_MARGIN, _MARGIN, PAGE_W - 2 * _MARGIN, PAGE_H - 2 * _MARGIN, 6, stroke=1, fill=0)
    c.setStrokeColor(_BORDER_BLACK)
    c.setLineWidth(1)
    c.roundRect(
        _MARGIN + _OUTER,
        _MARGIN + _OUTER,
        PAGE_W - 2 * (_MARGIN + _OUTER),
        PAGE_H - 2 * (_MARGIN + _OUTER),
        4,
        stroke=1,
        fill=0,
    )


def generate_certificate_pdf(
    *,
    title: str,
    recipient: str,
    details: dict[str, Any],
    issued_at: datetime | None = None,
    issued_by: str | None = None,
    certificate_number: str | None = None,
    qr_image_bytes: bytes | None = None,
    verification_url: str | None = None,
) -> bytes:
    """Render a canonical sacramental certificate as PDF bytes.

    Args:
        title: Human-readable certificate title, e.g. "Certificate of Baptism".
        recipient: Name of the person the certificate concerns.
        details: Flat map of display labels -> values for the certificate body.
        issued_at: Issue timestamp (defaults to now, rendered as local date).
        issued_by: Name of the issuing officer (e.g. the Curé / Chancellor).
        certificate_number: Unique serial shown in the top-right corner.
        qr_image_bytes: PNG bytes of the verification QR code (optional).
        verification_url: Full verification URL shown under the QR (optional).

    Returns:
        Complete PDF file bytes (starts with ``%PDF`` so it is a valid file).
    """
    issued_at = issued_at or datetime.now()
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setTitle(title or "Arkidi Certificate")
    c.setAuthor("Arkidi Platform - Archidiocèse de Kigali")
    c.setSubject(certificate_number or "Sacramental Certificate")

    _draw_ornate_border(c)

    inner_left = _MARGIN + _OUTER + 12
    inner_right = PAGE_W - _MARGIN - _OUTER - 12
    inner_top = PAGE_H - _MARGIN - _OUTER - 12
    content_width = inner_right - inner_left

    # --- Header -----------------------------------------------------------
    c.setFont("Times-Bold", 18)
    c.setFillColor(_ACCENT)
    c.drawCentredString(PAGE_W / 2, inner_top, "ARCHIDIOCÈSE DE KIGALI")
    c.setFont("Times-Italic", 11)
    c.setFillColor(colors.black)
    c.drawCentredString(
        PAGE_W / 2,
        inner_top - 18,
        "Archidiocèse de Kigali  •  Official Sacramental Certificate",
    )

    if certificate_number:
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(_BORDER_GOLD)
        c.drawRightString(inner_right, inner_top, f"N° {certificate_number}")

    # --- Title -------------------------------------------------------------
    c.setFont("Times-Bold", 22)
    c.setFillColor(_ACCENT)
    c.drawCentredString(PAGE_W / 2, inner_top - 56, title)

    # --- Body --------------------------------------------------------------
    y = inner_top - 100
    label_x = inner_left + 8
    value_x = inner_left + 150
    value_width = content_width - 150 - 8

    c.setFont("Times-Bold", 15)
    c.setFillColor(colors.black)
    c.drawString(inner_left, y, recipient)
    y -= 28

    intro = (
        "is hereby declared to have received the Sacrament of "
        f"{title} according to the canonical registers of the Catholic Church. "
        "This certificate is issued by the Archdiocese of Kigali and records "
        "the following particulars:"
    )
    c.setFont("Helvetica", 10)
    y = _wrap_text(c, intro, inner_left, y, content_width, 15)
    y -= 20

    for key, value in details.items():
        if not key or value is None or value == "":
            continue
        if y < _MARGIN + _OUTER + 110:
            break
        c.setFont("Helvetica-Bold", 10)
        c.drawString(label_x, y, f"{key}:")
        c.setFont("Helvetica", 10)
        _wrap_text(c, str(value), value_x, y, value_width, 14)
        y -= 18
    c.setFont("Helvetica", 10)

    # --- QR verification ---------------------------------------------------
    qr_size = 66
    if qr_image_bytes:
        try:
            img = ImageReader(io.BytesIO(qr_image_bytes))
            qr_x = inner_left + 6
            qr_y = _MARGIN + _OUTER + 26
            c.drawImage(img, qr_x, qr_y, width=qr_size, height=qr_size, mask="auto")
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(qr_x, qr_y + qr_size + 4, "Scan to verify authenticity")
            if verification_url:
                c.setFont("Helvetica-Oblique", 7)
                _wrap_text(
                    c,
                    verification_url,
                    qr_x + qr_size + 16,
                    qr_y + 2,
                    content_width - qr_size - 70,
                    9,
                )
        except Exception:  # pragma: no cover - non-fatal embedding failure
            c.setFont("Helvetica", 9)
            c.drawString(
                inner_left + 6, _MARGIN + _OUTER + 40, "QR verification image unavailable."
            )

    # --- Footer / signature line ------------------------------------------
    footer_top = _MARGIN + _OUTER + 14
    c.setStrokeColor(_BORDER_BLACK)
    c.setLineWidth(0.8)

    sig_left = inner_left + 160
    sig_right = inner_right - 40
    c.line(sig_left, footer_top, sig_right, footer_top)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.black)
    c.drawCentredString(
        (sig_left + sig_right) / 2,
        footer_top - 4,
        issued_by or "Chancellerie de l'Archidiocèse",
    )

    c.setFont("Helvetica", 9)
    c.drawString(inner_left + 6, footer_top - 26, f"Issued on: {issued_at.strftime('%d %B %Y')}")
    if certificate_number:
        c.drawString(inner_left + 6, footer_top - 38, f"Certificate: {certificate_number}")

    c.showPage()
    c.save()
    return buffer.getvalue()
