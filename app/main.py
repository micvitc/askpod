from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from backend.exceptions import (
    TranscriptLoadError,
    QueryError,
)
from backend.utils import write_to_env_file
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import (
    LoadDataRequest,
    QueryRequest,
    QueryResponse,
    MetadataResponse,
    HealthCheckResponse,
    SetEnvVarsInput,
)
from backend.workflows import query_transcripts, load_pdf, create_podcast

from datetime import datetime
import os


DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
FRONTEND_ORIGINS = os.environ.get("FRONTEND_ORIGINS", "").split(",")

app = FastAPI()
start_time = datetime.now()

# Remove this later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.post("/load")
# async def load_data(request: LoadDataRequest):
#     try:
#         return load_transcript(request.video_id)
#     except Exception as e:
#         raise TranscriptLoadError(detail=str(e))


# @app.post("/query", response_model=QueryResponse)
# async def query(request: QueryRequest):
#     try:
#         return query_transcripts(request.query, [])
#     except Exception as e:
#         raise QueryError(detail=str(e))


@app.get("/metadata", response_model=MetadataResponse)
async def metadata():
    return {
        "Debug": DEBUG,
        "Frontend_Origins": FRONTEND_ORIGINS,
        "OPENAI_API_Key_Set": bool(os.getenv("OPENAI_API_KEY")),
        "Model_Name": os.getenv("MODEL_NAME", "gpt-4o-mini"),
        "Base_URL": os.getenv("BASE_URL", "https://api.openai.com/v1/chat/completions"),
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    uptime = datetime.now() - start_time
    return {
        "status": "healthy",
        "uptime": str(uptime),
        "current_time": datetime.now().isoformat(),
    }


@app.post("/set_env_vars")
async def set_env_vars(input: SetEnvVarsInput):
    for key, value in input.vars.items():
        write_to_env_file(key, value)
    return {"status": "success"}


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        content = await file.read()
        os.makedirs("uploads", exist_ok=True)
        with open(f"uploads/{file.filename}", "wb") as f:
            f.write(content)
        parsed_text = await load_pdf(f"uploads/{file.filename}")
        return {"parsed_text": parsed_text}
    except Exception as e:
        raise TranscriptLoadError(detail=str(e))


@app.post("/create_podcast")
async def create_podcast_endpoint(file: UploadFile = File(...)):
    try:
        content = await file.read()
        os.makedirs("uploads", exist_ok=True)
        with open(f"uploads/{file.filename}", "wb") as f:
            f.write(content)
        podcast = create_podcast(f"uploads/{file.filename}")
        return {"podcast": podcast}
    except Exception as e:
        raise TranscriptLoadError(detail=str(e))
