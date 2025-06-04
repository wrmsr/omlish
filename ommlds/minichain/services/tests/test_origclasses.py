import typing as ta

from .._origclasses import _OrigClassCapture


T = ta.TypeVar('T')


class CheckedBox(_OrigClassCapture, ta.Generic[T]):
    def __init__(self, v: T) -> None:
        super().__init__()

        self._v = v

    def __init_subclass__(cls, **kwargs):
        raise TypeError('Final')

    @property
    def v(self) -> T:
        return self._v

    is_valid: bool

    def __on_capture_orig_class__(self, orig_class):
        super().__on_capture_orig_class__(orig_class)
        [v_ty] = ta.get_args(orig_class)
        self.is_valid = isinstance(self._v, v_ty)


def test_orig_class_capture():
    assert not(hasattr(CheckedBox(5), 'is_valid'))
    assert CheckedBox[int](5).is_valid
    assert not CheckedBox[str](5).is_valid  # type: ignore[arg-type]
