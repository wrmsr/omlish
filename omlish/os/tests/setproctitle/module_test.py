from .conftest import run_script


def test_no_import_side_effect():
    """Check that importing the module doesn't cause side effects."""

    rv = run_script(
        """
import os

def print_stuff():
    for fn in "cmdline status comm".split():
        if os.path.exists(f"/proc/self/{fn}"):
            with open(f"/proc/self/{fn}") as f:
                print(f.readline().rstrip())

print_stuff()
print("---")
import setproctitle
print_stuff()
""",
    )
    before, after = rv.split('---\n')
    assert before == after
