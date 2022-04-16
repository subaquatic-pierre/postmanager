from pathlib import Path
import boto3
from botocore.config import Config


def setup_s3_client(credentials={}, client_config={}):
    default_config = Config(
        connect_timeout=5, read_timeout=60, retries={"max_attempts": 2}
    )

    client = boto3.client("s3", config=default_config)
    return client


def setup_local_client():
    client = Path
    return client
