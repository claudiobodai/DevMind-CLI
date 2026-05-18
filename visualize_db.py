import chromadb
from sklearn.decomposition import PCA
import plotly.express as px
import pandas as pd
import os
import webbrowser

def create_3d_map():
    print("Connecting to local ChromaDB...")
    chroma_client = chromadb.PersistentClient(path="./local_db")
    collection = chroma_client.get_collection(name="devmind_codebase")
        
    # Extract embeddings and texts
    data = collection.get(include=["embeddings", "documents", "metadatas"])
    embeddings = data["embeddings"]
    documents = data["documents"]
    
    # FIX: Changed 'not embeddings' to 'embeddings is None' to avoid NumPy ambiguity errors
    if embeddings is None or len(embeddings) < 3:
        print("Error: You need at least 3 documents in the DB to create a 3D plot!")
        return

    print(f"Calculating: compressing {len(embeddings)} vectors from 2048 to 3 dimensions (PCA)...")
    
    # Initialize PCA to reduce to 3 dimensions (X, Y, Z)
    pca = PCA(n_components=3)
    vectors_3d = pca.fit_transform(embeddings)
    
    # Prepare data for the chart
    # Truncate text to 60 characters for cleaner chart labels
    short_texts = [doc[:60] + "..." if len(doc) > 60 else doc for doc in documents]
    
    df = pd.DataFrame({
        'X': vectors_3d[:, 0],
        'Y': vectors_3d[:, 1],
        'Z': vectors_3d[:, 2],
        'Text': short_texts
    })
    
    print("Generating interactive 3D interface...")
    # Create 3D scatter plot with Plotly
    fig = px.scatter_3d(
        df, x='X', y='Y', z='Z', 
        hover_name='Text',
        title="Vector Space Map (Local Codebase)",
        template="plotly_dark" # Dark theme, much better for devs!
    )
    
    # Enlarge the points to see them better
    fig.update_traces(marker=dict(size=8, opacity=0.8))
    
    # Save to a local HTML file
    file_name = "semantic_map.html"
    fig.write_html(file_name)

    abs_path = os.path.abspath(file_name)
    file_url = f"file:///{abs_path.replace(chr(92), '/')}"



    print(f"Map generated successfully!")
    print(f"🔗 Local Link: {file_url}")
    print("🌐 Opening the map in your default web browser...")

    try:
        webbrowser.open(file_url)
    except Exception as e:
        print(f"Could not open the browser automatically: {e}")

if __name__ == "__main__":
    create_3d_map()