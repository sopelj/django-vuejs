#!/usr/bin/env bash
echo "[Running Coala]"
docker run -ti -v "$(pwd):/app" --workdir=/app coala/base coala "$@"
find . -name '*.orig' -delete
echo "Done"
echo
