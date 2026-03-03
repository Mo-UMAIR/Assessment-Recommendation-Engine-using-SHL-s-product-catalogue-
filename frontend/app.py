import streamlit as st
import requests

API_URL = "http://13.233.25.185:8000"

st.set_page_config(page_title="SHL Assessment Recommendations", page_icon="📝")

st.title("SHL Assessment Recommendation Engine")
st.markdown("Search for relevant SHL assessments based on a job description or query.")

query = st.text_area("Enter your Job Description or Query:", height=150, 
                     placeholder="e.g. Need a Java developer who is good in collaborating with external teams and stakeholders.")

if st.button("Get Recommendations"):
    if not query.strip():
        st.warning("Please enter a query or job description.")
    else:
        with st.spinner("Finding recommendations..."):
            try:
                # Health check first
                hp = requests.get(f"{API_URL}/health")
                hp.raise_for_status()
                
                resp = requests.post(f"{API_URL}/recommend", json={"query": query})
                resp.raise_for_status()
                
                data = resp.json()
                recommendations = data.get("recommended_assessments", [])
                
                if recommendations:
                    st.success(f"Found {len(recommendations)} recommendations!")
                    for i, rec in enumerate(recommendations, 1):
                        st.markdown(f"**{i}. [{rec.get('name', 'Unknown')}]({rec.get('url', '#')})**")
                        
                        duration = rec.get('duration', 0)
                        categories = ", ".join(rec.get('test_type', []))
                        
                        st.caption(f"⏱️ Duration: {duration} mins | 🟢 Remote: {rec.get('remote_support', 'No')} | Categories: {categories}")
                        st.markdown(f"_{rec.get('description', '')}_")
                else:
                    st.info("No recommendations found.")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the backend API. Please make sure `uvicorn api:app --reload` is running.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

st.sidebar.title("About")
st.sidebar.info("This system uses local embeddings and ChromaDB to vector-search through the SHL Product Catalog.")
st.sidebar.text("Developed for SHL GenAI Task.")

## API_URL = "http://127.0.0.1:8000"