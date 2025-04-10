import inspect

from ..processing import Processor


##


class DocProcessor(Processor):
    def process(self, cls: type) -> type:
        if getattr(cls, '__doc__'):
            return cls

        try:
            text_sig = str(inspect.signature(cls)).replace(' -> None', '')
        except (TypeError, ValueError):
            text_sig = ''
        cls.__doc__ = (cls.__name__ + text_sig)

        return cls
