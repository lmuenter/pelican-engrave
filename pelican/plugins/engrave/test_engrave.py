import pytest
from pelican import Pelican
from pelican.contents import Article, Category
from pelican.settings import DEFAULT_CONFIG
from datetime import datetime
from engrave import get_qr_code
import os
import tempfile


class MockCategory(Category):
    def __init__(self, name, settings):
        super().__init__(name, settings)


@pytest.fixture
def pelican_settings():
    settings = DEFAULT_CONFIG.copy()
    temp_output_path = tempfile.mkdtemp()
    settings.update({
        "SITEURL": "http://example.com",
        "OUTPUT_PATH": temp_output_path,
        "ARTICLE_URL": "{slug}.html",
        "ARTICLE_SAVE_AS": "{slug}.html"
    })
    return settings


@pytest.fixture
def article(pelican_settings):
    category = MockCategory("Test Category", pelican_settings)
    return Article(
        content="<p>Test content</p>",
        metadata={
            "title": "Test Article",
            "slug": "test-article",
            "date": datetime(2024, 8, 28),
            "category": category
        },
        settings=pelican_settings
    )


def test_get_qr_code(article):

    # add qrcode
    get_qr_code(article)

    # get expected url
    relative_path = os.path.join("images", "engrave", f"{article.slug}_qrcode.svg")
    expected_url = f"http://example.com/{relative_path}"

    # chech presence of url in article context
    assert hasattr(article, "engrave_qrcode"), "Article should have engrave_qrcode attribute."
    assert article.engrave_qrcode == expected_url, f"Expected URL to be {expected_url}, but got {article.engrave_qrcode}"

    # check presence/structure of qrcode
    svg_path = os.path.join(article.settings["OUTPUT_PATH"], relative_path)
    assert os.path.exists(svg_path)
    assert os.path.getsize(svg_path) > 0
    with open(svg_path, 'r') as file:
        svg_content = file.read()
        assert '<svg' in svg_content and '</svg>' in svg_content, "QR code SVG file does not contain valid SVG content."
