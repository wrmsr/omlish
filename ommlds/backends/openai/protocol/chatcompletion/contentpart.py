import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from .._common import _set_class_marshal_options


##


@msh.set_polymorphic_from_subclasses(
    type_tagging=msh.FieldTypeTagging('type'),
    naming=msh.Naming.SNAKE,
    strip_suffix=True,
)
class ChatCompletionContentPart(lang.Abstract, lang.Sealed):
    pass


#


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class TextChatCompletionContentPart(ChatCompletionContentPart, lang.Final):
    text: str


#


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class ImageUrlChatCompletionContentPart(ChatCompletionContentPart, lang.Final):
    @dc.dataclass(frozen=True)
    class ImageUrl(lang.Final):
        url: str
        detail: ta.Literal[
            'auto',
            'low',
            'high',
        ]

    image_url: ImageUrl


#


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class FileChatCompletionContentPart(ChatCompletionContentPart, lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    class File(lang.Final):
        file_data: str | None = None
        file_id: str | None = None
        filename: str | None = None

    file: File


#


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class InputAudioChatCompletionContentPart(ChatCompletionContentPart, lang.Final):
    @dc.dataclass(frozen=True)
    @_set_class_marshal_options
    class InputAudio(lang.Final):
        data: str
        format: ta.Literal[
            'wav',
            'mp3',
        ]

    input_audio: InputAudio


#


@dc.dataclass(frozen=True)
@_set_class_marshal_options
class RefusalChatCompletionContentPart(ChatCompletionContentPart, lang.Final):
    refusal: str
