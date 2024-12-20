# ruff: noqa: UP006 UP007
from omlish.lite.check import check


def check_valid_deploy_spec_path(s: str) -> str:
    check.non_empty_str(s)
    for c in ['..', '//']:
        check.not_in(c, s)
    check.arg(not s.startswith('/'))
    return s
