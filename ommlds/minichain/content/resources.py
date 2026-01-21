from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .recursive import RecursiveContent


##


@dc.dataclass(frozen=True)
class ResourceContent(RecursiveContent, lang.Final):
    package: str
    file: str


def resource_content(*parts: str) -> ResourceContent:
    *package_parts, file = parts
    for p in check.not_empty(package_parts):
        check.non_empty_str(p)
        check.arg(not (p.startswith('.') or p.endswith('.')))
    return ResourceContent('.'.join(package_parts), file)
