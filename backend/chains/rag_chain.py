"""
Pipeline RAG médical — LangChain + FAISS + Mistral/OpenAI
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from vectorstore.indexer import load_vectorstore
from config import get_settings
from typing import AsyncIterator

settings = get_settings()

MEDICAL_SYSTEM_PROMPT = """Tu es MedAssist, un assistant médical expert et fiable.
Tu réponds aux questions des professionnels de santé en te basant UNIQUEMENT
sur les documents fournis dans le contexte.

Règles strictes:
- Cite toujours tes sources (nom du document + numéro de page si disponible)
- Si l'information n'est pas dans le contexte, dis-le clairement
- Ne fais JAMAIS de diagnostic définitif — oriente vers un médecin si besoin
- Utilise un langage médical précis mais accessible
- Réponds en français par défaut

Contexte médical:
{context}
"""


def get_llm():
    if settings.llm_provider == "openai":
        return ChatOpenAI(model=settings.openai_model, temperature=0.1, streaming=True)
    return ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url,
                      temperature=0.1)


def format_docs(docs) -> str:
    formatted = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Document inconnu")
        page = doc.metadata.get("page", "")
        page_info = f", p.{page}" if page else ""
        formatted.append(f"[{i+1}] Source: {source}{page_info}\n{doc.page_content}")
    return "\n\n".join(formatted)


def build_rag_chain():
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", MEDICAL_SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever


async def stream_rag_response(question: str, chain) -> AsyncIterator[str]:
    async for chunk in chain.astream(question):
        yield chunk
