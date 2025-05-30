import gc
import typing as ta
import uuid

import pytest

from ..converters import BaseConverter
from ..converters import UnicodeConverter
from ..exceptions import BuildError
from ..exceptions import MethodNotAllowed
from ..exceptions import NotFound
from ..exceptions import RequestRedirect
from ..exceptions import WebsocketMismatch
from ..map import Map
from ..rules import EndpointPrefix
from ..rules import Rule
from ..rules import RuleTemplate
from ..rules import Subdomain
from ..rules import Submount
from ..rules import parse_converter_args
from ..utils import MultiDict


def test_basic_routing():
    m = Map([
        Rule('/', endpoint='index'),
        Rule('/foo', endpoint='foo'),
        Rule('/bar/', endpoint='bar'),
        Rule('/ws', endpoint='ws', websocket=True),
        Rule('/', endpoint='indexws', websocket=True),
    ])
    adapter = m.bind('example.org', '/')
    assert adapter.match('/') == ('index', {})
    assert adapter.match('/foo') == ('foo', {})
    assert adapter.match('/bar/') == ('bar', {})
    pytest.raises(RequestRedirect, lambda: adapter.match('/bar'))
    pytest.raises(NotFound, lambda: adapter.match('/blub'))

    adapter = m.bind('example.org', '/', url_scheme='ws')
    assert adapter.match('/') == ('indexws', {})

    adapter = m.bind('example.org', '/test')
    with pytest.raises(RequestRedirect) as excinfo:
        adapter.match('/bar')
    assert excinfo.value.new_url == 'http://example.org/test/bar/'

    adapter = m.bind('example.org', '/')
    with pytest.raises(RequestRedirect) as excinfo:
        adapter.match('/bar')
    assert excinfo.value.new_url == 'http://example.org/bar/'

    adapter = m.bind('example.org', '/')
    with pytest.raises(RequestRedirect) as excinfo:
        adapter.match('/bar', query_args={'aha': 'muhaha'})
    assert excinfo.value.new_url == 'http://example.org/bar/?aha=muhaha'

    adapter = m.bind('example.org', '/')
    with pytest.raises(RequestRedirect) as excinfo:
        adapter.match('/bar', query_args='aha=muhaha')
    assert excinfo.value.new_url == 'http://example.org/bar/?aha=muhaha'

    adapter = m.bind('example.org', '/ws', url_scheme='wss')
    assert adapter.match('/ws', websocket=True) == ('ws', {})
    with pytest.raises(WebsocketMismatch):
        adapter.match('/ws', websocket=False)
    with pytest.raises(WebsocketMismatch):
        adapter.match('/foo', websocket=True)


def test_merge_slashes_match():
    url_map = Map([
        Rule('/no/tail', endpoint='no_tail'),
        Rule('/yes/tail/', endpoint='yes_tail'),
        Rule('/with/<path:path>', endpoint='with_path'),
        Rule('/no//merge', endpoint='no_merge', merge_slashes=False),
        Rule('/no/merging', endpoint='no_merging', merge_slashes=False),
    ])
    adapter = url_map.bind('localhost', '/')

    with pytest.raises(RequestRedirect) as excinfo:
        adapter.match('/no//tail')

    assert excinfo.value.new_url.endswith('/no/tail')

    with pytest.raises(RequestRedirect) as excinfo:
        adapter.match('/yes//tail')

    assert excinfo.value.new_url.endswith('/yes/tail/')

    with pytest.raises(RequestRedirect) as excinfo:
        adapter.match('/yes/tail//')

    assert excinfo.value.new_url.endswith('/yes/tail/')

    assert adapter.match('/no/tail')[0] == 'no_tail'
    assert adapter.match('/yes/tail/')[0] == 'yes_tail'

    _, rv = adapter.match('/with/http://example.com/')
    assert rv['path'] == 'http://example.com/'
    _, rv = adapter.match('/with/x//y')
    assert rv['path'] == 'x//y'

    assert adapter.match('/no//merge')[0] == 'no_merge'

    assert adapter.match('/no/merging')[0] == 'no_merging'
    pytest.raises(NotFound, lambda: adapter.match('/no//merging'))


@pytest.mark.parametrize(
    ('path', 'expected'),
    [('/merge/%//path', '/merge/%25/path'), ('/merge//st/path', '/merge/st/path')],
)
def test_merge_slash_encoding(path, expected):
    """This test is to make sure URLs are not double-encoded
    when a redirect is thrown with `merge_slash = True`"""
    url_map = Map([
        Rule('/merge/<some>/path'),
    ])
    adapter = url_map.bind('localhost', '/')

    with pytest.raises(RequestRedirect) as excinfo:
        adapter.match(path)

    assert excinfo.value.new_url.endswith(expected)


def test_merge_slashes_build():
    url_map = Map([
        Rule('/yes//merge', endpoint='yes_merge'),
        Rule('/no//merge', endpoint='no_merge', merge_slashes=False),
    ])
    adapter = url_map.bind('localhost', '/')
    assert adapter.build('yes_merge') == '/yes/merge'
    assert adapter.build('no_merge') == '/no//merge'


def test_strict_slashes_redirect():
    m = Map([
        Rule('/bar/', endpoint='get', methods=['GET']),
        Rule('/bar', endpoint='post', methods=['POST']),
        Rule('/foo/', endpoint='foo', methods=['POST']),
        Rule('/<path:var>/', endpoint='path', methods=['GET']),
    ])
    adapter = m.bind('example.org', '/')

    # Check if the actual routes works
    assert adapter.match('/bar/', method='GET') == ('get', {})
    assert adapter.match('/bar', method='POST') == ('post', {})
    assert adapter.match('/abc/', method='GET') == ('path', {'var': 'abc'})

    # Check if exceptions are correct
    pytest.raises(RequestRedirect, adapter.match, '/bar', method='GET')
    pytest.raises(MethodNotAllowed, adapter.match, '/bar/', method='POST')
    with pytest.raises(RequestRedirect) as error_info:
        adapter.match('/foo', method='POST')
    assert error_info.value.code == 308
    with pytest.raises(RequestRedirect) as error_info:
        adapter.match('/abc', method='GET')
    assert error_info.value.new_url == 'http://example.org/abc/'

    # Check differently defined order
    m = Map([
        Rule('/bar', endpoint='post', methods=['POST']),
        Rule('/bar/', endpoint='get', methods=['GET']),
    ])
    adapter = m.bind('example.org', '/')

    # Check if the actual routes works
    assert adapter.match('/bar/', method='GET') == ('get', {})
    assert adapter.match('/bar', method='POST') == ('post', {})

    # Check if exceptions are correct
    pytest.raises(RequestRedirect, adapter.match, '/bar', method='GET')
    pytest.raises(MethodNotAllowed, adapter.match, '/bar/', method='POST')

    # Check what happens when only slash route is defined
    m = Map([Rule('/bar/', endpoint='get', methods=['GET'])])
    adapter = m.bind('example.org', '/')

    # Check if the actual routes works
    assert adapter.match('/bar/', method='GET') == ('get', {})

    # Check if exceptions are correct
    pytest.raises(RequestRedirect, adapter.match, '/bar', method='GET')
    pytest.raises(MethodNotAllowed, adapter.match, '/bar/', method='POST')


