import qrcode
from qrcode.image.svg import SvgImage

from .template import Engraver


class QRCodeEngraver(Engraver):
    """Generate QR Code from given data."""

    def _create_image(self, data):
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

