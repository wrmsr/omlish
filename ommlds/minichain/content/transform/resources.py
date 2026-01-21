from omlish import lang

from ..content import Content
from ..metadata import ContentOriginal
from ..resources import ResourceContent
from ..standard import StandardContent
from ..text import TextContent
from .visitors import VisitorContentTransform


##


class ResourceContentCache:
    def __init__(self) -> None:
        super().__init__()

        self._cache: dict[tuple[str, str], StandardContent] = {}

    def get(self, rc: ResourceContent) -> StandardContent:
        key = (rc.package, rc.file)

        try:
            return self._cache[key]
        except KeyError:
            pass

        nc = self.load(rc)
        self._cache[key] = nc
        return nc

    def load(self, rc: ResourceContent) -> StandardContent:
        pr = lang.get_package_resources(rc.package)
        rf = pr[rc.file]
        txt = rf.read_text()
        return TextContent(txt)


RESOURCE_CONTENT_CACHE = ResourceContentCache()


##


class ResourceContentMaterializer(VisitorContentTransform[None]):
    def __init__(
            self,
            content_cache: ResourceContentCache | None = None,
    ) -> None:
        super().__init__()

        if content_cache is None:
            content_cache = RESOURCE_CONTENT_CACHE
        self._content_cache = content_cache

    def visit_resource_content(self, c: ResourceContent, ctx: None) -> Content:
        nc = self._content_cache.get(c)
        return nc.with_metadata(ContentOriginal(c))
