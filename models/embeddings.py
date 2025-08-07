from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from utils.document_loader import load_document
from config.config import GOOGLE_API_KEY

def create_vectorstore(file):
    text = load_document(file)

    if not text.strip():
        return "❌ Document is empty or unreadable."

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_text(text)

    if not chunks:
        return "❌ No chunks could be created from the document."

    embeddings = GoogleGenerativeAIEmbeddings(google_api_key=GOOGLE_API_KEY)

    try:
        return FAISS.from_texts(chunks, embedding=embeddings)
    except Exception as e:
        return f"❌ Failed to build vectorstore: {e}"
