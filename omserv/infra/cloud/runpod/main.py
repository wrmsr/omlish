"""
curl -s --request POST \
  --header 'content-type: application/json' \
  --url "https://api.runpod.io/graphql?api_key=$RUNPOD_API_KEY" \
  --data '{"query": "query Pods { myself { pods { id } } }"}'

curl -s --request POST \
  --header 'content-type: application/json' \
  --url "https://api.runpod.io/graphql?api_key=$RUNPOD_API_KEY" \
  --data '{"query": "query { gpuTypes { communityCloud communityPrice communitySpotPrice displayName id maxGpuCount memoryInGb oneMonthPrice secureCloud securePrice secureSpotPrice threeMonthPrice } }"}' | jq -C . | less -R

curl --request POST \
  --header 'content-type: application/json' \
  --url "https://api.runpod.io/graphql?api_key=$RUNPOD_API_KEY" \
  --data '{"query": "mutation { podStop(input: { id: \"ballsballsballs\" } ) } { id }" }'
"""
