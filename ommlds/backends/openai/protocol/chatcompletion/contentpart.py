import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


class ChatCompletionContentPart(lang.Abstract):
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
class TextChatCompletionContentPart(ChatCompletionContentPart, lang.Final):
    text: str


#


@dc.dataclass(frozen=True, kw_only=True)
class ImageUrlChatCompletionContentPart(ChatCompletionContentPart, lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    class ImageUrl(lang.Final):
        url: str
        detail: ta.Literal[
            'auto',
            'low',
            'high',
        ]

    image_url: ImageUrl


#


@dc.dataclass(frozen=True, kw_only=True)
class FileChatCompletionContentPart(ChatCompletionContentPart, lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    class File(lang.Final):
        file_data: str | None = None
        file_id: str | None = None
        filename: str | None = None

    file: File


#


@dc.dataclass(frozen=True, kw_only=True)
class InputAudioChatCompletionContentPart(ChatCompletionContentPart, lang.Final):
    @dc.dataclass(frozen=True, kw_only=True)
    class InputAudio(lang.Final):
        data: str
        format: ta.Literal[
            'wav',
            'mp3',
        ]

    input_audio: InputAudio


#


@dc.dataclass(frozen=True, kw_only=True)
class RefusalChatCompletionContentPart(ChatCompletionContentPart, lang.Final):
    refusal: str
