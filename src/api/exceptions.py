from fastapi import HTTPException

from src.core.relationaldb.repositories.exceptions import NoRecordFoundError  #noqa: F401


class ServerInitError(HTTPException):
    def __init__(self, code:int = 500, message:str = ''):
        super().__init__(status_code=code, detail=f"Server's Lifespawn Init Error, \n {message}")
