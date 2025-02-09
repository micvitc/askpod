from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http.models import Distance, VectorParams

load_dotenv()

client = QdrantClient(path=":memory:")
collection_name = "data"
embeddings = OpenAIEmbeddings()

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://api.openai.com/v1/chat/completions")

if collection_name not in [col.name for col in client.get_collections().collections]:
    client.create_collection(
        collection_name="data",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )

vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,
)

model = ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY, base_url=BASE_URL)
