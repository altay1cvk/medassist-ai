const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Envoie un message en mode RAG et stream la réponse via SSE.
 * @param {string} message
 * @param {function} onChunk - callback appelé pour chaque token reçu
 * @param {string} sessionId
 */
export async function sendMessageStream(message, onChunk, sessionId = "default") {
  const response = await fetch(`${API_URL}/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId, mode: "rag" }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const text = decoder.decode(value);
    const lines = text.split("\n").filter(l => l.startsWith("data: "));
    for (const line of lines) {
      const chunk = line.replace("data: ", "");
      if (chunk === "[DONE]") return;
      onChunk(chunk);
    }
  }
}

/**
 * Envoie un message en mode Agent (multi-étapes, outils).
 */
export async function sendAgentMessage(message, history = [], sessionId = "default") {
  const response = await fetch(`${API_URL}/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId, mode: "agent", history }),
  });
  return response.json();
}

/**
 * Transcrit un fichier audio en texte.
 */
export async function transcribeAudio(audioFile) {
  const formData = new FormData();
  formData.append("file", audioFile);
  const response = await fetch(`${API_URL}/chat/audio/transcribe`, {
    method: "POST",
    body: formData,
  });
  const { transcription } = await response.json();
  return transcription;
}
