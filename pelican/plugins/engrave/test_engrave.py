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


def test_generate_qr_code(article):

    # add qrcode to article
    get_qr_code(article)

    # get qrcode path
    svg_path = os.path.join(article.settings["OUTPUT_PATH"], "images", "engrave", f"{article.slug}_qrcode.svg")

    # check presence and structure of embedded qrcode
    assert svg_path in article.content
    assert f'<img src="{svg_path}" alt="QR Code" type="image/svg+xml">' in article.content

    # check presence and structure of qrcode
    assert os.path.exists(svg_path)
    assert os.path.getsize(svg_path) > 0
