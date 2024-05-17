import configparser
import io
import os.path
import uuid

import boto3
import botocore.auth
import botocore.model
import botocore.session


def _main() -> None:
    with open(os.path.expanduser('~/.aws/credentials'), 'r') as f:
        txt = f.read()

    config = configparser.ConfigParser()
    config.read_file(io.StringIO(txt))
    cred_cfg = {k.lower(): v for k, v in config.items('default')}

    session = botocore.session.get_session()
    loader = session.get_component('data_loader')

    service_name = 'ec2'
    region_name = 'us-west-1'
    access_key_id = cred_cfg['aws_access_key_id']
    secret_access_key = cred_cfg['aws_secret_access_key']

    session = botocore.session.Session()

    ec2_client = session.create_client(
        'ec2',
        region_name=region_name,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
    )

    response = ec2_client.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}],
    )

    print(response)

    ##

    service_model = ec2_client._service_model  # noqa
    operation_name = 'DescribeInstances'
    operation_model = service_model.operation_model(operation_name)
    request_context = {
        'client_region': ec2_client.meta.region_name,
        'client_config': ec2_client.meta.config,
        'has_streaming_input': operation_model.has_streaming_input,
        'auth_type': operation_model.auth_type,
    }

    # signer = botocore.auth.SigV4Auth()

    api_params = {'Filters': [{'Name': 'instance-state-name', 'Values': ['running']}]}
    (
        endpoint_url,
        additional_headers,
        properties,
    ) = ec2_client._resolve_endpoint_ruleset(
        operation_model, api_params, request_context
    )
    if properties:
        # Pass arbitrary endpoint info with the Request
        # for use during construction.
        request_context['endpoint_properties'] = properties
    request_dict = ec2_client._convert_to_request_dict(
        api_params=api_params,
        operation_model=operation_model,
        endpoint_url=endpoint_url,
        context=request_context,
        headers=additional_headers,
    )
    from botocore.httpchecksum import (
        apply_request_checksum,
        resolve_checksum_context,
    )
    resolve_checksum_context(request_dict, operation_model, api_params)

    from botocore.compress import maybe_compress_request
    maybe_compress_request(ec2_client.meta.config, request_dict, operation_model)
    apply_request_checksum(request_dict)

    # http, parsed_response = ec2_client._make_request(operation_model, request_dict, request_context)
    # print(parsed_response)

    endpoint = ec2_client._endpoint
    context = request_dict['context']
    request = endpoint.create_request(request_dict, operation_model)
    success_response, exception = endpoint._get_response(
        request, operation_model, context
    )
    print((success_response, exception))


    # if http.status_code >= 300:
    #     error_info = parsed_response.get("Error", {})
    #     error_code = error_info.get("QueryErrorCode") or error_info.get(
    #         "Code"
    #     )
    #     error_class = ec2_client.exceptions.from_code(error_code)
    #     raise error_class(parsed_response, operation_name)
    # else:
    #     return parsed_response


if __name__ == '__main__':
    _main()
