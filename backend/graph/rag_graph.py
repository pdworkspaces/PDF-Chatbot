
from typing import TypedDict, List

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

from backend.services.llm_service import get_llm
from backend.services.rag_service import retrieve_context


# 1. Define shared graph state
class RAGState(TypedDict):
    question: str
    document_id: str
    provider: str
    documents: List[Document]
    context: str
    source_pages: List[int]
    answer: str


# 2. Retrieve relevant documents from ChromaDB
def retrieve_node(state: RAGState):

    documents = retrieve_context(
        state["question"],
        state["document_id"]
    )

    context = "\n\n".join(
        doc.page_content for doc in documents
    )

    source_pages = sorted(set(
        int(doc.metadata.get("page", 0)) + 1
        for doc in documents
    ))

    return {
        "documents": documents,
        "context": context,
        "source_pages": source_pages
    }


# 3. Generate answer using LLM
def generate_node(state: RAGState):

    if not state["context"]:
        return {
            "answer": "I could not find relevant information in the PDF."
        }

    llm = get_llm(state["provider"])

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a PDF question-answering assistant.

Answer using only the provided context.
Do not make up information.

If the answer is unavailable in the context,
say that you could not find it in the PDF."""
        ),
        (
            "human",
            """Context:
{context}

Question:
{question}

Give a clear and concise answer."""
        )
    ])

    chain = prompt | llm

    response = chain.invoke({
        "context": state["context"],
        "question": state["question"]
    })

    return {
        "answer": response.content
    }


# 4. Build LangGraph workflow
def build_rag_graph():

    workflow = StateGraph(RAGState)

    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)

    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


# 5. Compile graph
rag_graph = build_rag_graph()


# 6. Public function
def ask_pdf(
    question: str,
    document_id: str,
    provider: str = "ollama"
):

    result = rag_graph.invoke({
        "question": question,
        "document_id": document_id,
        "provider": provider,
        "documents": [],
        "context": "",
        "source_pages": [],
        "answer": ""
    })

    return {
        "question": question,
        "answer": result["answer"],
        "source_pages": result["source_pages"]
    }
