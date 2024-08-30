import logging
import os
import shutil

from pelican import signals

from .engraver import QRCodeEngraver

logger = logging.getLogger(__name__)
ENGRAVE_DIR = "engrave"


def cleanup_engrave_directory(pelican):
    """Clear engrave directory before building."""
    if not pelican.settings.get("SITEURL"):
        logger.warning("SITEURL is not set. QR code generation is aborted.")
        return

    # clean directory tree for previous contents of engrave dir
    engrave_path = os.path.join(pelican.settings["OUTPUT_PATH"], ENGRAVE_DIR)
    if os.path.exists(engrave_path):
        shutil.rmtree(engrave_path)

    # recreate engrave directory
    os.makedirs(engrave_path, exist_ok=True)
    logger.info(f"Cleaned up {engrave_path}")


def construct_output_path(settings, slug):
    """Construct output path for QR code SVG."""
    output_dir = os.path.join(settings["OUTPUT_PATH"], ENGRAVE_DIR)
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"{slug}_qrcode.svg")


def process_content(content):
    """Process content to generate and save QR code."""
    site_url = content.settings.get("SITEURL")
    if not site_url:
        logger.warning(
            "SITEURL is not set. Skipping QR code generation for all content."
        )
        return

    full_url = f"{site_url.rstrip('/')}/{content.url.strip('/')}"
    qr_engraver = QRCodeEngraver()
    qr_image = qr_engraver.engrave(full_url)

    if qr_image:
        qr_image_path = construct_output_path(content.settings, content.slug)
        qr_image.save(qr_image_path)
        relative_image_path = os.path.relpath(
            qr_image_path, content.settings["OUTPUT_PATH"]
        )
        content.engrave_qrcode = f"{site_url}/{relative_image_path}"
    else:
        logger.warning(f"No QR Code was generated for page {content.slug}")


def register():
    """Register plugin hooks."""
    signals.initialized.connect(cleanup_engrave_directory)
    signals.content_object_init.connect(process_content)
