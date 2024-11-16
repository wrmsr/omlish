import os.path

import jedi
import jedi.inference.references

from omlish import lang


@lang.static_init
def _patch_jedi_subprocess_popen() -> None:
    import subprocess

    from jedi.inference.compiled import subprocess as js

    from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec

    #

    def _wrapped_popen(cmd, *rest, **kwargs):
        return subprocess.Popen(subprocess_maybe_shell_wrap_exec(*cmd), *rest, **kwargs)

    #

    js.subprocess = lang.proxy_import('subprocess')
    js.subprocess.Popen = _wrapped_popen


def find_method_references(project_path: str, base_file: str, line: int, column: int):
    """
    Finds references to a class method across the entire project using the jedi Project API.

    Args:
        project_path (str): The root path of the project.
        base_file (str): The file where the method is defined.
        line (int): Line number of the method definition.
        column (int): Column number of the method definition.
    """

    # jedi.api.set_debug_function(print)
    jedi.inference.references._PARSED_FILE_LIMIT = 30_000

    # Initialize the Jedi Project
    project = jedi.Project(path=project_path)

    for e in project.search('def omlish.c3.compose_mro'):
        print(e)

    # for e in project.search('def omlish.c3.mro'):
    #     print(e)
    #
    # # Load the base script where the method is defined
    # base_script = jedi.Script(path=base_file, project=project)
    #
    # # Get references within the base file to get the initial reference object
    # references = base_script.get_references(line, column, include_builtins=False)
    #
    # print(references)
    #
    # # If no references found in the base file, exit early
    # if not references:
    #     print(f"No references found in '{base_file}'")
    #     return
    #
    # # man wtf gpt
    # # Iterate over all Python files in the project to find references
    # print(f"Searching for references in project '{project_path}'...")
    # for python_file in project.get_python_files():
    #     # Skip the base file to avoid self-references
    #     if os.path.abspath(python_file) == os.path.abspath(base_file):
    #         continue
    #
    #     try:
    #         script = jedi.Script(path=python_file)
    #         for ref in script.get_references(line, column, include_builtins=False):
    #             print(f"  - {ref.module_path}:{ref.line}:{ref.column}: {ref.name}")
    #     except Exception as e:
    #         print(f"Error processing file {python_file}: {e}")


if __name__ == "__main__":
    # Define the base file where the method is defined
    base_file = 'omlish/c3.py'

    # Define the project path (root directory of the project)
    project_path = '.'

    # Line and column numbers where the method is defined in the base file
    method_line = 124
    method_column = 5

    # Perform the search for references across the entire project
    find_method_references(project_path, base_file, method_line, method_column)
