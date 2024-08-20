import dataclasses as dc
import typing as ta

import transformers

from omlish import cached


class ModelServer:
    @dc.dataclass(frozen=True)
    class Config:
        model: str
        task: str = 'text-generation'

    def __init__(self, config: Config) -> None:
        super().__init__()
        self._config = config

    @cached.function
    def generator(self) -> ta.Callable:
        return transformers.pipeline(self._config.task, model=self._config.model)

    @dc.dataclass(frozen=True)
    class Generation:
        generated_text: str

    def generate(self, prompt: str) -> list[Generation]:
        lst = self.generator()(prompt)
        return [self.Generation(**dct) for dct in lst]


def _main():
    ms = ModelServer(ModelServer.Config(
        model='facebook/opt-125m',
    ))
    print(ms.generate('Hello, my name is'))


if __name__ == '__main__':
    _main()