def test_strict_slashes_leaves_dont_consume():
    # See issue #1074
    m = Map(
        [
            Rule('/path1', endpoint='leaf'),
            Rule('/path1/', endpoint='branch'),
            Rule('/path2', endpoint='leaf', strict_slashes=False),
            Rule('/path2/', endpoint='branch'),
            Rule('/path3', endpoint='leaf'),
            Rule('/path3/', endpoint='branch', strict_slashes=False),
            Rule('/path4', endpoint='leaf', strict_slashes=False),
            Rule('/path4/', endpoint='branch', strict_slashes=False),
            Rule('/path5', endpoint='leaf'),
        ],
        strict_slashes=False,
    )

    adapter = m.bind('example.org', '/')

    assert adapter.match('/path1', method='GET') == ('leaf', {})
    assert adapter.match('/path1/', method='GET') == ('branch', {})
    assert adapter.match('/path2', method='GET') == ('leaf', {})
    assert adapter.match('/path2/', method='GET') == ('branch', {})
    assert adapter.match('/path3', method='GET') == ('leaf', {})
    assert adapter.match('/path3/', method='GET') == ('branch', {})
    assert adapter.match('/path4', method='GET') == ('leaf', {})
    assert adapter.match('/path4/', method='GET') == ('branch', {})
    assert adapter.match('/path5/', method='GET') == ('leaf', {})


def test_basic_building():
    m = Map([
        Rule('/', endpoint='index'),
        Rule('/foo', endpoint='foo'),
        Rule('/bar/<baz>', endpoint='bar'),
        Rule('/bar/<int:bazi>', endpoint='bari'),
        Rule('/bar/<float:bazf>', endpoint='barf'),
        Rule('/bar/<path:bazp>', endpoint='barp'),
        Rule('/hehe', endpoint='blah', subdomain='blah'),
        Rule('/ws', endpoint='ws', websocket=True),
    ])
    adapter = m.bind('example.org', '/', subdomain='blah')

    assert adapter.build('index', {}) == 'http://example.org/'
    assert adapter.build('foo', {}) == 'http://example.org/foo'
    assert adapter.build('bar', {'baz': 'blub'}) == 'http://example.org/bar/blub'
    assert adapter.build('bari', {'bazi': 50}) == 'http://example.org/bar/50'
    assert adapter.build('barf', {'bazf': 0.815}) == 'http://example.org/bar/0.815'
    assert adapter.build('barp', {'bazp': 'la/di'}) == 'http://example.org/bar/la/di'
    assert adapter.build('blah', {}) == '/hehe'
    pytest.raises(BuildError, lambda: adapter.build('urks'))

    adapter = m.bind('example.org', '/test', subdomain='blah')
    assert adapter.build('index', {}) == 'http://example.org/test/'
    assert adapter.build('foo', {}) == 'http://example.org/test/foo'
    assert adapter.build('bar', {'baz': 'blub'}) == 'http://example.org/test/bar/blub'
    assert adapter.build('bari', {'bazi': 50}) == 'http://example.org/test/bar/50'
    assert adapter.build('barf', {'bazf': 0.815}) == 'http://example.org/test/bar/0.815'
    assert adapter.build('barp', {'bazp': 'la/di'}) == 'http://example.org/test/bar/la/di'
    assert adapter.build('blah', {}) == '/test/hehe'

    adapter = m.bind('example.org')
    assert adapter.build('foo', {}) == '/foo'
    assert adapter.build('foo', {}, force_external=True) == 'http://example.org/foo'
    adapter = m.bind('example.org', url_scheme='')
    assert adapter.build('foo', {}) == '/foo'
    assert adapter.build('foo', {}, force_external=True) == '//example.org/foo'
    assert (
        adapter.build('foo', {}, url_scheme='https', force_external=True)
        == 'https://example.org/foo'
    )

    adapter = m.bind('example.org', url_scheme='ws')
    assert adapter.build('ws', {}) == 'ws://example.org/ws'
    assert adapter.build('foo', {}, force_external=True) == 'http://example.org/foo'
    assert adapter.build('foo', {}) == '/foo'
    assert adapter.build('ws', {}, url_scheme='https') == 'wss://example.org/ws'


def test_long_build():
    long_args = {f'v{x}': x for x in range(10000)}
    m = Map([
        Rule(
            ''.join(f'/<{k}>' for k in long_args),
            endpoint='bleep',
            build_only=True,
        ),
    ])
    adapter = m.bind('localhost', '/')
    url = f"{adapter.build('bleep', long_args)}/"
    for v in long_args.values():
        assert f'/{v}' in url


def test_defaults():
    m = Map([
        Rule('/foo/', defaults={'page': 1}, endpoint='foo'),
        Rule('/foo/<int:page>', endpoint='foo'),
    ])
    adapter = m.bind('example.org', '/')

    assert adapter.match('/foo/') == ('foo', {'page': 1})
    pytest.raises(RequestRedirect, lambda: adapter.match('/foo/1'))
    assert adapter.match('/foo/2') == ('foo', {'page': 2})
    assert adapter.build('foo', {}) == '/foo/'
    assert adapter.build('foo', {'page': 1}) == '/foo/'
    assert adapter.build('foo', {'page': 2}) == '/foo/2'


