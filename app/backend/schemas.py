from pydantic import BaseModel, Field
from typing import List, Tuple


class MaleHost(BaseModel):
    male_section: str = Field(description="Male host section.")


class FemaleHost(BaseModel):
    female_section: str = Field(description="Female host section.")


class PodcastTranscript(BaseModel):
    transcript: List[Tuple[MaleHost, FemaleHost]] = Field(
        description="Create a new podcast transcript based on the given material consisting of Two Hosts. One Male and one Female."
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
