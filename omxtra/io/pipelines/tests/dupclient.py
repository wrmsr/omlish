# ruff: noqa: UP045
# @omlish-lite
"""
Baseline (fast)
--conns 100 --requests-per-conn 200 --pipeline-depth 1

Slow readers (forces server backpressure)
--conns 50 --requests-per-conn 200 --pipeline-depth 1 --recv-read-size 64 --recv-sleep 0.002 --recv-jitter 0.002

Pipelining + slow readers (really pressures server buffering)
--conns 20 --requests-per-conn 200 --pipeline-depth 8 --recv-read-size 64 --recv-sleep 0.005 --recv-jitter 0.003

Fragmented sends
--conns 50 --requests-per-conn 200 --pipeline-depth 4 --send-chunk 3 --send-sleep 0.0005 --send-jitter 0.0005

Recipe A: pipeline pressure (client pushes ahead)
--conns 50 --requests-per-conn 200 --pipeline-depth 32 --recv-read-size 4096 --recv-sleep 0 --send-chunk 0

Recipe B: slow readers (forces outbound backpressure)
--conns 20 --requests-per-conn 100 --pipeline-depth 8 --recv-read-size 64 --recv-sleep 0.01 --recv-jitter 0.005

Recipe C: slow producer + pipelining (server can't keep up "upstream")
(server: --port 5003 --delay-ms 2 --delay-jitter-ms 2 --lines-per-chunk 16)
--conns 50 --requests-per-conn 200 --pipeline-depth 64 --recv-read-size 4096 --recv-sleep 0
"""
import argparse
import asyncio
import dataclasses as dc
import random
import string
import time
import typing as ta


##


def jittered_sleep(base: float, jitter: float) -> float:
    if base <= 0 and jitter <= 0:
        return 0.0
    j = (random.random() * 2.0 - 1.0) * jitter
    return max(0.0, base + j)


def make_text(line_len: int) -> str:
    # printable-ish ASCII, no newlines
    alphabet = string.ascii_letters + string.digits + ' .,:;_-+=/@'
    return ''.join(random.choice(alphabet) for _ in range(line_len))


@dc.dataclass()
class Knobs:
    host: str
    port: int
    conns: int
    requests_per_conn: int
    pipeline_depth: int

    min_n: int
    max_n: int
    line_len: int

    # sender behavior
    send_sleep: float
    send_jitter: float
    send_chunk: int  # bytes per write chunk (simulate fragmentation)

    # receiver behavior
    recv_sleep: float
    recv_jitter: float
    recv_read_size: int  # bytes per read call (simulate small reads)

    timeout: float
    seed: ta.Optional[int]


async def write_with_chunking(
        writer: asyncio.StreamWriter,
        data: bytes,
        chunk: int,
        sleep: float,
        jitter: float,
) -> None:
    if chunk <= 0 or chunk >= len(data):
        writer.write(data)
        await writer.drain()
        s = jittered_sleep(sleep, jitter)
        if s:
            await asyncio.sleep(s)
        return

    i = 0
    n = len(data)
    while i < n:
        j = min(n, i + chunk)
        writer.write(data[i:j])
        await writer.drain()
        i = j
        s = jittered_sleep(sleep, jitter)
        if s:
            await asyncio.sleep(s)


async def read_until_double_newline(
        reader: asyncio.StreamReader,
        read_size: int,
        sleep: float,
        jitter: float,
        timeout: float,
) -> bytes:
    buf = bytearray()
    deadline = time.monotonic() + timeout
    needle = b'\n\n'

    while True:
        if time.monotonic() > deadline:
            raise TimeoutError('timed out waiting for response terminator (\\n\\n)')

        # Check first to avoid extra reads.
        idx = buf.find(needle)
        if idx != -1:
            # include the needle; leave any extra bytes (shouldn't happen with this protocol unless server is buggy)
            return bytes(buf[: idx + len(needle)])

        # Read more
        to = max(0.0, deadline - time.monotonic())
        chunk = await asyncio.wait_for(reader.read(read_size), timeout=to)
        if not chunk:
            raise ConnectionError('server closed connection while reading response')
        buf.extend(chunk)

        s = jittered_sleep(sleep, jitter)
        if s:
            await asyncio.sleep(s)


def validate_response(resp: bytes, n: int, text: str) -> None:
    # resp should end with \n\n
    if not resp.endswith(b'\n\n'):
        raise AssertionError(f'response does not end with \\n\\n: tail={resp[-50:]!r}')

    body = resp[:-2]  # strip terminator
    if not body and n != 0:
        raise AssertionError(f'empty body but n={n}')

    # Split into lines; for n==0 body is b"".
    lines = [] if body == b'' else body.split(b'\n')
    # If body != "" it should not have trailing newline because we stripped only terminator, but body itself contains
    # each repetition ending with \n, so split() yields a trailing empty.
    # Example: "hi\nhi\n" split -> [b"hi", b"hi", b""]
    if lines and lines[-1] == b'':
        lines = lines[:-1]

    if len(lines) != n:
        raise AssertionError(f'expected {n} lines, got {len(lines)}')

    want = text.encode('ascii', 'strict')
    for i, ln in enumerate(lines):
        if ln != want:
            raise AssertionError(f'line {i} mismatch: got={ln!r} want={want!r}')


