from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import *

def get_chat_model(provider="openai", temperature=0.5):
    if not isinstance(provider, str):
        raise ValueError(f"❌ Provider must be a string, got: {type(provider)}")

    provider = provider.lower()

    if provider == "openai":
        return ChatOpenAI(api_key=OPENAI_API_KEY, temperature=temperature)
    
    elif provider == "groq":
        # ✅ Use the lighter and stable Groq model
        return ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192", temperature=temperature)
    
    elif provider == "google":
        return ChatGoogleGenerativeAI(google_api_key=GOOGLE_API_KEY, model="gemini-pro", temperature=temperature)
    
    else:
        raise ValueError(f"❌ Unknown provider: {provider}")
