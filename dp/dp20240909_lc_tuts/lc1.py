"""
https://python.langchain.com/v0.2/docs/tutorials/llm_chain/
"""
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from ..utils import load_secrets


def _main() -> None:
    load_secrets()

    chain = ChatOpenAI(model='gpt-4') | StrOutputParser()

    messages = [
        SystemMessage(content="Translate the following from English into Italian"),
        HumanMessage(content="hi!"),
    ]

    result = chain.invoke(messages)
    print(result)


if __name__ == '__main__':
    _main()
