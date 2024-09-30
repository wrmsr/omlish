import hashlib
import operator
import typing as ta
import urllib.parse
import urllib.request

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json

from .actions import Action
from .consts import SERIALIZATION_VERSION


##


@dc.dataclass(frozen=True)
class Spec(lang.Abstract, lang.Sealed):
    serialization_version: int = dc.field(default=SERIALIZATION_VERSION, kw_only=True)

    actions: ta.Sequence[Action] = dc.field(default=(), kw_only=True)

    @cached.property
    def json(self) -> str:
        return json.dumps_compact(msh.marshal(self, Spec), sort_keys=True)

    @cached.property
    def digest(self) -> str:
        return hashlib.md5(self.json.encode('utf-8')).hexdigest()  # noqa


##


def _maybe_sorted_strs(v: ta.Iterable[str] | None) -> ta.Sequence[str] | None:
    if v is None:
        return None
    return sorted(set(check.not_isinstance(v, str)))


@dc.dataclass(frozen=True)
class GitSpec(Spec):
    url: str

    branch: str | None = dc.field(default=None, kw_only=True)
    rev: str | None = dc.field(default=None, kw_only=True)

    subtrees: ta.Sequence[str] = dc.xfield(default=None, kw_only=True, coerce=_maybe_sorted_strs)


##


@dc.dataclass(frozen=True)
class UrlSpec(Spec):
    url: str = dc.xfield(validate=lambda u: bool(urllib.parse.urlparse(u)))
    file_name: str | None = None

    _: dc.KW_ONLY

    headers: ta.Mapping[str, str] | None = dc.field(default=None) | msh.update_field_metadata(omit_if=operator.not_)

    @cached.property
    def file_name_or_default(self) -> str:
        if self.file_name is not None:
            return self.file_name
        return urllib.parse.urlparse(self.url).path.split('/')[-1]


##


def _repo_str(s: str) -> str:
    u, r = check.non_empty_str(s).split('/')
    check.non_empty_str(u)
    check.non_empty_str(r)
    return s


@dc.dataclass(frozen=True)
class GithubContentSpec(Spec):
    repo: str = dc.field(validate=_repo_str)  # type: ignore
    rev: str
    files: lang.SequenceNotStr[str]


##


@lang.static_init
def _install_standard_marshalling() -> None:
    specs_poly = msh.polymorphism_from_subclasses(Spec, naming=msh.Naming.SNAKE, strip_suffix=True)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [msh.PolymorphismMarshalerFactory(specs_poly)]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [msh.PolymorphismUnmarshalerFactory(specs_poly)]
