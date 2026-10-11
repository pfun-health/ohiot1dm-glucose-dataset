#!/usr/bin/env sh

set -e

# install.sh

# installation for alpine 3.24

if [ "$(uv sync | python -c $'import sys; val = "true" if "--python-platform" in "".join(sys.stdin.readlines()) else ""; print(val)')" ]; then
	uv sync --python-platform=x86_64-manylinux_2_28
else
	uv sync --dev
fi
