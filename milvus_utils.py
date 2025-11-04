import requests
import json
from config import MILVUS_URI, MILVUS_API_KEY, COLLECTION_NAME, context
from openai_utils import generate_embedding

MILVUS_HEADERS = {
    "Authorization": f"Bearer {MILVUS_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}
SEARCH_URL = f"https://{MILVUS_URI}/v2/vectordb/entities/search"
QUERY_URL = f"https://{MILVUS_URI}/v2/vectordb/entities/query"

def search_similar_text(query_text, top_n=6):
    """Searches Milvus for similar text chunks."""
    query_vector = generate_embedding(query_text)
    
    payload = {
        "collectionName": COLLECTION_NAME,
        "vector": query_vector,
        "limit": top_n,
        "outputFields": ["id", "text", "path"],
        "params": {
            "metric_type": "COSINE"
        }
    }

    try:
        response = requests.post(
            SEARCH_URL,
            headers=MILVUS_HEADERS,
            data=json.dumps(payload),
            verify=False # Using context.verify_mode=ssl.CERT_NONE as per config
        )
        response.raise_for_status()
        return response.json().get('data', {}).get('search_results', [])
    except requests.exceptions.RequestException as e:
        print(f"Error during Milvus search: {e}")
        return []

def fetch_text_by_id(entity_id):
    """Retrieves the full text field for a given entity ID."""
    payload = {
        "collectionName": COLLECTION_NAME,
        "outputFields": ["text"],
        "filter": f"id in [{entity_id}]"
    }
    
    try:
        response = requests.post(
            QUERY_URL,
            headers=MILVUS_HEADERS,
            data=json.dumps(payload),
            verify=False
        )
        response.raise_for_status()
        
        results = response.json().get('data', {}).get('entities', [])
        return results[0]['text'] if results else ""
    except requests.exceptions.RequestException as e:
        print(f"Error fetching text by ID: {e}")
        return ""

def process_results(results):
    """Processes Milvus search results into a clean list of dictionaries."""
    processed_data = []
    for result in results:
        entity_id = result.get('id')
        distance = result.get('distance')
        
        # Fetch the full text content
        raw_text = fetch_text_by_id(entity_id)
        
        # Clean up the text
        cleaned_text = raw_text.replace('\n', ' ')
        
        processed_data.append({
            "id": entity_id,
            "distance": distance,
            "text": cleaned_text
        })
    return processed_data