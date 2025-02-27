from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from qdrant_client.http.models import Distance, VectorParams

# Update this URL with your PostgreSQL credentials
SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRES_URI")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

embeddings = OpenAIEmbeddings()

# qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"))

# qdrant_client.create_collection(
#     collection_name="askpod",
#     vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
# )

# vector_store = QdrantVectorStore(
#     client=qdrant_client,
#     collection_name="askpod",
#     embedding=embeddings,
# )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
