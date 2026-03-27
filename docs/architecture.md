# 🏗️ Architecture détaillée — MedAssist AI

## Vue d'ensemble

MedAssist AI est structuré autour de 3 piliers:

1. **RAG (Retrieval Augmented Generation)** — TP3 du cours
2. **Agents LangChain** — TP4 du cours
3. **Multimodalité** — TP5 du cours

## Décisions techniques

### Pourquoi FAISS ?
- Léger, performant, pas besoin d'une base externe
- Fonctionne en mémoire → latence très faible
- Sauvegarde locale → données médicales confidentielles

### Pourquoi Mistral via Ollama ?
- 100% on-premise → aucune donnée patient ne sort de l'infra
- Mistral 7B performant en français médical
- Compatible avec une future migration vers GPT-4o

### Pourquoi FastAPI + SSE ?
- Streaming natif via Server-Sent Events
- Documentation OpenAPI auto-générée
- Compatible avec le frontend React sans WebSocket complexe