async def one_connection(conn_id: int, k: Knobs) -> dict:
    reader, writer = await asyncio.open_connection(k.host, k.port)
    in_flight = 0
    sent = 0
    ok = 0
    fail = 0

    try:
        for req_i in range(k.requests_per_conn):  # noqa
            n = random.randint(k.min_n, k.max_n)
            text = make_text(k.line_len)

            req = f'{n}\n{text}\n'.encode('ascii', 'strict')

            # Optionally pipeline: allow up to pipeline_depth outstanding requests before reading responses.
            await write_with_chunking(writer, req, k.send_chunk, k.send_sleep, k.send_jitter)
            sent += 1
            in_flight += 1

            # If we hit pipeline depth, read one response.
            while in_flight >= max(1, k.pipeline_depth):
                resp = await read_until_double_newline(  # noqa
                    reader,
                    read_size=max(1, k.recv_read_size),
                    sleep=k.recv_sleep,
                    jitter=k.recv_jitter,
                    timeout=k.timeout,
                )

                # We don't know which request it corresponds to if you randomize per request. So: when pipelining, we
                # must remember expected (n,text) per in-flight request. Simplicity: disable randomization across
                # in-flight by storing a queue.
                raise RuntimeError('internal: pipeline queue not implemented')

        # Drain remaining responses (non-pipelined mode uses depth=1 so in_flight should be 0 here)
        return {'conn_id': conn_id, 'sent': sent, 'ok': ok, 'fail': fail}

    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:  # noqa
            pass


async def one_connection_with_queue(conn_id: int, k: Knobs) -> dict:
    reader, writer = await asyncio.open_connection(k.host, k.port)
    q: list[tuple[int, str]] = []  # in-flight expectations
    sent = 0
    ok = 0
    fail = 0

    async def read_one() -> None:
        nonlocal ok, fail
        (n, text) = q.pop(0)
        resp = await read_until_double_newline(
            reader,
            read_size=max(1, k.recv_read_size),
            sleep=k.recv_sleep,
            jitter=k.recv_jitter,
            timeout=k.timeout,
        )
        try:
            validate_response(resp, n, text)
            ok += 1
        except Exception as e:  # noqa
            fail += 1
            # Keep going to surface more issues
            print(f'[conn {conn_id}] validation failed: {e}')

    try:
        for _ in range(k.requests_per_conn):
            n = random.randint(k.min_n, k.max_n)
            text = make_text(k.line_len)
            req = f'{n}\n{text}\n'.encode('ascii', 'strict')

            await write_with_chunking(writer, req, k.send_chunk, k.send_sleep, k.send_jitter)
            q.append((n, text))
            sent += 1

            while len(q) >= max(1, k.pipeline_depth):
                await read_one()

        while q:
            await read_one()

        return {'conn_id': conn_id, 'sent': sent, 'ok': ok, 'fail': fail}

    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:  # noqa
            pass


async def main_async(k: Knobs) -> None:
    if k.seed is not None:
        random.seed(k.seed)

    t0 = time.time()
    tasks = [asyncio.create_task(one_connection_with_queue(i, k)) for i in range(k.conns)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    dt = time.time() - t0

    total_sent = 0
    total_ok = 0
    total_fail = 0
    crashed = 0

    r: ta.Any
    for r in results:
        if isinstance(r, Exception):
            crashed += 1
            print(f'[task] crashed: {r!r}')
            continue
        total_sent += r['sent']
        total_ok += r['ok']
        total_fail += r['fail']

    rps = total_ok / dt if dt > 0 else 0.0
    print(
        f'duration={dt:.3f}s '
        f'conns={k.conns} '
        f'sent={total_sent} '
        f'ok={total_ok} '
        f'fail={total_fail} '
        f'crashed={crashed} '
        f'rps={rps:.1f}',
    )


def parse_args() -> Knobs:
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=5003)

    ap.add_argument('--conns', type=int, default=50)
    ap.add_argument('--requests-per-conn', type=int, default=200)
    ap.add_argument('--pipeline-depth', type=int, default=1, help='>1 pipelines requests (pressures server buffering)')

    ap.add_argument('--min-n', type=int, default=0)
    ap.add_argument('--max-n', type=int, default=2000)
    ap.add_argument('--line-len', type=int, default=32)

    ap.add_argument('--send-sleep', type=float, default=0.0)
    ap.add_argument('--send-jitter', type=float, default=0.0)
    ap.add_argument('--send-chunk', type=int, default=0, help='bytes per write() chunk; 0 disables chunking')

    ap.add_argument('--recv-sleep', type=float, default=0.0)
    ap.add_argument('--recv-jitter', type=float, default=0.0)
    ap.add_argument('--recv-read-size', type=int, default=4096)

    ap.add_argument('--timeout', type=float, default=30.0)
    ap.add_argument('--seed', type=int, default=None)

    a = ap.parse_args()
    return Knobs(
        host=a.host,
        port=a.port,
        conns=a.conns,
        requests_per_conn=a.requests_per_conn,
        pipeline_depth=a.pipeline_depth,
        min_n=a.min_n,
        max_n=a.max_n,
        line_len=a.line_len,
        send_sleep=a.send_sleep,
        send_jitter=a.send_jitter,
        send_chunk=a.send_chunk,
        recv_sleep=a.recv_sleep,
        recv_jitter=a.recv_jitter,
        recv_read_size=a.recv_read_size,
        timeout=a.timeout,
        seed=a.seed,
    )


def main() -> None:
    k = parse_args()
    asyncio.run(main_async(k))


if __name__ == '__main__':
    main()
