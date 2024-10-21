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
"""
if [ "${SHELLNAME}" != "zsh" ] && [ "$SHELLNAME" != "bash" ]
then
  _throw_source_error "${@}"
fi

if [ "${SHELLNAME}" = "bash" ]
then
  (return 0 2>/dev/null) && sourced=1 || sourced=0
  if [ $sourced -eq 0 ]; then
    _throw_source_error "${@}"
  fi
fi

if [ "${SHELLNAME}" = "zsh" ]
then
  if [[ "${ZSH_EVAL_CONTEXT}" = "toplevel" ]]
  then
    _throw_source_error "${@}"
  fi
  if ! (( zsh_eval_context[(I)file] )); then
    _throw_source_error "${@}"
  fi
fi

# exit from ctrl-C without exiting user's shell
trap "return 0" SIGINT

AISH_SHELL="${SHELLNAME}"
AISH_OS="${OS}"

# start the actual request to OpenAI

request=`echo "${@}" | sed -r 's/"/\\\"/g'`

data='{
  "model": "'${MODEL}'",
  "messages": [
  {"role": "system", "content": "You are an AI shell-scripting expert called Aish."},{"role": "user", "content": "Please write a one-liner for '${AISH_SHELL}' shell for performing the following task. Assume you have access to all of the commonly available unix commands on a modern '${AISH_OS}' system. You can separate multi-line commands with a semicolon or double ampersand but please put them on one line. Respond without using markdown formatting. Please only return the exact bash one-liner command without any superfluous words explaining it, and no formatting. Do NOT use backticks. Do not put backticks around the one-liner. Code should be bare without any markdown formatting. IMPORTANT: If you need to ask for clarification or provide any information other than a one-liner solution, please prefix your response with the exact phrase AISH_FEEDBACK: in all caps, with a colon. If you are responding with anything other than a shell script one-liner you MUST include AISH_FEEDBACK: (including the colon) as the start of the response.\n\n Here is the task I would like you to carry out with the one-liner: '$request'"}
  ]
}'

# echo "Sending: ${data}"

echo -ne "...fetching solution..."
json=$( curl -s ${AISH_URL}/v1/chat/completions -u ":${OPENAI_API_KEY}" -H 'Content-Type: application/json' -d "${data}" )
echo -ne "\033[2K" ; printf "\r"

if `echo "${json}" | grep -q '"content": '`
then
  now=`date "+%Y-%m-%dT%H:%M:%S%:z"`
  echo "$now ${request}" >> ~/.aish-log
  result=`echo "${json}" | grep '"content": "' | sed -nr 's/"content": "(.*)"/\1/p' | sed -e 's/^[ \t]*//' | sed -e 's/\\\"/"/g'`
  if [ "${result#AISH_FEEDBACK: }" != "$result" ]
  then
    echo "${result#AISH_FEEDBACK: }"
  else
    echo "Hit Enter to add this command to history or ctrl-C to abort:"
    echo -n "$ ${result}"
    read -r _
    if [ "${SHELLNAME}" = "zsh" ]
    then
      print -s "${result}"
    fi
    if [ "${SHELLNAME}" = "bash" ]
    then
      set -o history
      shopt -s histappend
      history -s "${result}"
      history -w
    fi
    echo "Press the up arrow to access the solution."
  fi
else
  echo "${json}"
fi
"""
from omdev.secrets import load_secrets
from ommlx import minichain as mc
from ommlx.minichain.backends.openai import OpenaiChatModel


def _main() -> None:
    request = 'which process is running on port 8000'

    system_prompt = 'You are an AI shell-scripting expert called Aish.'
    user_template = (
        "Please write a one-liner for '{shell}' shell for performing the following task. "
        "Assume you have access to all of the commonly available unix commands on a modern '{os}' system. "
        "You can separate multi-line commands with a semicolon or double ampersand but please put them on one "
        "line. Respond without using markdown formatting. Please only return the exact bash one-liner command "
        "without any superfluous words explaining it, and no formatting. Do NOT use backticks. Do not put "
        "backticks around the one-liner. Code should be bare without any markdown formatting. IMPORTANT: If you "
        "need to ask for clarification or provide any information other than a one-liner solution, please prefix "
        "your response with the exact phrase AISH_FEEDBACK: in all caps, with a colon. If you are responding with "
        "anything other than a shell script one-liner you MUST include AISH_FEEDBACK: (including the colon) as the "
        "start of the response.\n\nHere is the task I would like you to carry out with the one-liner: '{request}'"
    )

    llm = OpenaiChatModel(api_key=load_secrets().get('openai_api_key').reveal())

    print(llm([
        mc.SystemMessage(system_prompt),
        mc.UserMessage(user_template.format(
            shell='zsh',
            os='Mac OSX',
            request=request,
        )),
    ]))


if __name__ == '__main__':
    _main()
