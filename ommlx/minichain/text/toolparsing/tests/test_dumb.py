from ..base import ParsedToolExec
from ..dumb import DumbToolExecParser


MODEL_RESPONSE = """\
<tools>
{"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}
</tools>"""


def test_dumb_tool_exec_parser():
    dp = DumbToolExecParser(
        '<tools>',
        '</tools>',
    )

    assert dp.parse_tool_exec(MODEL_RESPONSE) == [
        ParsedToolExec(
            'multiply',
            {
                'a': 12234585,
                'b': 48838483920,
            },
            raw_args='\n{"name": "multiply", "arguments": {"a": 12234585, "b": 48838483920}}\n',
        ),
    ]
