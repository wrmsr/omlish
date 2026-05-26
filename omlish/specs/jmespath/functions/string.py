import re
import typing as ta

from ..errors import JmespathError
from .base import FunctionsClass
from .base import signature


T = ta.TypeVar('T')


##


class StringFunctions(FunctionsClass):
    @signature({'types': ['string']})
    def _func_lower(self, arg):
        return arg.lower()

    @signature({'types': ['string']})
    def _func_upper(self, arg):
        return arg.upper()

    @signature({'types': ['string']}, {'types': ['string']})
    def _func_ends_with(self, search, suffix):
        return search.endswith(suffix)

    @signature({'types': ['string']}, {'types': ['string']})
    def _func_starts_with(self, search, suffix):
        return search.startswith(suffix)

    @signature({'type': 'string'}, {'type': 'string', 'optional': True})
    def _func_trim(self, text, chars=None):
        if chars is None or len(chars) == 0:
            return text.strip()
        return text.strip(chars)

    @signature({'type': 'string'}, {'type': 'string', 'optional': True})
    def _func_trim_left(self, text, chars=None):
        if chars is None or len(chars) == 0:
            return text.lstrip()
        return text.lstrip(chars)

    @signature({'type': 'string'}, {'type': 'string', 'optional': True})
    def _func_trim_right(self, text, chars=None):
        if chars is None or len(chars) == 0:
            return text.rstrip()
        return text.rstrip(chars)

    @signature({'types': ['string']}, {'types': ['array-string']})
    def _func_join(self, separator, array):
        return separator.join(array)

    #

    def _find_impl(self, text, search, func, start, end):
        if len(search) == 0:
            return None
        if end is None:
            end = len(text)

        pos = func(text[start:end], search)
        if start < 0:
            start = start + len(text)

        # restrict resulting range to valid indices
        start = min(max(start, 0), len(text))
        return start + pos if pos != -1 else None

    @signature(
        {'type': 'string'},
        {'type': 'string'},
        {'type': 'number', 'optional': True},
        {'type': 'number', 'optional': True},
    )
    def _func_find_first(self, text, search, start=0, end=None):
        self._ensure_integer('find_first', 'start', start)
        self._ensure_integer('find_first', 'end', end)
        return self._find_impl(
            text,
            search,
            lambda t, s: t.find(s),
            start,
            end,
        )

    @signature(
        {'type': 'string'},
        {'type': 'string'},
        {'type': 'number', 'optional': True},
        {'type': 'number', 'optional': True})
    def _func_find_last(self, text, search, start=0, end=None):
        self._ensure_integer('find_last', 'start', start)
        self._ensure_integer('find_last', 'end', end)
        return self._find_impl(
            text,
            search,
            lambda t, s: t.rfind(s),
            start,
            end,
        )

    #

    def _pad_impl(self, func, padding):
        if len(padding) != 1:
            raise JmespathError(
                f'syntax-error: pad_right() expects $padding to have a single character, but received '
                f'`{padding}` instead.',
            )
        return func()

    @signature(
        {'type': 'string'},
        {'type': 'number'},
        {'type': 'string', 'optional': True},
    )
    def _func_pad_left(self, text, width, padding=' '):
        self._ensure_non_negative_integer('pad_left', 'width', width)
        return self._pad_impl(lambda: text.rjust(width, padding), padding)

    @signature(
        {'type': 'string'},
        {'type': 'number'},
        {'type': 'string', 'optional': True},
    )
    def _func_pad_right(self, text, width, padding=' '):
        self._ensure_non_negative_integer('pad_right', 'width', width)
        return self._pad_impl(lambda: text.ljust(width, padding), padding)

    #

    @signature(
        {'type': 'string'},
        {'type': 'string'},
        {'type': 'string'},
        {'type': 'number', 'optional': True},
    )
    def _func_replace(self, text, search, replacement, count=None):
        self._ensure_non_negative_integer(
            'replace',
            'count',
            count,
        )

        if count is not None:
            return text.replace(search, replacement, int(count))

        return text.replace(search, replacement)

    @signature(
        {'type': 'string'},
        {'type': 'string'},
        {'type': 'number', 'optional': True},
    )
    def _func_split(self, text, search, count=None):
        self._ensure_non_negative_integer(
            'split',
            'count',
            count,
        )

        if len(search) == 0:
            chars = list(text)
            if count is None:
                return chars

            head = list(chars[:count])
            tail = [''.join(chars[count:])]
            return head + tail

        if count is not None:
            return text.split(search, count)

        return text.split(search)

    #

    @signature({'types': ['string']}, {'types': ['string']})
    def _func_match(self, string, pattern):
        return re.match(pattern, string) is not None
