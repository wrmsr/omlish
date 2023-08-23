#!/usr/bin/env bash
set -ex

find tinygrad -name '*.py' | egrep -o '^[^/]+/' | sort | uniq | \
    xargs ../.venv/bin/black

# sed -e 's/2/4/g' -i '' .editorconfig
rm tinygrad/.editorconfig

sed -i '' '/^    def __init__(self, name: str, prg: str,.*/a \
        print(prg)\
        print()\
' tinygrad/tinygrad/runtime/ops_gpu.py

sed -i '' '/class _Device:.*/i \
__import__("os").environ["GPU"] = "1"\
\
\
' tinygrad/tinygrad/ops.py
