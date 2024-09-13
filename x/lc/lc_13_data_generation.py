"""
https://python.langchain.com/v0.2/docs/tutorials/data_generation/
"""
import typing as ta

from langchain.chains import create_extraction_chain_pydantic
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_experimental.tabular_synthetic_data.openai import (
    OPENAI_TEMPLATE,
    create_openai_data_generator,
)
from langchain_experimental.tabular_synthetic_data.prompts import (
    SYNTHETIC_FEW_SHOT_PREFIX,
    SYNTHETIC_FEW_SHOT_SUFFIX,
)
from langchain_openai import ChatOpenAI
from langchain_experimental.synthetic_data import (
    DatasetGenerator,
    create_data_generation_chain,
)
from langchain_openai import ChatOpenAI

from dp.utils import load_secrets


def _main() -> None:
    load_secrets()

    #

    class MedicalBilling(BaseModel):
        patient_id: int
        patient_name: str
        diagnosis_code: str
        procedure_code: str
        total_charge: float
        insurance_claim_amount: float

    #

    examples = [
        {
            "example": """Patient ID: 123456, Patient Name: John Doe, Diagnosis Code: 
            J20.9, Procedure Code: 99203, Total Charge: $500, Insurance Claim Amount: $350"""
        },
        {
            "example": """Patient ID: 789012, Patient Name: Johnson Smith, Diagnosis 
            Code: M54.5, Procedure Code: 99213, Total Charge: $150, Insurance Claim Amount: $120"""
        },
        {
            "example": """Patient ID: 345678, Patient Name: Emily Stone, Diagnosis Code: 
            E11.9, Procedure Code: 99214, Total Charge: $300, Insurance Claim Amount: $250"""
        },
    ]

    #

    OPENAI_TEMPLATE = PromptTemplate(input_variables=["example"], template="{example}")

    prompt_template = FewShotPromptTemplate(
        prefix=SYNTHETIC_FEW_SHOT_PREFIX,
        examples=examples,
        suffix=SYNTHETIC_FEW_SHOT_SUFFIX,
        input_variables=["subject", "extra"],
        example_prompt=OPENAI_TEMPLATE,
    )

    #

    synthetic_data_generator = create_openai_data_generator(
        output_schema=MedicalBilling,
        llm=ChatOpenAI(
            temperature=1
        ),  # You'll need to replace with your actual Language Model instance
        prompt=prompt_template,
    )

    #

    synthetic_results = synthetic_data_generator.generate(
        subject="medical_billing",
        extra="the name must be chosen at random. Make it something you wouldn't normally choose.",
        runs=10,
    )

    print(synthetic_results)

    #

    # LLM
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    chain = create_data_generation_chain(model)

    print(chain({"fields": ["blue", "yellow"], "preferences": {}}))

    #

    print(chain(
        {
            "fields": {"colors": ["blue", "yellow"]},
            "preferences": {"style": "Make it in a style of a weather forecast."},
        }
    ))

    #

    print(chain(
        {
            "fields": {"actor": "Tom Hanks", "movies": ["Forrest Gump", "Green Mile"]},
            "preferences": None,
        }
    ))

    #

    print(chain(
        {
            "fields": [
                {"actor": "Tom Hanks", "movies": ["Forrest Gump", "Green Mile"]},
                {"actor": "Mads Mikkelsen", "movies": ["Hannibal", "Another round"]},
            ],
            "preferences": {"minimum_length": 200, "style": "gossip"},
        }
    ))

    #

    inp = [
        {
            "Actor": "Tom Hanks",
            "Film": [
                "Forrest Gump",
                "Saving Private Ryan",
                "The Green Mile",
                "Toy Story",
                "Catch Me If You Can",
            ],
        },
        {
            "Actor": "Tom Hardy",
            "Film": [
                "Inception",
                "The Dark Knight Rises",
                "Mad Max: Fury Road",
                "The Revenant",
                "Dunkirk",
            ],
        },
    ]

    generator = DatasetGenerator(model, {"style": "informal", "minimal length": 500})
    dataset = generator(inp)
    print(dataset)

    #

    class Actor(BaseModel):
        Actor: str = Field(description="name of an actor")
        Film: ta.List[str] = Field(description="list of names of films they starred in")

    #

    llm = OpenAI()
    parser = PydanticOutputParser(pydantic_object=Actor)

    prompt = PromptTemplate(
        template="Extract fields from a given text.\n{format_instructions}\n{text}\n",
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    _input = prompt.format_prompt(text=dataset[0]["text"])
    output = llm(_input.to_string())

    parsed = parser.parse(output)
    print(parsed)

    #

    print((parsed.Actor == inp[0]["Actor"]) & (parsed.Film == inp[0]["Film"]))

    #

    extractor = create_extraction_chain_pydantic(pydantic_schema=Actor, llm=model)
    extracted = extractor.run(dataset[1]["text"])
    print(extracted)

    #

    print((extracted[0].Actor == inp[1]["Actor"]) & (extracted[0].Film == inp[1]["Film"]))


if __name__ == '__main__':
    _main()
