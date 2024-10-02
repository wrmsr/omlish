import abc
import dataclasses as dc
import typing as ta

from omlish import lang


T = ta.TypeVar('T')
OptionT = ta.TypeVar('OptionT')
ModelRequestT = ta.TypeVar('ModelRequestT', bound='Model.Request')
ModelResponseT = ta.TypeVar('ModelResponseT', bound='Model.Response')


##


class Model(lang.Abstract, ta.Generic[ModelRequestT, ModelResponseT]):
    class Option(lang.Abstract):
        pass

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


@dc.dataclass(frozen=True)
class TopK(Model.Option, lang.Final):
    k: int


@dc.dataclass(frozen=True)
class Temperature(Model.Option, lang.Final):
    f: float


##


class PromptModel(Model['PromptModel.Request', 'PromptModel.Response']):
    @dc.dataclass(frozen=True)
    class Request(Model.Request[str, Model.Option]):
        pass

    @dc.dataclass(frozen=True)
    class Response(Model.Response[str]):
        pass

    def generate(self, request: Request) -> Response:
        print(request)
        return PromptModel.Response('foo')


##


class ChatModel(Model['ChatModel.Request', 'ChatModel.Response']):
    class Option(lang.Abstract):
        pass

    @dc.dataclass(frozen=True)
    class Request(Model.Request[list[str], Model.Option | Option]):
        pass

    @dc.dataclass(frozen=True)
    class Response(Model.Response[str]):
        pass

    def generate(self, request: Request) -> Response:
        print(request)
        return ChatModel.Response('foo')


@dc.dataclass(frozen=True)
class Tool(ChatModel.Option, lang.Final):
    name: str


##


def _main() -> None:
    pm = PromptModel()
    pm.generate(PromptModel.Request('foo', [TopK(1)]))
    pm.generate(PromptModel.Request('foo', [Temperature(.1)]))
    pm.generate(
        PromptModel.Request(
            'foo',
            [
                TopK(1),
                Temperature(.1),
                # Tool('foo'),
            ],
        ),
    )

    cm = ChatModel()
    cm.generate(ChatModel.Request(['foo'], [TopK(1)]))
    cm.generate(ChatModel.Request(['foo'], [Temperature(.1)]))
    cm.generate(ChatModel.Request(['foo'], [TopK(1), Temperature(.1), Tool('foo')]))


if __name__ == '__main__':
    _main()
