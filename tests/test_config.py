from pathlib import Path

from postmanager.config import setup_local_client, setup_s3_client


def test_setup_s3_client():
    client = setup_s3_client()

    # Assert
    assert client.__class__.__name__ == "S3"


def test_setup_local_client():
    client = setup_local_client()

    # Assert
    assert isinstance(client(), Path)