def test_negative():
    m = Map([
        Rule('/foos/<int(signed=True):page>', endpoint='foos'),
        Rule('/bars/<float(signed=True):page>', endpoint='bars'),
        Rule('/foo/<int:page>', endpoint='foo'),
        Rule('/bar/<float:page>', endpoint='bar'),
    ])
    adapter = m.bind('example.org', '/')

    assert adapter.match('/foos/-2') == ('foos', {'page': -2})
    assert adapter.match('/foos/-50') == ('foos', {'page': -50})
    assert adapter.match('/bars/-2.0') == ('bars', {'page': -2.0})
    assert adapter.match('/bars/-0.185') == ('bars', {'page': -0.185})

    # Make sure signed values are rejected in unsigned mode
    pytest.raises(NotFound, lambda: adapter.match('/foo/-2'))
    pytest.raises(NotFound, lambda: adapter.match('/foo/-50'))
    pytest.raises(NotFound, lambda: adapter.match('/bar/-0.185'))
    pytest.raises(NotFound, lambda: adapter.match('/bar/-2.0'))


def test_greedy():
    m = Map([
        Rule('/foo', endpoint='foo'),
        Rule('/<path:bar>', endpoint='bar'),
        Rule('/<path:bar>/<path:blub>', endpoint='bar'),
    ])
    adapter = m.bind('example.org', '/')

    assert adapter.match('/foo') == ('foo', {})
    assert adapter.match('/blub') == ('bar', {'bar': 'blub'})
    assert adapter.match('/he/he') == ('bar', {'bar': 'he', 'blub': 'he'})

    assert adapter.build('foo', {}) == '/foo'
    assert adapter.build('bar', {'bar': 'blub'}) == '/blub'
    assert adapter.build('bar', {'bar': 'blub', 'blub': 'bar'}) == '/blub/bar'


def test_path():
    m = Map([
        Rule('/', defaults={'name': 'FrontPage'}, endpoint='page'),
        Rule('/Special', endpoint='special'),
        Rule('/<int:year>', endpoint='year'),
        Rule('/<path:name>:foo', endpoint='foopage'),
        Rule('/<path:name>:<path:name2>', endpoint='twopage'),
        Rule('/<path:name>', endpoint='page'),
        Rule('/<path:name>/edit', endpoint='editpage'),
        Rule('/<path:name>/silly/<path:name2>', endpoint='sillypage'),
        Rule('/<path:name>/silly/<path:name2>/edit', endpoint='editsillypage'),
        Rule('/Talk:<path:name>', endpoint='talk'),
        Rule('/User:<username>', endpoint='user'),
        Rule('/User:<username>/<path:name>', endpoint='userpage'),
        Rule('/User:<username>/comment/<int:id>-<int:replyId>', endpoint='usercomment'),
        Rule('/Files/<path:file>', endpoint='files'),
        Rule('/<admin>/<manage>/<things>', endpoint='admin'),
    ])
    adapter = m.bind('example.org', '/')

    assert adapter.match('/') == ('page', {'name': 'FrontPage'})
    pytest.raises(RequestRedirect, lambda: adapter.match('/FrontPage'))
    assert adapter.match('/Special') == ('special', {})
    assert adapter.match('/2007') == ('year', {'year': 2007})
    assert adapter.match('/Some:foo') == ('foopage', {'name': 'Some'})
    assert adapter.match('/Some:bar') == ('twopage', {'name': 'Some', 'name2': 'bar'})
    assert adapter.match('/Some/Page') == ('page', {'name': 'Some/Page'})
    assert adapter.match('/Some/Page/edit') == ('editpage', {'name': 'Some/Page'})
    assert adapter.match('/Foo/silly/bar') == (
        'sillypage',
        {'name': 'Foo', 'name2': 'bar'},
    )
    assert adapter.match('/Foo/silly/bar/edit') == (
        'editsillypage',
        {'name': 'Foo', 'name2': 'bar'},
    )
    assert adapter.match('/Talk:Foo/Bar') == ('talk', {'name': 'Foo/Bar'})
    assert adapter.match('/User:thomas') == ('user', {'username': 'thomas'})
    assert adapter.match('/User:thomas/projects/werkzeug') == (
        'userpage',
        {'username': 'thomas', 'name': 'projects/werkzeug'},
    )
    assert adapter.match('/User:thomas/comment/123-456') == (
        'usercomment',
        {'username': 'thomas', 'id': 123, 'replyId': 456},
    )
    assert adapter.match('/Files/downloads/werkzeug/0.2.zip') == (
        'files',
        {'file': 'downloads/werkzeug/0.2.zip'},
    )
    assert adapter.match('/Jerry/eats/cheese') == (
        'admin',
        {'admin': 'Jerry', 'manage': 'eats', 'things': 'cheese'},
    )


def test_adapter_url_parameter_sorting():
    m = Map(
        [
            Rule('/', endpoint='index'),
        ],
        sort_parameters=True,
        sort_key=lambda x: x[1],
    )
    adapter = m.bind('localhost', '/')
    assert (
        adapter.build('index', {'x': 20, 'y': 10, 'z': 30}, force_external=True)
        == 'http://localhost/?y=10&x=20&z=30'
    )


def test_request_direct_charset_bug():
    m = Map([Rule('/öäü/')])
    adapter = m.bind('localhost', '/')

    with pytest.raises(RequestRedirect) as excinfo:
        adapter.match('/öäü')
    assert excinfo.value.new_url == 'http://localhost/%C3%B6%C3%A4%C3%BC/'


def test_request_redirect_default():
    m = Map([Rule('/foo', defaults={'bar': 42}), Rule('/foo/<int:bar>')])
    adapter = m.bind('localhost', '/')

    with pytest.raises(RequestRedirect) as excinfo:
        adapter.match('/foo/42')
    assert excinfo.value.new_url == 'http://localhost/foo'


def test_request_redirect_default_subdomain():
    m = Map([
        Rule('/foo', defaults={'bar': 42}, subdomain='test'),
        Rule('/foo/<int:bar>', subdomain='other'),
    ])
    adapter = m.bind('localhost', '/', subdomain='other')

    with pytest.raises(RequestRedirect) as excinfo:
        adapter.match('/foo/42')
    assert excinfo.value.new_url == 'http://test.localhost/foo'


def test_adapter_match_return_rule():
    rule = Rule('/foo/', endpoint='foo')
    m = Map([rule])
    adapter = m.bind('localhost', '/')
    assert adapter.match('/foo/', return_rule=True) == (rule, {})


