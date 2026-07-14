import re
import typing as ta

from omcore import lang
from omcore.lang.casing import StringCasingError
from omcore.marshal.api.naming import Naming


##


_LOW_CAMEL_TO_SNAKE = lang.LOW_CAMEL_CASE.to(lang.SNAKE_CASE)
_SNAKE_TO_CAMEL = lang.SNAKE_CASE.to(lang.CAMEL_CASE)


_WORD_PAT: ta.Final = re.compile(r'[A-Za-z0-9]+')


def split_loose_words(s: str) -> list[str]:
    try:
        return lang.split_string_casing(s)
    except StringCasingError:
        pass

    words = [m.group(0).lower() for m in _WORD_PAT.finditer(s)]
    if words:
        return words

    raise ValueError(s)


def ref_name(ref_str: str) -> str:
    parts = ref_str.split('/')
    if len(parts) != 3 or parts[0] != '#' or parts[1] not in ('$defs', 'definitions') or not parts[2]:
        raise ValueError(ref_str)

    return parts[2].replace('~1', '/').replace('~0', '~')


def python_class_name(json_name: str) -> str:
    try:
        return _SNAKE_TO_CAMEL(_LOW_CAMEL_TO_SNAKE(json_name))
    except StringCasingError:
        pass

    try:
        parts = split_loose_words(json_name)
    except ValueError:
        return json_name
    return lang.CAMEL_CASE.join(*parts)


def python_field_name(json_name: str) -> str:
    if json_name.startswith('_'):
        return json_name.lstrip('_')

    try:
        return _LOW_CAMEL_TO_SNAKE(json_name)
    except StringCasingError:
        pass

    try:
        return lang.SNAKE_CASE.join(*split_loose_words(json_name))
    except ValueError:
        return json_name


def tag_to_camel(tag: str) -> str:
    return lang.CAMEL_CASE.join(*split_loose_words(tag))


def infer_naming(names: ta.Iterable[str]) -> Naming | None:
    counts: dict[Naming, int] = {}
    for name in names:
        if name.startswith('_'):
            continue
        for naming, casing in [
            (Naming.CAMEL, lang.CAMEL_CASE),
            (Naming.LOW_CAMEL, lang.LOW_CAMEL_CASE),
            (Naming.SNAKE, lang.SNAKE_CASE),
            (Naming.UP_SNAKE, lang.UP_SNAKE_CASE),
            (Naming.KEBAB, lang.KEBAB_CASE),
            (Naming.UP_KEBAB, lang.UP_KEBAB_CASE),
        ]:
            if casing.match(name):
                counts[naming] = counts.get(naming, 0) + 1

    if not counts:
        return None

    best = max(counts.items(), key=lambda kv: kv[1])
    if list(counts.values()).count(best[1]) > 1:
        return None
    return best[0]
