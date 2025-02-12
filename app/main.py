from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Request
from backend.exceptions import (
    TranscriptLoadError,
    QueryError,
)
from fastapi.responses import JSONResponse

from fastapi.staticfiles import StaticFiles

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
from backend.workflows import query_transcripts, load_pdf, create_transcript

from backend.tts.generate import generate_audio

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

app.mount("/audio", StaticFiles(directory="audio"), name="audio")


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


@app.post("/create_transcript")
async def create_transcript_endpoint(file: UploadFile = File(...)):
    try:
        content = await file.read()
        os.makedirs("uploads", exist_ok=True)
        with open(f"uploads/{file.filename}", "wb") as f:
            f.write(content)
        podcast = create_transcript(f"uploads/{file.filename}")
        return podcast
    except Exception as e:
        raise TranscriptLoadError(detail=str(e))


@app.post("/generate_podcast")
async def generate_podcast_endpoint(request: Request, file: UploadFile = File(...)):
    try:
        content = await file.read()
        os.makedirs("uploads", exist_ok=True)
        with open(f"uploads/{file.filename}", "wb") as f:
            f.write(content)
        transcript = create_transcript(f"uploads/{file.filename}")
        generate_audio(transcript["transcript"])
        podcast_path = os.path.join("audio", "combined_audio.wav")
        full_url = request.url_for("audio", path="combined_audio.wav")
        return {"podcast_path": full_url._url}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
