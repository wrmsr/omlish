- First, read `README.md` and `CODESTYLE.md` to understand the repo.
- Use the `python` executable in the project root to run everything - it will take care of virtualenvs and `PYTHONPATH`
  for you. In general, prefer to run everything via `./python -m ...`, not via scripts in a venv's `bin/` dir.
- Use pytest to run tests via the `python` script: `./python -m pytest ...`. During iterative development, only run
  tests relevant to code changed.
- Run `make fix` after significant changes to fix simple formatting issues - this command should never fail, but may
  rewrite some files, so be sure to check for modifications after running. It isn't necessary to run this frequently
  during iterative development - doing so would likely result in having to re-read files which changed only by simple
  formatting tweaks.
- Run `make check` regularly and before committing - it will run linters and typecheckers, but tests are run separately.
  During iterative development, run this after moderate changes when the code is believed to be back in a 'working'
  state. Fix all reported issues before committing.
- Run `make gen` to run various code generation steps. This is generally not necessary unless modifying `codegen=True`
  dataclasses.
- Before committing, run `make fix gen check` and ensure that succeeds, then rerun relevant pytests and ensure they
  pass.
