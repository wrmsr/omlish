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
import io
import typing as ta

import aiohttp

from omlish import json

from ....secrets import load_secrets


async def _a_main() -> None:
    cfg = load_secrets()
    api_key = cfg['runpod_api_key']

    pod_schema = [
        # 'lowestBidPriceToResume',
        # 'aiApiId',
        # 'apiKey',
        # 'consumerUserId',
        # 'containerDiskInGb',
        # 'containerRegistryAuthId',
        # 'costMultiplier',
        # 'costPerHr',
        # 'adjustedCostPerHr',
        # 'desiredStatus',
        # 'dockerArgs',
        # 'dockerId',
        # 'env',
        # 'gpuCount',
        # 'gpuPowerLimitPercent',
        # 'gpus',
        'id',
        'imageName',
        # 'lastStatusChange',
        # 'locked',
        # 'machineId',
        # 'memoryInGb',
        'name',
        'podType',
        'port',
        'ports',
        # 'registry',
        # 'templateId',
        'uptimeSeconds',
        'vcpuCount',
        # 'version',
        # 'volumeEncrypted',
        # 'volumeInGb',
        # 'volumeKey',
        # 'volumeMountPath',
        ('runtime', [
            # 'container'
            ('gpus', [
                'id',
                'gpuUtilPercent',
                'memoryUtilPercent',
            ]),
            ('ports', [
                'ip',
                'isIpPublic',
                'privatePort',
                'publicPort',
                'type',
            ]),
            # 'uptimeInSeconds'
        ]),
        # 'machine',
        # 'latestTelemetry',
        # 'endpoint',
        # 'networkVolume',
        # 'savingsPlans',
    ]

    def render_gql_schema(o: ta.Any, out: ta.TextIO) -> None:
        match o:
            case str(n):
                out.write(n)
            case list(l):
                out.write('{ ')
                for e in l:
                    render_gql_schema(e, out)
                    out.write(' ')
                out.write('}')
            case (n, c):
                out.write(n)
                out.write(' ')
                render_gql_schema(c, out)
            case _:
                raise TypeError(o)

    out = io.StringIO()
    render_gql_schema(pod_schema, out)
    pod_cols = out.getvalue()

    async with aiohttp.ClientSession() as session:
        query = 'query Pods { myself { pods ' + pod_cols + ' } }'

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
