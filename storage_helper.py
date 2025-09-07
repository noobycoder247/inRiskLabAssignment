import json

from google.cloud import storage


class BucketHelper:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def _get_client(self):
        return storage.Client()

    def _get_bucket(self):
        client = self._get_client()
        return client.bucket(self.bucket_name)

    def upload_file(self, local_file_path, cloud_file_path):
        bucket = self._get_bucket()
        blob = bucket.blob(cloud_file_path)
        blob.upload_from_filename(local_file_path)

    def download_file(self, cloud_file_path, local_file_path):
        bucket = self._get_bucket()
        blob = bucket.blob(cloud_file_path)
        blob.download_to_filename(local_file_path)

    def list_files(self, folder_path=""):
        bucket = self._get_bucket()
        blobs = bucket.list_blobs(prefix=folder_path)
        return [blob.name for blob in blobs]

    def file_exists(self, cloud_file_path):
        bucket = self._get_bucket()
        blob = bucket.blob(cloud_file_path)
        print(blob.name, blob.exists())
        return blob.exists()

    def read_json(self, cloud_file_path):
        bucket = self._get_bucket()
        blob = bucket.blob(cloud_file_path)
        content = blob.download_as_text(encoding="utf-8")
        return json.loads(content)
