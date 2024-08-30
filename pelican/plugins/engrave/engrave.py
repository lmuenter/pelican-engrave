import logging
import os
import shutil

from .engraver import QRCodeEngraver

from pelican import signals

logger = logging.getLogger(__name__)

IMAGE_DIR = "images"
BASE_DIR = "engrave"

def cleanup_engrave_directory(pelican):
    """Clears engrave directory at build start"""
    engrave_path = os.path.join(pelican.settings["OUTPUT_PATH"], "images", "engrave")
    if os.path.exists(engrave_path):
        shutil.rmtree(engrave_path)
        os.makedirs(engrave_path)
        logger.info(f"Cleaned up {engrave_path}")

def construct_output_path(settings, slug):
    output_dir = os.path.join(settings["OUTPUT_PATH"], IMAGE_DIR, BASE_DIR)
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"{slug}_qrcode.svg")

def process_content(content):
    if content._content is None or not content.url:
        return

    site_url = content.settings.get("SITEURL", "").rstrip("/")
    full_url = f"{site_url}/{content.url.strip('/')}"

    qr_engraver = QRCodeEngraver()

    qr_image = qr_engraver.engrave(full_url)

    if qr_image:
        qr_image_path = construct_output_path(content.settings, content.slug)
        qr_image.save(qr_image_path)

        relative_image_path = os.path.relpath(
            qr_image_path, content.settings["OUTPUT_PATH"]
        )
        qrcode_url = f"{site_url}/{relative_image_path}"

        content.engrave_qrcode = qrcode_url
    else:
        logger.warning(f"No QR Code was generated for page {content.slug}")


def register():
    signals.initialized.connect(cleanup_engrave_directory)
    signals.content_object_init.connect(process_content)