#!/usr/bin/env bash
set -ex

find tinygrad -name '*.py' | egrep -o '^[^/]+/' | sort | uniq | \
    xargs ../.venv/bin/black

# sed -e 's/2/4/g' -i '' .editorconfig
rm tinygrad/.editorconfig
