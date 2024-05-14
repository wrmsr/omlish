"""
https://graphql-spec.runpod.io/

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
import asyncio

import aiohttp

from omlish import json

from ....secrets import load_secrets


async def _a_main() -> None:
    cfg = load_secrets()
    api_key = cfg['runpod_api_key']

    async with aiohttp.ClientSession() as session:
        cols = [
            # "lowestBidPriceToResume",
            # "aiApiId",
            # "apiKey",
            # "consumerUserId",
            # "containerDiskInGb",
            # "containerRegistryAuthId",
            # "costMultiplier",
            # "costPerHr",
            # "adjustedCostPerHr",
            # "desiredStatus",
            # "dockerArgs",
            # "dockerId",
            # "env",
            # "gpuCount",
            # "gpuPowerLimitPercent",
            # "gpus",
            "id",
            "imageName",
            # "lastStatusChange",
            # "locked",
            # "machineId",
            # "memoryInGb",
            # "name",
            # "podType",
            "port",
            "ports",
            # "registry",
            # "templateId",
            # "uptimeSeconds",
            # "vcpuCount",
            # "version",
            # "volumeEncrypted",
            # "volumeInGb",
            # "volumeKey",
            # "volumeMountPath",
            # "runtime",
            # "machine",
            # "latestTelemetry",
            # "endpoint",
            # "networkVolume",
            # "savingsPlans",
        ]
        query = 'query Pods { myself { pods { ' + ' '.join(cols) + ' } } }'

        async with session.post(
                f'https://api.runpod.io/graphql?api_key={api_key}',
                data='{"query": "' + query + '"}',
                headers={
                    'content-type': 'application/json',
                },
        ) as resp:
            print(resp.status)
            buf = await resp.text()
            print(json.dumps_pretty(json.loads(buf)))


if __name__ == '__main__':
    asyncio.run(_a_main())