def test_rule_emptying():
    rule = Rule(
        '/foo',
        {'meh': 'muh'},
        'x',
        ['POST'],
        False,
        'x',
        True,
        None,
    )
    rule2 = rule.empty()
    assert rule.__dict__ == rule2.__dict__
    rule.methods.add('GET')  # type: ignore
    assert rule.__dict__ != rule2.__dict__
    rule.methods.discard('GET')  # type: ignore
    rule.defaults['meh'] = 'aha'  # type: ignore
    assert rule.__dict__ != rule2.__dict__


def test_rule_unhashable():
    rule = Rule('/foo', {'meh': 'muh'}, 'x', ['POST'], False, 'x', True, None)
    pytest.raises(TypeError, hash, rule)


def test_rule_templates():
    testcase = RuleTemplate(
        [
            Submount(
                '/test/$app',
                [
                    Rule('/foo/', endpoint='handle_foo'),
                    Rule('/bar/', endpoint='handle_bar'),
                    Rule('/baz/', endpoint='handle_baz'),
                ],
            ),
            EndpointPrefix(
                '${app}',
                [
                    Rule('/${app}-blah', endpoint='bar'),
                    Rule('/${app}-meh', endpoint='baz'),
                ],
            ),
            Subdomain(
                '$app',
                [Rule('/blah', endpoint='x_bar'), Rule('/meh', endpoint='x_baz')],
            ),
        ],
    )

    url_map = Map([
        testcase(app='test1'),
        testcase(app='test2'),
        testcase(app='test3'),
        testcase(app='test4'),
    ])

    out = sorted((x.rule, x.subdomain, x.endpoint) for x in url_map.iter_rules())

    assert out == [
        ('/blah', 'test1', 'x_bar'),
        ('/blah', 'test2', 'x_bar'),
        ('/blah', 'test3', 'x_bar'),
        ('/blah', 'test4', 'x_bar'),
        ('/meh', 'test1', 'x_baz'),
        ('/meh', 'test2', 'x_baz'),
        ('/meh', 'test3', 'x_baz'),
        ('/meh', 'test4', 'x_baz'),
        ('/test/test1/bar/', '', 'handle_bar'),
        ('/test/test1/baz/', '', 'handle_baz'),
        ('/test/test1/foo/', '', 'handle_foo'),
        ('/test/test2/bar/', '', 'handle_bar'),
        ('/test/test2/baz/', '', 'handle_baz'),
        ('/test/test2/foo/', '', 'handle_foo'),
        ('/test/test3/bar/', '', 'handle_bar'),
        ('/test/test3/baz/', '', 'handle_baz'),
        ('/test/test3/foo/', '', 'handle_foo'),
        ('/test/test4/bar/', '', 'handle_bar'),
        ('/test/test4/baz/', '', 'handle_baz'),
        ('/test/test4/foo/', '', 'handle_foo'),
        ('/test1-blah', '', 'test1bar'),
        ('/test1-meh', '', 'test1baz'),
        ('/test2-blah', '', 'test2bar'),
        ('/test2-meh', '', 'test2baz'),
        ('/test3-blah', '', 'test3bar'),
        ('/test3-meh', '', 'test3baz'),
        ('/test4-blah', '', 'test4bar'),
        ('/test4-meh', '', 'test4baz'),
    ]


def test_non_string_parts():
    m = Map([Rule('/<foo>', endpoint='foo')])
    a = m.bind('example.com')
    assert a.build('foo', {'foo': 42}) == '/42'


def test_complex_routing_rules():
    m = Map([
        Rule('/', endpoint='index'),
        Rule('/<int:blub>', endpoint='an_int'),
        Rule('/<blub>', endpoint='a_string'),
        Rule('/foo/', endpoint='nested'),
        Rule('/foobar/', endpoint='nestedbar'),
        Rule('/foo/<path:testing>/', endpoint='nested_show'),
        Rule('/foo/<path:testing>/edit', endpoint='nested_edit'),
        Rule('/users/', endpoint='users', defaults={'page': 1}),
        Rule('/users/page/<int:page>', endpoint='users'),
        Rule('/foox', endpoint='foox'),
        Rule('/<path:bar>/<path:blub>', endpoint='barx_path_path'),
    ])
    a = m.bind('example.com')

    assert a.match('/') == ('index', {})
    assert a.match('/42') == ('an_int', {'blub': 42})
    assert a.match('/blub') == ('a_string', {'blub': 'blub'})
    assert a.match('/foo/') == ('nested', {})
    assert a.match('/foobar/') == ('nestedbar', {})
    assert a.match('/foo/1/2/3/') == ('nested_show', {'testing': '1/2/3'})
    assert a.match('/foo/1/2/3/edit') == ('nested_edit', {'testing': '1/2/3'})
    assert a.match('/users/') == ('users', {'page': 1})
    assert a.match('/users/page/2') == ('users', {'page': 2})
    assert a.match('/foox') == ('foox', {})
    assert a.match('/1/2/3') == ('barx_path_path', {'bar': '1', 'blub': '2/3'})

    assert a.build('index') == '/'
    assert a.build('an_int', {'blub': 42}) == '/42'
    assert a.build('a_string', {'blub': 'test'}) == '/test'
    assert a.build('nested') == '/foo/'
    assert a.build('nestedbar') == '/foobar/'
    assert a.build('nested_show', {'testing': '1/2/3'}) == '/foo/1/2/3/'
    assert a.build('nested_edit', {'testing': '1/2/3'}) == '/foo/1/2/3/edit'
    assert a.build('users', {'page': 1}) == '/users/'
    assert a.build('users', {'page': 2}) == '/users/page/2'
    assert a.build('foox') == '/foox'
    assert a.build('barx_path_path', {'bar': '1', 'blub': '2/3'}) == '/1/2/3'


def test_default_converters():
    class MyMap(Map):
        default_converters = dict(Map.default_converters)  # noqa
        default_converters['foo'] = UnicodeConverter

    m = MyMap(
        [
            Rule('/a/<foo:a>', endpoint='a'),
            Rule('/b/<foo:b>', endpoint='b'),
            Rule('/c/<c>', endpoint='c'),
        ],
        converters={'bar': UnicodeConverter},
    )
    a = m.bind('example.org', '/')
    assert a.match('/a/1') == ('a', {'a': '1'})
    assert a.match('/b/2') == ('b', {'b': '2'})
    assert a.match('/c/3') == ('c', {'c': '3'})
    assert 'foo' not in Map.default_converters


def test_uuid_converter():
    m = Map([Rule('/a/<uuid:a_uuid>', endpoint='a')])
    a = m.bind('example.org', '/')
    route, kwargs = a.match('/a/a8098c1a-f86e-11da-bd1a-00112444be1e')
    assert type(kwargs['a_uuid']) == uuid.UUID  # noqa: E721


