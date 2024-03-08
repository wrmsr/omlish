"""
https://graphql-spec.runpod.io/

curl -s --request POST \
  --header 'content-type: application/json' \
  --url "https://api.runpod.io/graphql?api_key=$RUNPOD_API_KEY" \
  --data '{"query": "query Pods { myself { pods { id } } }"}'

curl --request POST \
  --header 'content-type: application/json' \
  --url "https://api.runpod.io/graphql?api_key=$RUNPOD_API_KEY" \
  --data '{"query": "mutation { podStop(input: { id: \"hcbt5m4crrm1wu\" } ) } { id }" }'
"""


def _main():
    pass


if __name__ == '__main__':
    _main()
