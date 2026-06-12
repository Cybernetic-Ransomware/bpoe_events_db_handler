from fastapi import HTTPException


class ServerInitError(HTTPException):
    def __init__(self, code: int = 500, message: str = ""):
        super().__init__(status_code=code, detail=f"Server lifespan init error: {message}")
