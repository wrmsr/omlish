import dataclasses as dc
import tomllib
import typing as ta

from omlish import cached
from omlish import lang
from omlish import marshal as msh
from omlish.configs import all as cfgs


##


@dc.dataclass(frozen=True)
class Cdep:
    @dc.dataclass(frozen=True)
    class Git:
        url: str
        rev: str

        subtrees: ta.Sequence[str] | None = None

    git: Git

    #

    sources: ta.Sequence[str] | None = None
    include: ta.Sequence[str] | None = None

    #

    @dc.dataclass(frozen=True)
    class Cmake:
        @dc.dataclass(frozen=True)
        class FetchContent:
            url: str | None = None

            @dc.dataclass(frozen=True)
            class Git:
                repository: str | None = None
                tag: str | None = None

            git: Git | None = None

        fetch_content: FetchContent | None = None

    cmake: Cmake | None = None


def process_marshaled_cdep(obj: ta.Any) -> ta.Any:
    obj = cfgs.processing.matched_rewrite(
        lambda s: s if isinstance(s, str) else ''.join(s),
        obj,
        ('sources', None),
        ('include', None),
    )

    return obj


@cached.function
def load_cdeps() -> ta.Mapping[str, Cdep]:
    src = lang.get_relative_resources(globals=globals())['cdeps.toml'].read_text()
    dct = tomllib.loads(src)

    dct = {
        **dct,
        'deps': {
            k: process_marshaled_cdep(v)
            for k, v in dct.get('deps', {}).items()
        },
    }

    return msh.unmarshal(dct.get('deps', {}), ta.Mapping[str, Cdep])
