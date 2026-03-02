import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000/recommend"

def generate_predictions(test_csv_path, output_csv_path="predictions.csv"):
    try:
        df = pd.read_csv(test_csv_path)
    except Exception as e:
        print(f"Could not read test csv: {e}")
        return
        
    predictions_list = []
    
    for idx, row in df.iterrows():
        # Assuming test set has a 'query' column
        query = row.get('query', '')
        if not query:
            # Maybe the column name is different
            query = str(row.values[0]) if len(row.values) > 0 else ""
            
        if not query:
            continue
            
        print(f"Processing query: {query[:50]}...")    
        try:
             resp = requests.post(API_URL, json={"query": query})
             if resp.status_code == 200:
                 recs = resp.json().get('recommended_assessments', [])
                 if not recs:
                      predictions_list.append({"Query": query, "Assessment_url": "No recommendations found"})
                 for rec in recs:
                      predictions_list.append({
                          "Query": query,
                          "Assessment_url": rec.get("url", "")
                      })
             else:
                 predictions_list.append({"Query": query, "Assessment_url": "Error: API returned " + str(resp.status_code)})
        except Exception as e:
             print(f"Error querying backend: {e}")
             predictions_list.append({"Query": query, "Assessment_url": "Error: Could not connect to API"})
             
    out_df = pd.DataFrame(predictions_list)
    out_df.to_csv(output_csv_path, index=False)
    print(f"Saved predictions to {output_csv_path} in proper format.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        generate_predictions(sys.argv[1])
    else:
        print("Usage: python generate_predictions.py path/to/unlabeled_test_data.csv")
        print("Note: The backend API must be running.")
