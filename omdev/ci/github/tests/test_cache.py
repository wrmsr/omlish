# ruff: noqa: PT009
import unittest

from ..cache import GithubCacheServiceV1ShellClient


class TestClient(unittest.TestCase):
    def test_client(self) -> None:
        client = GithubCacheServiceV1ShellClient(
            base_url='https://githubcache/',
            auth_token='DUMMY_AUTH_TOKEN',  # noqa
            key_suffix='test-suffix',
        )

        curl_cmd = client.build_get_entry_curl_cmd('foo')

        print(curl_cmd)
