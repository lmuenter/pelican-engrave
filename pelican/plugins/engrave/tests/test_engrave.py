import os
from tempfile import TemporaryDirectory
import pytest
from pelican import Pelican
from pelican.settings import read_settings
from pathlib import Path


@pytest.fixture
def temp_path():
    with TemporaryDirectory() as tempdir:
        yield os.path.abspath(tempdir)


@pytest.fixture
def create_article(temp_path):
    content_dir = Path(temp_path) / 'content'
    content_dir.mkdir(parents=True, exist_ok=True)

    article_content = """
Test Article
#############

:date: 2023-01-01
:category: Test

This is a test article content in reStructuredText format.
"""
    article_path = content_dir / "test-article.rst"
    article_path.write_text(article_content)
    return article_path


@pytest.fixture
def create_previous_qrcodes(temp_path, num_dummy_files=5):
    engrave_path = Path(temp_path) / 'output' / 'images' / 'engrave'
    engrave_path.mkdir(parents=True, exist_ok=True)
    for i in range(num_dummy_files):
        dummy_file_path = engrave_path / f"dummy_{i}.svg"
        dummy_file_path.write_text("Dummy QR code content")


def test_plugin_functionality(create_previous_qrcodes, create_article, temp_path):
    engrave_output_path = Path(temp_path) / 'output' / 'images' / 'engrave'
    svg_files = list(engrave_output_path.glob('*.svg'))
    print(svg_files)
    assert len(svg_files) == 5, "Engrave dir should contain 5 files of a simulated previous run"

    settings = read_settings(override={
        'SITEURL': "https://example.com",
        'PATH': temp_path,
        'OUTPUT_PATH': os.path.join(temp_path, 'output'),
        'PLUGIN_PATHS': ['../../'],
        'PLUGINS': ['engrave'],
    })
    pelican = Pelican(settings=settings)
    pelican.run()

    engrave_output_path = Path(temp_path) / 'output' / 'images' / 'engrave'

    # Check dir structure
    assert engrave_output_path.exists(), "Output directory was not created."

    # List all SVG files
    svg_files = list(engrave_output_path.glob('*.svg'))
    assert len(svg_files) == 1, "Engrave dir should have been cleaned prior to execution."

    # Check QR code correctness
    article_name = "test-article"
    svg_with_article_name = any(article_name in file.name for file in svg_files)
    assert svg_with_article_name, f"No SVG file found for article name {article_name}."
