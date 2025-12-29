- First, read `README.md` and `CODESTYLE.md` to understand the repo.
- Use the `python` executable in the project root to run everything - it will take care of virtualenvs and `PYTHONPATH`
  for you.
- Use pytest to run tests via the `python` script: `./python -m pytest ...`.
- Run `make check` after significant changes and before committing - it will run linters and typecheckers, but tests are
  run separately.
