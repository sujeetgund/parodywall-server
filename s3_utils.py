import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from config import settings
import uuid
from typing import Optional

def get_s3_client():
    if not settings.aws_access_key_id or not settings.aws_secret_access_key:
        return None
    
    return boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region_name
    )

def upload_file_to_s3(file_obj, filename: str, content_type: str = "image/jpeg") -> Optional[str]:
    """
    Uploads a file object to AWS S3 and returns the public URL.
    """
    s3_client = get_s3_client()
    if not s3_client:
        print("S3 client not configured. Missing credentials.")
        return None
        
    bucket_name = settings.aws_s3_bucket_name
    if not bucket_name:
        print("S3 bucket name not configured.")
        return None

    # Generate a unique filename to prevent overwriting
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    try:
        s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            unique_filename,
            ExtraArgs={
                "ContentType": content_type
            }
        )
        
        # Build the URL
        url = f"https://{bucket_name}.s3.{settings.aws_region_name}.amazonaws.com/{unique_filename}"
        return url
    
    except NoCredentialsError:
        print("Credentials not available")
        return None
    except ClientError as e:
        print(f"Failed to upload to S3: {e}")
        return None
