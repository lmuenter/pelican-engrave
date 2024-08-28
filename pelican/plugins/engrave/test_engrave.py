import io
import os
import tempfile
from datetime import datetime

import cairosvg
import pytest
import pyzbar.pyzbar as pyzbar
import qrcode
from engrave import get_qr_code, register
from pelican.contents import Article, Category
from pelican.settings import DEFAULT_CONFIG
from PIL import Image
from pyzbar.pyzbar import ZBarSymbol

from pelican import Pelican


class MockCategory(Category):
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
    """Creates dummy QR code files to simulate old QR codes using os."""
    engrave_path = os.path.join(output_path, "images", "engrave")
    if not os.path.exists(engrave_path):
        os.makedirs(engrave_path)
    for i in range(num_dummy_files):
        dummy_file_path = os.path.join(engrave_path, f"dummy_{i}.svg")
        with open(dummy_file_path, "w") as f:
            f.write("Dummy QR code content")


@pytest.fixture
def article(pelican_settings):
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
    setup_dummy_qr_codes(
        str(tmp_path / "output")
    )  # create initial dummy qrcodes for testing of removal
    return Pelican(settings=pelican_settings)


def decode_qr_code_from_svg(svg_path):
    try:
        with open(svg_path, "r") as svg_file:
            svg_content = svg_file.read()

        png_output = cairosvg.svg2png(bytestring=svg_content, background_color="white")
        image = Image.open(io.BytesIO(png_output))

        decoded_objects = pyzbar.decode(image, symbols=[ZBarSymbol.QRCODE])
        if decoded_objects:
            return decoded_objects[0].data.decode("utf-8")
        else:
            print("No QR code detected in the image.")
            return None
    except Exception as e:
        print(f"Error decoding QR code from SVG: {str(e)}")
        return None


def test_get_qr_code(article):
    get_qr_code(article)

    site_url = "http://example.com"
    full_article_url = f"{site_url}/{article.slug}.html"

    # get expected url for QR code file path
    relative_path = os.path.join("images", "engrave", f"{article.slug}_qrcode.svg")
    expected_url = f"http://example.com/{relative_path}"

    # check presence of URL in article context
    assert hasattr(
        article, "engrave_qrcode"
    ), "Article should have engrave_qrcode attribute."
    assert (
        article.engrave_qrcode == expected_url
    ), f"Expected URL to be {expected_url}, but got {article.engrave_qrcode}"

    # check presence/structure of QR code
    svg_path = os.path.join(article.settings["OUTPUT_PATH"], relative_path)
    assert os.path.exists(svg_path)
    assert os.path.getsize(svg_path) > 0

    # decode the QR code and check its content
    decoded_content = decode_qr_code_from_svg(svg_path)
    assert (
        decoded_content == full_article_url
    ), f"QR code should encode the full article URL. Expected {full_article_url}, got {decoded_content}"


def test_qr_code_cleanup(pelican_instance, article):
    """tests qr cleanup prior to run"""
    register()
    pelican_instance.run()

    # verify cleanup
    qr_code_dir = os.path.join(
        pelican_instance.settings["OUTPUT_PATH"], "images", "engrave"
    )
    assert os.path.isdir(qr_code_dir), "QR code directory should exist"

    qr_files = [f for f in os.listdir(qr_code_dir) if f.endswith(".svg")]
    assert len(qr_files) == 1, "Only one QR code should exist after cleanup"
    assert (
        qr_files[0] == f"{article.slug}_qrcode.svg"
    ), "The existing QR code should match the article slug"
