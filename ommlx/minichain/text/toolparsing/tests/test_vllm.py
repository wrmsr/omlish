import json
import re


MODEL_INPUT = """\
<|im_start|>system
You are Qwen, created by Alibaba Cloud. You are a helpful assistant.

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{"type": "function", "function": {"name": "python", "description": "Runs code in an ipython interpreter and returns the result of the execution after 60 seconds.", "parameters": {"type": "object", "properties": {"code": {"type": "string", "description": "The code to run in the ipython interpreter."}}, "required": ["code"]}}}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call><|im_end|>
<|im_start|>user
Print a hello world message with python.<|im_end|>
<|im_start|>assistant
"""  # noqa

MODEL_OUTPUT = """\
<tool_call>
{"name": "python", "arguments": {"code": "print('Hello world!')"}}
</tool_call>
"""


def test_vllm_style():
    pat = re.compile(r'<tool_call>(.*?)</tool_call>|<tool_call>(.*)', re.DOTALL)

    rfcs = [
        json.loads(m[0] if m[0] else m[1])
        for m in pat.findall(MODEL_OUTPUT)
    ]

    tcs = [
        dict(
            type='function',
            function=dict(
                name=fc['name'],
                arguments=json.dumps(
                    fc['arguments'],
                    ensure_ascii=False,
                ),
            ),
        )
        for fc in rfcs
    ]

    print(tcs)
