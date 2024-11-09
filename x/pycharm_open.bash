#!/bin/bash

# Check if a directory is provided
if [ -z "$1" ]; then
    echo "Usage: pycharm-open <directory>"
    exit 1
fi

# Run the AppleScript with the directory path as an argument
osascript pycharm_open.scpt "$1"

