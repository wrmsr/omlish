import typing as ta

from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class SrcLang:
    name: str

    ext: str
    alt_exts: ta.Sequence[str] | None = None

    cmd: str

    std: str | None = None


class SrcLangs(lang.Namespace):
    CPP = SrcLang(
        name='cpp',
        ext='cc',
        alt_exts=['cpp'],
        cmd='clang++',
        std='c++20',
    )

    C = SrcLang(
        name='c',
        ext='c',
        cmd='clang',
        std='c17',
    )


SRC_LANGS_BY_EXT: ta.Mapping[str, SrcLang] = col.make_map([
    (ext, sl)
    for _, sl in SrcLangs
    for ext in [sl.ext, *(sl.alt_exts or [])]
], strict=True)
