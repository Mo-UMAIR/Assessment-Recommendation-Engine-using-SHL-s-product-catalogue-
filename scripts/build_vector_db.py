import json
import chromadb
from chromadb.utils import embedding_functions

def build_db():
    try:
        with open('data/shl_catalog.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: data/shl_catalog.json not found. Please run scripts/scrape_catalog.py first.")
        return

    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(path="./data/chroma_db")
    
    # Using sentence-transformers for local, free embeddings
    print("Loading embedding model (this may take a moment on first run)...")
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # Create or get collection
    try:
        client.delete_collection(name="shl_assessments")
    except Exception:
        pass
        
    collection = client.create_collection(
        name="shl_assessments",
        embedding_function=sentence_transformer_ef,
        metadata={"hnsw:space": "cosine"}
    )
    
    documents = []
    metadatas = []
    ids = []
    
    print("Preparing documents for embedding...")
    for i, item in enumerate(data):
        name = item.get("name", "")
        url = item.get("url", "")
        test_type = item.get("test_type", "")
        description = item.get("description", "")
        duration = item.get("duration", "")
        
        # Convert "CPAB" string to list of categories
        cats = list(test_type.replace(" ", "")) if test_type and test_type != "Not found" else []
        
        # Categorize into domains for balancing recommendations
        domain = "Unknown"
        if any(c in ['P', 'B', 'C'] for c in cats):
            domain = "Behavioral"
        elif any(c in ['K', 'A', 'S'] for c in cats):
            domain = "Technical"
            
        # Extract duration digit
        duration_int = 0
        import re
        if duration:
            match = re.search(r'\d+', duration)
            if match:
                duration_int = int(match.group())

        # Extract adaptive/remote support as Yes/No
        adaptive_support = item.get("adaptive/irt_support", "")
        remote_support = item.get("remote_testing", "")
        
        adaptive_str = "Yes" if "🟢" in adaptive_support else "No"
        remote_str = "Yes" if "🟢" in remote_support else "No"
        
        # We need categories as list of strings for DB, or comma separated if Chroma prefers strings.
        # But for API we need array of strings. Chroma DB metadata values must be strings, ints, or floats.
        # So we'll store as string and parse it in the API.
        
        # Create a rich text representation for the vector DB
        doc_text = f"Assessment Name: {name}. Description: {description}. Categories: {', '.join(cats)}."
        
        documents.append(doc_text)
        metadatas.append({
            "url": url, 
            "name": name, 
            "domain": domain, 
            "categories": ",".join(cats), # Keep for internal logic
            "description": description,
            "duration": duration_int,
            "adaptive_support": adaptive_str,
            "remote_support": remote_str
        })
        ids.append(str(i))
        
    print(f"Adding {len(documents)} documents to ChromaDB...")
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )
        print(f"Processed {min(i+batch_size, len(documents))} / {len(documents)}")

    print("Vector database built successfully at ./data/chroma_db")

if __name__ == "__main__":
    build_db()
