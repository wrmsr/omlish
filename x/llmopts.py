import abc
import dataclasses as dc
import typing as ta

from omlish import lang


T = ta.TypeVar('T')
ModelRequestT = ta.TypeVar('ModelRequestT', bound='Model.Request')
ModelResponseT = ta.TypeVar('ModelResponseT', bound='Model.Response')
OptionT = ta.TypeVar('OptionT', bound='Option')


##


@dc.dataclass(frozen=True)
class Option(ta.Generic[T], lang.Abstract):
    v: T


@dc.dataclass(frozen=True)
class TopK(Option[int], lang.Final):
    pass


@dc.dataclass(frozen=True)
class Temperature(Option[float], lang.Final):
    pass


##


class Model(lang.Abstract, ta.Generic[ModelRequestT, ModelResponseT]):
    @dc.dataclass(frozen=True)
    class Request(lang.Abstract, ta.Generic[T, OptionT]):
        v: T

        options: ta.Sequence[OptionT] = ()

    @dc.dataclass(frozen=True)
    class Response(lang.Abstract, ta.Generic[T]):
        v: T

    @abc.abstractmethod
    def generate(self, request: ModelRequestT) -> ModelResponseT:
        raise NotImplementedError


##


class PromptModel(Model['PromptModel.Request', 'PromptModel.Response']):
    @dc.dataclass(frozen=True)
    class Request(Model.Request[str, Option]):
        pass

    @dc.dataclass(frozen=True)
    class Response(Model.Response[str]):
        pass

    def generate(self, request: Request) -> Response:
        print(request.options)
        return PromptModel.Response('foo')


def _main() -> None:
    m = PromptModel()
    m.generate(PromptModel.Request('foo', [TopK(1)]))
    m.generate(PromptModel.Request('foo', [Temperature(.1)]))
    m.generate(PromptModel.Request('foo', [TopK(1), Temperature(.1)]))


if __name__ == '__main__':
    _main()
