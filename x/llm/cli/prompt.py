import abc
import os.path
import sys
import typing as ta

from omlish import lang


if ta.TYPE_CHECKING:
    import llama_cpp
    import openai
    import transformers

else:
    llama_cpp = lang.proxy_import('llama_cpp')
    openai = lang.proxy_import('openai')
    transformers = lang.proxy_import('transformers')


##


class PromptLlm(abc.ABC):
    @abc.abstractmethod
    def get_completion(self, prompt: str) -> str:
        raise NotImplementedError


class OpenaiPromptLlm(PromptLlm):
    model = 'gpt-3.5-turbo-instruct'

    def get_completion(self, prompt: str) -> str:
        response = openai.completions.create(
            model=self.model,
            prompt=prompt,
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
        )

        return response.choices[0].text


class LlamacppPromptLlm(PromptLlm):
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--QuantFactory--Meta-Llama-3-8B-GGUF',
        'snapshots',
        '1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
        'Meta-Llama-3-8B.Q8_0.gguf',
    )

    def get_completion(self, prompt: str) -> str:
        llm = llama_cpp.Llama(
            model_path=self.model_path,
        )

        output = llm.create_completion(
            prompt,
            max_tokens=1024,
            stop=["\n"],
        )

        return output['choices'][0]['text']


class TransformersPromptLlm(PromptLlm):
    model = "meta-llama/Meta-Llama-3-8B"

    def get_completion(self, prompt: str) -> str:
        pipeline = transformers.pipeline(
            "text-generation",
            model=self.model,
            device='mps' if sys.platform == 'darwin' else 'cuda',
            token=os.environ.get('HUGGINGFACE_HUB_TOKEN'),
        )
        output = pipeline(prompt)
        return output
