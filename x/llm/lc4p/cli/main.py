import argparse
import dataclasses as dc
import datetime
import os.path
import sys

from x.dp.utils import load_secrets
from omlish import logs
from omlish.diag import pycharm

from ..models import Request
from ..openai import OpenaiPromptModel
from ..prompts import Prompt


def _main() -> None:
    logs.configure_standard_logging('INFO')

    #

    parser = argparse.ArgumentParser()
    parser.add_argument('prompt')
    args = parser.parse_args()

    args.new = True

    #

    prompt = args.prompt

    if not sys.stdin.isatty() and not pycharm.is_pycharm_hosted():
        stdin_data = sys.stdin.read()
        prompt = '\n'.join([prompt, stdin_data])

    #

    load_secrets()

    #

    pm = OpenaiPromptModel()
    req = Request(Prompt(prompt))
    resp = pm.generate(req)

    print(resp)


if __name__ == '__main__':
    _main()
