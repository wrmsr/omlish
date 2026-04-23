import typing as ta

from ....chat.choices.services import ChatChoicesService
from ..resolving import DEFAULT_BACKEND_SPEC_RESOLVER
from ..types import BackendSpec
from ..types import ConfigBackendSpec
from ..types import ModelBackendSpec
from ..types import NameBackendSpec
from ..types import ResolvedBackendSpec
from ..types import RetryBackendSpec


def instantiate_backend(rbs: ResolvedBackendSpec) -> ta.Any:
    args: list[ta.Any] = []

    if (ch := rbs.children) is None:
        pass
    elif isinstance(ch, tuple):
        args.append(tuple(instantiate_backend(x) for x in ch))
    else:
        args.append(instantiate_backend(ch))

    args.extend(rbs.configs or ())

    return rbs.ctor(*args)


def test_strings():
    bsr = DEFAULT_BACKEND_SPEC_RESOLVER

    for _ in range(2):
        for bs in [
            NameBackendSpec('openai'),
            BackendSpec.of('openai'),
            BackendSpec.of("{model: 'gpt'}"),
            ConfigBackendSpec(ModelBackendSpec('gpt'), [{'api_key': 'foo'}]),
            RetryBackendSpec(ConfigBackendSpec(ModelBackendSpec('gpt'), [{'api_key': 'foo'}])),
        ]:
            rbs = bsr.resolve(ChatChoicesService, bs)
            print(rbs)

            svc = instantiate_backend(rbs)
            print(svc)

            print()
