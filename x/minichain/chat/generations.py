"""
Not really sure how this'll work out - the first decoupling of 'Outputs' from 'Services', and some weird midpoint
inheriting part of the complexity of 'Response' and part of the complexity of 'Message', but the whole chat api is
currently broken and has to be fixed somehow. Let's see if this sticks :|

TODO:
 - originals?
  - generalized 'Original' system now? 3 cvars..
  - drop this whole thing?
"""
import typing as ta

from omcore import check
from omcore import dataclasses as dc
from omcore import lang
from omcore import typedvalues as tv

from .._typedvalues import _tv_field_metadata
from ..metadata import CommonMetadata
from ..metadata import Metadata
from ..metadata import MetadataContainerDataclass
from ..registries.globals import register_type
from .messages import AiChat
from .types import ChatOutputs


##


# @om-manifest $.minichain.registries.manifests.RegistryTypeManifest
class ChatGenerationMetadata(Metadata, lang.Abstract):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        check.state(cls.__name__.endswith('ChatGenerationMetadata'))


register_type(ChatGenerationMetadata, module=__name__)


ChatGenerationMetadatas: ta.TypeAlias = ChatGenerationMetadata | CommonMetadata


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class ChatGeneration(MetadataContainerDataclass[ChatGenerationMetadatas], lang.Final):
    chat: AiChat

    #

    _outputs: ta.Sequence[ChatOutputs] = dc.field(
        default=(),
        metadata=_tv_field_metadata(
            ChatOutputs,
            marshal_name='outputs',
        ),
    )

    @property
    def outputs(self) -> tv.TypedValues[ChatOutputs]:
        return check.isinstance(self._outputs, tv.TypedValues)

    def with_outputs(
            self,
            *add: ChatOutputs,
            discard: ta.Literal['all'] | ta.Iterable[type] | None = None,
            mode: ta.Literal['append', 'prepend', 'override', 'default'] = 'append',
            # no_original: bool = False,
    ) -> ta.Self:
        new = (old := self.outputs).update(
            *add,
            discard=discard,
            mode=mode,
        )

        if new is old:
            return self

        # if not no_original:
        #     return self.replace(self, _outputs=new)
        return dc.replace(self, _outputs=new)

    #

    _metadata: ta.Sequence[ChatGenerationMetadatas] = dc.field(
        default=(),
        kw_only=True,
        repr=False,
    )

    MetadataContainerDataclass._configure_metadata_field(_metadata, ChatGenerationMetadatas)  # noqa
