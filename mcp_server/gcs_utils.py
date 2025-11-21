import os
from google.cloud import storage
import sys

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
        print(f"Downloaded storage object {source_blob_name} from bucket {bucket_name} to local file {destination_file_name}.", file=sys.stderr)
    except Exception as e:
        print(f"Failed to download {source_blob_name} from {bucket_name}: {e}", file=sys.stderr)
        raise

def download_directory(bucket_name, prefix, local_dir):
    """Downloads a directory from the bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        for blob in blobs:
            if blob.name.endswith("/"):
                continue
            
            # Remove the prefix from the local path to keep the structure relative
            relative_path = os.path.relpath(blob.name, prefix)
            local_path = os.path.join(local_dir, relative_path)
            
            local_dir_path = os.path.dirname(local_path)
            if not os.path.exists(local_dir_path):
                os.makedirs(local_dir_path)
                
            blob.download_to_filename(local_path)
            print(f"Downloaded {blob.name} to {local_path}", file=sys.stderr)
            
    except Exception as e:
        print(f"Failed to download directory {prefix} from {bucket_name}: {e}", file=sys.stderr)
        raise
