from ..joining import AiDeltaJoiner
from ..types import ContentAiDelta
from ..types import PartialToolUseAiDelta


def test_joiner():
    adj = AiDeltaJoiner()
    adj.add([
        ContentAiDelta('hi'),
        PartialToolUseAiDelta(id='tu0', name='t0'),
        PartialToolUseAiDelta(raw_args='"'),
        PartialToolUseAiDelta(raw_args='a'),
        PartialToolUseAiDelta(raw_args='b'),
        PartialToolUseAiDelta(raw_args='"'),
        PartialToolUseAiDelta(id='tu1', name='t0'),
        PartialToolUseAiDelta(raw_args='"'),
        PartialToolUseAiDelta(raw_args='c'),
        PartialToolUseAiDelta(raw_args='"'),
    ])
    for m in adj.build():
        print((m, m.metadata))


def test_joiner_indexed():
    adj = AiDeltaJoiner()
    adj.add([
        ContentAiDelta('hi'),
        PartialToolUseAiDelta(id='tu0', name='t0', index=0),
        PartialToolUseAiDelta(raw_args='"', index=0),
        PartialToolUseAiDelta(raw_args='a', index=0),
        PartialToolUseAiDelta(id='tu1', name='t0', index=1),
        PartialToolUseAiDelta(raw_args='b', index=0),
        PartialToolUseAiDelta(raw_args='"', index=1),
        PartialToolUseAiDelta(raw_args='c', index=1),
        PartialToolUseAiDelta(raw_args='d', index=0),
        PartialToolUseAiDelta(raw_args='e', index=1),
        PartialToolUseAiDelta(raw_args='f', index=1),
        PartialToolUseAiDelta(raw_args='"', index=0),
        PartialToolUseAiDelta(raw_args='"', index=1),
    ])
    for m in adj.build():
        print((m, m.metadata))
