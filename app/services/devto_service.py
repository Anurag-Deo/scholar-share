from typing import Any, Dict

import requests

from app.config.settings import settings
from app.models.schemas import BlogContent


class DevToService:
    def __init__(self):
        self.api_key = settings.DEVTO_API_KEY
        self.base_url = "https://dev.to/api"

    async def publish_article(
        self, blog_content: BlogContent, publish_now: bool = False
    ) -> Dict[str, Any]:
        """Publish article to DEV.to"""
        try:
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json",
            }

            article_data = {
                "article": {
                    "title": blog_content.title,
                    "body_markdown": blog_content.content,
                    "published": publish_now,
                    "tags": blog_content.tags,
                    "description": blog_content.meta_description,
                },
            }

            response = requests.post(
                f"{self.base_url}/articles",
                json=article_data,
                headers=headers,
            )

            response.raise_for_status()
            result = response.json()

            return {
                "success": True,
                "url": result.get("url"),
                "id": result.get("id"),
                "published": result.get("published", False),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def get_my_articles(self, per_page: int = 10) -> Dict[str, Any]:
        """Get user's published articles"""
        try:
            headers = {
                "api-key": self.api_key,
            }

            response = requests.get(
                f"{self.base_url}/articles/me/published?per_page={per_page}",
                headers=headers,
            )
            response.raise_for_status()
            return {"success": True, "articles": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}


devto_service = DevToService()
