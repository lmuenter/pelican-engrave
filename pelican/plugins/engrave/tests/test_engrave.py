import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from pelican import Pelican
from pelican.settings import read_settings


@pytest.fixture
def temp_path():
    """Create temp path for tests."""
    with TemporaryDirectory() as tempdir:
        yield os.path.abspath(tempdir)


@pytest.fixture
def create_article(temp_path):
    """Create dummy article in content dir."""
    content_dir = Path(temp_path) / "content"
    content_dir.mkdir(parents=True, exist_ok=True)

    article_content = """
Test Article
#############

:date: 2023-01-01
:category: Test

Test article.
"""
    article_path = content_dir / "test-article.rst"
    article_path.write_text(article_content)
    return article_path


@pytest.fixture
def create_previous_qrcodes(temp_path, num_dummy_files=5):
    """Create previous qr codes to simulate a previous run."""
    engrave_path = Path(temp_path) / "output" / "engrave"
    engrave_path.mkdir(parents=True, exist_ok=True)
    for i in range(num_dummy_files):
        dummy_file_path = engrave_path / f"dummy_{i}.svg"
        dummy_file_path.write_text("Dummy QR code content")


def test_plugin_functionality(create_previous_qrcodes, create_article, temp_path):
    """Test basic plugin functionality: directory cleanup and QRCOde generation."""
    engrave_output_path = Path(temp_path) / "output" / "engrave"
    svg_files = list(engrave_output_path.glob("*.svg"))
    print(svg_files)
    assert (
        len(svg_files) == 5
    ), "Engrave dir should contain 5 files of a simulated previous run."

    settings = read_settings(
        override={
            "SITEURL": "https://example.com",
            "PATH": temp_path,
            "OUTPUT_PATH": os.path.join(temp_path, "output"),
            "PLUGIN_PATHS": ["../../"],
            "PLUGINS": ["engrave"],
        }
    )
    pelican = Pelican(settings=settings)
    pelican.run()

    engrave_output_path = Path(temp_path) / "output" / "engrave"

    # check dir structure
    assert engrave_output_path.exists(), "Output directory was not created."
    svg_files = list(engrave_output_path.glob("*.svg"))
    assert (
        len(svg_files) == 1
    ), "Engrave dir should have been cleaned prior to execution."

    # check QR code
    article_name = "test-article"
    svg_with_article_name = any(article_name in file.name for file in svg_files)
    assert svg_with_article_name, f"No SVG file found for article name {article_name}."


def test_no_siteurl(create_article, temp_path, caplog):
    """Test behaviour with missing siteurl."""
    settings = read_settings(
        override={
            "PATH": temp_path,
            "OUTPUT_PATH": os.path.join(temp_path, "output"),
            "PLUGIN_PATHS": ["../../"],
            "PLUGINS": ["engrave"],
        }
    )
    pelican = Pelican(settings=settings)
    pelican.run()

    # check siteurl warning
    assert (
        "SITEURL is not set" in caplog.text
    ), "Warning over missing SITEURL should've been logged."

    # check that no directory/files were created
    engrave_output_path = Path(temp_path) / "output" / "engrave"
    assert (
        not engrave_output_path.exists()
    ), "Engrave directory should'nt have been created."

    if engrave_output_path.exists():
        svg_files = list(engrave_output_path.glob("*.svg"))
        assert len(svg_files) == 0, "No QR Code should have been generated."
