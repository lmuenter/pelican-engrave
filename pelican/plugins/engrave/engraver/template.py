import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class Engraver:
    """Generate images based on provided data.

    Base class for other engravers. Provides URL validation, schema validation.

    Attributes
    ----------
    url (str): A valid URL to be engraved into an image.
    allowed_schemes (str): Subdirectory within `image_dir` for storing generated images.

    """

    def __init__(self, allowed_schemes=["https"]):
        """Initialise Engraver."""
        self.allowed_schemes = allowed_schemes

    def _is_valid_url(self, url):
        """Validate the URL's scheme and structure."""
        try:
            result = urlparse(url)
            # Ensure the scheme, netloc, and path are valid as per the requirements.
            is_valid = result.scheme in self.allowed_schemes and result.netloc

            if is_valid:
                return is_valid
            else:
                logger.info(f"Could not generate QR Code for {url}. Not a URL with expected structure.")
                return False
        except Exception as e:
            logger.error(f"Invalid URL: {url}, Error: {e}")
            return False

    def engrave(self, data):
        """Generate image from URL."""
        if self._is_valid_url(data):
            return self._create_image(data)
        return None

    def _create_image(self, data):
        raise NotImplementedError("Subclasses must implement this method.")
