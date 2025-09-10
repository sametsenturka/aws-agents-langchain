from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional, Type, Any
import boto3, json, os


class NoInputSchema(BaseModel):
    """Schema for tools that take no arguments"""
    pass


class S3ListBucketsTool(BaseTool):
    name: str = "s3_list_buckets"
    description: str = "List all S3 buckets"
    args_schema: Type[BaseModel] = NoInputSchema
    _s3: Any = PrivateAttr()

    def __init__(self, region_name: str = "eu-north-1"):
        super().__init__()
        self._s3 = boto3.client("s3", region_name=region_name)

    def _run(self) -> str:
        try:
            response = self._s3.list_buckets()
            buckets = [{"Name": b["Name"], "CreationDate": b["CreationDate"].strftime("%Y-%m-%d %H:%M:%S")}
                       for b in response.get("Buckets", [])]
            return json.dumps(buckets, indent=2)
        except Exception as e:
            return f"Error listing buckets: {str(e)}"


class S3UploadFileInput(BaseModel):
    file_path: str = Field(..., description="Local path of the file")
    bucket_name: str = Field(..., description="Target S3 bucket name")
    key: Optional[str] = Field(None, description="S3 object key (defaults to file name)")

class S3UploadFileTool(BaseTool):
    name: str = "s3_upload_file"
    description: str = "Upload a file to an S3 bucket"
    args_schema: Type[BaseModel] = S3UploadFileInput
    _s3: Any = PrivateAttr()

    def __init__(self, region_name: str = "eu-north-1"):
        super().__init__()
        self._s3 = boto3.client("s3", region_name=region_name)

    def _run(self, file_path: str, bucket_name: str, key: Optional[str] = None) -> str:
        try:
            key = key or os.path.basename(file_path)
            self._s3.upload_file(file_path, bucket_name, key)
            return f"Uploaded {file_path} to s3://{bucket_name}/{key}"
        except Exception as e:
            return f"Error uploading file: {str(e)}"


class S3DownloadFileInput(BaseModel):
    bucket_name: str = Field(..., description="S3 bucket name")
    key: str = Field(..., description="S3 object key to download")
    file_path: str = Field(..., description="Local path to save the file")

class S3DownloadFileTool(BaseTool):
    name: str = "s3_download_file"
    description: str = "Download a file from an S3 bucket"
    args_schema: Type[BaseModel] = S3DownloadFileInput
    _s3: Any = PrivateAttr()

    def __init__(self, region_name: str = "eu-north-1"):
        super().__init__()
        self._s3 = boto3.client("s3", region_name=region_name)

    def _run(self, bucket_name: str, key: str, file_path: str) -> str:
        try:
            self._s3.download_file(bucket_name, key, file_path)
            return f"Downloaded s3://{bucket_name}/{key} to {file_path}"
        except Exception as e:
            return f"Error downloading file: {str(e)}"


