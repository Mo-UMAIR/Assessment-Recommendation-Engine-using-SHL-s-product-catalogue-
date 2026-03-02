# SHL Assessment Recommendation System

This repository contains the SHL Assessment Recommendation System, comprised of a multi-stage pipeline: a data scraper, a vector database processor, a FastAPI backend, and a Streamlit frontend. It uses AI embeddings (`sentence-transformers`) to semantically match job descriptions to the SHL Assessment Catalog, automatically balancing technical and behavioral assessments.

## Folder Structure

The project has been refactored into a clean, well-structured format:

```
.
├── api/
│   └── api.py                  # FastAPI Backend serving recommendations
├── data/
│   ├── shl_catalog.json        # The scraped JSON catalog of SHL assessments
│   └── chroma_db/              # The local Chroma Vector Database
├── evaluation/
│   ├── evaluate.py             # Script calculating MRR and Hit Rate
│   └── generate_predictions.py # Script generating the final CSV output
├── frontend/
│   └── app.py                  # Streamlit User Interface
├── scripts/
│   ├── scrape_catalog.py       # Data crawler
│   └── build_vector_db.py      # Script to embed catalog and create ChromaDB
├── requirements.txt            # Python dependencies
├── Approach.md                 # 2-page methodology and evaluation document
└── README.md                   # Project documentation
```

## Running the Project Locally

**1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**2. Scrape and Build Database**
If the database doesn't exist yet, run the pipeline:
```bash
python scripts/build_vector_db.py
```

**3. Start the Backend API**
Run the FastAPI server from the root directory so it can access the `data` folder correctly:
```bash
uvicorn api.api:app --reload --host 0.0.0.0 --port 8000
```
*The API should now be running at `http://127.0.0.1:8000`.*

**4. Start the Frontend UI**
In a separate terminal, launch the Streamlit frontend:
```bash
streamlit run frontend/app.py
```

---

## API Endpoints

The FastAPI backend exposes the following endpoints (available at `http://localhost:8000/docs`):

### `GET /health` - Health Check
Verifies if the API is active.
**Response:**
```json
{
  "status": "healthy"
}
```

### `POST /recommend` - Recommendation Engine
Returns a balanced list of top 5-10 SHL assessments based on a job description or text querying.
**Request Body:**
```json
{
  "query": "Looking for a candidate skilled in Java, SQL, and effective team collaboration."
}
```
**Response:**
```json
{
  "recommended_assessments": [
    {
      "url": "https://www.shl.com/...",
      "name": "Java 11 Developer",
      "adaptive_support": "No",
      "description": "Multi-choice test...",
      "duration": 30,
      "remote_support": "Yes",
      "test_type": [
        "Knowledge & Skills"
      ]
    }
  ]
}
```

---

## Deployment Instructions

### 1. Deploying on GitHub
To push your codebase to GitHub:

```bash
git init
git add .
git commit -m "Initial commit for SHL Recommendation System"
git branch -M main
git remote add origin https://github.com/your-username/your-repo-name.git
git push -u origin main
```
*Note: Exclude `venv/` and optionally `data/chroma_db` (if too large) by creating a `.gitignore` file.*

### 2. Deploying on Render (Free Tier)

Render makes deployments extremely simple for both Backend APIs and Streamlit Apps.

**Deploying the FastAPI Backend:**
1. Log into your Render Dashboard.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. **Environment:** `Python 3`
5. **Build Command:** `pip install -r requirements.txt`
6. **Start Command:** `uvicorn api.api:app --host 0.0.0.0 --port 10000`
7. Click **Deploy**. Render will grant you a public URL (e.g., `https://your-api.render.com`).

**Deploying the Streamlit Frontend:**
*Important: You must update `frontend/app.py` line 4 (`API_URL`) to point to your new Render Backend URL before deploying the app.*
1. In Render, click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. **Environment:** `Python 3`
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `streamlit run frontend/app.py --server.port 10000 --server.address 0.0.0.0`
6. Click **Deploy**.

### 3. Deploying on AWS (EC2 / ECS)

For an enterprise deployment, AWS EC2 or App Runner provides more control.

**AWS EC2 (Virtual Machine) Deployment:**
1. Launch an **Ubuntu Server** EC2 instance.
2. Configure **Security Groups** to allow inbound traffic on `HTTP (80)` and Custom TCP on ports `8000` (API) and `8501` (Streamlit).
3. Connect to the EC2 via SSH and configure the environment:
```bash
sudo apt update
sudo apt install python3-pip python3-venv git
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
4. Start the backend using `tmux`, `nohup`, or a `systemd` service:
```bash
nohup uvicorn api.api:app --host 0.0.0.0 --port 8000 &
```
5. Start the frontend:
```bash
nohup streamlit run frontend/app.py --server.port 8501 &
```
*Note: Make sure to edit the `API_URL` variable in `frontend/app.py` to point to the Public IPv4 Address of your EC2 instance (e.g. `http://X.X.X.X:8000`).*
