"""
QR Code Generation Utility for Sacramental Certificates & Land Deeds
"""
import io
import base64
import qrcode
from qrcode.image.pil import PilImage


def generate_qr_code_bytes(data: str) -> bytes:
    """Generate PNG bytes of a QR code containing verification URI or data."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img: PilImage = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def generate_qr_code_base64(data: str) -> str:
    """Generate base64 data URI of a QR code."""
    png_bytes = generate_qr_code_bytes(data)
    return f"data:image/png;base64,{base64.b64encode(png_bytes).decode('utf-8')}"
