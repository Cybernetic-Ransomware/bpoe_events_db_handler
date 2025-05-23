from fastapi import HTTPException


class PoolNotInitializedError(HTTPException):
    def __init__(self, message: str = ''):
        super().__init__(
            status_code=503,
            detail=f"Connection pool is not initialized.\n{message}"
        )


class ConnectionNotEstablishedError(HTTPException):
    def __init__(self, message: str = ''):
        super().__init__(
            status_code=500,
            detail=f"Connection not established. Call connect() first.\n{message}"
        )


class InvalidConnectorModeError(HTTPException):
    def __init__(self, mode: str):
        super().__init__(
            status_code=400,
            detail=f"Unknown connector mode '{mode}'. Use 'sync' or 'async'."
        )


class RecordUpdateNotAllowedError(HTTPException):
    def __init__(self, code:int = 404, message:str = ''):
        super().__init__(status_code=code, detail=f"Record can not be modified\n {message}")


class NoRecordFoundError(HTTPException):
    def __init__(self, code:int = 404, message:str = ''):
        super().__init__(status_code=code, detail=f"Record not found\n {message}")
