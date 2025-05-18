import pytest

from ..grammars import rfc9116


@pytest.mark.parametrize('src', [
    """-----BEGIN PGP SIGNED MESSAGE-----\r\n"""
    """Hash: SHA512\r\n\r\n"""
    """Contact: charles@declaresub.com\r\n"""
    """Expires: 2023-03-14T00:00:00.000Z\r\n"""
    """-----BEGIN PGP SIGNATURE-----\r\n\r\n"""
    """iHUEARYKAB0WIQSsP2kEdoKDVFpSg6u3rK+YCkjapwUCYhjpQwAKCRC3rK+YCkjapyk2AP97ePaFUo8K8e1D+N+G6caqXjC/pwnZB+Wkk15AI+xstgD/VR5rOLKLZ7QFgKk5ohVS7qHou8Ux9cdodY2BRUIdrww==gFfQ\r\n"""  # noqa
    """-----END PGP SIGNATURE-----\r\n""",
])
def test_securitytxt_contact(src):
    assert rfc9116.Rule('body').parse_all(src)
