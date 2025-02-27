from dotenv import load_dotenv

load_dotenv()
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
import shutil
from backend.exceptions import (
    TranscriptLoadError,
    QueryError,
)

import urllib.parse


from backend.models import PodcastSession
from sqlalchemy.orm import Session
from backend.database import get_db  # Assume a dependency providing a database session


from fastapi import Body, HTTPException


from fastapi import Query

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

from minio import Minio
from minio.error import S3Error


DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
FRONTEND_ORIGINS = os.environ.get("FRONTEND_ORIGINS", "").split(",")

app = FastAPI()
start_time = datetime.now()

Base.metadata.create_all(bind=engine)
minio_client = Minio(
    os.getenv("MINIO_SERVER_ADDRESS"),  # Replace with your MinIO server address
    access_key=os.getenv("MINIO_ACCESS_KEY"),  # Replace with your MinIO access key
    secret_key=os.getenv("MINIO_SECRET_KEY"),  # Replace with your MinIO secret key
    secure=False,  # Set to True if using HTTPS
)
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


def ensure_bucket_exists(bucket_name: str):
    """Ensure that the specified bucket exists in MinIO."""
    found = minio_client.bucket_exists(bucket_name)
    if not found:
        minio_client.make_bucket(bucket_name)


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


import urllib.parse
import requests


@app.post("/upload_pdf_to_session")
async def upload_pdf_to_session(
    session_id: int = Query(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Retrieve session record belonging to current user.
    session_record = (
        db.query(PodcastSession)
        .filter(
            PodcastSession.id == session_id, PodcastSession.user_id == user.username
        )
        .first()
    )
    if not session_record:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        user_upload_dir = f"uploads/{user.username}"
        os.makedirs(user_upload_dir, exist_ok=True)
        file_path = f"{user_upload_dir}/{session_id}/{file.filename}"

        # Save the file locally first
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        # Upload the file to MinIO
        minio_bucket = "files"  # Replace with your MinIO bucket name
        ensure_bucket_exists(minio_bucket)
        minio_object_name = f"{user.username}/{session_id}/{file.filename}"
        minio_object_name = urllib.parse.unquote(
            minio_object_name
        )  # Decode the object name
        minio_client.fput_object(minio_bucket, minio_object_name, file_path)

        # Get the MinIO URL
        minio_url = minio_client.presigned_get_object(minio_bucket, minio_object_name)
        # Update the session record with the MinIO URL
        session_record.pdf_path = minio_url
        session_record.pdf_name = file.filename
        db.commit()

        return {
            "message": "PDF uploaded successfully",
            "session_id": session_id,
            "minio_url": minio_url,
        }
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        # Clean up the directory if it is empty
        if os.path.exists(user_upload_dir) and not os.listdir(user_upload_dir):
            shutil.rmtree(user_upload_dir)


@app.post("/generate_podcast")
async def generate_podcast_endpoint(
    request: Request,
    session_id: int = Body(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    local_pdf_path = None
    audio_path = None
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

        # Download the PDF file from the URL stored in pdf_path
        pdf_url = session_record.pdf_path
        pdf_filename = os.path.basename(urllib.parse.urlparse(pdf_url).path)
        local_pdf_path = f"downloads/{user.username}/{session_record.id}/{pdf_filename}"
        os.makedirs(os.path.dirname(local_pdf_path), exist_ok=True)

        response = requests.get(pdf_url)
        with open(local_pdf_path, "wb") as f:
            f.write(response.content)

        # Generate transcript using the downloaded PDF file.
        transcript = create_transcript(local_pdf_path)

        # Create audio in a folder under audio/<username>/<session_id>
        audio_folder = f"audio/{user.username}/{session_record.id}"
        os.makedirs(audio_folder, exist_ok=True)
        # Use the original PDF basename with a .wav extension.
        base = os.path.splitext(pdf_filename)[0]
        audio_path = f"{audio_folder}/{base}.wav"
        generate_audio(transcript["transcript"], output_filename=audio_path)

        # Upload the audio file to MinIO
        minio_bucket = "audio"  # Replace with your MinIO bucket name
        ensure_bucket_exists(minio_bucket)
        minio_object_name = f"{user.username}/{session_record.id}/{base}.wav"
        minio_object_name = urllib.parse.unquote(
            minio_object_name
        )  # Decode the object name
        minio_client.fput_object(minio_bucket, minio_object_name, audio_path)

        # Get the MinIO URL
        minio_url = minio_client.presigned_get_object(minio_bucket, minio_object_name)

        # Update the session record with the MinIO URL
        session_record.audio_path = minio_url
        db.commit()

        return {
            "message": "Podcast generated successfully",
            "session_id": session_record.id,
            "minio_url": minio_url,
        }
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO error: {str(e)}")
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    finally:
        # Clean up the downloaded PDF file and generated audio file
        if local_pdf_path and os.path.exists(local_pdf_path):
            os.remove(local_pdf_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        # Clean up the directories if they are empty
        if (
            local_pdf_path
            and os.path.exists(os.path.dirname(local_pdf_path))
            and not os.listdir(os.path.dirname(local_pdf_path))
        ):
            shutil.rmtree(os.path.dirname(local_pdf_path))
        if audio_path and os.path.exists(audio_folder) and not os.listdir(audio_folder):
            shutil.rmtree(audio_folder)


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
            "pdf_name": s.pdf_name,
            "pdf_path": s.pdf_path,
            "audio_path": s.audio_path,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]


app.include_router(auth_router)
