import typing as ta


# This has to be in a separate module to ensure it's not directly in test module's globals (thus intentionally making it
# difficult to handle for inspection machinery).
IntTree: ta.TypeAlias = int | list['IntTree']
