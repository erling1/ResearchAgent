from serpapi import GoogleSearch
import os
import aiohttp



class WebSearch:

    def __init__(self, api_key):
        self._url = "https://serpapi.com/search"
        self.API_KEY = api_key


    async def search_web(self, query):
        params = {
                "engine": "google",
                "q": query,
                "api_key":  self.API_KEY
                }
        
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self._url, params=params) as response:
                results = await response.json()
                organic_results = results['organic_results']
                return organic_results


    

