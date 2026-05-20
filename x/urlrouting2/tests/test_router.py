# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
import typing as ta
import unittest
import uuid

from ..converters import UrlRouteConverter
from ..router import UrlRouter
from ..types import UrlRoute
from ..types import UrlRouteBuildError
from ..types import UrlRouteConflictError
from ..types import UrlRouteMethodNotAllowedError
from ..types import UrlRouteNotFoundError
from ..types import UrlRouteRedirectRequiredError
from ..types import UrlRouteSlashStyle


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
            config=UrlRouter.Config(slash_style=UrlRouteSlashStyle.IGNORE),
        )

        self.assertEqual(router.match('/users').endpoint, 'users')

    def test_merge_slashes(self) -> None:
        router = UrlRouter(
            [
                UrlRoute('/users/list', 'users'),
            ],
            config=UrlRouter.Config(merge_slashes=True),
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


    def test_match_metadata(self) -> None:
        router = UrlRouter([
            UrlRoute('/users/{user_id:int}', 'user'),
        ])

        match = router.match('/users/42?q=x')
        self.assertEqual(match.path, '/users/42')
        self.assertEqual(match.matched_path, '/users/42')
        self.assertEqual(match.metadata.query, 'q=x')

    def test_percent_decoding(self) -> None:
        router = UrlRouter([
            UrlRoute('/files/{name}', 'file'),
            UrlRoute('/static/a b', 'space'),
        ])

        self.assertEqual(router.match('/files/a%20b').values, {'name': 'a b'})
        self.assertEqual(router.match('/files/a%2Fb').values, {'name': 'a/b'})
        self.assertEqual(router.match('/static/a%20b').endpoint, 'space')

    def test_converter_args(self) -> None:
        router = UrlRouter([
            UrlRoute('/pages/{page:int(min=1,max=3)}', 'page', name='page'),
            UrlRoute('/langs/{lang:string(length=2)}', 'lang'),
            UrlRoute('/colors/{color:any(red,"dark blue")}', 'color'),
        ])

        self.assertEqual(router.match('/pages/2').values, {'page': 2})
        self.assertEqual(router.match('/langs/en').values, {'lang': 'en'})
        self.assertEqual(router.match('/colors/dark%20blue').values, {'color': 'dark blue'})

        with self.assertRaises(UrlRouteNotFoundError):
            router.match('/pages/4')
        with self.assertRaises(UrlRouteNotFoundError):
            router.match('/langs/eng')
        with self.assertRaises(UrlRouteBuildError):
            router.build('page', {'page': 4})

    def test_build_unknown_values(self) -> None:
        router = UrlRouter([
            UrlRoute('/users/{user_id:int}', 'user', name='user'),
        ])

        with self.assertRaises(UrlRouteBuildError):
            router.build('user', {'user_id': 42, 'q': 'x'})

        self.assertEqual(
            router.build('user', {'user_id': 42, 'q': 'x', 'tag': ['a', 'b']}, append_unknown=True),
            '/users/42?q=x&tag=a&tag=b',
        )

    def test_route_conflicts(self) -> None:
        with self.assertRaises(UrlRouteConflictError):
            UrlRouter([
                UrlRoute('/users/{user_id}', 'user'),
                UrlRoute('/users/{name}', 'user2'),
            ])

        UrlRouter([
            UrlRoute('/items', 'list', methods=frozenset(['GET'])),
            UrlRoute('/items', 'create', methods=frozenset(['POST'])),
        ])

        with self.assertRaises(UrlRouteConflictError):
            UrlRouter([
                UrlRoute('/users/{user_id}', 'user', name='user'),
                UrlRoute('/users/{user_id}/posts/{post_id}', 'post', name='user'),
            ])

    def test_strict_slashes(self) -> None:
        router = UrlRouter(
            [
                UrlRoute('/users/', 'users'),
            ],
            config=UrlRouter.Config(slash_style=UrlRouteSlashStyle.STRICT),
        )

        self.assertEqual(router.match('/users/').endpoint, 'users')
        with self.assertRaises(UrlRouteNotFoundError):
            router.match('/users')

    def test_query_is_ignored(self) -> None:
        router = UrlRouter([
            UrlRoute('/users/{user_id:int}', 'user'),
        ])

        match = router.match('/users/42?q=x')
        self.assertEqual(match.values, {'user_id': 42})

    def test_allowed_methods(self) -> None:
        router = UrlRouter([
            UrlRoute('/items', 'list', methods=frozenset(['GET'])),
            UrlRoute('/items', 'create', methods=frozenset(['POST'])),
        ])

        self.assertEqual(router.allowed_methods('/items'), frozenset(['GET', 'HEAD', 'POST']))
        self.assertEqual(router.allowed_methods('/missing'), frozenset())

    def test_build_string_escapes_slash(self) -> None:
        router = UrlRouter([UrlRoute('/files/{name}', 'file', name='f')])

        built = router.build('f', {'name': 'a/b'})
        self.assertEqual(built, '/files/a%2Fb')

        match = router.match(built)
        self.assertEqual(match.values, {'name': 'a/b'})

    def test_build_int_unsigned_rejects_negative(self) -> None:
        router = UrlRouter([UrlRoute('/items/{n:int}', 'item', name='it')])

        with self.assertRaises(UrlRouteBuildError):
            router.build('it', {'n': -5})

        signed_router = UrlRouter([UrlRoute('/items/{n:int(signed=True)}', 'item', name='it')])
        self.assertEqual(signed_router.build('it', {'n': -5}), '/items/-5')

    def test_build_float_unsigned_rejects_negative(self) -> None:
        router = UrlRouter([UrlRoute('/x/{v:float}', 'x', name='x')])

        with self.assertRaises(UrlRouteBuildError):
            router.build('x', {'v': -1.5})

        signed_router = UrlRouter([UrlRoute('/x/{v:float(signed=True)}', 'x', name='x')])
        self.assertEqual(signed_router.build('x', {'v': -1.5}), '/x/-1.5')

    def test_build_defaults_mismatched_user_value(self) -> None:
        router = UrlRouter([UrlRoute('/x/{a}', 'e', name='n', defaults={'unused': 'default_val'})])

        # User-provided value matches default - silently consumed.
        self.assertEqual(router.build('n', {'a': 'foo', 'unused': 'default_val'}), '/x/foo')

        # User-provided value differs from default - raises without append_unknown.
        with self.assertRaises(UrlRouteBuildError):
            router.build('n', {'a': 'foo', 'unused': 'OTHER'})

        # With append_unknown, the mismatched value lands in the query string.
        self.assertEqual(
            router.build('n', {'a': 'foo', 'unused': 'OTHER'}, append_unknown=True),
            '/x/foo?unused=OTHER',
        )

    def test_mini_yelp_webapp_routes(self) -> None:
        photo_id = uuid.UUID('2b5b0911-fdcf-4dd2-921b-28ace88db8a0')
        router = UrlRouter([
            UrlRoute('/', 'home', methods=frozenset(['GET']), name='home'),
            UrlRoute('/search', 'search', methods=frozenset(['GET']), name='search'),

            UrlRoute('/businesses', 'business_list', methods=frozenset(['GET']), name='business_list'),
            UrlRoute('/businesses', 'business_create', methods=frozenset(['POST'])),
            UrlRoute('/businesses/new', 'business_new', methods=frozenset(['GET'])),
            UrlRoute('/businesses/{business_id:int}', 'business_detail', methods=frozenset(['GET']), name='business'),
            UrlRoute('/businesses/{business_id:int}', 'business_update', methods=frozenset(['PATCH'])),
            UrlRoute('/businesses/{business_id:int}/edit', 'business_edit', methods=frozenset(['GET'])),
            UrlRoute('/businesses/{business_id:int}/photos', 'business_photos', methods=frozenset(['GET'])),
            UrlRoute('/businesses/{business_id:int}/photos', 'business_photo_create', methods=frozenset(['POST'])),
            UrlRoute(
                '/businesses/{business_id:int}/photos/{photo_id:uuid}',
                'business_photo',
                methods=frozenset(['GET']),
                name='business_photo',
            ),
            UrlRoute(
                '/businesses/{business_id:int}/reviews',
                'business_reviews',
                methods=frozenset(['GET']),
                name='business_reviews',
            ),
            UrlRoute('/businesses/{business_id:int}/reviews', 'business_review_create', methods=frozenset(['POST'])),
            UrlRoute(
                '/businesses/{business_id:int}/reviews/{review_id:int}',
                'business_review',
                methods=frozenset(['GET']),
                name='business_review',
            ),
            UrlRoute(
                '/businesses/{business_id:int}/reviews/{review_id:int}',
                'business_review_delete',
                methods=frozenset(['DELETE']),
            ),
            UrlRoute(
                '/businesses/{business_id:int}/menu/{path:path}',
                'business_menu_file',
                methods=frozenset(['GET']),
                name='business_menu_file',
            ),

            UrlRoute('/users', 'user_list', methods=frozenset(['GET']), name='user_list'),
            UrlRoute('/users/me', 'current_user', methods=frozenset(['GET']), name='current_user'),
            UrlRoute('/users/{user_id:int}', 'user_profile', methods=frozenset(['GET']), name='user'),
            UrlRoute('/users/{user_id:int}/reviews', 'user_reviews', methods=frozenset(['GET']), name='user_reviews'),
            UrlRoute('/users/{user_id:int}/followers', 'user_followers', methods=frozenset(['GET'])),

            UrlRoute(
                '/categories/{category:any(restaurants,bars,cafes)}',
                'category',
                methods=frozenset(['GET']),
                name='category',
            ),
            UrlRoute(
                '/admin/reports/{year:int(min=2020,max=2030)}/{month:int(min=1,max=12)}',
                'admin_report',
                methods=frozenset(['GET']),
                name='admin_report',
            ),
        ])

        self.assertEqual(router.match('/', method='GET').endpoint, 'home')
        self.assertEqual(router.match('/businesses', method='GET').endpoint, 'business_list')
        self.assertEqual(router.match('/businesses', method='POST').endpoint, 'business_create')
        self.assertEqual(router.match('/businesses/new', method='GET').endpoint, 'business_new')

        business_match = router.match('/businesses/42?ref=nearby', method='GET')
        self.assertEqual(business_match.endpoint, 'business_detail')
        self.assertEqual(business_match.values, {'business_id': 42})
        self.assertEqual(business_match.metadata.query, 'ref=nearby')

        self.assertEqual(router.match('/businesses/42', method='PATCH').endpoint, 'business_update')
        self.assertEqual(router.match('/businesses/42/photos', method='POST').endpoint, 'business_photo_create')
        self.assertEqual(
            router.match('/businesses/42/photos/2b5b0911-fdcf-4dd2-921b-28ace88db8a0', method='GET').values,
            {'business_id': 42, 'photo_id': photo_id},
        )
        self.assertEqual(
            router.match('/businesses/42/reviews/7', method='DELETE').endpoint,
            'business_review_delete',
        )
        self.assertEqual(
            router.match('/businesses/42/menu/dinner/spring%20specials.pdf', method='GET').values,
            {'business_id': 42, 'path': 'dinner/spring specials.pdf'},
        )

        self.assertEqual(router.match('/users/me', method='GET').endpoint, 'current_user')
        self.assertEqual(router.match('/users/10', method='GET').values, {'user_id': 10})
        self.assertEqual(router.match('/users/10/reviews', method='HEAD').endpoint, 'user_reviews')
        self.assertEqual(router.match('/categories/bars', method='GET').values, {'category': 'bars'})
        self.assertEqual(router.match('/admin/reports/2026/5', method='GET').values, {'year': 2026, 'month': 5})

        self.assertEqual(router.allowed_methods('/businesses'), frozenset(['GET', 'HEAD', 'POST']))
        self.assertEqual(router.allowed_methods('/businesses/42'), frozenset(['GET', 'HEAD', 'PATCH']))
        self.assertEqual(router.allowed_methods('/businesses/42/reviews/7'), frozenset(['DELETE', 'GET', 'HEAD']))

        with self.assertRaises(UrlRouteMethodNotAllowedError):
            router.match('/businesses/42/reviews', method='PATCH')
        with self.assertRaises(UrlRouteNotFoundError):
            router.match('/categories/hotels', method='GET')
        with self.assertRaises(UrlRouteNotFoundError):
            router.match('/admin/reports/2019/1', method='GET')
        with self.assertRaises(UrlRouteNotFoundError):
            router.match('/admin/reports/2026/13', method='GET')

        self.assertEqual(router.build('business', {'business_id': 42}), '/businesses/42')
        self.assertEqual(
            router.build('business_photo', {'business_id': 42, 'photo_id': photo_id}),
            '/businesses/42/photos/2b5b0911-fdcf-4dd2-921b-28ace88db8a0',
        )
        self.assertEqual(
            router.build('business_review', {'business_id': 42, 'review_id': 7}),
            '/businesses/42/reviews/7',
        )
        self.assertEqual(
            router.build('business_menu_file', {'business_id': 42, 'path': 'dinner/spring specials.pdf'}),
            '/businesses/42/menu/dinner/spring%20specials.pdf',
        )
        self.assertEqual(router.build('user', {'user_id': 10}), '/users/10')
        self.assertEqual(router.build('category', {'category': 'cafes'}), '/categories/cafes')
        self.assertEqual(router.build('admin_report', {'year': 2026, 'month': 5}), '/admin/reports/2026/5')
        self.assertEqual(
            router.build('search', {'q': 'coffee', 'near': 'SoMa'}, append_unknown=True),
            '/search?q=coffee&near=SoMa',
        )
