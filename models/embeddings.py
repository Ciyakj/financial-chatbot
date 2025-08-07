from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.document_loader import load_document
import os

def create_vectorstore(file):
    text = load_document(file)
    print("TEXT EXTRACTED:", text[:1000])

    if not text.strip():
        return "❌ Document is empty or unreadable."

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_text(text)

    if not chunks:
        return "❌ No chunks could be created from the document."

    # Auto-switch: Use OpenAI on Streamlit Cloud, HuggingFace locally
    is_streamlit_cloud = os.getenv("STREMLIT_ENV") == "cloud" or os.getenv("OPENAI_API_KEY") is not None

    try:
        if is_streamlit_cloud:
            from langchain_openai import OpenAIEmbeddings
            from config.config import OPENAI_API_KEY
            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        else:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        return FAISS.from_texts(chunks, embedding=embeddings)
    
    except Exception as e:
        return f"❌ Failed to build vectorstore: {e}"
