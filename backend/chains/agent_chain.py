"""
Agent LangChain avec outils médicaux.
Capable de: calcul de dosages, interactions médicamenteuses, recherche PubMed.
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from chains.rag_chain import get_llm
from tools.medical_tools import get_medical_tools

AGENT_SYSTEM_PROMPT = """Tu es MedAssist, un agent médical expert.
Tu as accès à plusieurs outils spécialisés pour t'aider à répondre précisément.

Utilise les outils disponibles quand c'est pertinent:
- Pour un calcul de dosage → utilise `calcul_dosage`
- Pour vérifier des interactions → utilise `interactions_medicamenteuses`
- Pour chercher des études → utilise `recherche_pubmed`

Sois méthodique: explique chaque étape de ton raisonnement.
"""


def build_agent():
    llm = get_llm()
    tools = get_medical_tools()

    prompt = ChatPromptTemplate.from_messages([
        ("system", AGENT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=5)


def format_history(messages: list[dict]) -> list:
    history = []
    for msg in messages:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history.append(AIMessage(content=msg["content"]))
    return history
