import asyncio
from typing import Any, Dict

import requests

from app.config.settings import settings
from app.models.schemas import BlogContent


class DevToService:
    def __init__(self):
        self.api_key = settings.DEVTO_API_KEY
        self.base_url = "https://dev.to/api"

    async def publish_article(
        self,
        blog_content: BlogContent,
        publish_now: bool = False,
    ) -> Dict[str, Any]:
        """Publish article to DEV.to"""

        def _sync_publish():
            try:
                # Check if API key is configured
                if not self.api_key:
                    return {
                        "success": False,
                        "error": "DEV.to API key is not configured. Please set the DEVTO_API_KEY environment variable.",
                    }

                headers = {
                    "api-key": self.api_key,
                    "Content-Type": "application/json",
                }

                # Ensure tags is a list of strings
                tags = blog_content.tags if isinstance(blog_content.tags, list) else []
                # DEV.to has a limit of 4 tags max
                tags = tags[:4] if len(tags) > 4 else tags

                article_data = {
                    "article": {
                        "title": blog_content.title,
                        "body_markdown": blog_content.content,
                        "published": publish_now,
                        "tags": tags,
                        "description": blog_content.meta_description,
                    },
                }

                # Only add series if it's not empty
                if hasattr(blog_content, "series") and blog_content.series:
                    article_data["article"]["series"] = blog_content.series

                print("=== DEV.to Publish Debug Info ===")
                print(f"API Key present: {bool(self.api_key)}")
                print(f"API Key length: {len(self.api_key) if self.api_key else 0}")
                print(f"Title: {blog_content.title}")
                print(f"Tags: {tags}")
                print(f"Content length: {len(blog_content.content)}")
                print(f"Description: {blog_content.meta_description}")
                print("Article data structure:")
                print(article_data)

                response = requests.post(
                    f"{self.base_url}/articles",
                    json=article_data,
                    headers=headers,
                    timeout=30,  # Add timeout
                )
                response.raise_for_status()
                result = response.json()

                return {
                    "success": True,
                    "url": result.get("url"),
                    "id": result.get("id"),
                    "published": result.get("published", False),
                }

            except requests.exceptions.HTTPError as e:
                # Get the detailed error response from DEV.to
                error_details = "Unknown error"
                if hasattr(e, "response") and e.response is not None:
                    try:
                        error_details = e.response.json()
                    except:
                        error_details = e.response.text

                print(f"DEV.to API Error: {e}")
                print(f"Error details: {error_details}")

                return {
                    "success": False,
                    "error": f"DEV.to API Error: {e!s} - Details: {error_details}",
                }
            except Exception as e:
                print(f"General error: {e}")
                return {
                    "success": False,
                    "error": str(e),
                }

        # Run the synchronous function in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_publish)

    async def get_my_articles(self, per_page: int = 10) -> Dict[str, Any]:
        """Get user's published articles"""

        def _sync_get_articles():
            try:
                headers = {
                    "api-key": self.api_key,
                }

                response = requests.get(
                    f"{self.base_url}/articles/me/published?per_page={per_page}",
                    headers=headers,
                    timeout=30,  # Add timeout
                )
                response.raise_for_status()
                result = response.json()
                return {"success": True, "articles": result}
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Run the synchronous function in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_get_articles)


devto_service = DevToService()
