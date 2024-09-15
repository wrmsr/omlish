"""
TODO:
 - https://crates.io/crates/rusty_v8
"""
import io
import os
import subprocess
import tempfile
import textwrap
import typing as ta


def build_loop(func: str, setup: str = '') -> str:
    return textwrap.dedent(f"""
        {setup}
        (function(fn) {{
          const readline = require('readline');
          async function run() {{
            const lines = readline.createInterface({{
              input: process.stdin,
              crlfDelay: Infinity
            }});
            for await (const line of lines) {{
              process.stdout.write(JSON.stringify(fn(JSON.parse(line))) + '\\n');
            }}
          }}
          return run
        }})({func})()
    """)


def launch_node(body: str, *, tag: ta.Optional[str] = None) -> subprocess.Popen:
    fd, path = tempfile.mkstemp((('-' + tag) if tag is not None else '') + '.js')
    os.close(fd)

    with open(path, 'w') as f:
        f.write(body)

    return subprocess.Popen(
        ['node', path],
        bufsize=1024 * 1024,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )


##


JS_WITH_MINML_HEADER = """
/*
args: {
  x: int,
  y: int,
]
*/

call_count = 0;

function add2(x, y) {
  call_count += 1;
  return x + 2;
}
"""


def _cut_lines(chunks, max_buf_size=10 * 1024 * 1024, Buf=io.StringIO):  # noqa
    buf = Buf()
    for chunk in chunks:
        if os.linesep not in chunk:
            buf.write(chunk)
        else:
            line_chunks = chunk.splitlines()
            buf.write(line_chunks[0])
            yield buf.getvalue()
            if buf.tell() > max_buf_size:
                buf.close()
                buf = Buf()
            else:
                buf.seek(0, 0)
                buf.truncate()
            if len(line_chunks) > 1:
                for i in range(1, len(line_chunks) - 1):
                    yield line_chunks[i]
                buf.write(line_chunks[-1])
    if buf.tell() > 0:
        yield buf.getvalue()


def test_fallback_js(tmpdir):
    loop = build_loop('function(s){ return s + "!" }')
    proc = launch_node(loop)

    lines = _cut_lines(iter(io.TextIOWrapper(proc.stdout).readline, ''))

    proc.stdin.write(b'"abc"\n')
    proc.stdin.write(b'"def"\n')
    proc.stdin.write(b'"ghi"\n')
    proc.stdin.flush()
    proc.stdin.close()

    print(list(lines))

    rc = proc.wait()
    print(rc)
