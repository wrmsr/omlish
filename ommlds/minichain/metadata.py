import abc
import datetime
import typing as ta
import uuid

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ._typedvalues import _tv_field_metadata


##


class Metadata(tv.TypedValue, lang.Abstract, lang.PackageSealed):
    pass


MetadataT = ta.TypeVar('MetadataT', bound=Metadata)


#


class MetadataContainer(
    lang.Abstract,
    lang.PackageSealed,
    ta.Generic[MetadataT],
):
    @property
    @abc.abstractmethod
    def metadata(self) -> tv.TypedValues[MetadataT]:
        raise NotImplementedError

    @abc.abstractmethod
    def with_metadata(
            self,
            *add: MetadataT,
            discard: ta.Iterable[type] | None = None,
            override: bool = False,
    ) -> ta.Self:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class MetadataContainerDataclass(  # noqa
    MetadataContainer[MetadataT],
    lang.Abstract,
):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.state(hasattr(cls, '_metadata'))

    @staticmethod
    def _configure_metadata_field(md_fld, md_cls):
        dc.set_field_metadata(
            check.isinstance(md_fld, dc.Field),
            _tv_field_metadata(
                check.not_none(md_cls),
                marshal_name='metadata',
            ),
        )

    @property
    def metadata(self) -> tv.TypedValues[MetadataT]:
        return check.isinstance(getattr(self, '_metadata'), tv.TypedValues)

    def with_metadata(
            self,
            *add: MetadataT,
            discard: ta.Iterable[type] | None = None,
            override: bool = False,
    ) -> ta.Self:
        new = (old := self.metadata).update(
            *add,
            discard=discard,
            override=override,
        )

        if new is old:
            return self

        return dc.replace(self, _metadata=new)  # type: ignore[call-arg]  # noqa


##


class CommonMetadata(Metadata, lang.Abstract):
    pass


class Uuid(tv.ScalarTypedValue[uuid.UUID], CommonMetadata, lang.Final):
    pass


class CreatedAt(tv.ScalarTypedValue[datetime.datetime], CommonMetadata, lang.Final):
    pass
