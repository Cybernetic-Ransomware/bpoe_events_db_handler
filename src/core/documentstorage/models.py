import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, EmailStr, Field


class OCROnlyResult(BaseModel):
    ocr_result: list[str]

class OCRedImageInput(BaseModel):
    user_email: EmailStr
    filename: str
    ocr_result: list[str]

class OCRedImageResult(OCRedImageInput):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, alias='_id')
    upload_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    class Config:
        populate_by_name = True
