import functools

from ..sse import SseComment
from ..sse import SseDecoder
from ..sse import SseEvent


_message_event = functools.partial(SseEvent, b'message')


TESTS = [

    (
        [
            b'data: YHOO',
            b'data: +2',
            b'data: 10',
            b'',
        ],
        [
            _message_event(b'YHOO\n+2\n10'),
        ],
    ),

    (
        [
            b': test stream',
            # b'',  # FIXME: ???
            b'data: first event',
            b'id: 1',
            b'',
            b'data:second event',
            b'id',
            b'',
            b'data:  third event',
            b'',
        ],
        [
            SseComment(b': test stream'),
            _message_event(b'first event', last_id=b'1'),
            _message_event(b'second event'),
            _message_event(b' third event'),
        ],
    ),

    (
        [
            b'data',
            b'',
            b'data',
            b'data',
            b'',
            b'data:',
        ],
        [
            _message_event(b''),
            _message_event(b'\n'),
        ],
    ),

    (
        [
            b'data:test',
            b'',
            b'data: test',
            b'',
        ],
        [
            _message_event(b'test'),
            _message_event(b'test'),
        ],
    ),

    (
        [
            b'event: add',
            b'data: 73857293',
            b'',
            b'event: remove',
            b'data: 2153',
            b'',
            b'event: add',
            b'data: 113411',
            b'',
        ],
        [
            SseEvent(b'add', b'73857293'),
            SseEvent(b'remove', b'2153'),
            SseEvent(b'add', b'113411'),
        ],
    ),

]


def test_sse():
    for i, (test, expected) in enumerate(TESTS):
        print(i)
        dec = SseDecoder()
        output = [
            event
            for line in test
            for event in dec.process_line(line)
        ]
        print(output)
        print()
        assert output == expected
