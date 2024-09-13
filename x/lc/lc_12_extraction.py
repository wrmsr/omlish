"""
https://python.langchain.com/v0.2/docs/tutorials/extraction/
"""
import typing as ta

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI

from dp.utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    class Person(BaseModel):
        """Information about a person."""

        # ^ Doc-string for the entity Person.
        # This doc-string is sent to the LLM as the description of the schema Person,
        # and it can help to improve extraction results.

        # Note that:
        # 1. Each field is an `optional` -- this allows the model to decline to extract it!
        # 2. Each field has a `description` -- this description is used by the LLM.
        # Having a good description can help improve extraction results.
        name: ta.Optional[str] = Field(default=None, description="The name of the person")
        hair_color: ta.Optional[str] = Field(
            default=None, description="The color of the person's hair if known"
        )
        height_in_meters: ta.Optional[str] = Field(
            default=None, description="Height measured in meters"
        )

    #

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value.",
            ),
            # Please see the how-to about improving performance with
            # reference examples.
            # MessagesPlaceholder('examples'),
            ("human", "{text}"),
        ]
    )

    #

    llm = ChatOpenAI(model="gpt-4o")

    # llm = ChatMistralAI(model="mistral-large-latest", temperature=0)

    runnable = prompt | llm.with_structured_output(schema=Person)

    #

    text = "Alan Smith is 6 feet tall and has blond hair."
    result = runnable.invoke({"text": text})
    print(result)

    #

    class Person(BaseModel):
        """Information about a person."""

        # ^ Doc-string for the entity Person.
        # This doc-string is sent to the LLM as the description of the schema Person,
        # and it can help to improve extraction results.

        # Note that:
        # 1. Each field is an `optional` -- this allows the model to decline to extract it!
        # 2. Each field has a `description` -- this description is used by the LLM.
        # Having a good description can help improve extraction results.
        name: ta.Optional[str] = Field(default=None, description="The name of the person")
        hair_color: ta.Optional[str] = Field(
            default=None, description="The color of the person's hair if known"
        )
        height_in_meters: ta.Optional[str] = Field(
            default=None, description="Height measured in meters"
        )

    class Data(BaseModel):
        """Extracted data about people."""

        # Creates a model so that we can extract multiple entities.
        people: ta.List[Person]

    #

    runnable = prompt | llm.with_structured_output(schema=Data)
    text = "My name is Jeff, my hair is black and i am 6 feet tall. Anna has the same color hair as me."
    result = runnable.invoke({"text": text})
    print(result)


if __name__ == '__main__':
    _main()
