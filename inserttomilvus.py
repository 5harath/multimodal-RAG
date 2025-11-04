import os
import re
import fitz # PyMuPDF
import json
from milvus_utils import fetch_text_by_id # Not strictly needed here but imported
from openai_utils import generate_embedding, create_image_json
from config import OUTPUT_FOLDER, PDF_IMAGES_FOLDER, INPUT_FOLDER, COLLECTION_NAME, MILVUS_HEADERS, MILVUS_URI

# Define insertion URL for Milvus
INSERT_URL = f"https://{MILVUS_URI}/v2/vectordb/entities"

def extract_text_and_images(pdf_path):
    """Extracts text and saves images from a PDF."""
    text_content = ""
    pdf_file_name = os.path.basename(pdf_path)
    
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content += page.get_text() + "\n"
            
            # Image extraction logic
            for img_index, img in enumerate(doc.get_page_images(page_num)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Save image to disk
                image_filename = f"{pdf_file_name}_page{page_num+1}_img{img_index}.{image_ext}"
                image_path = os.path.join(PDF_IMAGES_FOLDER, image_filename)
                with open(image_path, "wb") as img_out:
                    img_out.write(image_bytes)
                    
        return text_content
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return ""

def embed_text(text, pdf_path):
    """Generates embedding and inserts data into Milvus."""
    vector = generate_embedding(text)
    
    payload = {
        "collectionName": COLLECTION_NAME,
        "data": [
            {
                "vector": vector,
                "text": text,
                "path": pdf_path
            }
        ]
    }
    
    try:
        response = requests.post(
            INSERT_URL,
            headers=MILVUS_HEADERS,
            data=json.dumps(payload),
            verify=False
        )
        response.raise_for_status()
        print(f"Successfully inserted text from {pdf_path}. Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error during Milvus insertion for {pdf_path}: {e}")

def process_documents():
    # 1. Ensure folders exist
    os.makedirs(PDF_IMAGES_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # 2. Process PDFs (extract text and images)
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(INPUT_FOLDER, filename)
            # Text extraction also extracts and saves images
            extracted_text = extract_text_and_images(pdf_path)
            
            # Save raw text to disk (optional, but good for debugging/checking)
            text_output_path = os.path.join(OUTPUT_FOLDER, filename.replace('.pdf', '_raw.txt'))
            with open(text_output_path, 'w', encoding='utf-8') as f:
                f.write(extracted_text)

    # 3. Process Images (generate captions via GPT-4o)
    for filename in os.listdir(PDF_IMAGES_FOLDER):
        image_path = os.path.join(PDF_IMAGES_FOLDER, filename)
        
        # Use GPT-4o to generate structured description
        json_description = create_image_json(image_path)
        
        if json_description:
            # Save the LLM's text description
            output_filename = filename.rsplit('.', 1)[0] + '_desc.txt'
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_description)

    # 4. Process all text files (raw and image descriptions) for embedding
    for filename in os.listdir(OUTPUT_FOLDER):
        if filename.endswith(".txt"):
            text_file_path = os.path.join(OUTPUT_FOLDER, filename)
            pdf_path = filename # Using the filename as a simple 'path' metadata
            
            with open(text_file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Sentence splitting for fine-grained chunks
            # Split by '.', '!', or '?' while keeping the delimiter
            sentences = re.split(r'(\.|\!|\?)', text_content)
            
            # Recombine the split parts (sentence + delimiter)
            docs = [''.join(i) for i in zip(sentences[0::2], sentences[1::2])]
            if len(sentences) % 2 != 0:
                docs.append(sentences[-1])

            for doc in docs:
                currentdoc = doc.strip()
                if currentdoc:
                    # Embed and insert into Milvus
                    embed_text(currentdoc, pdf_path)

if __name__ == '__main__':
    process_documents()