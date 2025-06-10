"""
TODO:
 - marshal situation
  - is this externally extensible or not? marshal has to know poly
   - manifests? registry? injection?
 - rename 'Detail'?
"""
import abc
import uuid

from omlish import lang
from omlish import typedvalues as tv


##


class ContentMetadata(tv.TypedValue, lang.Abstract):
    pass


#


class MetadataContent(lang.Abstract, lang.PackageSealed):
    @property
    @abc.abstractmethod
    def metadata(self) -> tv.TypedValues[ContentMetadata]:
        raise NotImplementedError


##


class ContentUuid(tv.ScalarTypedValue[uuid.UUID], ContentMetadata, lang.Final):
    pass
