import chromadb
from test_ollama import ask_ollama, generate_embedding  

chroma_client = chromadb.PersistentClient(path="./local_db")
collection = chroma_client.get_collection(name="devmind_codebase")


def get_relevant_context(question, n_result=1):
    """
    Retrieves the most relevant context from the ChromaDB collection based on the question.
    """
    print(f"Searching local database...")

    question_vector = generate_embedding(question)

    if question_vector:
        results = collection.query(
            query_embeddings=[question_vector],
            n_results=n_result,
            include=["documents", "metadatas", "distances"]
        )
        if results and "documents" in results and len(results["documents"][0]) > 0:
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            context_items = []
            for idx, doc in enumerate(docs):
                meta = metas[idx] if idx < len(metas) and metas[idx] else {}
                source = meta.get("source", "unknown") if isinstance(meta, dict) else "unknown"
                distance = distances[idx] if idx < len(distances) else None
                context_items.append(
                    {
                        "source": source,
                        "distance": distance,
                        "snippet": doc[:1200],
                    }
                )

            return context_items

    return None

def generate_hypothetical_code(question):
    """
    HyDE: asks the LLM to write a fake code snippet that would answer the question.
    Searching "code vs code" in ChromaDB is far more precise than "sentence vs code".
    """
    hyde_prompt = f"""You are a code generation assistant.
A developer asked: "{question}"

Write a SHORT, realistic code snippet (5-15 lines) that directly implements or answers this question.
Output ONLY raw code. No explanations, no markdown fences, no comments.

CODE:"""

    print("  [HyDE] Generating hypothetical code for semantic search...")
    hypothetical_code = ask_ollama(hyde_prompt)
    return hypothetical_code.strip()


def ask_codebase(question):
    """
    The heart of RAG: combines context found in the DB with power of Ollama.
    Uses HyDE to bridge the semantic gap between natural language and source code.
    """
    hypothetical_code = generate_hypothetical_code(question)
    context_data = get_relevant_context(hypothetical_code, n_result=4)

    if not context_data:
        return "Did not find relevant information in local files to answer this question."

    source_list = ", ".join(item["source"] for item in context_data)
    print(f"Found context from sources: {source_list}")
    print(f"Generating response ...")

    context_blocks = []
    for i, item in enumerate(context_data, start=1):
        context_blocks.append(
            f"[CHUNK {i}]\nSOURCE: {item['source']}\nTEXT:\n{item['snippet']}"
        )

    merged_context = "\n\n---\n\n".join(context_blocks)

    rag_prompt = f"""You are a helpful assistant. Analyze the provided TEXT to answer the QUESTION.

    TEXT:
    {merged_context}

    QUESTION: {question}

    INSTRUCTIONS:
    1. Provide a direct, readable answer in the EXACT SAME LANGUAGE as the QUESTION.
    2. If a portion of the TEXT is unrelated to the QUESTION, completely IGNORE IT. Do not summarize irrelevant information.
    3. If the question is a partial query, extract only the facts related to those specific keywords.
    4. Only if the ENTIRE TEXT is completely unrelated to the QUESTION, output exactly: "I don't have enough information."

    ANSWER:"""
     
    answer = ask_ollama(rag_prompt)

    clean_answer = answer.strip()
    
    # Riaggiungiamo il trattino se l'LLM se l'è perso
    if clean_answer and not clean_answer.startswith("I don't") and not clean_answer.startswith("-"):
        clean_answer = "- " + clean_answer

    # Guardrail di sicurezza ancorato all'inglese (come da istruzione n.3)
    if "I don't have enough information" in clean_answer:
         return " Did not find relevant information in the project files."

    return f"{clean_answer}\n\n Sources: {source_list}"

if __name__ == "__main__":
    print("=== DEVMIND CLI: RAG TEST ===")

    user_question = "How owls hunt at night?"

    print(f"\n User: {user_question}")
    answer = ask_codebase(user_question)
    print(f"\n DevMind: {answer}")