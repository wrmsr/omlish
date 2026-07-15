# @om-precheck-allow-any-unicode
from ..sse import StrSseDecoder
from ..sse import Utf8SseDecoder


def decode_all(text, chunk_size=1):
    decoder = StrSseDecoder()
    events: list = []
    for i in range(0, len(text), chunk_size):
        events.extend(decoder.feed(text[i:i + chunk_size]))
    events.extend(decoder.finish())
    return events


def test_basic_event():
    events = decode_all('event: message_start\ndata: {"a": 1}\n\n')
    assert len(events) == 1
    assert events[0].event == 'message_start'
    assert events[0].data == '{"a": 1}'


def test_data_only_event():
    events = decode_all('data: hello\n\n')
    assert len(events) == 1
    assert events[0].event is None
    assert events[0].data == 'hello'


def test_multi_line_data():
    events = decode_all('data: line1\ndata: line2\n\n')
    assert len(events) == 1
    assert events[0].data == 'line1\nline2'


def test_comments_ignored():
    events = decode_all(': comment\ndata: x\n\n')
    assert len(events) == 1
    assert events[0].data == 'x'


def test_crlf_line_endings():
    events = decode_all('event: e1\r\ndata: d1\r\n\r\ndata: d2\r\n\r\n', chunk_size=3)
    assert len(events) == 2
    assert events[0].event == 'e1'
    assert events[0].data == 'd1'
    assert events[1].data == 'd2'


def test_trailing_event_without_blank_line():
    events = decode_all('data: incomplete')
    assert len(events) == 1
    assert events[0].data == 'incomplete'


def test_sse_events_over_bytes():
    text = 'event: a\ndata: {"x": "é中"}\n\ndata: end\n\n'
    data = text.encode('utf-8')

    dec = Utf8SseDecoder()
    events: list = []

    # Byte-level chunks that split multi-byte UTF-8 sequences.
    for i in range(0, len(data), 3):
        events.extend(dec.feed(data[i:i + 3]))
    events.extend(dec.finish())

    assert len(events) == 2
    assert events[0].event == 'a'
    assert events[0].data == '{"x": "é中"}'
    assert events[1].data == 'end'


def test_fuzz():
    import random

    def run(cls, chunks):
        d = cls()
        out = []
        for c in chunks:
            out.append(('feed', list(d.feed(c))))
        out.append(('finish', list(d.finish())))
        return out

    toks = [
        'event', 'data', 'id', 'retry', ':', ': ', ':ok', ' ', '\r', '\n', '\r\n',
        'x', 'yz', '', 'a: b', '\r\r', '\n\n', '\r\n\r\n', 'événement',
    ]

    def random_doc(rng):
        return ''.join(rng.choice(toks) for _ in range(rng.randrange(0, 60)))

    def random_chunks(rng, s):
        chunks = []
        i = 0
        while i < len(s):
            j = i + rng.randrange(1, 6)
            chunks.append(s[i:j])
            i = j
        for _ in range(rng.randrange(0, 3)):
            chunks.insert(rng.randrange(0, len(chunks) + 1), '')
        return chunks

    # Targeted edge cases first.
    targeted = [
        [],
        [''],
        ['\r'],
        ['\n'],
        ['\r', '\n'],
        ['\r', '\r'],
        ['\r', 'x'],
        ['data: x\r'],
        ['data: x\r', '\n'],
        ['data: x\r', '\ndata: y\n\n'],
        ['data: x\r', '\r'],
        ['data: x\r', 'data: y\n\n'],
        ['da', 'ta: x\n', '\n'],
        ['event: a\ndata: b\n\n'],
        ['event: a\r\ndata: b\r\n\r\n'],
        ['event: a\rdata: b\r\r'],
        [': comment\ndata: hi\n\n'],
        ['data: trailing no break'],
        ['data: trailing cr\r'],
        ['\n\n\n\n'],
        ['a\rb\rc\r'],
        ['x' * 100, '\n', 'y' * 100, '\n\n'],
        ['\r\n' * 5],
        list('event: a\r\ndata: b\r\n\r\ndata: c\n\n'),  # 1-char chunks
    ]

    for chunks in targeted:
        run(StrSseDecoder, chunks)

    for seed in range(500):
        rng = random.Random(seed)
        s = random_doc(rng)
        chunks = random_chunks(rng, s)
        run(StrSseDecoder, chunks)

    for seed in range(500):
        rng = random.Random(10 ** 9 + seed)
        dn = StrSseDecoder()
        outs_n = []
        for _ in range(2):
            s = random_doc(rng)
            for c in random_chunks(rng, s):
                outs_n.append(list(dn.feed(c)))
            outs_n.append(list(dn.finish()))
