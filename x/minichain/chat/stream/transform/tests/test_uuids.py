from ...types import ContentAiDelta
from ...types import PartialToolUseAiDelta
from ..uuids import TypeSequentialMessageUuidAddingAiDeltaTransform


def test_uuids():
    tfm = TypeSequentialMessageUuidAddingAiDeltaTransform()

    print()
    for d in [
        ContentAiDelta('hi'),
        PartialToolUseAiDelta(id='tu0', name='t0'),
        PartialToolUseAiDelta(raw_args='a'),
        PartialToolUseAiDelta(raw_args='b'),
        PartialToolUseAiDelta(id='tu1', name='t0'),
        PartialToolUseAiDelta(raw_args='c'),
    ]:
        for od in tfm.transform(d):
            print((od, od.metadata))
        print()


def test_uuids_indexed():
    tfm = TypeSequentialMessageUuidAddingAiDeltaTransform()

    print()
    for d in [
        ContentAiDelta('hi'),
        PartialToolUseAiDelta(id='tu0', name='t0', index=0),
        PartialToolUseAiDelta(raw_args='a', index=0),
        PartialToolUseAiDelta(id='tu1', name='t0', index=1),
        PartialToolUseAiDelta(raw_args='b', index=0),
        PartialToolUseAiDelta(raw_args='c', index=1),
        PartialToolUseAiDelta(raw_args='d', index=0),
        PartialToolUseAiDelta(raw_args='e', index=1),
        PartialToolUseAiDelta(raw_args='f', index=1),
    ]:
        for od in tfm.transform(d):
            print((od, od.metadata))
        print()
