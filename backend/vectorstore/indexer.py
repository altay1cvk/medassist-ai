import argparse
import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from config import get_settings

settings = get_settings()


def get_embeddings():
    return OllamaEmbeddings(
        model="nomic-embed-text",     # ← 768 dims = correspond à l'index
        base_url=settings.ollama_base_url,
    )


def load_documents(source_path: str):
    all_docs = []
    loader = DirectoryLoader(source_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    try:
        all_docs.extend(loader.load())
    except Exception as e:
        print(f"⚠️  {e}")
    return all_docs


def index_documents(source_path: str):
    print(f"📂 Chargement depuis: {source_path}")
    docs = load_documents(source_path)
    print(f"   → {len(docs)} documents")
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    print(f"   → {len(chunks)} chunks")
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    os.makedirs(settings.faiss_index_path, exist_ok=True)
    vectorstore.save_local(settings.faiss_index_path)
    print(f"✅ Index sauvegardé dans: {settings.faiss_index_path}")
    return vectorstore


def load_vectorstore():
    embeddings = get_embeddings()
    return FAISS.load_local(
        settings.faiss_index_path,
        embeddings,
        allow_dangerous_deserialization=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="./data/documents/")
    args = parser.parse_args()
    index_documents(args.source)
