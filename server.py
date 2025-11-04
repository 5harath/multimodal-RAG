from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from milvus_utils import search_similar_text, process_results
from openai_utils import refine_response

# Basic Flask setup
app = Flask(__name__)
CORS(app) # Enables Cross-Origin Resource Sharing
logging.basicConfig(level=logging.INFO)

@app.route('/generate', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({"error": "No query provided"}), 400

        # --- RAG Pipeline ---
        
        # 1. Retrieval (Search Milvus)
        results = search_similar_text(query, top_n=6)
        
        # 2. Process results to get clean text
        processed_data = process_results(results)
        
        # 3. Augmentation (Construct the prompt)
        context = ""
        for item in processed_data:
            context += item['text'] + "\n"
            
        # Strict instruction to ground the model
        prompt = "Answer based on the following text only : \n"
        prompt += context
        prompt += "\n now : " + query

        # 4. Generation (Refine with GPT-4o-mini)
        refined_response = refine_response(prompt)
        
        # Log response for debugging
        logging.info(f"Query: {query}, Response: {refined_response[:50]}...")
        
        return jsonify({"response": refined_response})

    except Exception as e:
        logging.error(f"An error occurred during RAG pipeline: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    # Flask runs on 127.0.0.1:8080 as expected by the frontend
    app.run(host='127.0.0.1', port=8080, debug=True)