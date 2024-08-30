import os
from tempfile import TemporaryDirectory
import pytest
from pelican import Pelican
from pelican.settings import read_settings
from pathlib import Path


@pytest.fixture
def pelican_environment():
    with TemporaryDirectory() as tempdir:
        cwd = os.path.dirname(os.path.abspath(__file__))
        temp_path = os.path.abspath(tempdir)
        settings = read_settings(override={
            'SITEURL': "https://example.com",
            'PATH': temp_path,
            'OUTPUT_PATH': os.path.join(temp_path, 'output'),
            'PLUGIN_PATHS': ['../../'],
            'PLUGINS': ['engrave'],
        })
        pelican = Pelican(settings=settings)
        yield pelican, temp_path

@pytest.fixture
def create_article(pelican_environment):
    pelican, temp_path = pelican_environment
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
def create_previous_qrcodes(pelican_environment, num_dummy_files=5):
    _, temp_path = pelican_environment
    engrave_path = Path(temp_path) / 'output' / 'images' / 'engrave'
    if not os.path.exists(engrave_path):
        os.makedirs(engrave_path)
    for i in range(num_dummy_files):
        dummy_file_path = engrave_path / f"dummy_{i}.svg"
        with open(dummy_file_path, "w") as f:
            f.write("Dummy QR code content")


def test_plugin_functionality(create_previous_qrcodes, create_article, pelican_environment):
    pelican, temp_path = pelican_environment
    engrave_output_path = Path(temp_path) / 'output' / 'images' / 'engrave'
    article_path = create_article

    pelican.run()

    # check dir structure
    assert engrave_output_path.exists(), "Output directory was not created."

    # list all svg files
    svg_files = list(engrave_output_path.glob('*.svg'))
    assert len(svg_files) > 0, "Engrave dir should not be empty."

    # check qrcode correctness
    article_name = "test-article"
    svg_with_article_name = any(article_name in file.name for file in svg_files)
    assert svg_with_article_name, f"No SVG file found for article name {article_name}."
