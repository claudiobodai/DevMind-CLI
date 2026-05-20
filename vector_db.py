import chromadb
from test_ollama import generate_embedding

chroma_client = chromadb.PersistentClient(path="./local_db")
collection = chroma_client.get_or_create_collection(name="devmind_codebase")


def reset_database():
    """Delete all indexed data by recreating the target collection."""
    global collection
    try:
        chroma_client.delete_collection(name="devmind_codebase")
    except Exception:
        # Collection may not exist yet; this is safe to ignore.
        pass

    collection = chroma_client.get_or_create_collection(name="devmind_codebase")

def add_document(doc_id, text, metadata=None):
    """
    Use Ollama to generate embeddings for the given text and add it to the ChromaDB collection.
    """
    print(f"Adding document with ID: {doc_id}")
    vector = generate_embedding(text)

    if vector:
        metadatas = [metadata] if metadata else None
        collection.upsert(
            ids=[doc_id],
            embeddings=[vector],
            documents=[text],
            metadatas=metadatas
        )
        print(f"Document '{doc_id}' saved.")

def search_similar(query_text, n_results=1):
    """
    Convert the query text and search mathematically similar documents in the ChromaDB collection.
    """
    print(f"Searching for documents similar to: '{query_text}'")
    query_vector =  generate_embedding(query_text)

    if query_vector:
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        return results
    return None

if __name__ == "__main__":
    print("--- Adding sample documents to the vector database ---")
    # CODING & PROGRAMMING DOCUMENTS (similar to each other)
    add_document("doc1", "Install dependencies with 'npm install' to set up the Node.js project environment.")
    add_document("doc2", "Run 'npm start' to launch the development server and start coding in React.")
    add_document("doc3", "Use 'git commit -m' to save your code changes with descriptive messages to the repository.")
    add_document("doc4", "Python functions are defined with the 'def' keyword and can accept parameters and return values.")
    add_document("doc5", "JavaScript async/await syntax allows you to write asynchronous code that looks synchronous and is easier to read.")
    
    # ANIMALS DOCUMENTS (similar to each other)
    add_document("doc6", "Lions are powerful predators that live in African savannas and hunt in coordinated packs called prides.")
    add_document("doc7", "Dolphins are highly intelligent marine mammals known for their playful behavior and complex communication skills.")
    add_document("doc8", "Eagles are birds of prey with exceptional eyesight that can spot fish from miles away while soaring in the sky.")
    add_document("doc9", "Penguins are flightless birds that live in Antarctica and are excellent swimmers adapted to cold ocean waters.")
    add_document("doc10", "Wolves are social animals that live in packs and use howling as a form of communication with their family members.")
    
    # EMOTIONS & SENTIMENTS DOCUMENTS (similar to each other)
    add_document("doc11", "Happiness fills your heart with warmth and makes you smile, creating beautiful memories with loved ones.")
    add_document("doc12", "Sadness can overwhelm you with deep emotions, but it teaches resilience and helps you appreciate joyful moments.")
    add_document("doc13", "Fear is a natural response that protects us from danger and keeps us alert in threatening situations.")
    add_document("doc14", "Love is a powerful emotion that connects people together and motivates us to care for others unconditionally.")
    add_document("doc15", "Anger arises when we feel wronged and can fuel determination, but it must be channeled constructively for positive change.")

    # EXTRA CODING CONTEXTS
    add_document("doc16", "To start the frontend in Vite projects, run 'npm run dev' and open the local URL shown in terminal.")
    add_document("doc17", "In Express applications, middleware order matters because each function processes the request in sequence.")
    add_document("doc18", "A REST API endpoint should return clear HTTP status codes such as 200, 201, 400, and 401.")
    add_document("doc19", "Environment variables are loaded from a .env file and should never include private secrets in Git commits.")
    add_document("doc20", "For Python virtual environments, use 'python -m venv venv' and activate it before installing packages.")

    # EXTRA ANIMAL CONTEXTS
    add_document("doc21", "Owls are nocturnal birds with exceptional hearing that helps them detect prey in complete darkness.")
    add_document("doc22", "Cheetahs are the fastest land animals and can accelerate quickly during short hunting sprints.")
    add_document("doc23", "Octopuses are intelligent sea creatures that can solve puzzles and change color for camouflage.")
    add_document("doc24", "Bees communicate food locations through a waggle dance that indicates distance and direction.")
    add_document("doc25", "Turtles can live for decades, and many sea turtles migrate thousands of kilometers across oceans.")

    # EXTRA SENTIMENT CONTEXTS
    add_document("doc26", "Joy often appears as an expansive feeling, bringing energy, curiosity, and openness toward others.")
    add_document("doc27", "Loneliness can persist even in crowds when a person feels unseen or emotionally disconnected.")
    add_document("doc28", "Hope is the emotion that keeps people moving forward when outcomes are uncertain.")
    add_document("doc29", "Jealousy can reveal unmet needs, but it becomes destructive when mixed with control and insecurity.")
    add_document("doc30", "Calmness is not the absence of problems but the ability to stay centered while facing them.")


    print("\n--- Searching for similar documents ---")
    question= "How do I start the frontend development server?"

    results = search_similar(question)

    if results and results['documents']:
        print("\n Results found:")
        print(results["documents"][0][0])