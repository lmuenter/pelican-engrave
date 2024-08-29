from datetime import datetime
import io
import os
from unittest.mock import Mock

import cairosvg
from PIL import Image
import pytest
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol

from engrave import EngravePlugin, QRCodeEngraver
from pelican import Pelican
from pelican.contents import Article, Category
from pelican.settings import DEFAULT_CONFIG


class MockCategory(Category):
    """Set up a mock category."""

    def __init__(self, name, settings):
        super().__init__(name, settings)


@pytest.fixture
def pelican_settings(tmp_path):
    """Create Pelican settings using pytest's temporary path fixture."""
    settings = DEFAULT_CONFIG.copy()
    settings.update(
        {
            "SITEURL": "http://example.com",
            "OUTPUT_PATH": str(tmp_path / "output"),
            "ARTICLE_URL": "{slug}.html",
            "ARTICLE_SAVE_AS": "{slug}.html",
            "PATH": str(tmp_path / "content"),
            "PLUGINS": ["engrave"],
            "FEED_ALL_ATOM": None,
            "FEED_DOMAIN": "http://example.com",
            "PAGINATED_TEMPLATES": {},
            "DEFAULT_PAGINATION": False,
        }
    )
    return settings


def setup_dummy_qr_codes(output_path, num_dummy_files=5):
    """Create dummy QR code files to simulate old QR codes using os."""
    engrave_path = os.path.join(output_path, "images", "engrave")
    if not os.path.exists(engrave_path):
        os.makedirs(engrave_path)
    for i in range(num_dummy_files):
        dummy_file_path = os.path.join(engrave_path, f"dummy_{i}.svg")
        with open(dummy_file_path, "w") as f:
            f.write("Dummy QR code content")


@pytest.fixture
def article(pelican_settings):
    """Set up a basic article instance."""
    category = MockCategory("Test Category", pelican_settings)
    return Article(
        content="<p>Test content</p>",
        metadata={
            "title": "Test Article",
            "slug": "test-article",
            "date": datetime(2024, 8, 28),
            "category": category,
        },
        settings=pelican_settings,
    )


@pytest.fixture
def pelican_instance(pelican_settings, tmp_path):
    """Set up Pelican instance with dummy qrcode files."""
    setup_dummy_qr_codes(str(tmp_path / "output"))
    return Pelican(settings=pelican_settings)


@pytest.fixture
def engrave_plugin(pelican_settings):
    """Instantiate QRCoceEngraver."""
    qr_engraver = QRCodeEngraver(image_dir="images", base_dir="engrave")
    return EngravePlugin(qr_engraver)


def decode_qr_code_from_svg(svg_path):
    """Extract string from QRCode using cairosvg and pyzbar."""
    with open(svg_path) as svg_file:
        svg_content = svg_file.read()

    png_output = cairosvg.svg2png(bytestring=svg_content, background_color="white")
    image = Image.open(io.BytesIO(png_output))

    decoded_objects = pyzbar.decode(image, symbols=[ZBarSymbol.QRCODE])
    return decoded_objects[0].data.decode("utf-8")


def test_engraving(article, engrave_plugin, tmp_path):
    """Test basic plugin functionality."""
    engrave_plugin.process_content(article)
    output_path = article.settings["OUTPUT_PATH"]
    expected_image_path = os.path.join(
        output_path, "images", "engrave", f"{article.slug}_code.svg"
    )

    assert os.path.exists(expected_image_path), "Engraved image file should be created"
    assert (
        os.path.getsize(expected_image_path) > 0
    ), "Engraved image file should not be empty"


def test_cleanup_directory_on_init(engrave_plugin, pelican_settings, tmp_path):
    """Test cleanup of previous QRCodes for QRCode devalidation."""
    # simulate a previous run with engrave
    previous_run_path = os.path.join(
        pelican_settings["OUTPUT_PATH"], "images", "engrave", "old_file.svg"
    )
    os.makedirs(os.path.dirname(previous_run_path), exist_ok=True)
    with open(previous_run_path, "w") as f:
        f.write("Old content")

    assert os.path.exists(previous_run_path), "Old file should exist before cleanup"

    # run cleanup
    pelican = Mock(settings=pelican_settings)
    engrave_plugin.engraver._cleanup_directory(pelican)

    assert not os.path.exists(
        previous_run_path
    ), "Old file should be removed after cleanup"
    assert os.path.isdir(
        os.path.dirname(previous_run_path)
    ), "Directory should still exist after cleanup"


def test_qr_code_decoding(article, engrave_plugin, tmp_path):
    """Test QRCode content match expected URL."""
    engrave_plugin.process_content(article)
    output_path = article.settings["OUTPUT_PATH"]
    qr_svg_path = os.path.join(
        output_path, "images", "engrave", f"{article.slug}_code.svg"
    )

    assert os.path.exists(qr_svg_path), "QR code SVG should have been generated"

    # decode and check QR code
    decoded_url = decode_qr_code_from_svg(qr_svg_path)
    expected_url = f"http://example.com/{article.slug}.html"
    assert (
        decoded_url == expected_url
    ), f"Decoded QR code URL should have been {expected_url}"
