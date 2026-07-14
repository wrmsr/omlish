import base64
import dataclasses as dc
import json
import pickle
import typing as ta

from rich.segment import Segment

from omcore.http.pipelines.websockets.objects import IoPipelineWebsocketText


##


Message = dict[str, ta.Any]


@dc.dataclass(frozen=True)
class DevtoolsWebsocketSend:
    message: ta.Any


def encode_message(message: ta.Mapping[str, ta.Any]) -> IoPipelineWebsocketText:
    return IoPipelineWebsocketText(json.dumps(message, separators=(',', ':')))


def decode_message(message: IoPipelineWebsocketText | str) -> Message:
    if isinstance(message, IoPipelineWebsocketText):
        text = message.text
    else:
        text = message

    obj = json.loads(text)
    if not isinstance(obj, dict):
        raise TypeError(obj)
    return obj


def encode_segments(segments: list[Segment]) -> str:
    pickled = pickle.dumps(segments, protocol=4)
    return base64.b64encode(pickled).decode('ascii')


def decode_segments(encoded: str) -> list[Segment]:
    obj = pickle.loads(base64.b64decode(encoded.encode('ascii')))  # noqa
    if not isinstance(obj, list):
        raise TypeError(obj)
    return obj
