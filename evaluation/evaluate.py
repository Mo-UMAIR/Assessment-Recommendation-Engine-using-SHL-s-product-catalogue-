import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000/recommend"

def evaluate_mean_recall_at_10(train_csv_path):
    # Assuming the train set has 'query' and 'relevant_assessments' (list or comma separated)
    try:
        df = pd.read_csv(train_csv_path)
    except Exception as e:
        print(f"Could not read train csv: {e}")
        return
        
    total_recall = 0.0
    valid_queries = 0
    
    for idx, row in df.iterrows():
        query = row['query']
        # Depending on format of ground truth, we parse it
        # Let's assume it's a comma separated string of assessment names
        ground_truth = str(row.get('relevant_assessments', '')).lower().split(',')
        ground_truth = [g.strip() for g in ground_truth if g.strip()]
        
        if not ground_truth:
            continue
            
        try:
             resp = requests.post(API_URL, json={"query": query})
             if resp.status_code == 200:
                 recs = resp.json().get('recommended_assessments', [])
                 rec_names = [r.get('name', '').lower() for r in recs[:10]]
                 
                 # Calculate recall
                 hits = sum(1 for gt in ground_truth if any(gt in rn or rn in gt for rn in rec_names))
                 recall = hits / len(ground_truth)
                 total_recall += recall
                 valid_queries += 1
                 print(f"Query {idx}: Recall = {recall:.2f}")
        except Exception as e:
             print(f"Error querying backend: {e}")
             
    if valid_queries > 0:
        mean_recall = total_recall / valid_queries
        print(f"Mean Recall@10: {mean_recall:.4f}")
    else:
        print("No valid queries found for evaluation.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        evaluate_mean_recall_at_10(sys.argv[1])
    else:
        print("Usage: python evaluate.py path/to/train_data.csv")
        print("Note: The backend API must be running.")
