from pydantic import BaseModel


class UploadLimitsResponse(BaseModel):
    max_upload_bytes: int
    max_upload_mb: float