def test_converter_with_tuples():
    """
    Regression test for https://github.com/pallets/werkzeug/issues/709
    """

    class TwoValueConverter(BaseConverter):
        part_isolating = False

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.regex = r'(\w\w+)/(\w\w+)'

        def to_python(self, two_values):
            one, two = two_values.split('/')
            return one, two

        def to_url(self, values):
            return f'{values[0]}/{values[1]}'

    m = Map(
        [
            Rule('/<two:foo>/', endpoint='handler'),
        ],
        converters={'two': TwoValueConverter},
    )
    a = m.bind('example.org', '/')
    route, kwargs = a.match('/qwert/yuiop/')
    assert kwargs['foo'] == ('qwert', 'yuiop')


def test_nested_regex_groups():
    """
    Regression test for https://github.com/pallets/werkzeug/issues/2590
    """

    class RegexConverter(BaseConverter):
        def __init__(self, url_map, *items):
            super().__init__(url_map)
            self.part_isolating = False
            self.regex = items[0]

    # This is a regex pattern with nested groups
    date_pattern = r'((\d{8}T\d{6}([.,]\d{1,3})?)|(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([.,]\d{1,3})?))Z'

    m = Map(
        [
            Rule(
                f"/<regex('{date_pattern}'):start>/<regex('{date_pattern}'):end>/",
                endpoint='handler',
            ),
        ],
        converters={'regex': RegexConverter},
    )
    a = m.bind('example.org', '/')
    route, kwargs = a.match('/2023-02-16T23:36:36.266Z/2023-02-16T23:46:36.266Z/')
    assert kwargs['start'] == '2023-02-16T23:36:36.266Z'
    assert kwargs['end'] == '2023-02-16T23:46:36.266Z'


def test_anyconverter():
    m = Map([
        Rule('/<any(a1, a2):a>', endpoint='no_dot'),
        Rule('/<any(a.1, a.2):a>', endpoint='yes_dot'),
    ])
    a = m.bind('example.org', '/')
    assert a.match('/a1') == ('no_dot', {'a': 'a1'})
    assert a.match('/a2') == ('no_dot', {'a': 'a2'})
    assert a.match('/a.1') == ('yes_dot', {'a': 'a.1'})
    assert a.match('/a.2') == ('yes_dot', {'a': 'a.2'})


def test_any_converter_build_validates_value() -> None:
    m = Map([Rule('/<any(patient, provider):value>', endpoint='actor')])
    a = m.bind('localhost')

    assert a.build('actor', {'value': 'patient'}) == '/patient'
    assert a.build('actor', {'value': 'provider'}) == '/provider'

    with pytest.raises(ValueError) as exc:  # noqa
        a.build('actor', {'value': 'invalid'})

    assert str(exc.value) == "'invalid' is not one of 'patient', 'provider'"


def test_part_isolating_default() -> None:
    class TwoConverter(BaseConverter):
        regex = r'\w+/\w+'

        def to_python(self, value: str) -> ta.Any:
            return value.split('/')

    m = Map(
        [
            Rule('/<two:values>/', endpoint='two'),
        ],
        converters={'two': TwoConverter},
    )
    a = m.bind('localhost')
    assert a.match('/a/b/') == ('two', {'values': ['a', 'b']})


@pytest.mark.parametrize(
    ('endpoint', 'value', 'expect'),
    [
        ('int', 1, '/1'),
        ('int', None, BuildError),
        ('int', [1], TypeError),
        ('list', [1], '/1'),
        ('list', [1, None, 2], '/1.None.2'),
        ('list', 1, TypeError),
    ],
)
def test_build_values_dict(endpoint, value, expect):
    class ListConverter(BaseConverter):
        def to_url(self, value: ta.Any) -> str:
            return super().to_url('.'.join(map(str, value)))

    url_map = Map(
        [
            Rule('/<int:v>', endpoint='int'),
            Rule('/<list:v>', endpoint='list'),
        ],
        converters={'list': ListConverter},
    )
    adapter = url_map.bind('localhost')

    if isinstance(expect, str):
        assert adapter.build(endpoint, {'v': value}) == expect
    else:
        with pytest.raises(expect):
            adapter.build(endpoint, {'v': value})


@pytest.mark.parametrize(
    ('endpoint', 'value', 'expect'),
    [
        ('int', 1, '/1'),
        ('int', [1], '/1'),
        ('int', [], BuildError),
        ('int', None, TypeError),
        ('int', [None], TypeError),
        ('list', 1, TypeError),
        ('list', [1], TypeError),
        ('list', [[1]], '/1'),
        ('list', [1, None, 2], '/1.None.2'),
    ],
)
def test_build_values_multidict(endpoint, value, expect):
    class ListConverter(BaseConverter):
        def to_url(self, value: ta.Any) -> str:
            return super().to_url('.'.join(map(str, value)))

    url_map = Map(
        [
            Rule('/<int:v>', endpoint='int'),
            Rule('/<list:v>', endpoint='list'),
        ],
        converters={'list': ListConverter},
    )
    adapter = url_map.bind('localhost')

    if isinstance(expect, str):
        assert adapter.build(endpoint, MultiDict({'v': value})) == expect
    else:
        with pytest.raises(expect):
            adapter.build(endpoint, MultiDict({'v': value}))


@pytest.mark.parametrize(
    ('value', 'expect'),
    [
        (None, ''),
        ([None], ''),
        ([None, None], ''),
        ('', '?v='),
        ([''], '?v='),
        (0, '?v=0'),
        (1.0, '?v=1.0'),
        ([1, 2], '?v=1&v=2'),
        ([1, None, 2], '?v=1&v=2'),
        ([1, '', 2], '?v=1&v=&v=2'),
        ('1+2', '?v=1%2B2'),
    ],
)
def test_build_append_unknown_dict(value, expect):
    m = Map([Rule('/', endpoint='a')])
    adapter = m.bind('localhost')
    assert adapter.build('a', {'v': value}) == f'/{expect}'
    assert adapter.build('a', {'v': value}, append_unknown=False) == '/'


