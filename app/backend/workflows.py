from backend.connect import model
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from backend.connect import vector_store
from langgraph.graph import START, StateGraph
from langchain_community.document_loaders import PyMuPDFLoader
from backend.prompts import rag_prompt, podcast_prompt, podcast_parser


class RAG_State(TypedDict):
    question: str
    context: List[Document]
    answer: str


def retrieve(state: RAG_State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: RAG_State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = rag_prompt.invoke(
        {"question": state["question"], "context": docs_content}
    )
    response = model.invoke(messages)
    return {"answer": response.content}


graph_builder = StateGraph(RAG_State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
rag_graph = graph_builder.compile()


def query_transcripts(query: str, chat_history: List[str]):
    return {
        "answer": rag_graph.invoke({"question": query, "context": chat_history})[
            "answer"
        ]
    }


podcast_chain = podcast_prompt | model | podcast_parser


def load_pdf(file):
    loader = PyMuPDFLoader(file)
    data = loader.load()
    content = ""
    for page in data:
        content += page.page_content + "\n\n"
    return content


def create_podcast(file):
    data = load_pdf(file)
    return podcast_chain.invoke(data)
