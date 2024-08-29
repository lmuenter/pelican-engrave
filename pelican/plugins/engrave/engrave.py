import logging
import os
import shutil

import qrcode
from qrcode.image.svg import SvgImage

from pelican import signals

logger = logging.getLogger(__name__)


class Engraver:
    """Generate images based on provided data.

    Attributes
    ----------
    image_dir (str): Directory within output path where images are stored.
    base_dir (str): Subdirectory within `image_dir` for storing generated images.

    """

    def __init__(self, image_dir, base_dir):
        """Initialise Engraver with input arguments."""
        self.image_dir = image_dir
        self.base_dir = base_dir

    def engrave(self, data):
        """Generate image from data. Must be implemented by individual Engravers."""
        raise NotImplementedError("Engravers must implement this method!")

    def _construct_output_path(self, settings, slug):
        output_dir = os.path.join(
            settings["OUTPUT_PATH"], self.image_dir, self.base_dir
        )
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, f"{slug}_code.svg")

    def _cleanup_directory(self, pelican):
        path = os.path.join(
            pelican.settings["OUTPUT_PATH"], self.image_dir, self.base_dir
        )
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
        logger.info(f"Cleaned up {path}")


class QRCodeEngraver(Engraver):
    """Generate QR Code from given data."""

    def engrave(self, data):
        """Generate QR  code from given data.

        Data
        ----------
        String data to be encoded as QR code.

        Returns
        -------
        An svg image object representing the QR Code of the given data.

        """
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
            image_factory=SvgImage,
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white")


class EngravePlugin:
    """Encode URLs as image representations.

    This plugin utilizes `Engraver` classes to encode URLs as image representations.
    Currently, it offers the generation of QRCode images in SVG format
    at a given location.

    The URL of the generated QRCode for each article can be accessed
    in the article context as the `engrave_qrcode` attribute.

    Attributes
    ----------
    engraver (Engraver): An `Engraver` instance for generating the image
        representation of a URL.

    """

    def __init__(self, engraver):
        """Initialise Plugin with an `Engraver`."""
        self.engraver = engraver

    def _save_engraved_image(self, image, path):
        image.save(path)

    def _append_engraved_image_to_content(self, content, image_path):
        relative_path = os.path.relpath(image_path, content.settings["OUTPUT_PATH"])
        site_url = content.settings.get("SITEURL", "").rstrip("/")
        full_image_url = f"{site_url}/{relative_path}"
        content._content += (
            f'<img src="{full_image_url}" alt="Engraved Image" type="image/svg+xml">'
        )

    def process_content(self, content):
        """Run the `Engraver` with Data."""
        if content._content is None or not content.url:
            return
        full_url = f'{content.settings.get("SITEURL", "").rstrip("/")}/{content.url.strip("/")}'
        engraved_image = self.engraver.engrave(full_url)
        engraved_image_path = self.engraver._construct_output_path(
            content.settings, content.slug
        )
        self._save_engraved_image(engraved_image, engraved_image_path)
        self._append_engraved_image_to_content(content, engraved_image_path)

    def register(self):
        """Register the Plugin with Pelican."""
        signals.initialized.connect(self.engraver._cleanup_directory)
        signals.content_object_init.connect(self.process_content)


qr_engraver = QRCodeEngraver(image_dir="images", base_dir="engrave")
plugin = EngravePlugin(qr_engraver)
plugin.register()
