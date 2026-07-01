import dataclasses as dc
import typing as ta


##


class ContentPart:
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
class TextContentPart(ContentPart):
    text: str
    type: ta.Literal['text'] = 'text'


#


@dc.dataclass(frozen=True, kw_only=True)
class ImageUrlContentPart[
    ImageUrlT = ta.Any,
](
    ContentPart,
):
    image_url: ImageUrlT
    type: ta.Literal['image_url'] = 'image_url'
