from fastapi import HTTPException

from src.core.relationaldb.models.exceptions import RecordUpdateNotAllowedError  # noqa: F401


class NoRecordFoundError(HTTPException):
    def __init__(self, code:int = 404, message:str = ''):
        super().__init__(status_code=code, detail=f"Record not found\n {message}")
