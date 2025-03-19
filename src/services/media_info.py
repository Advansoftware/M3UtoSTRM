import aiohttp
from typing import Dict, Optional

class MediaInfo:
    def __init__(self, omdb_api_key: str = None, tmdb_api_key: str = None):
        self.omdb_api_key = omdb_api_key
        self.tmdb_api_key = tmdb_api_key
        self.omdb_url = "http://www.omdbapi.com/"
        self.tmdb_url = "https://api.themoviedb.org/3"

    async def search_title(self, title: str) -> Optional[Dict]:
        """Busca informações do título em ambas as APIs"""
        results = {}
        
        if self.omdb_api_key:
            omdb_data = await self._search_omdb(title)
            if omdb_data:
                results.update(omdb_data)
        
        if self.tmdb_api_key:
            tmdb_data = await self._search_tmdb(title)
            if tmdb_data:
                results.update(tmdb_data)
        
        return results if results else None

    async def _search_omdb(self, title: str) -> Optional[Dict]:
        async with aiohttp.ClientSession() as session:
            params = {
                'apikey': self.omdb_api_key,
                't': title,
                'plot': 'short'
            }
            async with session.get(self.omdb_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('Response') == 'True':
                        return {
                            'omdb_title': data.get('Title'),
                            'year': data.get('Year'),
                            'omdb_poster': data.get('Poster'),
                            'plot': data.get('Plot'),
                            'imdb_id': data.get('imdbID'),
                            'type': data.get('Type')
                        }
        return None

    async def _search_tmdb(self, title: str) -> Optional[Dict]:
        async with aiohttp.ClientSession() as session:
            params = {
                'api_key': self.tmdb_api_key,
                'query': title
            }
            async with session.get(f"{self.tmdb_url}/search/multi", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('results'):
                        result = data['results'][0]
                        return {
                            'tmdb_id': result.get('id'),
                            'tmdb_title': result.get('title') or result.get('name'),
                            'tmdb_poster': f"https://image.tmdb.org/t/p/w500{result.get('poster_path')}",
                            'overview': result.get('overview'),
                            'media_type': result.get('media_type')
                        }
        return None
