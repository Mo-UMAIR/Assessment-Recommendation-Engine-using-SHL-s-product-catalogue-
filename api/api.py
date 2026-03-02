from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions

app = FastAPI()

# Global variables for DB
client = None
collection = None

@app.on_event("startup")
def startup_event():
    global client, collection
    try:
        print("Connecting to ChromaDB...")
        client = chromadb.PersistentClient(path="./data/chroma_db")
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        collection = client.get_collection(name="shl_assessments", embedding_function=sentence_transformer_ef)
        print("Connected to SHL collection.")
    except Exception as e:
        print(f"Warning: Could not initialize ChromaDB. Make sure you've built the DB first. Error: {e}")

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/recommend")
def recommend(request: QueryRequest):
    if not collection:
        raise HTTPException(status_code=500, detail="Database not initialized. Please run scripts/build_vector_db.py first.")
        
    query_text = request.query
    
    # Simple logic to determine if we need to balance the recommendations
    # If the query mentions technical and soft skills (like "collaborate", "team", etc.)
    q_lower = query_text.lower()
    needs_technical = any(word in q_lower for word in ["developer", "python", "java", "sql", "engineer", "analyst"])
    needs_behavioral = any(word in q_lower for word in ["collaborate", "team", "behavior", "personality", "leadership"])
    
    is_balanced_needed = needs_technical and needs_behavioral
    
    # We fetch more initially so we can filter down
    fetch_count = 20 if is_balanced_needed else 10
    
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=fetch_count
        )
        
        recommendations = []
        if results and results['metadatas'] and len(results['metadatas'][0]) > 0:
            for i in range(len(results['metadatas'][0])):
                meta = results['metadatas'][0][i]
                
                rec_item = {
                    "Assessment name": meta.get("name"),
                    "URL": meta.get("url"),
                    "Domain": meta.get("domain", "Unknown"),
                    "Categories": meta.get("categories", ""),
                    "adaptive_support": meta.get("adaptive_support", "No"),
                    "description": meta.get("description", "Description unavailable"),
                    "duration": meta.get("duration", 0),
                    "remote_support": meta.get("remote_support", "No")
                }
                
                if rec_item not in recommendations:
                    recommendations.append(rec_item)
        
        final_recs = []
        
        # If balanced is needed, enforce a mix
        if is_balanced_needed:
            tech_assessments = [r for r in recommendations if r['Domain'] == 'Technical']
            behav_assessments = [r for r in recommendations if r['Domain'] == 'Behavioral']
            
            # Take up to 3 technical and 2 behavioral (ideal 5)
            # If we need up to 10, let's say 5 tech, 5 behav
            final_recs.extend(tech_assessments[:5])
            final_recs.extend(behav_assessments[:5])
            
            # If we still have less than 5, fill gaps
            if len(final_recs) < 5:
                for r in recommendations:
                    if r not in final_recs:
                        final_recs.append(r)
                        if len(final_recs) >= 5:
                            break
                            
            # Sort them interwoven a bit or just return as is
        else:
            final_recs = recommendations
            
        # Ensure we return at least 5 and at most 10
        # Check against the boundaries
        if len(final_recs) < 5:
            # Maybe the DB has fewer items or we filtered too much
             for r in recommendations:
                 if r not in final_recs:
                     final_recs.append(r)
                 if len(final_recs) == 5:
                     break
                     
        # Cap at 10
        final_recs = final_recs[:10]
                     
        # Clean output removing 'Domain' and 'Categories' if strict format is required,
        # but the prompt said "at least the following attributes", so we can keep them or remove.
        # Let's cleanly just return what they asked, plus Domain for proof of balance working.
        
        formatted_recs = []
        for r in final_recs:
            # Reconstruct the exact output format
            cat_str = r.get("Categories", "")
            
            # Map the letters to full names if needed, or just return them
            test_types = []
            if 'K' in cat_str: test_types.append("Knowledge & Skills")
            if 'P' in cat_str: test_types.append("Personality & Behavior")
            if 'B' in cat_str: test_types.append("Biodata & Situational Judgement")
            if 'C' in cat_str: test_types.append("Competencies")
            if 'A' in cat_str: test_types.append("Ability & Aptitude")
            if 'S' in cat_str: test_types.append("Simulations")
            if 'E' in cat_str: test_types.append("Assessment Exercises")
            if 'D' in cat_str: test_types.append("Development & 360")
            
            if not test_types:
                test_types.append("Unknown")

            formatted_rec = {
                "url": r.get("URL", ""),
                "name": r.get("Assessment name", ""),
                "adaptive_support": r.get("adaptive_support", "No"),
                "description": r.get("description", "Description unavailable"),
                "duration": r.get("duration", 0),
                "remote_support": r.get("remote_support", "No"),
                "test_type": test_types
            }
            formatted_recs.append(formatted_rec)
            
        return {"recommended_assessments": formatted_recs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
