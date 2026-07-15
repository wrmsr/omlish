import typing as ta

from omcore import dataclasses as dc

from .typetags import TypeTagged


##


class ContentPart(
    TypeTagged,
    type_tag_field='type',
):
    pass


#


@dc.dataclass(frozen=True, kw_only=True)
class TextContentPart(
    ContentPart,
    type_tag='text',
):
    text: str


#


@dc.dataclass(frozen=True, kw_only=True)
class ImageUrlContentPart[
    ImageUrlT = ta.Any,
](
    ContentPart,
    type_tag='image_url',
):
    image_url: ImageUrlT
