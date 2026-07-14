# ruff: noqa: UP006 UP007 UP037 UP045
# @om-lite
import re
import typing as ta
import urllib.parse

from ...lite.namespaces import NamespaceClass
from .types import UrlRouteArgParseError


##


class UrlRoutingUtils(NamespaceClass):
    @staticmethod
    def quote_static_part(s: str) -> str:
        return urllib.parse.quote(s, safe="!$&'()*+,/:;=@")

    @staticmethod
    def unquote_part(s: str) -> str:
        return urllib.parse.unquote(s, errors='strict')

    #

    @staticmethod
    def query_encode(values: ta.Mapping[str, ta.Any]) -> str:
        items = []
        for k, v in values.items():
            if v is None:
                continue
            if isinstance(v, (list, tuple)):
                for e in v:
                    if e is not None:
                        items.append((k, e))
            else:
                items.append((k, v))
        return urllib.parse.urlencode(items, doseq=True, safe="!$'()*,/:;?@")

    #

    @staticmethod
    def normalize_method_set(
            methods: ta.Optional[ta.AbstractSet[str]],
            *,
            add_head: bool,
    ) -> ta.Optional[ta.AbstractSet[str]]:
        if methods is None:
            return None

        ret = {m.upper() for m in methods}
        if add_head and 'GET' in ret:
            ret.add('HEAD')
        return frozenset(ret)

    @staticmethod
    def methods_overlap(
            a: ta.Optional[ta.AbstractSet[str]],
            b: ta.Optional[ta.AbstractSet[str]],
    ) -> bool:
        if a is None or b is None:
            return True
        return bool(a & b)

    #

    @staticmethod
    def split_raw_path(path: str) -> ta.List[str]:
        if not path.startswith('/'):
            raise ValueError(path)

        if path == '/':
            return []

        return path[1:].split('/')

    #

    @staticmethod
    def parse_arg_value(s: str) -> ta.Any:
        if s == 'True':
            return True
        if s == 'False':
            return False
        if s == 'None':
            return None
        if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
            return bytes(s[1:-1], 'utf-8').decode('unicode_escape')
        try:
            return int(s)
        except ValueError:
            pass
        try:
            return float(s)
        except ValueError:
            pass
        return s

    URL_ROUTE_ARG_PAT: ta.ClassVar[re.Pattern] = re.compile(
        r"""
        \s*
        (?:(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*)?
        (?P<value>
            True|False|None|
            -?\d+\.\d+|
            -?\d+|
            "(?:[^"\\]|\\.)*"|
            '(?:[^'\\]|\\.)*'|
            [^,\s]+)
        \s*(?:,|\Z)
        """,
        re.VERBOSE,
    )

    @classmethod
    def parse_converter_args(cls, s: str) -> ta.Tuple[
        ta.Tuple[ta.Any, ...],
        ta.Dict[str, ta.Any],
    ]:
        if not s:
            return (), {}

        args: ta.List[ta.Any] = []
        kwargs: ta.Dict[str, ta.Any] = {}
        pos = 0
        while pos < len(s):
            m = cls.URL_ROUTE_ARG_PAT.match(s, pos)
            if m is None:
                raise UrlRouteArgParseError(s[pos:])
            value = cls.parse_arg_value(m.group('value'))
            name = m.group('name')
            if name is None:
                if kwargs:
                    raise UrlRouteArgParseError(s[pos:])
                args.append(value)
            else:
                kwargs[name] = value
            pos = m.end()
        return tuple(args), kwargs

    URL_ROUTE_VARIABLE_PAT: ta.ClassVar[re.Pattern] = re.compile(
        r"""
        \{
            (?P<name>[a-zA-Z_][a-zA-Z0-9_]*)
            (?:
                :
                (?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)
                (?:
                    \(
                        (?P<args>[^{}]*)
                    \)
                )?
            )?
        \}
        """,
        re.VERBOSE,
    )

    #

    @staticmethod
    def alternate_slash_path(path: str) -> ta.Optional[str]:
        if path == '/':
            return None
        if path.endswith('/'):
            return path[:-1] or '/'
        return path + '/'
