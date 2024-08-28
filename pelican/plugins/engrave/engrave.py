import os
import qrcode
from qrcode.image.svg import SvgImage
from pelican import signals


IMAGE_DIR = "images"
BASE_DIR = "engrave"


def generate_qr_code(data, 
                     image_factory, 
                     box_size=10, 
                     border=4, 
                     error_correction=qrcode.constants.ERROR_CORRECT_L):
    qr = qrcode.QRCode(
        error_correction=error_correction,
        box_size=box_size,
        border=border,
        image_factory=image_factory
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def construct_output_path(settings, slug):
    output_dir = os.path.join(settings["OUTPUT_PATH"], IMAGE_DIR, BASE_DIR)
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"{slug}_qrcode.svg")


def save_qr_image(image, path):
    image.save(path)


def append_qr_code_to_content(content, image_path):
    content._content += f'<img src="{image_path}" alt="QR Code" type="image/svg+xml">'


def get_qr_code(content):
    if content._content is None or not content.url:
        return
    
    img = generate_qr_code(content.url, SvgImage)
    qr_image_path = construct_output_path(content.settings, content.slug)
    save_qr_image(img, qr_image_path)

    append_qr_code_to_content(content, qr_image_path)


def register():
    signals.content_written.connect(get_qr_code)
