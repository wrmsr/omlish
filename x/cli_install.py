#!/usr/bin/env python3
"""
if uv --version 2>/dev/null ; then \
    MGR="uv tool" ; \
    INST="install --prerelease=allow --python=${INSTALL_PYTHON_VERSION}"; \
    INJ="--with" ; \
else \
    MGR="pipx" ; \
    INST="install"; \
    INJ="--preinstall" ; \
fi ; \
\
CMD="$$MGR uninstall omdev-cli || true ; $$MGR $$INST omdev-cli" ; \
for D in ${INSTALL_EXTRAS} ; do \
    CMD+=" $$INJ $$D" ; \
done ; \
${SHELL} -c "$$CMD"
"""
import sys


def _main() -> None:
    if sys.version_info < (3, 8):
        raise RuntimeError(f'Unsupported python version: {sys.version_info}')

    raise NotImplementedError


if __name__ == '__main__':
    _main()
