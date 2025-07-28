import typing as ta

from omlish import check


##


class _OrigClassCapture:
    @property
    def __orig_class__(self):
        return object.__getattribute__(self, '__captured_orig_classes__')[0]

    @__orig_class__.setter
    @ta.final
    def __orig_class__(self, orig_class):
        try:
            lst = self.__dict__['__captured_orig_classes__']
        except KeyError:
            pass
        else:
            # # NOTE: This would be swallowed by typing machinery.
            # raise TypeError('__orig_class__ already set')
            lst.append(orig_class)
            return

        lst = [orig_class]
        object.__setattr__(self, '__captured_orig_classes__', lst)
        self.__on_capture_orig_class__(orig_class)

    def __on_capture_orig_class__(self, orig_class):
        """
        Note: Exceptions raised will be silently swallowed by typing machinery, so if anything important is done here
        code should check that it actually succeeded as necessary.

        See:
            https://github.com/python/cpython/blob/f66c75f11d3aeeb614600251fd5d3fe1a34b5ff1/Lib/typing.py#L1187-L1190
            https://github.com/python/cpython/issues/115165
        """

    @property
    def __captured_orig_class__(self):
        """Enforces that __orig_class__ has only been set once."""

        return check.single(object.__getattribute__(self, '__captured_orig_classes__'))
