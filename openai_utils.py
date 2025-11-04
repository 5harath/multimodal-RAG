import openai
import base64
import os
from config import OPENAI_API_KEY, MODEL_NAME, INFERENCE_MODEL_NAME, EMBEDDING_MODEL, MODEL_MAX_TOKENS

openai.api_key = OPENAI_API_KEY

def generate_embedding(text):
    """Generates a vector embedding for a given text string."""
    response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response['data'][0]['embedding']

def refine_response(prompt):
    """Generates a final, grounded response using the RAG prompt."""
    try:
        completion = openai.ChatCompletion.create(
            model=INFERENCE_MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=MODEL_MAX_TOKENS
        )
        return completion.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error refining response: {e}")
        return "I am sorry, I couldn't generate a response."

def create_image_json(image_path):
    """Generates a structured text description (JSON format) from an image using GPT-4o Vision."""
    try:
        # 1. Encode image to Base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # 2. Construct the prompt payload
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe the content of this image, including any text, objects, and their locations, in a detailed JSON format."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
        
        # 3. Call GPT-4o (Vision model)
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=2000 # Increased tokens for detailed description
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error creating image JSON: {e}")
        return None