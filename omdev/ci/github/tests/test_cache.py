# ruff: noqa: PT009
import unittest

from ..cache import GithubV1CacheShellClient


class TestClient(unittest.TestCase):
    def test_client(self) -> None:
        client = GithubV1CacheShellClient(
            base_url='https://githubcache/',
            auth_token='DUMMY_AUTH_TOKEN',  # noqa
        )

        get_curl_cmd = client.build_get_curl_cmd('foo')

        print(get_curl_cmd)
