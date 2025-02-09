from pydantic import BaseModel, Field
from typing import List


class PodcastTranscript(BaseModel):
    transcript: str = Field(
        description="Create a new podcast transcript based on the given material."
    )


class QueryRequest(BaseModel):
    query: str
    chat_history: list[str]


class QueryResponse(BaseModel):
    answer: str


class HealthCheckResponse(BaseModel):
    status: str
    uptime: str
    current_time: str


class MetadataResponse(BaseModel):
    Debug: bool
    Frontend_Origins: List[str]
    OPENAI_API_Key_Set: bool
    Model_Name: str
    Base_URL: str


class SetEnvVarInput(BaseModel):
    key: str
    value: str


class SetEnvVarsInput(BaseModel):
    vars: dict


class LoadDataRequest(BaseModel):
    video_id: str


class LoadDataResponse(BaseModel):
    message: str
    points_added: int
