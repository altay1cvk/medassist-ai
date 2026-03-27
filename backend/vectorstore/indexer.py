"""
Indexeur de documents médicaux vers FAISS.
Usage: python indexer.py --source ./data/documents/
"""
import argparse
import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from embeddings import get_embeddings
from config import get_settings

settings = get_settings()


def load_documents(source_path: str):
    """Charge tous les PDF et TXT depuis un dossier."""
    loaders = {
        "**/*.pdf": PyPDFLoader,
        "**/*.txt": TextLoader,
    }
    all_docs = []
    for glob_pattern, loader_cls in loaders.items():
        loader = DirectoryLoader(source_path, glob=glob_pattern, loader_cls=loader_cls)
        try:
            all_docs.extend(loader.load())
        except Exception as e:
            print(f"⚠️  Erreur lors du chargement {glob_pattern}: {e}")
    return all_docs


def index_documents(source_path: str):
    """Pipeline complet: load → split → embed → index FAISS."""
    print(f"📂 Chargement des documents depuis: {source_path}")
    docs = load_documents(source_path)
    print(f"   → {len(docs)} documents chargés")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(docs)
    print(f"   → {len(chunks)} chunks générés")

    print("🧠 Génération des embeddings...")
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    index_path = settings.faiss_index_path
    os.makedirs(index_path, exist_ok=True)
    vectorstore.save_local(index_path)
    print(f"✅ Index FAISS sauvegardé dans: {index_path}")
    return vectorstore


def load_vectorstore():
    """Charge un index FAISS existant."""
    embeddings = get_embeddings()
    return FAISS.load_local(
        settings.faiss_index_path,
        embeddings,
        allow_dangerous_deserialization=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indexeur MedAssist AI")
    parser.add_argument("--source", default="./data/documents/", help="Dossier source")
    args = parser.parse_args()
    index_documents(args.source)
