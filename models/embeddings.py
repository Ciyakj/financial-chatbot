
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils.document_loader import load_document

def create_vectorstore(file):
    text = load_document(file)
    print("TEXT EXTRACTED:", text[:1000])

    if not text.strip():
        return "❌ Document is empty or unreadable."

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_text(text)

    if not chunks:
        return "❌ No chunks could be created from the document."

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    try:
        return FAISS.from_texts(chunks, embedding=embeddings)
    except Exception as e:
        return f"❌ Failed to build vectorstore: {e}"
