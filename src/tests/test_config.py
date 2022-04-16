from pathlib import Path
from unittest import TestCase
import boto3

from postmanager.config import setup_local_client, setup_s3_client


class TestConfig(TestCase):
    def test_setup_s3_client(self):
        client = setup_s3_client()

        # Assert
        self.assertEqual(client.__class__.__name__, "S3")

    def test_setup_local_client(self):
        client = setup_local_client()

        # Assert
        self.assertIsInstance(client(), Path)
