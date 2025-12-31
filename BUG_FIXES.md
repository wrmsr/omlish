# Bug Fixes in omlish/lang/

## Summary

Found and fixed 3 bugs in the `omlish/lang/` directory with regression tests added for each.

---

## Bug 1: Value.is_error Returns Incorrect Value

**File:** `omlish/lang/outcomes.py:217`

**Issue:** The `Value.is_error` property was returning `True` instead of `False`. A `Value` outcome represents a successful result (not an error), so `is_error` should be `False`.

**Fix:**
```python
# Before:
@property
def is_error(self) -> bool:
    return True

# After:
@property
def is_error(self) -> bool:
    return False
```

**Regression Test:** Added `test_is_error_property()` in `omlish/lang/tests/test_outcomes.py` which verifies:
- `Value.is_error` returns `False`
- `Error.is_error` returns `True`

---

## Bug 2: Variable Used Before Definition in try_()

**File:** `omlish/lang/functions.py:81`

**Issue:** The `try_()` function referenced the variable `exct` in the `except` clause before it was defined. The tuple conversion of exception types was happening after the inner function definition, causing a `NameError` when an exception was actually raised.

**Fix:**
```python
# Before:
def try_(...):
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except exct:  # NameError: exct not defined yet!
            return default

    exct = (exc,) if isinstance(exc, type) else tuple(exc)
    return inner

# After:
def try_(...):
    exct = (exc,) if isinstance(exc, type) else tuple(exc)

    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except exct:
            return default

    return inner
```

**Regression Test:** Added `test_try_with_multiple_exceptions()` in `omlish/lang/tests/test_functions.py` which tests:
- Catching multiple exception types using an iterable
- Verifying that the correct exceptions are caught
- Verifying that non-specified exceptions are not caught

---

## Bug 3: Incorrect Logic in Recursion Depth Validation

**File:** `omlish/lang/recursion.py:68`

**Issue:** The condition to validate that the previous depth is a positive integer was incorrect. The original logic used `if not isinstance(pd, int) and pd > 0:` which would:
1. Never be True because if `pd` is not an int, then `pd > 0` would fail
2. Use incorrect boolean logic (`and` instead of `or`)

The correct logic should check if pd is NOT a valid positive integer, i.e., if it's either not an int OR not positive.

**Fix:**
```python
# Before:
if not isinstance(pd, int) and pd > 0:  # type: ignore[operator]
    raise RuntimeError

# After:
if not isinstance(pd, int) or pd <= 0:
    raise RuntimeError
```

**Regression Test:** Added `test_recursion_depth_validation()` in `omlish/lang/tests/test_recursion.py` which verifies:
- Normal recursive calls work correctly
- The recursion limit is properly enforced
- Recovery after hitting the limit works

---

## Test Results

All 78 tests in `omlish/lang/tests/` pass:
```
=================== 78 passed, 1 skipped, 1 warning in 1.29s ===================
```

The three new regression tests specifically verify each bug fix:
1. `test_is_error_property` - PASSED
2. `test_try_with_multiple_exceptions` - PASSED
3. `test_recursion_depth_validation` - PASSED
