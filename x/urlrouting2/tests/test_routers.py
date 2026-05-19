# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
import typing as ta
import unittest
import uuid

from ..converters import UrlRouteConverter
from ..routers import UrlRoute
from ..routers import UrlRouteMethodNotAllowedError
from ..routers import UrlRouteNotFoundError
from ..routers import UrlRouter
from ..routers import UrlRouterConfig
from ..routers import UrlRouteRedirectRequiredError
from ..routers import UrlRouteSlashStyle


class UrlRouterTest(unittest.TestCase):
    def test_static(self) -> None:
        router = UrlRouter([
            UrlRoute('/', 'index'),
            UrlRoute('/users', 'users'),
        ])

        self.assertEqual(router.match('/').endpoint, 'index')
        self.assertEqual(router.match('/users').endpoint, 'users')

        with self.assertRaises(UrlRouteNotFoundError):
            router.match('/missing')

    def test_dynamic(self) -> None:
        router = UrlRouter([
            UrlRoute('/users/{user_id:int}/profile', 'profile'),
        ])

        match = router.match('/users/42/profile')
        self.assertEqual(match.endpoint, 'profile')
        self.assertEqual(match.values, {'user_id': 42})

        with self.assertRaises(UrlRouteNotFoundError):
            router.match('/users/abc/profile')

    def test_static_precedence(self) -> None:
        router = UrlRouter([
            UrlRoute('/users/{user_id}', 'user'),
            UrlRoute('/users/me', 'me'),
        ])

        self.assertEqual(router.match('/users/me').endpoint, 'me')

    def test_mixed_segment(self) -> None:
        router = UrlRouter([
            UrlRoute('/v{major:int}.{minor:int}', 'version'),
        ])

        match = router.match('/v1.2')
        self.assertEqual(match.values, {'major': 1, 'minor': 2})

    def test_methods(self) -> None:
        router = UrlRouter([
            UrlRoute('/items', 'list', methods=frozenset(['GET'])),
            UrlRoute('/items', 'create', methods=frozenset(['POST'])),
        ])

        self.assertEqual(router.match('/items', method='GET').endpoint, 'list')
        self.assertEqual(router.match('/items', method='HEAD').endpoint, 'list')
        self.assertEqual(router.match('/items', method='POST').endpoint, 'create')

        with self.assertRaises(UrlRouteMethodNotAllowedError) as cm:
            router.match('/items', method='DELETE')

        self.assertEqual(cm.exception.allowed_methods, frozenset(['GET', 'HEAD', 'POST']))

    def test_path_converter(self) -> None:
        router = UrlRouter([
            UrlRoute('/static/{path:path}', 'static'),
        ])

        match = router.match('/static/a/b/c.txt')
        self.assertEqual(match.values, {'path': 'a/b/c.txt'})

    def test_slash_redirect(self) -> None:
        router = UrlRouter([
            UrlRoute('/users/', 'users'),
        ])

        with self.assertRaises(UrlRouteRedirectRequiredError) as cm:
            router.match('/users')

        self.assertEqual(cm.exception.redirect_path, '/users/')

    def test_slash_ignore(self) -> None:
        router = UrlRouter(
            [
                UrlRoute('/users/', 'users'),
            ],
            config=UrlRouterConfig(slash_style=UrlRouteSlashStyle.IGNORE),
        )

        self.assertEqual(router.match('/users').endpoint, 'users')

    def test_merge_slashes(self) -> None:
        router = UrlRouter(
            [
                UrlRoute('/users/list', 'users'),
            ],
            config=UrlRouterConfig(merge_slashes=True),
        )

        self.assertEqual(router.match('/users//list').endpoint, 'users')

    def test_build(self) -> None:
        router = UrlRouter([
            UrlRoute('/users/{user_id:int}/profile', 'profile', name='profile'),
        ])

        self.assertEqual(router.build('profile', {'user_id': 42}), '/users/42/profile')
        self.assertEqual(router.build('profile', {'user_id': '42'}), '/users/42/profile')

    def test_uuid(self) -> None:
        value = uuid.UUID('2b5b0911-fdcf-4dd2-921b-28ace88db8a0')
        router = UrlRouter([
            UrlRoute('/objects/{value:uuid}', 'object'),
        ])

        match = router.match('/objects/2b5b0911-fdcf-4dd2-921b-28ace88db8a0')
        self.assertEqual(match.values, {'value': value})

    def test_custom_converter(self) -> None:
        class HexUrlRouteConverter(UrlRouteConverter):
            regex = r'[0-9a-f]+'

            def to_python(self, s: str) -> int:
                return int(s, 16)

            def to_url(self, v: ta.Any) -> str:
                return format(int(v), 'x')

        router = UrlRouter(
            [
                UrlRoute('/colors/{value:hex}', 'color', name='color'),
            ],
            converters={'hex': HexUrlRouteConverter},
        )

        self.assertEqual(router.match('/colors/ff').values, {'value': 255})
        self.assertEqual(router.build('color', {'value': 255}), '/colors/ff')

    def test_query_is_ignored(self) -> None:
        router = UrlRouter([
            UrlRoute('/users/{user_id:int}', 'user'),
        ])

        match = router.match('/users/42?q=x')
        self.assertEqual(match.values, {'user_id': 42})


if __name__ == '__main__':
    unittest.main()

