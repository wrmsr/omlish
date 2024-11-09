#!/bin/bash

# Check if a directory is provided
if [ -z "$1" ]; then
    echo "Usage: pycharm-open <directory>"
    exit 1
fi

PROJECT_PATH=$(realpath "$1")

# Check if PyCharm is already running
if pgrep -x "pycharm.sh" > /dev/null; then
    echo "PyCharm is already running. Opening project..."

    # Bring PyCharm to the foreground
    wmctrl -a "PyCharm"

    # Simulate the keyboard shortcut to open a new project
    xdotool key --delay 100 ctrl+shift+a
    xdotool type "$PROJECT_PATH"
    xdotool key Return
else
    echo "Starting PyCharm with project..."
    nohup pycharm.sh "$PROJECT_PATH" > /dev/null 2>&1 &
fi