@pytest.mark.parametrize(
    ('value', 'expect'),
    [
        (None, ''),
        ([None], ''),
        ([None, None], ''),
        ('', '?v='),
        ([''], '?v='),
        (0, '?v=0'),
        (1.0, '?v=1.0'),
        ([1, 2], '?v=1&v=2'),
        ([1, None, 2], '?v=1&v=2'),
        ([1, '', 2], '?v=1&v=&v=2'),
    ],
)
def test_build_append_unknown_multidict(value, expect):
    m = Map([Rule('/', endpoint='a')])
    adapter = m.bind('localhost')
    assert adapter.build('a', MultiDict({'v': value})) == f'/{expect}'
    assert adapter.build('a', MultiDict({'v': value}), append_unknown=False) == '/'


def test_build_drop_none():
    m = Map([Rule('/flob/<flub>', endpoint='endp')])
    adapter = m.bind('', '/')
    params: dict = {'flub': None, 'flop': None}
    with pytest.raises(BuildError):
        adapter.build('endp', params)
    params = {'flub': 'x', 'flop': None}
    url = adapter.build('endp', params)
    assert 'flop' not in url


def test_method_fallback():
    m = Map([
        Rule('/', endpoint='index', methods=['GET']),
        Rule('/<name>', endpoint='hello_name', methods=['GET']),
        Rule('/select', endpoint='hello_select', methods=['POST']),
        Rule('/search_get', endpoint='search', methods=['GET']),
        Rule('/search_post', endpoint='search', methods=['POST']),
    ])
    adapter = m.bind('example.com')
    assert adapter.build('index') == '/'
    assert adapter.build('index', method='GET') == '/'
    assert adapter.build('hello_name', {'name': 'foo'}) == '/foo'
    assert adapter.build('hello_select') == '/select'
    assert adapter.build('hello_select', method='POST') == '/select'
    assert adapter.build('search') == '/search_get'
    assert adapter.build('search', method='GET') == '/search_get'
    assert adapter.build('search', method='POST') == '/search_post'


def test_implicit_head():
    url_map = Map([
        Rule('/get', methods=['GET'], endpoint='a'),
        Rule('/post', methods=['POST'], endpoint='b'),
    ])
    adapter = url_map.bind('example.org')
    assert adapter.match('/get', method='HEAD') == ('a', {})
    pytest.raises(MethodNotAllowed, adapter.match, '/post', method='HEAD')


def test_pass_str_as_router_methods():
    with pytest.raises(TypeError):
        Rule('/get', methods='GET')


def test_protocol_joining_bug():
    m = Map([Rule('/<foo>', endpoint='x')])
    a = m.bind('example.org')
    assert a.build('x', {'foo': 'x:y'}) == '/x:y'
    assert a.build('x', {'foo': 'x:y'}, force_external=True) == 'http://example.org/x:y'


def test_allowed_methods_querying():
    m = Map([
        Rule('/<foo>', methods=['GET', 'HEAD']),
        Rule('/foo', methods=['POST']),
    ])
    a = m.bind('example.org')
    assert sorted(a.allowed_methods('/foo')) == ['GET', 'HEAD', 'POST']


def test_external_building_with_port():
    m = Map([Rule('/', endpoint='index')])
    adapter = m.bind('example.org:5000', '/')
    built_url = adapter.build('index', {}, force_external=True)
    assert built_url == 'http://example.org:5000/', built_url


def test_bind_long_idna_name_with_port():
    m = Map([Rule('/', endpoint='index')])
    adapter = m.bind('🐍' + 'a' * 52 + ':8443')
    name, _, port = adapter.server_name.partition(':')
    assert len(name) == 63
    assert port == '8443'


def test_converter_parser():
    args, kwargs = parse_converter_args('test, a=1, b=3.0')

    assert args == ('test',)
    assert kwargs == {'a': 1, 'b': 3.0}

    args, kwargs = parse_converter_args('')
    assert not args and not kwargs

    args, kwargs = parse_converter_args('a, b, c,')
    assert args == ('a', 'b', 'c')
    assert not kwargs

    args, kwargs = parse_converter_args('True, False, None')
    assert args == (True, False, None)

    args, kwargs = parse_converter_args('"foo", "bar"')
    assert args == ('foo', 'bar')

    with pytest.raises(ValueError):  # noqa
        parse_converter_args('min=0;max=500')


def test_alias_redirects():
    m = Map([
        Rule('/', endpoint='index'),
        Rule('/index.html', endpoint='index', alias=True),
        Rule('/users/', defaults={'page': 1}, endpoint='users'),
        Rule('/users/index.html', defaults={'page': 1}, alias=True, endpoint='users'),
        Rule('/users/page/<int:page>', endpoint='users'),
        Rule('/users/page-<int:page>.html', alias=True, endpoint='users'),
    ])
    a = m.bind('example.com')

    def ensure_redirect(path, new_url, args=None):
        with pytest.raises(RequestRedirect) as excinfo:
            a.match(path, query_args=args)
        assert excinfo.value.new_url == f'http://example.com{new_url}'

    ensure_redirect('/index.html', '/')
    ensure_redirect('/users/index.html', '/users/')
    ensure_redirect('/users/page-2.html', '/users/page/2')
    ensure_redirect('/users/page-1.html', '/users/')
    ensure_redirect('/users/page-1.html', '/users/?foo=bar', {'foo': 'bar'})

    assert a.build('index') == '/'
    assert a.build('users', {'page': 1}) == '/users/'
    assert a.build('users', {'page': 2}) == '/users/page/2'


@pytest.mark.parametrize('prefix', ['', '/aaa'])
def test_double_defaults(prefix):
    m = Map([
        Rule(f'{prefix}/', defaults={'foo': 1, 'bar': False}, endpoint='x'),
        Rule(f'{prefix}/<int:foo>', defaults={'bar': False}, endpoint='x'),
        Rule(f'{prefix}/bar/', defaults={'foo': 1, 'bar': True}, endpoint='x'),
        Rule(f'{prefix}/bar/<int:foo>', defaults={'bar': True}, endpoint='x'),
    ])
    a = m.bind('example.com')

    assert a.match(f'{prefix}/') == ('x', {'foo': 1, 'bar': False})
    assert a.match(f'{prefix}/2') == ('x', {'foo': 2, 'bar': False})
    assert a.match(f'{prefix}/bar/') == ('x', {'foo': 1, 'bar': True})
    assert a.match(f'{prefix}/bar/2') == ('x', {'foo': 2, 'bar': True})

    assert a.build('x', {'foo': 1, 'bar': False}) == f'{prefix}/'
    assert a.build('x', {'foo': 2, 'bar': False}) == f'{prefix}/2'
    assert a.build('x', {'bar': False}) == f'{prefix}/'
    assert a.build('x', {'foo': 1, 'bar': True}) == f'{prefix}/bar/'
    assert a.build('x', {'foo': 2, 'bar': True}) == f'{prefix}/bar/2'
    assert a.build('x', {'bar': True}) == f'{prefix}/bar/'


