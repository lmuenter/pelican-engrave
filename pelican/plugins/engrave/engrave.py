import os
import shutil

import qrcode
from qrcode.image.svg import SvgImage

from pelican import signals

IMAGE_DIR = "images"
BASE_DIR = "engrave"


def generate_qr_code(
    data,
    image_factory,
    box_size=10,
    border=4,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
):
    qr = qrcode.QRCode(
        error_correction=error_correction,
        box_size=box_size,
        border=border,
        image_factory=image_factory,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def construct_output_path(settings, slug):
    output_dir = os.path.join(settings["OUTPUT_PATH"], IMAGE_DIR, BASE_DIR)
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"{slug}_qrcode.svg")


def cleanup_engrave_directory(pelican):
    """Clears engrave directory at build start"""
    engrave_path = os.path.join(pelican.settings["OUTPUT_PATH"], "images", "engrave")
    if os.path.exists(engrave_path):
        shutil.rmtree(engrave_path)
        os.makedirs(engrave_path)
        print(f"Cleaned up {engrave_path}")


def save_qr_image(image, path):
    image.save(path)


def append_qr_code_to_content(content, image_path):
    relative_image_path = os.path.relpath(image_path, content.settings["OUTPUT_PATH"])
    site_url = content.settings.get("SITEURL", "").rstrip("/")
    full_image_url = f"{site_url}/{relative_image_path}"

    content._content += (
        f'<img src="{full_image_url}" alt="QR Code" type="image/svg+xml">'
    )


def get_qr_code(content):
    if content._content is None or not content.url:
        return

    site_url = content.settings.get("SITEURL", "").rstrip("/")
    full_url = f"{site_url}/{content.url.strip('/')}"

    img = generate_qr_code(full_url, SvgImage)
    qr_image_path = construct_output_path(content.settings, content.slug)
    save_qr_image(img, qr_image_path)

    relative_image_path = os.path.relpath(
        qr_image_path, content.settings["OUTPUT_PATH"]
    )
    qrcode_url = f"{site_url}/{relative_image_path}"

    content.engrave_qrcode = qrcode_url


def register():
    signals.initialized.connect(cleanup_engrave_directory)
    signals.content_object_init.connect(get_qr_code)
