
import instructor
from openai import OpenAI
from pydantic import BaseModel

from x.dp.utils import load_secrets


load_secrets()


__client = instructor.from_openai(OpenAI())


class BoolEvalResult(BaseModel):
    value: bool
    reason: str | None


def evaluate_with_llm_bool(instruction, data) -> BoolEvalResult:
    eval_result, _ = __client.chat.completions.create_with_completion(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': instruction},
            {'role': 'user', 'content': data},
        ],
        response_model=BoolEvalResult,
    )
    return eval_result
