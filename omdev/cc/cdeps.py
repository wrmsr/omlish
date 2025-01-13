import dataclasses as dc
import tomllib
import typing as ta

from omlish import cached
from omlish import lang
from omlish import marshal as msh


@dc.dataclass(frozen=True)
class Cdep:
    @dc.dataclass(frozen=True)
    class Git:
        url: str
        rev: str

        subtrees: ta.Sequence[str] | None = None

    git: Git

    #

    include: ta.Sequence[str] | None = None

    #

    @dc.dataclass(frozen=True)
    class Cmake:
        fetch_content_url: str | None = None

    cmake: Cmake | None = None


@cached.function
def load_cdeps() -> ta.Mapping[str, Cdep]:
    src = lang.get_relative_resources(globals=globals())['cdeps.toml'].read_text()
    dct = tomllib.loads(src)
    return msh.unmarshal(dct.get('deps', {}), ta.Mapping[str, Cdep])  # type: ignore
