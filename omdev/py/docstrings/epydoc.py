"""
Epyoc-style docstring parsing.

.. seealso:: http://epydoc.sourceforge.net/manual-fields.html
"""
import inspect
import re
import typing as ta

from .common import Docstring
from .common import DocstringMeta
from .common import DocstringParam
from .common import DocstringRaises
from .common import DocstringReturns
from .common import DocstringStyle
from .common import ParseError


##


def _clean_str(string: str) -> str | None:
    string = string.strip()
    if len(string) > 0:
        return string
    return None


_PARAM_PAT = re.compile(r'(param|keyword|type)(\s+[_A-z][_A-z0-9]*\??):')
_RAISE_PAT = re.compile(r'(raise)(\s+[_A-z][_A-z0-9]*\??)?:')
_RETURN_PAT = re.compile(r'(return|rtype|yield|ytype):')
_META_PAT = re.compile(r'([_A-z][_A-z0-9]+)((\s+[_A-z][_A-z0-9]*\??)*):')


def parse(text: str) -> Docstring:
    """
    Parse the epydoc-style docstring into its components.

    :returns: parsed docstring
    """

    ret = Docstring(style=DocstringStyle.EPYDOC)
    if not text:
        return ret

    text = inspect.cleandoc(text)
    match = re.search('^@', text, flags=re.MULTILINE)
    if match:
        desc_chunk = text[: match.start()]
        meta_chunk = text[match.start():]
    else:
        desc_chunk = text
        meta_chunk = ''

    parts = desc_chunk.split('\n', 1)
    ret.short_description = parts[0] or None
    if len(parts) > 1:
        long_desc_chunk = parts[1] or ''
        ret.blank_after_short_description = long_desc_chunk.startswith('\n')
        ret.blank_after_long_description = long_desc_chunk.endswith('\n\n')
        ret.long_description = long_desc_chunk.strip() or None

    # tokenize
    stream: list[tuple[str, str, list[str], str]] = []
    for match in re.finditer(r'(^@.*?)(?=^@|\Z)', meta_chunk, flags=re.DOTALL | re.MULTILINE):
        chunk = match.group(0)
        if not chunk:
            continue

        param_match = re.search(_PARAM_PAT, chunk)
        raise_match = re.search(_RAISE_PAT, chunk)
        return_match = re.search(_RETURN_PAT, chunk)
        meta_match = re.search(_META_PAT, chunk)

        match = param_match or raise_match or return_match or meta_match
        if not match:
            raise ParseError(f'Error parsing meta information near "{chunk}".')

        desc_chunk = chunk[match.end():]

        key: str
        if param_match:
            base = 'param'
            key = match.group(1)
            args = [match.group(2).strip()]

        elif raise_match:
            base = 'raise'
            key = match.group(1)
            args = [] if match.group(2) is None else [match.group(2).strip()]

        elif return_match:
            base = 'return'
            key = match.group(1)
            args = []

        else:
            base = 'meta'
            key = match.group(1)
            token = _clean_str(match.group(2).strip())
            args = [] if token is None else re.split(r'\s+', token)

            # Make sure we didn't match some existing keyword in an incorrect way here:
            if key in [
                'param',
                'keyword',
                'type',
                'return',
                'rtype',
                'yield',
                'ytype',
            ]:
                raise ParseError(f'Error parsing meta information near "{chunk}".')

        desc = desc_chunk.strip()
        if '\n' in desc:
            first_line, rest = desc.split('\n', 1)
            desc = first_line + '\n' + inspect.cleandoc(rest)
        stream.append((base, key, args, desc))

    # Combine type_name, arg_name, and description information
    params: dict[str, dict[str, ta.Any]] = {}
    for base, key, args, desc in stream:
        if base not in ['param', 'return']:
            continue  # nothing to do

        (arg_name,) = args or ('return',)
        info = params.setdefault(arg_name, {})
        info_key = 'type_name' if 'type' in key else 'description'
        info[info_key] = desc

        if base == 'return':
            is_generator = key in {'ytype', 'yield'}
            if info.setdefault('is_generator', is_generator) != is_generator:
                raise ParseError(
                    f'Error parsing meta information for "{arg_name}".',
                )

    is_done: dict[str, bool] = {}
    meta_item: DocstringMeta
    for base, key, args, desc in stream:
        if base == 'param' and not is_done.get(args[0], False):
            (arg_name,) = args
            info = params[arg_name]
            type_name = info.get('type_name')

            if type_name and type_name.endswith('?'):
                is_optional = True
                type_name = type_name[:-1]
            else:
                is_optional = False

            match = re.match(r'.*defaults to (.+)', desc, flags=re.DOTALL)
            default = match.group(1).rstrip('.') if match else None

            meta_item = DocstringParam(
                args=[key, arg_name],
                description=info.get('description'),
                arg_name=arg_name,
                type_name=type_name,
                is_optional=is_optional,
                default=default,
            )
            is_done[arg_name] = True

        elif base == 'return' and not is_done.get('return', False):
            info = params['return']
            meta_item = DocstringReturns(
                args=[key],
                description=info.get('description'),
                type_name=info.get('type_name'),
                is_generator=info.get('is_generator', False),
            )
            is_done['return'] = True

        elif base == 'raise':
            (type_name,) = args or (None,)
            meta_item = DocstringRaises(
                args=[key, *args],
                description=desc,
                type_name=type_name,
            )

        elif base == 'meta':
            meta_item = DocstringMeta(
                args=[key, *args],
                description=desc,
            )

        else:
            (key, *_) = args or ('return',)
            if not is_done.get(key, False):
                raise ParseError
            continue  # don't append

        ret.meta.append(meta_item)

    return ret
