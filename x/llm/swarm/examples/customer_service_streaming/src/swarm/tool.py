from typing import Literal

from pydantic import BaseModel
from pydantic import Field


class Parameter(BaseModel):
    type: str
    description: str | None = None
    enum: list[str] | None = Field(None, alias='choices')


class FunctionParameters(BaseModel):
    type: Literal['object']  # Ensuring it's always 'object'
    properties: dict[str, Parameter] = {}
    required: list[str] | None = None


class FunctionTool(BaseModel):
    name: str
    description: str | None
    parameters: FunctionParameters


class Tool(BaseModel):
    type: str
    function: FunctionTool | None
    human_input: bool | None = False
