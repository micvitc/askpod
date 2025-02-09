from fastapi import HTTPException


class QueryError(HTTPException):
    def __init__(self, detail: str = "Error processing query"):
        super().__init__(status_code=500, detail=detail)


class TranscriptLoadError(HTTPException):
    def __init__(self, detail: str = "Error loading transcript"):
        super().__init__(status_code=500, detail=detail)
