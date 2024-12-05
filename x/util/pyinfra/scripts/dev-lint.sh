#!/usr/bin/env bash

set -euo pipefail

echo "Execute black..."
black ./

echo "Execute flake8..."
flake8

echo "Execute mypy..."
mypy

echo "Linting complete!"