def test_host_matching():
    m = Map(
        [
            Rule('/', endpoint='index', host='www.<domain>'),
            Rule('/', endpoint='files', host='files.<domain>'),
            Rule('/foo/', defaults={'page': 1}, host='www.<domain>', endpoint='x'),
            Rule('/<int:page>', host='files.<domain>', endpoint='x'),
        ],
        host_matching=True,
    )

    a = m.bind('www.example.com')
    assert a.match('/') == ('index', {'domain': 'example.com'})
    assert a.match('/foo/') == ('x', {'domain': 'example.com', 'page': 1})

    with pytest.raises(RequestRedirect) as excinfo:
        a.match('/foo')
    assert excinfo.value.new_url == 'http://www.example.com/foo/'

    a = m.bind('files.example.com')
    assert a.match('/') == ('files', {'domain': 'example.com'})
    assert a.match('/2') == ('x', {'domain': 'example.com', 'page': 2})

    with pytest.raises(RequestRedirect) as excinfo:
        a.match('/1')
    assert excinfo.value.new_url == 'http://www.example.com/foo/'


def test_host_matching_building():
    m = Map(
        [
            Rule('/', endpoint='index', host='www.domain.com'),
            Rule('/', endpoint='foo', host='my.domain.com'),
        ],
        host_matching=True,
    )

    www = m.bind('www.domain.com')
    assert www.match('/') == ('index', {})
    assert www.build('index') == '/'
    assert www.build('foo') == 'http://my.domain.com/'

    my = m.bind('my.domain.com')
    assert my.match('/') == ('foo', {})
    assert my.build('foo') == '/'
    assert my.build('index') == 'http://www.domain.com/'


def test_unicode_rules():
    m = Map([
        Rule('/войти/', endpoint='enter'),
        Rule('/foo+bar/', endpoint='foobar'),
    ])
    a = m.bind('☃.example.com')
    with pytest.raises(RequestRedirect) as excinfo:
        a.match('/войти')
    assert (
        excinfo.value.new_url
        == 'http://xn--n3h.example.com/%D0%B2%D0%BE%D0%B9%D1%82%D0%B8/'
    )

    endpoint, values = a.match('/войти/')
    assert endpoint == 'enter'
    assert values == {}

    with pytest.raises(RequestRedirect) as excinfo:
        a.match('/foo+bar')
    assert excinfo.value.new_url == 'http://xn--n3h.example.com/foo+bar/'

    endpoint, values = a.match('/foo+bar/')
    assert endpoint == 'foobar'
    assert values == {}

    url = a.build('enter', {}, force_external=True)
    assert url == 'http://xn--n3h.example.com/%D0%B2%D0%BE%D0%B9%D1%82%D0%B8/'

    url = a.build('foobar', {}, force_external=True)
    assert url == 'http://xn--n3h.example.com/foo+bar/'


def test_empty_path_info():
    m = Map([Rule('/', endpoint='index')])

    b = m.bind('example.com', script_name='/approot')
    with pytest.raises(RequestRedirect) as excinfo:
        b.match('')
    assert excinfo.value.new_url == 'http://example.com/approot/'

    a = m.bind('example.com')
    with pytest.raises(RequestRedirect) as excinfo:
        a.match('')
    assert excinfo.value.new_url == 'http://example.com/'


def test_both_bind_and_match_path_info_are_none():
    m = Map([Rule('/', endpoint='index')])
    ma = m.bind('example.org')
    assert ma.match() == ('index', {})


def test_map_repr():
    m = Map([Rule('/wat', endpoint='enter'), Rule('/woop', endpoint='foobar')])
    rv = repr(m)
    assert rv == "Map([<Rule '/wat' -> enter>, <Rule '/woop' -> foobar>])"


def test_empty_subclass_rules_with_custom_kwargs():
    class CustomRule(Rule):
        def __init__(self, string=None, custom=None, *args, **kwargs):
            self.custom = custom
            super().__init__(string, *args, **kwargs)

    rule1 = CustomRule('/foo', endpoint='bar')
    try:
        rule2 = rule1.empty()
        assert rule1.rule == rule2.rule
    except TypeError as e:  # raised without fix in PR #675  # noqa
        raise e  # noqa


def test_finding_closest_match_by_endpoint():
    m = Map([
        Rule('/foo/', endpoint='users.here'),
        Rule('/wat/', endpoint='admin.users'),
        Rule('/woop', endpoint='foo.users'),
    ])
    adapter = m.bind('example.com')
    assert BuildError(
        'admin.user',
        {},
        None,
        adapter,
    ).suggested.endpoint == 'admin.users'  # type: ignore[union-attr]


def test_finding_closest_match_by_values():
    rule_id = Rule('/user/id/<id>/', endpoint='users')
    rule_slug = Rule('/user/<slug>/', endpoint='users')
    rule_random = Rule('/user/emails/<email>/', endpoint='users')
    m = Map([rule_id, rule_slug, rule_random])
    adapter = m.bind('example.com')
    assert BuildError('x', {'slug': ''}, None, adapter).suggested == rule_slug


def test_finding_closest_match_by_method():
    post = Rule('/post/', endpoint='foobar', methods=['POST'])
    get = Rule('/get/', endpoint='foobar', methods=['GET'])
    put = Rule('/put/', endpoint='foobar', methods=['PUT'])
    m = Map([post, get, put])
    adapter = m.bind('example.com')
    assert BuildError('invalid', {}, 'POST', adapter).suggested == post
    assert BuildError('invalid', {}, 'GET', adapter).suggested == get
    assert BuildError('invalid', {}, 'PUT', adapter).suggested == put


def test_finding_closest_match_when_none_exist():
    m = Map([])
    assert not BuildError('invalid', {}, None, m.bind('test.com')).suggested


