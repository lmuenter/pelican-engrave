import io

import cairosvg
from PIL import Image
import pytest
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
from qrcode.image.svg import SvgImage

from ...engraver.qrcode import QRCodeEngraver


@pytest.fixture
def qr_engraver():
    """Instantiate Engraver."""
    return QRCodeEngraver()


def decode_qr_code_from_svg(svg_path):
    """Extract data from QRCode using cairosvg and pyzbar."""
    with open(svg_path) as svg_file:
        svg_content = svg_file.read()

    png_output = cairosvg.svg2png(bytestring=svg_content, background_color="white")
    image = Image.open(io.BytesIO(png_output))

    decoded_objects = pyzbar.decode(image, symbols=[ZBarSymbol.QRCODE])
    return decoded_objects[0].data.decode("utf-8")


def test_qr_code_generation_and_content(tmp_path, qr_engraver):
    """Check functioning and correctness of output."""
    qr_image = qr_engraver.engrave("https://example.com")
    assert qr_image, "QR code generation should return an image"

    # Save as QR code
    svg_path = tmp_path / "qr_code.svg"
    qr_image.save(svg_path)

    decoded_data = decode_qr_code_from_svg(svg_path)

    # Decode and check
    decoded_data = decode_qr_code_from_svg(svg_path)
    assert (
        decoded_data == "https://example.com"
    ), f"Expected 'https://example.com', got {decoded_data}"


def test_invalid_url_handling(qr_engraver):
    """Ensure no QR code is generated for invalid URLs."""
    assert (
        qr_engraver.engrave("http://not-allowed.com") is None
    ), "Shouldn't generate QR code for invalid URL"


def test_output_svg_format(qr_engraver):
    """Check return type."""
    qr_image = qr_engraver.engrave("https://example.com")
    assert isinstance(qr_image, SvgImage), "Generated QR code should be an SvgImage"
