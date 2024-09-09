"""
https://python.langchain.com/v0.2/docs/tutorials/llm_chain/
"""
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from ..utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    model = ChatOpenAI(model='gpt-4')
    parser = StrOutputParser()

    #

    chain = model | parser

    messages = [
        SystemMessage(content="Translate the following from English into Italian"),
        HumanMessage(content="hi!"),
    ]

    result = chain.invoke(messages)
    print(result)

    #

    system_template = "Translate the following into {language}:"

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", "{text}"),
    ])

    result = prompt_template.invoke({"language": "italian", "text": "hi"})
    print(result)

    #

    chain = prompt_template | model | parser

    result = chain.invoke({"language": "italian", "text": "hi"})
    print(result)


if __name__ == '__main__':
    _main()
