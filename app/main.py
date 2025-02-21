from dotenv import load_dotenv
import jwt
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Request,
    BackgroundTasks,
    HTTPException,
    APIRouter,
    Depends,
    status,
)
from backend.exceptions import (
    TranscriptLoadError,
    QueryError,
)

from sqlalchemy.orm import Session

from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime, timedelta

from fastapi.staticfiles import StaticFiles
import aiofiles
import uuid
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
from backend.auth import router as auth_router
from backend.auth import get_current_user
from backend.models import PodcastSession
from backend.database import Base, engine, SessionLocal

Base.metadata.create_all(bind=engine)
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

os.makedirs("uploads", exist_ok=True)
os.makedirs("audio", exist_ok=True)
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
async def create_transcript_endpoint(
    file: UploadFile = File(...), user: dict = Depends(get_current_user)
):
    try:
        content = await file.read()
        # Use the username rather than an id
        user_upload_dir = f"uploads/{user.username}"
        os.makedirs(user_upload_dir, exist_ok=True)
        file_path = f"{user_upload_dir}/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        podcast = create_transcript(file_path)
        return podcast
    except Exception as e:
        raise TranscriptLoadError(detail=str(e))


# LANGUAGE: python
from backend.models import PodcastSession
from sqlalchemy.orm import Session
from backend.database import get_db  # Assume a dependency providing a database session


from fastapi import Body, HTTPException


from fastapi import Query


@app.post("/create_session")
async def create_session(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # Create a session record with empty pdf_path and audio_path.
        session_record = PodcastSession(
            user_id=user.username,
            pdf_path="",
            audio_path="",
        )
        db.add(session_record)
        db.commit()
        db.refresh(session_record)

        # Create the session folder under uploads/<username>/<session_id>
        session_folder = f"uploads/{user.username}/{session_record.id}"
        os.makedirs(session_folder, exist_ok=True)
        return session_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload_pdf_to_session")
async def upload_pdf_to_session(
    session_id: int = Query(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # Retrieve the session record and ensure it belongs to the current user.
        session_record = (
            db.query(PodcastSession)
            .filter(
                PodcastSession.id == session_id, PodcastSession.user_id == user.username
            )
            .first()
        )
        if not session_record:
            raise HTTPException(status_code=404, detail="Session not found")

        # Use the existing session folder.
        session_folder = f"uploads/{user.username}/{session_record.id}"
        os.makedirs(session_folder, exist_ok=True)
        pdf_path = f"{session_folder}/{file.filename}"
        content = await file.read()
        async with aiofiles.open(pdf_path, "wb") as f:
            await f.write(content)

        # Update the session record with the correct pdf_path.
        session_record.pdf_path = pdf_path
        db.commit()
        return session_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_podcast")
async def generate_podcast_endpoint(
    request: Request,
    session_id: int = Body(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # Retrieve the session record and ensure it belongs to the current user.
        session_record = (
            db.query(PodcastSession)
            .filter(
                PodcastSession.id == session_id, PodcastSession.user_id == user.username
            )
            .first()
        )
        if not session_record:
            raise HTTPException(status_code=404, detail="Session not found")

        # Generate transcript using the stored PDF file.
        transcript = create_transcript(session_record.pdf_path)

        # Create audio in a folder under audio/<username>/<session_id>
        audio_folder = f"audio/{user.username}/{session_record.id}"
        os.makedirs(audio_folder, exist_ok=True)
        # Use the original PDF basename with a .wav extension.
        base = os.path.splitext(os.path.basename(session_record.pdf_path))[0]
        audio_path = f"{audio_folder}/{base}.wav"
        generate_audio(transcript["transcript"], output_filename=audio_path)

        # Update the session record with the audio path.
        session_record.audio_path = audio_path
        db.commit()

        # Create a full URL to the generated audio.
        full_url = request.url_for(
            "audio",
            path=f"{user.username}/{session_record.id}/{os.path.basename(audio_path)}",
        )
        return {"podcast_path": full_url._url, "session_id": session_record.id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.get("/sessions")
async def list_sessions(
    user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    sessions = (
        db.query(PodcastSession).filter(PodcastSession.user_id == user.username).all()
    )
    # Return a simple list of sessions
    return [
        {
            "id": s.id,
            "pdf_path": s.pdf_path,
            "audio_path": s.audio_path,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]


app.include_router(auth_router)
