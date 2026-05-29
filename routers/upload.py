from fastapi import APIRouter, UploadFile, File, HTTPException, status
from s3_utils import upload_file_to_s3
from typing import Dict

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

@router.post("/", response_model=Dict[str, str])
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File provided is not an image."
        )

    # Upload to S3
    image_url = upload_file_to_s3(file.file, file.filename, file.content_type)
    
    if not image_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image. Please check server configuration."
        )
        
    return {"url": image_url}
