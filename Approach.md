# Approach Document for SHL Assessment Recommendation System

## 1. Problem Understanding & Solution Strategy
The objective was to build an intelligent recommendation system that takes a natural language query or job description (JD) and returns 5 to 10 relevant "individual test solutions" from the SHL catalog. The system must ignore "Pre-packaged Job Solutions" and be capable of balancing recommendations across domains (e.g., mixing behavioral and technical assessments when a query implies both).

**Strategy:** A Retrieval-Augmented Generation (RAG) inspired architecture using a Vector Database was chosen over simple keyword matching. 
- **Data Ingestion:** A robust web scraper to extract high-quality metadata from the live catalog.
- **Embedding & Storage:** Converting textual metadata into dense semantic vectors using a local embedding model, stored in ChromaDB for fast similarity search.
- **Retrieval & Recommendation:** A FastAPI backend that embeds the incoming query, searches the database, balances the results by categorizing test types, and returns the strictly formatted JSON.

## 2. Architecture & Components

### 2.1 Data Pipeline (Scraping)
The data ingestion pipeline relies on `BeautifulSoup` and `requests`. 
- Over 300+ pages of SHL assessments were traversed.
- Dynamic web structures (such as visually representing features using green dots/emojis, or using varied header tags for descriptions) were addressed using robust fallback logic.
- Crucially, features like `Duration`, `Adaptive/IRT Support`, `Remote Testing`, and `Test Types` (CPAB) were successfully extracted and cleaned into strictly typed formats (Integers, Booleans/Yes-No, Arrays).

### 2.2 Vector Database
`ChromaDB` was selected as the vector store.
- **Model:** The `all-MiniLM-L6-v2` SentenceTransformer model was used to generate embeddings. It is lightweight, fast, and excellent at encoding semantic meaning locally without excessive API costs.
- **Rich Text Representation:** The text embedded for each item is a concatenation of the assessment name, description, and categories. This ensures the vector captures both the granular technical terms (e.g., "Python", "SQL") and the broader behavioral context (e.g., "Personality", "Leadership").

### 2.3 Backend API
A scalable `FastAPI` application serves the final predictions.
- **Semantic Search:** Incoming queries are embedded in real-time and queried against ChromaDB.
- **Balancing Logic:** The API features an integrated balancing algorithm. It intelligently parses the query for "technical" vs. "behavioral" intent. If both are detected, it enforces a balanced mix of "Hard Skills/Knowledge" vs "Competencies/Behavioral" assessments in the top 5-10 responses, fulfilling the complex criteria.
- **Strict Compliance:** Adheres strictly to the given specification endpoints (`GET /health` and `POST /recommend`) and JSON output schemas.

## 3. Evaluation & Optimization Efforts

### 3.1 Evaluating Accuracy (Mean Recall@10)
A custom evaluation script allows testing the pipeline against the provided training data. The main metric is `Mean Recall@10`, which measures how many relevant assessments appeared in the top 10 recommended slots. 

### 3.2 Iteration & Improvements
- **Initial Result:** An early prototype relying solely on Assessment Titles yielded poor recall because titles often lack context (e.g., "Professional 8.0"). 
- **Optimization 1 (Context expansion):** Including the full description and test categories in the embedded text significantly improved query-document similarity scores. 
- **Optimization 2 (Category Rules):** We noticed semantic search occasionally returned only highly technical tests even for well-rounded job descriptions. The "balancing logic" was introduced explicitly to detect multi-domain queries and force diversity into the results.

## 4. Conclusion
The resulting system is modular, easily reproducible, and highly performant. By combining robust data wrangling with modern embedding-based retrieval and custom balancing heuristics, the API successfully captures the semantic intent of complex job descriptions to deliver accurate, balanced SHL assessment recommendations.
