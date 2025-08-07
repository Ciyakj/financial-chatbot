import os
from dotenv import load_dotenv

load_dotenv()  # This loads your .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
print("GROQ:", os.getenv("GROQ_API_KEY")) 