def test_error_message_without_suggested_rule():
    m = Map([Rule('/foo/', endpoint='world', methods=['GET'])])
    adapter = m.bind('example.com')

    with pytest.raises(BuildError) as excinfo:
        adapter.build('urks')
    assert str(excinfo.value).startswith("Could not build url for endpoint 'urks'.")

    with pytest.raises(BuildError) as excinfo:
        adapter.build('world', method='POST')
    assert str(excinfo.value).startswith(
        "Could not build url for endpoint 'world' ('POST').",
    )

    with pytest.raises(BuildError) as excinfo:
        adapter.build('urks', values={'user_id': 5})
    assert str(excinfo.value).startswith(
        "Could not build url for endpoint 'urks' with values ['user_id'].",
    )


def test_error_message_suggestion():
    m = Map([Rule('/foo/<id>/', endpoint='world', methods=['GET'])])
    adapter = m.bind('example.com')

    with pytest.raises(BuildError) as excinfo:
        adapter.build('helloworld')
    assert "Did you mean 'world' instead?" in str(excinfo.value)

    with pytest.raises(BuildError) as excinfo:
        adapter.build('world')
    assert "Did you forget to specify values ['id']?" in str(excinfo.value)
    assert 'Did you mean to use methods' not in str(excinfo.value)

    with pytest.raises(BuildError) as excinfo:
        adapter.build('world', {'id': 2}, method='POST')
    assert "Did you mean to use methods ['GET', 'HEAD']?" in str(excinfo.value)


def test_no_memory_leak_from_rule_builder():
    """See #1520"""

    # generate a bunch of objects that *should* get collected
    for _ in range(100):
        Map([Rule('/a/<string:b>')])

    # ensure that the garbage collection has had a chance to collect cyclic
    # objects
    for _ in range(5):
        gc.collect()

    # assert they got collected!
    count = sum(1 for obj in gc.get_objects() if isinstance(obj, Rule))
    assert count == 0


def test_build_url_with_arg_self():
    m = Map([Rule('/foo/<string:self>', endpoint='foo')])
    adapter = m.bind('example.org', '/', subdomain='blah')

    ret = adapter.build('foo', {'self': 'bar'})
    assert ret == 'http://example.org/foo/bar'


def test_build_url_with_arg_keyword():
    m = Map([Rule('/foo/<string:class>', endpoint='foo')])
    adapter = m.bind('example.org', '/', subdomain='blah')

    ret = adapter.build('foo', {'class': 'bar'})
    assert ret == 'http://example.org/foo/bar'


def test_build_url_same_endpoint_multiple_hosts():
    m = Map(
        [
            Rule('/', endpoint='index', host='alpha.example.com'),
            Rule('/', endpoint='index', host='beta.example.com'),
            Rule('/', endpoint='gamma', host='gamma.example.com'),
        ],
        host_matching=True,
    )

    alpha = m.bind('alpha.example.com')
    assert alpha.build('index') == '/'
    assert alpha.build('gamma') == 'http://gamma.example.com/'

    alpha_case = m.bind('AlPhA.ExAmPlE.CoM')
    assert alpha_case.build('index') == '/'
    assert alpha_case.build('gamma') == 'http://gamma.example.com/'

    beta = m.bind('beta.example.com')
    assert beta.build('index') == '/'

    beta_case = m.bind('BeTa.ExAmPlE.CoM')
    assert beta_case.build('index') == '/'


def test_rule_websocket_methods():
    with pytest.raises(ValueError):  # noqa
        Rule('/ws', endpoint='ws', websocket=True, methods=['post'])
    with pytest.raises(ValueError):  # noqa
        Rule(
            '/ws',
            endpoint='ws',
            websocket=True,
            methods=['get', 'head', 'options', 'post'],
        )
    Rule('/ws', endpoint='ws', websocket=True, methods=['get', 'head', 'options'])


def test_path_weighting():
    m = Map([
        Rule('/<path:path>/c', endpoint='simple'),
        Rule('/<path:path>/<a>/<b>', endpoint='complex'),
    ])
    a = m.bind('localhost', path_info='/a/b/c')

    assert a.match() == ('simple', {'path': 'a/b'})


def test_newline_match():
    m = Map([Rule('/hello', endpoint='hello')])
    a = m.bind('localhost')

    with pytest.raises(NotFound):
        a.match('/hello\n')


def test_weighting():
    m = Map([
        Rule('/<int:value>', endpoint='int'),
        Rule('/<uuid:value>', endpoint='uuid'),
    ])
    a = m.bind('localhost')

    assert a.match('/2b5b0911-fdcf-4dd2-921b-28ace88db8a0') == (
        'uuid',
        {'value': uuid.UUID('2b5b0911-fdcf-4dd2-921b-28ace88db8a0')},
    )


def test_strict_slashes_false():
    m = Map([
        Rule('/path1', endpoint='leaf_path', strict_slashes=False),
        Rule('/path2/', endpoint='branch_path', strict_slashes=False),
        Rule('/<path:path>', endpoint='leaf_path_converter', strict_slashes=False),
    ])

    adapter = m.bind('example.org', '/')

    assert adapter.match('/path1', method='GET') == ('leaf_path', {})
    assert adapter.match('/path1/', method='GET') == ('leaf_path', {})
    assert adapter.match('/path2', method='GET') == ('branch_path', {})
    assert adapter.match('/path2/', method='GET') == ('branch_path', {})
    assert adapter.match('/any', method='GET') == ('leaf_path_converter', {'path': 'any'})
    assert adapter.match('/any/', method='GET') == ('leaf_path_converter', {'path': 'any/'})


def test_invalid_rule():
    with pytest.raises(ValueError):  # noqa
        Map([Rule('/<int()>', endpoint='test')])


def test_multiple_converters_per_part():
    map_ = Map([
        Rule('/v<int:major>.<int:minor>', endpoint='version'),
    ])
    adapter = map_.bind('localhost')
    assert adapter.match('/v1.2') == ('version', {'major': 1, 'minor': 2})


def test_static_regex_escape():
    map_ = Map([
        Rule('/.<int:value>', endpoint='dotted'),
    ])
    adapter = map_.bind('localhost')
    assert adapter.match('/.2') == ('dotted', {'value': 2})
    with pytest.raises(NotFound):
        adapter.match('/a2')


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super().__init__(url_map)
        self.regex = items[0]


def test_regex():
    map_ = Map(
        [
            Rule(r"/<regex('[^/:]+\.[^/:]+'):value>", endpoint='regex'),
        ],
        converters={'regex': RegexConverter},
    )
    adapter = map_.bind('localhost')
    assert adapter.match('/asdfsa.asdfs') == ('regex', {'value': 'asdfsa.asdfs'})
