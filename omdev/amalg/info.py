# ruff: noqa: UP045
# @omlish-lite
import typing as ta


##


AMALG_INFO_ATTR = '__omlish_amalg__'


class AmalgInfoSrcFile(ta.NamedTuple):
    path: str
    sha1: str


class AmalgInfo(ta.NamedTuple):
    src_files: ta.Sequence[AmalgInfoSrcFile]


def get_amalg_info() -> ta.Optional[AmalgInfo]:
    try:
        fn = globals()[AMALG_INFO_ATTR]
    except KeyError:
        return None
    dct = fn()
    dct['src_files'] = [AmalgInfoSrcFile(**sf_dct) for sf_dct in dct['src_files']]
    return AmalgInfo(**dct)


def is_amalg() -> bool:
    return AMALG_INFO_ATTR in globals()
