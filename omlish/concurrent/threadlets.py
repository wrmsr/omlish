"""
An abstraction over greenlet's api. Greenlet doesn't currently support nogil but its functionality is needed for async
bridge code (both here and in sqlalchemy). This can be implemented with real threads at the expense of overhead, but
this code is only intended to be used in already fairly heavy situations (bootstrap, db calls).
"""
import abc
import dataclasses as dc
import typing as ta

from .. import lang


if ta.TYPE_CHECKING:
    import greenlet
else:
    greenlet = lang.proxy_import('greenlet')


##


class Threadlet(abc.ABC):
    """Not safe to identity-key - use `underlying`."""

    def __hash__(self):
        raise TypeError('use `underlying`')

    def __eq__(self, other):
        raise TypeError('use `underlying`')

    @property
    @abc.abstractmethod
    def underlying(self) -> ta.Any:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parent(self) -> ta.Optional['Threadlet']:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def dead(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def switch(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def throw(self, ex: BaseException) -> ta.Any:
        raise NotImplementedError


class Threadlets(abc.ABC):
    @abc.abstractmethod
    def spawn(self, fn: ta.Callable[[], None]) -> Threadlet:
        raise NotImplementedError

    @abc.abstractmethod
    def get_current(self) -> Threadlet:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class GreenletThreadlet(Threadlet):
    g: 'greenlet.greenlet'

    @property
    def underlying(self) -> 'greenlet.greenlet':
        return self.g

    @property
    def parent(self) -> ta.Optional['GreenletThreadlet']:
        return GreenletThreadlet(self.g.parent)

    @property
    def dead(self) -> bool:
        return self.g.dead

    def switch(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        return self.g.switch(*args, **kwargs)

    def throw(self, ex: BaseException) -> ta.Any:
        return self.g.throw(ex)


class GreenletThreadlets(Threadlets):
    def spawn(self, fn: ta.Callable[[], None]) -> Threadlet:
        return GreenletThreadlet(greenlet.greenlet(fn))

    def get_current(self) -> Threadlet:
        return GreenletThreadlet(greenlet.getcurrent())
