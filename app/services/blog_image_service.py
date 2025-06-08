import asyncio
import base64
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

from app.models.schemas import PaperAnalysis


class BlogImageService:
    """Service for generating and managing images for blog posts"""

    def __init__(self):
        self.deepinfra_model = "black-forest-labs/FLUX-1.1-pro"
        self.output_dir = Path("outputs/images/blog")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.upload_api_key = (
            "6d207e02198a847aa98d0a2a901485a5"  # FreeImage.host API key
        )

    async def generate_blog_images(
        self,
        analysis: PaperAnalysis,
        content: str,
    ) -> list[str]:
        """Generate multiple images for a blog post and return markdown image tags"""
        try:
            # Generate image prompts based on the blog content
            image_prompts = await self._generate_image_prompts(analysis, content)

            # Generate images using DeepInfra
            image_urls = await self._generate_images_async(image_prompts)

            # Create markdown image tags with proper formatting
            markdown_images = []
            for i, url in enumerate(image_urls):
                if url and url != "No image URL found":
                    caption = self._generate_image_caption(analysis, i)
                    markdown_images.append(f"![{caption}]({url})")

            return markdown_images

        except Exception as e:
            print(f"Error generating blog images: {e}")
            return []

    async def _generate_image_prompts(
        self,
        analysis: PaperAnalysis,
        content: str,
    ) -> list[str]:
        """Generate image prompts based on the research paper and blog content"""
        from app.services.llm_service import LLMService

        llm_service = LLMService()

        prompt_generation_text = f"""
        You are an expert in creating visual prompts for AI image generation to enhance blog posts about research papers.
        
        Research Paper Details:
        Title: {analysis.title}
        Abstract: {analysis.abstract[:300]}...
        Key Findings: {", ".join(analysis.key_findings[:3])}
        Methodology: {analysis.methodology[:200]}...
        
        Blog Content Preview: {content[:500]}...
        
        Create 2-3 detailed visual prompts for FLUX image generation that would enhance this blog post. 
        Each prompt should:
        1. Be scientifically accurate and relevant to the research
        2. Create visually appealing, professional diagrams or illustrations
        3. Help explain complex concepts through visual metaphors
        4. Be suitable for a blog audience (clear, engaging, informative)
        
        Generate prompts for:
        1. A main concept illustration (abstract/conceptual)
        2. A methodology visualization (process/workflow)
        3. A results/findings/use-case illustration (if applicable)

        Each prompt should be highly detailed, incorporating the elements that needed along with the details like colors, style, textures, background details, and also mention the correct position of the elements in the image.

        Return only the prompts, one per line, without numbering or additional text.
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert visual designer specializing in scientific and educational imagery for blog posts.",
            },
            {"role": "user", "content": prompt_generation_text},
        ]

        response = await llm_service.generate_completion(
            messages=messages,
            model_type="heavy",
            temperature=0.7,
        )

        # Parse the response to extract individual prompts
        prompts = [prompt.strip() for prompt in response.split("\n") if prompt.strip()]

        # Enhance prompts with style guidelines
        enhanced_prompts = []
        for prompt in prompts[:3]:  # Limit to 3 images
            enhanced_prompt = f"{prompt}, professional scientific illustration, clean modern design, educational diagram style, high quality, detailed"
            enhanced_prompts.append(enhanced_prompt)

        return enhanced_prompts

    async def _generate_images_async(self, prompts: list[str]) -> list[str]:
        """Generate images asynchronously using DeepInfra API"""
        loop = asyncio.get_event_loop()

        # Use ThreadPoolExecutor to handle blocking requests
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                loop.run_in_executor(executor, self._fetch_image_url, prompt)
                for prompt in prompts
            ]

            results = await asyncio.gather(*futures, return_exceptions=True)

            # Process results and upload images
            upload_futures = []
            for result in results:
                if isinstance(result, str) and result != "No image URL found":
                    upload_futures.append(
                        loop.run_in_executor(
                            executor,
                            self._process_and_upload_image,
                            result,
                        ),
                    )

            if upload_futures:
                uploaded_urls = await asyncio.gather(
                    *upload_futures,
                    return_exceptions=True,
                )
                return [
                    url if not isinstance(url, Exception) else "No image URL found"
                    for url in uploaded_urls
                ]

            return []

    def _fetch_image_url(self, prompt: str) -> str:
        """Fetch image from DeepInfra API (synchronous)"""
        url = f"https://api.deepinfra.com/v1/inference/{self.deepinfra_model}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"bearer {os.getenv('DEEPINFRA_API_KEY')}",
        }
        payload = {
            "prompt": prompt,
            "num_inference_steps": 20,
            "width": 1024,
            "height": 768,  # Better aspect ratio for blog images
            "response_format": "b64_json",
        }
        print(f"Payload: {payload}")  # Debugging output

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                response_data = response.json()
                print(f"Response: {response_data}")  # Debugging output

                # Handle response format with data array and b64_json
                data = response_data.get("data", [])
                if data and len(data) > 0:
                    b64_json = data[0].get("b64_json")
                    if b64_json:
                        return self._save_and_return_base64_image(
                            b64_json, "temp_image.png"
                        )

                # Handle response format with direct image_url
                if "image_url" in response_data:
                    return self._download_and_convert_image(response_data["image_url"])

                return "No image URL found"

            print(f"Request failed: {response.status_code}, {response.text}")
            return "No image URL found"
        except Exception as e:
            print(f"An error occurred: {e!s}")
            return "No image URL found"

    def _save_and_return_base64_image(self, b64_data: str, filename: str) -> str:
        """Save base64 image data to file and return data URL."""
        print(f"Saving image to temp file: {filename}")
        print(f"Base64 length: {len(b64_data)}")
        print(f"Image data: {b64_data[:30]}...")  # Print first 30 chars for debugging

        temp_path = self.output_dir / filename
        with temp_path.open("wb") as image_file:
            image_file.write(base64.b64decode(b64_data))

        return f"data:image/png;base64,{b64_data}"

    def _download_and_convert_image(self, image_url: str) -> str:
        """Download image from URL and convert to base64."""
        print(f"Downloading image from URL: {image_url}")

        try:
            img_response = requests.get(image_url, timeout=60)
            if img_response.status_code == 200:
                # Convert image to base64
                image_data = img_response.content
                b64_encoded = base64.b64encode(image_data).decode("utf-8")

                # Save the image to a file for debugging
                print("Saving downloaded image to temp file...")
                print(f"Image size: {len(image_data)} bytes")

                temp_path = self.output_dir / "temp_downloaded_image.png"
                with temp_path.open("wb") as image_file:
                    image_file.write(image_data)

                return f"data:image/png;base64,{b64_encoded}"

            print(f"Failed to download image: {img_response.status_code}")
            return "No image URL found"
        except Exception as download_error:
            print(f"Error downloading image: {download_error}")
            return "No image URL found"

    def _process_and_upload_image(self, base64_string: str) -> str:
        """Process base64 image and upload to hosting service (synchronous)"""
        try:
            # Handle both formats: "data:image/png;base64,..." and just base64 string
            if base64_string.startswith("data:image"):
                # Extract base64 data from data URL
                image_data = base64.b64decode(base64_string.split(",")[-1])
            else:
                # Direct base64 string
                image_data = base64.b64decode(base64_string)

            temp_filename = f"temp_blog_image_{hash(base64_string) % 1000000}.png"
            temp_path = self.output_dir / temp_filename

            with open(temp_path, "wb") as image_file:
                image_file.write(image_data)

            # Upload to hosting service
            url = "https://freeimage.host/api/1/upload"

            with open(temp_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

            payload = {
                "key": self.upload_api_key,
                "action": "upload",
                "source": base64_image,
                "format": "json",
            }

            response = requests.post(url, data=payload, timeout=60)

            if response.status_code == 200:
                response_data = response.json()
                hosted_url = response_data.get("image", {}).get(
                    "url",
                    "No image URL found",
                )

                # Clean up temp file
                try:
                    temp_path.unlink()
                except:
                    pass

                return hosted_url
            print(f"Upload failed: {response.status_code}, {response.text}")
            return "No image URL found"

        except Exception as e:
            print(f"Error processing/uploading image: {e!s}")
            return "No image URL found"

    def _generate_image_caption(self, analysis: PaperAnalysis, image_index: int) -> str:
        """Generate appropriate captions for images"""
        captions = [
            f"Conceptual illustration of {analysis.title[:50]}...",
            f"Methodology visualization for {analysis.title[:50]}...",
            f"Key findings illustration from {analysis.title[:50]}...",
        ]

        if image_index < len(captions):
            return captions[image_index]
        return f"Research illustration from {analysis.title[:50]}..."

    async def embed_images_in_content(self, content: str, images: list[str]) -> str:
        """Embed images into blog content at appropriate locations"""
        if not images:
            return content

        # Split content into sections (by headers)
        sections = re.split(r"(^#{1,3}\s+.*$)", content, flags=re.MULTILINE)

        # Insert images at strategic points
        enhanced_content = []
        image_index = 0

        for i, section in enumerate(sections):
            enhanced_content.append(section)

            # Add image after introduction (first section after first header)
            if (
                (i == 2 and image_index < len(images))
                or (i == len(sections) // 2 and image_index < len(images))
                or (i == len(sections) - 3 and image_index < len(images))
            ):
                enhanced_content.append(f"\n\n{images[image_index]}\n\n")
                image_index += 1

        return "".join(enhanced_content)


# Global instance
blog_image_service = BlogImageService()
