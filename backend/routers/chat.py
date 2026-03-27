"""
Routes FastAPI pour le chat.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import tempfile
import os

router = APIRouter()

# État global simple — utiliser Redis en prod
_rag_chain = None
_agent_executor = None


def get_rag_chain():
    global _rag_chain
    if _rag_chain is None:
        from chains.rag_chain import build_rag_chain
        _rag_chain, _ = build_rag_chain()
    return _rag_chain


def get_agent():
    global _agent_executor
    if _agent_executor is None:
        from chains.agent_chain import build_agent
        _agent_executor = build_agent()
    return _agent_executor


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    mode: Optional[str] = "rag"  # "rag" | "agent"
    history: Optional[list[dict]] = []


class IndexRequest(BaseModel):
    source_path: str = "./data/documents/"


@router.post("/")
async def chat(req: ChatRequest):
    """Envoie un message — retourne en streaming SSE."""
    if req.mode == "agent":
        agent = get_agent()
        from chains.agent_chain import format_history
        result = await agent.ainvoke({
            "input": req.message,
            "chat_history": format_history(req.history),
        })
        return {"answer": result["output"], "mode": "agent"}

    # Mode RAG (défaut)
    chain = get_rag_chain()

    async def generate():
        async for chunk in chain.astream(req.message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/index")
async def index_documents(req: IndexRequest):
    """Indexe les documents depuis un dossier."""
    from vectorstore.indexer import index_documents
    try:
        index_documents(req.source_path)
        return {"status": "success", "message": "Documents indexés avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audio/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcrit un fichier audio en texte via Whisper."""
    import whisper
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        model = whisper.load_model("base")
        result = model.transcribe(tmp_path)
        return {"transcription": result["text"]}
    finally:
        os.unlink(tmp_path)
