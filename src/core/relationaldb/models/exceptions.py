from fastapi import HTTPException


class RecordUpdateNotAllowedError(HTTPException):
    def __init__(self, code:int = 404, message:str = ''):
        super().__init__(status_code=code, detail=f"Record can not be modified\n {message}")
