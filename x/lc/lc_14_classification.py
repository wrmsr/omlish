"""
https://python.langchain.com/v0.2/docs/tutorials/classification/
"""
import typing as ta

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

from dp.utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    tagging_prompt = ChatPromptTemplate.from_template(
        """
    Extract the desired information from the following passage.

    Only extract the properties mentioned in the 'Classification' function.

    Passage:
    {input}
    """
    )

    class Classification(BaseModel):
        sentiment: str = Field(description="The sentiment of the text")
        aggressiveness: int = Field(
            description="How aggressive the text is on a scale from 1 to 10"
        )
        language: str = Field(description="The language the text is written in")

    # LLM
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125").with_structured_output(
        Classification
    )

    tagging_chain = tagging_prompt | llm

    #

    inp = "Estoy increiblemente contento de haberte conocido! Creo que seremos muy buenos amigos!"
    result = tagging_chain.invoke({"input": inp})
    print(result)

    #

    inp = "Estoy muy enojado con vos! Te voy a dar tu merecido!"
    res = tagging_chain.invoke({"input": inp})
    print(res.dict())

    #

    class Classification(BaseModel):
        sentiment: str = Field(..., enum=["happy", "neutral", "sad"])
        aggressiveness: int = Field(
            ...,
            description="describes how aggressive the statement is, the higher the number the more aggressive",
            enum=[1, 2, 3, 4, 5],
        )
        language: str = Field(
            ..., enum=["spanish", "english", "french", "german", "italian"]
        )

    #

    tagging_prompt = ChatPromptTemplate.from_template(
        """
    Extract the desired information from the following passage.

    Only extract the properties mentioned in the 'Classification' function.

    Passage:
    {input}
    """
    )

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125").with_structured_output(
        Classification
    )

    chain = tagging_prompt | llm

    #

    inp = "Estoy increiblemente contento de haberte conocido! Creo que seremos muy buenos amigos!"
    result = chain.invoke({"input": inp})
    print(result)

    #

    inp = "Estoy muy enojado con vos! Te voy a dar tu merecido!"
    result = chain.invoke({"input": inp})
    print(result)

    #

    inp = "Weather is ok here, I can go outside without much more than a coat"
    result = chain.invoke({"input": inp})
    print(result)


if __name__ == '__main__':
    _main()
