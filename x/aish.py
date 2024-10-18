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
# aish: AI shell completions
# <https://github.com/chr15m/aish>

# vi: ft=bash
# Why no hash-bang?
# It's so this script can be sourced under both bash and zsh.

# Website: <https://mccormick.cx>
# Donate:  <https://www.patreon.com/chr15m>
# Donate:  <ko-fi.com/chr15m>

# TODO:
# - set up basic tests via github actions

if [ "$1" = "" -o "$1" = "-h" ]
then
  echo "Usage: . aish QUERY"
  echo
  echo "QUERY:   tell the AI what you want"
  echo "Example: '. aish a for loop going from 5 to 15'."
  echo "Note:    You must include the . to source the script."
  echo "         The result will be available from history with the up key."
  echo
  echo 'You an add variables to ~/.aish to configure it:'
  echo 'OPENAI_API_KEY="sk-..."'
  echo 'AISH_MODEL=gpt-4 # defaults to gpt-3.5-turbo (gpt-4 is recommended)'
  echo 'AISH_URL=http... # defaults to https://api.openai.com - set to any OpenAI compatible API.'
  echo ''
  echo '- Create a new API key here: <https://platform.openai.com/api-keys>'
  echo '- List the available models with `aish models`'
  echo '- Requests will be logged to ~/.aish-log'
  exit 0
fi

# source aish config file with overrides if it exists
if [ -f ~/.aish ]
then
  . ~/.aish
fi

AISH_URL=${AISH_URL:-https://api.openai.com}

# check if API key is set
if [ -z "$OPENAI_API_KEY" ]
then
  echo "Error: OPENAI_API_KEY not set."
  echo
  echo "Get your key from <https://platform.openai.com/account/api-keys>."
  echo "Put it in ~/.aish like this:"
  echo "OPENAI_API_KEY=sk-..."
  echo
  return 1
fi

if [ "$1" = "models" ]
then
  echo "Fetching available model list from the API."
  curl -s -H "Authorization: Bearer $OPENAI_API_KEY" ${AISH_URL}/v1/models | grep gpt- | cut -d'"' -f4 | sort -r
  exit 0
fi

# test if user has sourced the script and notify them if not

_throw_source_error () {
  echo "Please source aish in a bash or zsh shell like this:"
  echo ". aish ${@}"
  # echo ${1}
  exit 1
}

OS=`uname`
OS="${OS//Darwin/Mac OSX}"

case $BASH_VERSION in *.*)
  SHELLNAME="bash"
  ;;
esac
case $ZSH_VERSION  in *.*)
  SHELLNAME="zsh"
  ;;
esac
case "$VERSION" in *zsh*)
  SHELLNAME="zsh"
  ;;
esac

MODEL=${AISH_MODEL:-gpt-3.5-turbo}

#echo "SHELLNAME: ${SHELLNAME}"
#echo "OS: ${OS}"
#echo "MODEL: ${MODEL}"

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
MESSAGES = [
    {
        "role": "system",
        "content": "You are an AI shell-scripting expert called Aish.",
    },
    {
        "role": "user",
        "content": (
            "Please write a one-liner for '${AISH_SHELL}' shell for performing the following task. "
            "Assume you have access to all of the commonly available unix commands on a modern '${AISH_OS}' system. "
            "You can separate multi-line commands with a semicolon or double ampersand but please put them on one "
            "line. Respond without using markdown formatting. Please only return the exact bash one-liner command "
            "without any superfluous words explaining it, and no formatting. Do NOT use backticks. Do not put "
            "backticks around the one-liner. Code should be bare without any markdown formatting. IMPORTANT: If you "
            "need to ask for clarification or provide any information other than a one-liner solution, please prefix "
            "your response with the exact phrase AISH_FEEDBACK: in all caps, with a colon. If you are responding with "
            "anything other than a shell script one-liner you MUST include AISH_FEEDBACK: (including the colon) as the "
            "start of the response.\n\n Here is the task I would like you to carry out with the one-liner: '$request'"
        ),
    },
]
