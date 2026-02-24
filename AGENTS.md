### Context

**Do these before doing anything**:

- First, read `README.md` and `CODESTYLE.md` to understand the repo.

### DO-NOTS

- Do NOT remove an `@omlish-lite` marker from a source file if one is present. If the file is marked as lite, it is used
  in a lite context, and must remain lite-compatible.
- Do NOT forget the **blank line** after a class or function docstring. For example, do NOT do this:
  ```python
  class MyClass:
      """Some docstring"""
      def __init__(self) -> None:
          """My init method"""
          super().__init__()
  ```
  Do NOT do that because the docstrings are missing blank after them! It SHOULD look like this:
  ```python
  class MyClass:
      """Some docstring"""

      def __init__(self) -> None:
          """My init method"""

          super().__init__()
  ```

### Running stuff

- Do not use the system python - use the `python` executable in the project root to run everything - it will take care
  of virtualenvs and `PYTHONPATH` for you.
  - I repeat: **DO NOT USE THE SYSTEM PYTHON - USE THE `python` EXECUTABLE SCRIPT IN THE REPO ROOT**.
  - In general, prefer to run everything via `./python -m ...`, not via scripts in a venv's `bin/` dir.
- Use pytest to run tests via the `python` script: `./python -m pytest ...`. During iterative development, only run
  tests relevant to code changed.

### Makefile targets

- Run `make fix check` regularly and before committing - it will run linters and typecheckers, but tests are run
  separately. During iterative development, run this after moderate changes when the code is believed to be back in a
  'working' state. Fix all reported issues before committing.
- Run `make gen` to run various code generation steps. This is generally not necessary unless modifying `codegen=True`
  dataclasses.
- Before committing, run `make fix gen check` and ensure that succeeds, then rerun relevant pytests and ensure they
  pass.
