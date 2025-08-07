import requests
from config.config import SERPAPI_API_KEY

def search_web(query):
    url = "https://serpapi.com/search"
    params = {"q": query, "api_key": SERPAPI_API_KEY, "engine": "google"}
    try:
        res = requests.get(url, params=params).json()
        return res["organic_results"][0]["snippet"]
    except:
        return "No relevant results found online."
