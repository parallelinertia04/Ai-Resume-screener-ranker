import aiohttp
import re
from typing import Optional, Tuple
from src.config import GITHUB_TOKEN

class GithubEnricher:
    @staticmethod
    def extract_username(url: str) -> Optional[str]:
        match = re.search(r"github\.com/([a-zA-Z0-9-]+)", url)
        if match:
            return match.group(1)
        return None

    @staticmethod
    async def get_github_score_async(url: str) -> Tuple[int, str]:
        if not url:
            return 0, "No GitHub profile available"
            
        username = GithubEnricher.extract_username(url)
        if not username:
            return 0, "No valid GitHub URL"
            
        headers = {}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"https://api.github.com/users/{username}", headers=headers, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        repos = data.get("public_repos", 0)
                        
                        score = 0
                        if repos > 0:
                            score += 5
                        if repos >= 5:
                            score += 5
                            
                        # Cap at 10
                        score = min(10, score)
                        return score, f"Recently active; {repos} public repositories."
                    elif response.status == 403:
                        return 0, "GitHub API rate limited."
                    else:
                        return 0, "GitHub profile not found or private."
            except Exception as e:
                return 0, f"GitHub API error: {str(e)}"
