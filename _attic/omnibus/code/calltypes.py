import sys
import textwrap


class CallTypes:

    def __iter__(self):
        for k, v in type(self).__dict__.items():
            if callable(v) and not k.startswith('_'):
                yield v

    def _visit(self, *args, **kwargs):
        pass

    def nullary(self):
        return self._visit()

    def arg(self, arg):
        return self._visit(arg)

    def default(self, default=None):
        return self._visit(default)

    def varargs(self, *varargs):
        return self._visit(*varargs)

    def kwonly(self, *, kwonly=None):
        return self._visit(kwonly=kwonly)

    if sys.version_info[1] > 7:
        exec(textwrap.dedent("""
            def posonly(self, /, posonly):
                return self._visit(posonly)
        """), globals(), locals())

    def kwargs(self, **kwargs):
        return self._visit(**kwargs)

    def all(self, arg, *varargs, default=None, **kwargs):
        return self._visit(arg, *varargs, default=default, **kwargs)

    def all2(self, arg0, arg1, *varargs, default0=None, default1=None, **kwargs):
        return self._visit(arg0, arg1, *varargs, default0=default0, default1=default1, **kwargs)


CALL_TYPES = CallTypes()
