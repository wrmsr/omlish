"""
https://python.langchain.com/v0.2/docs/tutorials/chatbot/
"""
import operator

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langchain_core.messages import trim_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from ..utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    model = ChatOpenAI(model="gpt-3.5-turbo")

    result = model.invoke([HumanMessage(content="Hi! I'm Bob")])
    print(result)

    #

    result = model.invoke([HumanMessage(content="What's my name?")])
    print(result)

    #

    result = model.invoke([
        HumanMessage(content="Hi! I'm Bob"),
        AIMessage(content="Hello Bob! How can I assist you today?"),
        HumanMessage(content="What's my name?"),
    ])
    print(result)

    #

    store = {}

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    with_message_history = RunnableWithMessageHistory(model, get_session_history)

    #

    config = {"configurable": {"session_id": "abc2"}}
    response = with_message_history.invoke(
        [HumanMessage(content="Hi! I'm Bob")],
        config=config,
    )
    print(response)

    #

    response = with_message_history.invoke(
        [HumanMessage(content="What's my name?")],
        config=config,
    )
    print(response)

    #

    config = {"configurable": {"session_id": "abc3"}}
    response = with_message_history.invoke(
        [HumanMessage(content="What's my name?")],
        config=config,
    )
    print(response)

    #

    config = {"configurable": {"session_id": "abc2"}}
    response = with_message_history.invoke(
        [HumanMessage(content="What's my name?")],
        config=config,
    )
    print(response)

    #

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Answer all questions to the best of your ability.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    chain = prompt | model

    #

    response = chain.invoke({"messages": [HumanMessage(content="hi! I'm bob")]})
    print(response)

    #

    with_message_history = RunnableWithMessageHistory(chain, get_session_history)

    #

    config = {"configurable": {"session_id": "abc5"}}
    response = with_message_history.invoke(
        [HumanMessage(content="Hi! I'm Jim")],
        config=config,
    )
    print(response)

    #

    response = with_message_history.invoke(
        [HumanMessage(content="What's my name?")],
        config=config,
    )
    print(response)

    #

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    chain = prompt | model

    #

    response = chain.invoke(
        {"messages": [HumanMessage(content="hi! I'm bob")], "language": "Spanish"}
    )
    print(response)

    #

    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="messages",
    )

    #

    config = {"configurable": {"session_id": "abc11"}}
    response = with_message_history.invoke(
        {"messages": [HumanMessage(content="hi! I'm todd")], "language": "Spanish"},
        config=config,
    )
    print(response)

    #

    response = with_message_history.invoke(
        {"messages": [HumanMessage(content="whats my name?")], "language": "Spanish"},
        config=config,
    )
    print(response)

    #

    trimmer = trim_messages(
        max_tokens=65,
        strategy="last",
        token_counter=model,
        include_system=True,
        allow_partial=False,
        start_on="human",
    )

    messages = [
        SystemMessage(content="you're a good assistant"),
        HumanMessage(content="hi! I'm bob"),
        AIMessage(content="hi!"),
        HumanMessage(content="I like vanilla ice cream"),
        AIMessage(content="nice"),
        HumanMessage(content="whats 2 + 2"),
        AIMessage(content="4"),
        HumanMessage(content="thanks"),
        AIMessage(content="no problem!"),
        HumanMessage(content="having fun?"),
        AIMessage(content="yes!"),
    ]

    response = trimmer.invoke(messages)
    print(response)

    #

    chain = (
            RunnablePassthrough.assign(messages=operator.itemgetter("messages") | trimmer)
            | prompt
            | model
    )

    response = chain.invoke(
        {
            "messages": messages + [HumanMessage(content="what's my name?")],
            "language": "English",
        }
    )
    print(response)

    #

    response = chain.invoke(
        {
            "messages": messages + [HumanMessage(content="what math problem did i ask")],
            "language": "English",
        }
    )
    print(response)

    #

    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="messages",
    )

    config = {"configurable": {"session_id": "abc20"}}
    response = with_message_history.invoke(
        {
            "messages": messages + [HumanMessage(content="whats my name?")],
            "language": "English",
        },
        config=config,
    )
    print(response)

    #

    response = with_message_history.invoke(
        {
            "messages": [HumanMessage(content="what math problem did i ask?")],
            "language": "English",
        },
        config=config,
    )
    print(response)

    #

    config = {"configurable": {"session_id": "abc15"}}
    for r in with_message_history.stream(
            {
                "messages": [HumanMessage(content="hi! I'm todd. tell me a joke")],
                "language": "English",
            },
            config=config,
    ):
        print(r.content, end="|")


if __name__ == '__main__':
    _main()
