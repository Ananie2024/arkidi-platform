"""Unit tests for the ReportLab-based sacramental certificate PDF generator."""

import pytest

from app.utils.pdf import generate_certificate_pdf
from app.utils.qr import generate_qr_code_bytes


@pytest.mark.parametrize(
    "with_qr",
    [True, False],
)
def test_generate_certificate_pdf_produces_valid_pdf(with_qr):
    qr_bytes = (
        generate_qr_code_bytes("https://arkidi.archidiocesekigali.org/verify/TOKEN")
        if with_qr
        else None
    )
    pdf = generate_certificate_pdf(
        title="Certificate of Baptism",
        recipient="Jean Baptiste Karemera",
        details={
            "Celebration Date": "2026-01-05",
            "Minister": "Abbé Jean Uwimana",
            "Register": "Vol I - p.12",
        },
        certificate_number="CERT-BAP-ABCD1234",
        qr_image_bytes=qr_bytes,
        verification_url="https://arkidi.archidiocesekigali.org/verify/TOKEN",
        issued_by="Chancellerie de l'Archidiocèse",
    )
    # A real PDF starts with the %PDF magic and is a substantial file.
    assert pdf[:5] == b"%PDF-"
    assert len(pdf) > 1000
    assert b"/Type /Page" in pdf or b"/Type/Page" in pdf
