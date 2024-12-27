#!/bin/sh
set -e

if [ -z "${VENV}" ] ; then
    if [ $(uname) = "Linux" ] && (cat /proc/mounts | grep -E '^overlay / .*/(docker|desktop-containerd)/' > /dev/null) ; then
        VENV=docker
    else
        VENV=default
    fi
fi

SCRIPT_DIR=$(dirname "$0")
VENV_PYTHON_PATH="$SCRIPT_DIR/.venvs/$VENV/bin/python"
if [ -f "$VENV_PYTHON_PATH" ] ; then
    PYTHON="$VENV_PYTHON_PATH"
elif command -v python3 &> /dev/null ; then
    PYTHON=python3
else
    PYTHON=python
fi

export PYTHONPATH="$PYTHONPATH:."

if [ $# -eq 0 ] && "$PYTHON" -c "import IPython" 2> /dev/null ; then
    exec "$PYTHON" -m IPython
else
    exec "$PYTHON" "$@"
fi
