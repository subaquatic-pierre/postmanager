import json
from unittest import TestCase
from unittest.mock import MagicMock

from postmanager.proxy import MockBucketProxy
from postmanager.utils import BUCKET_NAME, BUCKET_ROOT_DIR


class BucketProxyTest(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.bucket = MockBucketProxy(BUCKET_NAME, BUCKET_ROOT_DIR)

    def test_get_json(self):
        object_key = "index.json"
        json = self.bucket.get_json(object_key)
        self.assertEqual(json["test"], "ok")
        self.assertIsInstance(json, dict)

    def test_save_json(self):
        filename = "filename.txt"
        body = {}
        self.bucket.save_json(body, filename)

        call_count = self.bucket.bucket_interface.put_object.call_count
        self.assertEqual(call_count, 2)

        self.bucket.bucket_interface.put_object.assert_called_with(
            Bucket=self.bucket.bucket_name,
            Key=f"{self.bucket.root_dir}{filename}",
            Body=json.dumps(body),
        )

    def test_delete_files(self):
        filenames = ["filename1.txt", "filename1.txt"]

        self.bucket.delete_files(filenames)
        objects = [{"Key": filename} for filename in filenames]
        self.bucket.bucket_interface.delete_objects.assert_called_with(
            Bucket=self.bucket.bucket_name, Delete={"Objects": objects}
        )

    def test_delete_files_empty_array(self):
        filenames = []

        self.bucket.delete_files(filenames)
        self.bucket.bucket_interface.delete_objects.assert_not_called()

    def test_list_dir(self):
        expected_res = [
            f"{self.bucket.root_dir}something",
            f"{self.bucket.root_dir}somethingelse",
        ]

        list_objects_res = {
            "Contents": [
                {"Key": f"{self.bucket.root_dir}something"},
                {"Key": f"{self.bucket.root_dir}somethingelse"},
            ]
        }

        self.bucket.bucket_interface.list_objects_v2 = MagicMock(
            return_value=list_objects_res
        )
        dir_response = self.bucket.list_dir()
        self.bucket.bucket_interface.list_objects_v2.assert_called_once()

        self.assertIsInstance(dir_response, list)
        self.assertEqual(expected_res, dir_response)

    def test_save_bytes(self):
        body = b"0x00"
        filename = "something.jpg"
        self.bucket.save_bytes(body, filename)

        call_count = self.bucket.bucket_interface.put_object.call_count

        self.bucket.bucket_interface.put_object.assert_called_with(
            Key=f"{self.bucket.root_dir}{filename}", Body=body
        )
