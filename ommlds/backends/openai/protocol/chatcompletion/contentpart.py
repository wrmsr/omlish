# ruff: noqa: UP007 UP045
import typing as ta


##


class TextChatCompletionContentPart(ta.TypedDict):
    text: str
    type: ta.Literal['text']


#


class ImageChatCompletionContentPartImageUrl(ta.TypedDict):
    url: ta.Required[str]
    detail: ta.NotRequired[ta.Literal[
        'auto',
        'low',
        'high',
    ]]


class ImageChatCompletionContentPart(ta.TypedDict):
    image_url: ImageChatCompletionContentPartImageUrl
    type: ta.Literal['image_url']


#


class FileChatCompletionContentPartFileInfo(ta.TypedDict, total=False):
    file_data: str
    file_id: str
    filename: str


class FileChatCompletionContentPart(ta.TypedDict):
    file: FileChatCompletionContentPartFileInfo
    type: ta.Literal['file']


#


class InputAudioChatCompletionContentPartInputAudio(ta.TypedDict):
    data: str
    format: ta.Literal[
        'wav',
        'mp3',
    ]


class InputAudioChatCompletionContentPart(ta.TypedDict):
    input_audio: InputAudioChatCompletionContentPartInputAudio
    type: ta.Literal['input_audio']


#


class RefusalChatCompletionContentPart(ta.TypedDict):
    refusal: str
    type: ta.Literal['refusal']


#


ChatCompletionContentPart: ta.TypeAlias = ta.Union[
    TextChatCompletionContentPart,
    ImageChatCompletionContentPart,
    FileChatCompletionContentPart,
    InputAudioChatCompletionContentPart,
    RefusalChatCompletionContentPart,
]
