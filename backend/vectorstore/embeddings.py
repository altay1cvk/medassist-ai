from langchain_openai import OpenAIEmbeddings
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from config import get_settings

settings = get_settings()


def get_embeddings():
    """Retourne le modèle d'embedding selon la configuration."""
    if settings.embedding_model == "openai":
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key,
        )
    elif settings.embedding_model == "mistral":
        return MistralAIEmbeddings()
    else:
        # Ollama local — 100% on-premise
        return OllamaEmbeddings(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
        )
