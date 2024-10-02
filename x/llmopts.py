import abc
import dataclasses as dc
import typing as ta

from omlish import lang


T = ta.TypeVar('T')
OptionT = ta.TypeVar('OptionT', bound='Option')
OptionU = ta.TypeVar('OptionU', bound='Option')
UniqueOptionT = ta.TypeVar('UniqueOptionT', bound='UniqueOption')
ModelRequestT = ta.TypeVar('ModelRequestT', bound='Model.Request')
ModelResponseT = ta.TypeVar('ModelResponseT', bound='Model.Response')


##
##


##

##




##


def _main() -> None:
    pm = PromptModel()
    pm.generate(PromptModel.Request('foo', Options(TopK(1))))
    pm.generate(PromptModel.Request('foo', Options(Temperature(.1))))
    pm.generate(
        PromptModel.Request(
            'foo',
            Options(
                TopK(1),
                Temperature(.1),
                # Tool('foo'),
            ),
        ),
    )

    cm = ChatModel()
    cm.generate(ChatModel.Request(['foo'], Options(TopK(1))))
    cm.generate(ChatModel.Request(['foo'], Options(Temperature(.1))))
    cm.generate(ChatModel.Request(['foo'], Options(TopK(1), Temperature(.1), Tool('foo'))))


if __name__ == '__main__':
    _main()
