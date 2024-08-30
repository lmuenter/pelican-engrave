import pytest

from engrave.engraver.template import Engraver


def test_url_validation():
    """Assert validation of URLs prior to engraving."""
    engraver = Engraver()
    assert engraver._is_valid_url(
        "https://example.com"
    ), "Should be True for valid URL with https scheme"
    assert not engraver._is_valid_url(
        "http://example.com"
    ), "Should be False for http scheme when only https is allowed"
    assert not engraver._is_valid_url(
        "not_a_valid_url"
    ), "Should be False for incorrectly formatted URL"
