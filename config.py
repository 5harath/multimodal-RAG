import os
import ssl

# --- OpenAI API Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-...")
MODEL_NAME = "gpt-4o"
INFERENCE_MODEL_NAME = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-ada-002"
MODEL_MAX_TOKENS = 200

# --- Milvus API Configuration (Zilliz Cloud) ---
MILVUS_API_KEY = os.getenv("MILVUS_API_KEY", "s-...")
MILVUS_URI = "gcp-us-west1.cloud.zilliz.com"
COLLECTION_NAME = "openai_pdfs_images_check_copy"

# --- Folder Paths ---
OUTPUT_FOLDER = "pdf-image-to-text"
PDF_IMAGES_FOLDER = "pdf-images"
INPUT_FOLDER = "input"

# --- SSL Context for Milvus Connection ---
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE