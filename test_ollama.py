import requests
import json

def ask_ollama(prompt_text, model="llama3.2:1b"):
    """
    Sends a POST request to the local Ollama API.
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt_text,
        "stream": False,
        "options": {
            "temperature": 0.0
        }
    }
        
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json() 
            return data["response"]
        else:
            return f"API Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "Connection error. Is Ollama running in the background?"

def generate_embedding(text, model="nomic-embed-text"):
    """
    Converts text into a mathematical vector (embedding) 
    """
    url = "http://localhost:11434/api/embeddings"
    
    payload = {
        "model": model,
        "prompt": text
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json() 
            return data["embedding"]
        else:
            return f"API Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "Connection error. Is Ollama running in the background?"

# Execute this block only if the script is run directly
if __name__ == "__main__":
    
    question = "Explain what a REST API is in one sentence."
    print(f"Q: {question}")
    result = ask_ollama(question)
    print(f"A: {result}")

    print("testing embedding generation...")
    sample_text = "I love cats and dogs."
    sample_text2 = "The cat is on the roof."

    print(f"Generating embedding for: '{sample_text}'")
    vector = generate_embedding(sample_text)
    vector2 = generate_embedding(sample_text2)
    if vector: 
        print(f"Text was converted to a vector of length {len(vector)}")
        print(f"First 5 values of the embedding: {vector[:5]}")

    if vector2:
        print(f"Text was converted to a vector of length {len(vector2)}")
        print(f"First 5 values of the embedding: {vector2[:5]}")
