"""
TODO:
 - log
 - check BASH_VERSION/ZSH_VERSION, sys.platform

==

eval `om aish ...`
. <(om aish ...)
"""
# Copyright © 2023 Chris McCormick
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
Examples:
 - which process is running on port 8000
 - numeric for loop boilerplate going from 5 to 15
 - restart openssh
 - start a simple webserver using python3
 - rename every file in ./images from .jpg to .png
 - resize all of images in ./images to a maximum of 100 pixels in any dimension
 - create a small webserver with netcat
 - get the ips that amazon.com resolves to and ping each one
 - list all network interfaces and their ip addresses
 - print out the source of function __git_ps1
 - delete all unused docker images
 - concatenate two .mkv video files
 - use ffmpeg to shrink an mp4 file's size
 - use imagemagick change the white background in screenshot.png to transparent
"""
import argparse
import subprocess
import getpass
import os
import pwd
import sys

from omdev.secrets import load_secrets
from omlish import check
from ommlx import minichain as mc
from ommlx.minichain.backends.openai import OpenaiChatModel


def _detect_os() -> str:
    return {
        'linux': 'Linux',
        'darwin': 'Mac OSX',
    }[sys.platform]


def _detect_shell() -> str:
    if 'BASH_VERSION' in os.environ:
        return 'bash'
    elif 'ZSH_VERSION' in os.environ:
        return 'zsh'

    if not (sh_exe := os.environ.get('SHELL')):
        sh_exe = pwd.getpwnam(getpass.getuser()).pw_shell
    sh_exe = sh_exe.split('/')[-1]
    if sh_exe == 'bash':
        return 'bash'
    elif sh_exe == 'zsh':
        return 'zsh'
    else:
        raise RuntimeError("Can't get shell name")


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--os', nargs='?')
    parser.add_argument('--shell', nargs='?')
    parser.add_argument('request', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    #

    request = ' '.join(args.request).strip()
    if not request:
        parser.print_help()

    if (os_name := args.os) is None:
        os_name = _detect_os()

    if (shell_name := args.shell) is None:
        shell_name = _detect_shell()

    #

    system_prompt = 'You are an AI shell-scripting expert called Aish.'

    feedback_pfx = 'AISH_FEEDBACK'

    user_template = (
        "Please write a one-liner for '{shell_name}' shell for performing the following task. "
        
        "Assume you have access to all of the commonly available unix commands on a modern '{os_name}' system. "
        
        "You can separate multi-line commands with a semicolon or double ampersand but please put them on one line. "
        
        "Respond without using markdown formatting. "

        "Please only return the exact bash one-liner command without any superfluous words explaining it, and no "
        "formatting. "

        "Do NOT use backticks. "

        "Do not put backticks around the one-liner. "

        "Code should be bare without any markdown formatting. "

        "IMPORTANT: If you need to ask for clarification or provide any information other than a one-liner solution, "
        "please prefix your response with the exact phrase {feedback_pfx}: in all caps, with a colon. "

        "If you are responding with anything other than a shell script one-liner you MUST include {feedback_pfx}: "
        "(including the colon) as the start of the response."

        "\n\n"

        "Here is the task I would like you to carry out with the one-liner: '{request}'"
    )

    #

    llm = OpenaiChatModel(api_key=load_secrets().get('openai_api_key'))

    resp = llm([
        mc.SystemMessage(system_prompt),
        mc.UserMessage(user_template.format(
            shell_name=shell_name,
            os_name=os_name,
            request=args.request,
            feedback_pfx=feedback_pfx,
        )),
    ])

    out = check.single(resp.v).m.s

    #

    """
    if [ "${SHELLNAME}" = "zsh" ]; then
      print -s "${result}"
    fi

    if [ "${SHELLNAME}" = "bash" ] ; then
      set -o history
      shopt -s histappend
      history -s "${result}"
      history -w
    fi
    """

    print(out)


if __name__ == '__main__':
    _main()
