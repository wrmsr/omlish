import abc
import dataclasses as dc
import typing as ta

from omlish import lang


T = ta.TypeVar('T')
ModelRequestT = ta.TypeVar('ModelRequestT', bound='Model.Request')
ModelResponseT = ta.TypeVar('ModelResponseT', bound='Model.Response')
OptionT = ta.TypeVar('OptionT', bound='Option', contravariant=True)


##


class Option(lang.Abstract):
    pass


##


class ModelRequestOption(Option, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class TopK(ModelRequestOption, lang.Final):
    k: int


@dc.dataclass(frozen=True)
class Temperature(ModelRequestOption, lang.Final):
    f: float


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
    class Request(Model.Request[str, ModelRequestOption]):
        pass

    @dc.dataclass(frozen=True)
    class Response(Model.Response[str]):
        pass

    def generate(self, request: Request) -> Response:
        print(request)
        return PromptModel.Response('foo')


##


class ChatModelRequestOption(Option, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Tool(ChatModelRequestOption, lang.Final):
    name: str


#


class ChatModel(Model['ChatModel.Request', 'ChatModel.Response']):
    @dc.dataclass(frozen=True)
    class Request(Model.Request[list[str], ModelRequestOption | ChatModelRequestOption]):
        pass

    @dc.dataclass(frozen=True)
    class Response(Model.Response[str]):
        pass

    def generate(self, request: Request) -> Response:
        print(request)
        return ChatModel.Response('foo')


##


def _main() -> None:
    pm = PromptModel()
    pm.generate(PromptModel.Request('foo', [TopK(1)]))
    pm.generate(PromptModel.Request('foo', [Temperature(.1)]))
    pm.generate(PromptModel.Request('foo', [TopK(1), Temperature(.1)]))  # , Tool('foo')]))

    cm = ChatModel()
    cm.generate(ChatModel.Request(['foo'], [TopK(1)]))
    cm.generate(ChatModel.Request(['foo'], [Temperature(.1)]))
    cm.generate(ChatModel.Request(['foo'], [TopK(1), Temperature(.1), Tool('foo')]))


if __name__ == '__main__':
    _main()
