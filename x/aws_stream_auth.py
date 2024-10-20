import datetime
import hashlib
import hmac

import requests


# AWS S3 Configuration
AWS_ACCESS_KEY_ID = 'YOUR_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'YOUR_SECRET_ACCESS_KEY'
AWS_REGION = 'us-west-2'
SERVICE = 's3'
BUCKET_NAME = 'your-bucket-name'
KEY_NAME = 'your-object-key'

# AWS S3 Endpoint
ENDPOINT = f'https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{KEY_NAME}'

# Constants for SigV4
CHUNK_SIZE = 64 * 1024  # 64 KB chunks for streaming
ISO8601_BASIC_FORMAT = "%Y%m%dT%H%M%SZ"
DATESTAMP_FORMAT = "%Y%m%d"


def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def get_signature_key(key, date_stamp, region_name, service_name):
    k_date = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, 'aws4_request')
    return k_signing


def create_canonical_request(method, uri, query_string, headers, payload_hash):
    canonical_headers = ''.join(f'{k}:{v}\n' for k, v in headers.items())
    signed_headers = ';'.join(headers.keys())
    return f"{method}\n{uri}\n{query_string}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"


def create_string_to_sign(canonical_request, request_datetime, datestamp):
    credential_scope = f"{datestamp}/{AWS_REGION}/{SERVICE}/aws4_request"
    hash_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    return f"AWS4-HMAC-SHA256\n{request_datetime}\n{credential_scope}\n{hash_canonical_request}"


def create_authorization_header(signature, headers, datestamp):
    credential_scope = f"{datestamp}/{AWS_REGION}/{SERVICE}/aws4_request"
    signed_headers = ';'.join(headers.keys())
    return f"AWS4-HMAC-SHA256 Credential={AWS_ACCESS_KEY_ID}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"


def calculate_chunk_signature(previous_signature, chunk_data, date_stamp):
    string_to_sign = f"AWS4-HMAC-SHA256-PAYLOAD\n{date_stamp}\n{previous_signature}\n{hashlib.sha256(chunk_data.encode('utf-8')).hexdigest()}"
    signing_key = get_signature_key(AWS_SECRET_ACCESS_KEY, date_stamp, AWS_REGION, SERVICE)
    return hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()


def stream_to_s3(file_path):
    with open(file_path, 'rb') as file:
        # Get request datetime
        request_datetime = datetime.datetime.utcnow().strftime(ISO8601_BASIC_FORMAT)
        date_stamp = datetime.datetime.utcnow().strftime(DATESTAMP_FORMAT)

        # Prepare headers
        headers = {
            'host': f"{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com",
            'x-amz-date': request_datetime,
            'x-amz-content-sha256': 'STREAMING-AWS4-HMAC-SHA256-PAYLOAD',
        }

        # Initial payload hash
        payload_hash = 'STREAMING-AWS4-HMAC-SHA256-PAYLOAD'

        # Create Canonical Request
        canonical_request = create_canonical_request(
            method='PUT',
            uri=f"/{KEY_NAME}",
            query_string='',
            headers=headers,
            payload_hash=payload_hash
        )

        # Create String to Sign
        string_to_sign = create_string_to_sign(canonical_request, request_datetime, date_stamp)

        # Calculate Signature
        signing_key = get_signature_key(AWS_SECRET_ACCESS_KEY, date_stamp, AWS_REGION, SERVICE)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        # Add Authorization Header
        authorization_header = create_authorization_header(signature, headers, date_stamp)
        headers['Authorization'] = authorization_header

        # Start streaming the file in chunks
        with requests.Session() as session:
            with session.put(ENDPOINT, headers=headers, stream=True) as response:
                previous_signature = signature

                while True:
                    chunk_data = file.read(CHUNK_SIZE)
                    if not chunk_data:
                        break

                    chunk_signature = calculate_chunk_signature(previous_signature, chunk_data.decode('utf-8'),
                                                                date_stamp)

                    chunk_header = f"{len(chunk_data)};chunk-signature={chunk_signature}\r\n".encode('utf-8')
                    chunk_footer = b"\r\n"

                    # Send the chunk header, data, and footer
                    response.raw.write(chunk_header)
                    response.raw.write(chunk_data)
                    response.raw.write(chunk_footer)

                    previous_signature = chunk_signature

        if response.status_code == 200:
            print("File uploaded successfully.")
        else:
            print(f"Failed to upload file. Status Code: {response.status_code}")


# Example Usage
file_path = 'path/to/your/large/file'
stream_to_s3(file_path)
