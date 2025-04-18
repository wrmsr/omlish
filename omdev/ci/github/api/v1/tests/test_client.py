# ruff: noqa: PT009
import unittest

from ..client import GithubCacheServiceV1Client


class TestClient(unittest.TestCase):
    def test_client(self) -> None:
        client = GithubCacheServiceV1Client(
            base_url='https://githubcache/',
            auth_token='DUMMY_AUTH_TOKEN',  # noqa
            key_suffix='test-suffix',
        )

        path = client.build_get_entry_url_path('foo-x', 'foo-')

        print(path)
