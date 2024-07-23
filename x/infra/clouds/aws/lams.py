"""
See:
 - https://docs.aws.amazon.com/lambda/latest/api/API_Invoke.html
 - https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
 - https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/python/example_code/lambda
 - https://docs.aws.amazon.com/lambda/latest/dg/creating-deleting-layers.html

==

Context methods
get_remaining_time_in_millis – Returns the number of milliseconds left before the execution times out.

Context properties
function_name – The name of the Lambda function.
function_version – The version of the function.
invoked_function_arn – The Amazon Resource Name (ARN) that's used to invoke the function. Indicates if the invoker specified a version number or alias.
memory_limit_in_mb – The amount of memory that's allocated for the function.
aws_request_id – The identifier of the invocation request.
log_group_name – The log group for the function.
log_stream_name – The log stream for the function instance.
identity – (mobile apps) Information about the Amazon Cognito identity that authorized the request.
  cognito_identity_id – The authenticated Amazon Cognito identity.
  cognito_identity_pool_id – The Amazon Cognito identity pool that authorized the invocation.
client_context – (mobile apps) Client context that's provided to Lambda by the client application.
  client.installation_id
  client.app_title
  client.app_version_name
  client.app_version_code
  client.app_package_name
  custom – A dict of custom values set by the mobile client application.
  env – A dict of environment information provided by the AWS SDK.

==

response = client.create_function(
    FunctionName='string',
    Runtime='nodejs'|'nodejs4.3'|'nodejs6.10'|'nodejs8.10'|'nodejs10.x'|'nodejs12.x'|'nodejs14.x'|'nodejs16.x'|'java8'|'java8.al2'|'java11'|'python2.7'|'python3.6'|'python3.7'|'python3.8'|'python3.9'|'dotnetcore1.0'|'dotnetcore2.0'|'dotnetcore2.1'|'dotnetcore3.1'|'dotnet6'|'dotnet8'|'nodejs4.3-edge'|'go1.x'|'ruby2.5'|'ruby2.7'|'provided'|'provided.al2'|'nodejs18.x'|'python3.10'|'java17'|'ruby3.2'|'ruby3.3'|'python3.11'|'nodejs20.x'|'provided.al2023'|'python3.12'|'java21',
    Role='string',
    Handler='string',
    Code={
        'ZipFile': b'bytes',
        'S3Bucket': 'string',
        'S3Key': 'string',
        'S3ObjectVersion': 'string',
        'ImageUri': 'string'
    },
    Description='string',
    Timeout=123,
    MemorySize=123,
    Publish=True|False,
    VpcConfig={
        'SubnetIds': [
            'string',
        ],
        'SecurityGroupIds': [
            'string',
        ],
        'Ipv6AllowedForDualStack': True|False
    },
    PackageType='Zip'|'Image',
    DeadLetterConfig={
        'TargetArn': 'string'
    },
    Environment={
        'Variables': {
            'string': 'string'
        }
    },
    KMSKeyArn='string',
    TracingConfig={
        'Mode': 'Active'|'PassThrough'
    },
    Tags={
        'string': 'string'
    },
    Layers=[
        'string',
    ],
    FileSystemConfigs=[
        {
            'Arn': 'string',
            'LocalMountPath': 'string'
        },
    ],
    ImageConfig={
        'EntryPoint': [
            'string',
        ],
        'Command': [
            'string',
        ],
        'WorkingDirectory': 'string'
    },
    CodeSigningConfigArn='string',
    Architectures=[
        'x86_64'|'arm64',
    ],
    EphemeralStorage={
        'Size': 123
    },
    SnapStart={
        'ApplyOn': 'PublishedVersions'|'None'
    },
    LoggingConfig={
        'LogFormat': 'JSON'|'Text',
        'ApplicationLogLevel': 'TRACE'|'DEBUG'|'INFO'|'WARN'|'ERROR'|'FATAL',
        'SystemLogLevel': 'DEBUG'|'INFO'|'WARN',
        'LogGroup': 'string'
    }
)

==

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    ...
    result = None
    action = event.get('action')
    if action == 'increment':
        result = event.get('number', 0) + 1
        logger.info('Calculated result of %s', result)
    else:
        logger.error("%s is not a valid action.", action)

    response = {'result': result}
    return response
"""
