import asyncio
import base64
from email.mime import base
from pathlib import Path
from typing import Optional

import aiofiles
from openai import AsyncOpenAI

from app.config.settings import settings
from app.models.schemas import PaperAnalysis


class ImageGenerationService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.LIGHT_MODEL_API_KEY, base_url=settings.IMAGE_GEN_BASE_URL)
        self.output_dir = Path("outputs/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_image_prompt(
        self,
        analysis: PaperAnalysis,
        platform: str,
    ) -> str:
        """Generate a visual prompt for the research paper using LLM"""
        prompt_generation_prompt = f"""
        You are an expert in creating visual prompts for AI image generation. 
        Create a detailed visual prompt for DALL-E to generate an image that represents this research paper for {platform.upper()} social media.

        Research Paper Details:
        Title: {analysis.title}
        Abstract: {analysis.abstract}
        Key Findings: {", ".join(analysis.key_findings)}
        Methodology: {analysis.methodology}
        Results: {analysis.results}
        Technical Terms: {", ".join(analysis.technical_terms)}

        Requirements for the visual prompt:
        1. Create a modern, professional, and visually appealing image
        2. The image should represent the core concept/findings of the research
        3. Use abstract or symbolic representations rather than literal interpretations
        4. Include visual elements that would work well for {platform.upper()}
        5. Avoid text in the image (it will be added separately)
        6. Make it suitable for a {platform} audience
        7. Use scientific/academic visual themes if appropriate
        8. Consider color psychology for engagement

        Choose the correct set of colors and visual elements that align with the research topic and findings.
        Consider the following aspects:
        - Use colors that evoke trust and professionalism (e.g., blues, greens)
        - Include abstract representations of key findings (e.g., graphs, charts, symbols)
        - Use modern design elements (e.g., gradients, geometric shapes)

        You can also include some text elements in the image, but keep them minimal and relevant to the research.

        Platform-specific considerations:
        - LinkedIn: Professional, clean, business-appropriate
        - Twitter: Eye-catching, modern, tech-focused
        - Facebook: Engaging, accessible, community-friendly
        - Instagram: Vibrant, aesthetic, visual-first

        Generate a detailed DALL-E prompt (max 600 characters) that will create an engaging image for this research:
        """

        from app.services.llm_service import LLMService

        llm_service = LLMService()

        messages = [
            {
                "role": "system",
                "content": "You are an expert visual designer and prompt engineer specializing in creating engaging scientific and academic imagery.",
            },
            {"role": "user", "content": prompt_generation_prompt},
        ]

        image_prompt = await llm_service.generate_completion(
            messages=messages,
            model_type="heavy",
            temperature=0.8,
        )

        # Clean and truncate the prompt if needed
        image_prompt = image_prompt.strip().replace("\n", " ")
        if len(image_prompt) > 600:
            image_prompt = image_prompt[:597] + "..."

        return image_prompt

    async def generate_social_media_image(
        self,
        analysis: PaperAnalysis,
        platform: str,
        style: str = settings.IMAGE_GEN_IMAGE_STYLE,
    ) -> Optional[str]:
        """Generate an image for social media post using Image Generation model"""
        try:
            # Generate the image prompt using LLM
            image_prompt = await self.generate_image_prompt(analysis, platform)

            # Add platform-specific styling to the prompt
            styled_prompt = f"{image_prompt}, {platform} social media style, professional, high quality, digital art"

            # Generate image using Image Generation model
            response = await self.client.images.generate(
                model=settings.IMAGE_GEN_MODEL,
                prompt=styled_prompt,
                size=settings.IMAGE_GEN_IMAGE_SIZE,
                quality=settings.IMAGE_GEN_IMAGE_QUALITY,
                style=style,
                n=1,
            )

            # Download and save the image
            # image_url = response.data[0].url
            # if image_url:
            #     # Create filename based on paper title and platform
            #     safe_title = "".join(
            #         c for c in analysis.title if c.isalnum() or c in (" ", "-", "_")
            #     ).rstrip()
            #     safe_title = safe_title.replace(" ", "_")[:50]  # Limit length
            #     filename = f"{safe_title}_{platform}.png"
            #     image_path = self.output_dir / filename

            #     # Download the image
            #     async with aiohttp.ClientSession() as session:
            #         async with session.get(image_url) as response:
            #             if response.status == 200:
            #                 async with aiofiles.open(image_path, "wb") as f:
            #                     async for chunk in response.content.iter_chunked(8192):
            #                         await f.write(chunk)

            #                 return str(image_path)
            base64_data = response.data[0].b64_json
            image_data = base64.b64decode(base64_data)
            # Create filename based on paper title and platform
            safe_title = "".join(
                c for c in analysis.title if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            safe_title = safe_title.replace(" ", "_")[:50]  # Limit length
            filename = f"{safe_title}_{platform}.png"
            image_path = self.output_dir / filename
            async with aiofiles.open(image_path, "wb") as f:
                await f.write(image_data)
            return str(image_path)

            # return None

        except Exception as e:
            print(f"Error generating image for {platform}: {e!s}")
            return None

    async def generate_all_social_images(self, analysis: PaperAnalysis) -> dict:
        """Generate images for all social media platforms"""
        platforms = ["linkedin", "twitter", "facebook", "instagram"]
        results = {}

        # Generate images concurrently for better performance
        tasks = [
            self.generate_social_media_image(analysis, platform)
            for platform in platforms
        ]

        images = await asyncio.gather(*tasks, return_exceptions=True)

        for platform, image_path in zip(platforms, images):
            if isinstance(image_path, Exception):
                print(f"Failed to generate image for {platform}: {image_path!s}")
                results[platform] = None
            else:
                results[platform] = image_path

        return results

    async def create_simple_fallback_image(
        self,
        analysis: PaperAnalysis,
        platform: str,
    ) -> str:
        """Create a simple text-based fallback image if DALL-E fails"""
        try:
            import textwrap

            from PIL import Image, ImageDraw, ImageFont

            # Create a simple image with the paper title
            img = Image.new(
                "RGB",
                (1024, 1024),
                color="#1e3a8a",
            )  # Nice blue background
            draw = ImageDraw.Draw(img)

            # Try to use a nice font, fallback to default
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    48,
                )
                title_font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    36,
                )
            except:
                font = ImageFont.load_default()
                title_font = ImageFont.load_default()

            # Wrap the title text
            title_lines = textwrap.wrap(analysis.title, width=30)

            # Calculate text positioning
            y_offset = 400
            for line in title_lines[:3]:  # Maximum 3 lines
                bbox = draw.textbbox((0, 0), line, font=title_font)
                text_width = bbox[2] - bbox[0]
                x = (1024 - text_width) // 2
                draw.text((x, y_offset), line, fill="white", font=title_font)
                y_offset += 60

            # Add "Research Insights" text
            research_text = "Research Insights"
            bbox = draw.textbbox((0, 0), research_text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (1024 - text_width) // 2
            draw.text(
                (x, 300),
                research_text,
                fill="#fbbf24",
                font=font,
            )  # Golden color

            # Save the image
            safe_title = "".join(
                c for c in analysis.title if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            safe_title = safe_title.replace(" ", "_")[:50]
            filename = f"{safe_title}_{platform}_fallback.png"
            image_path = self.output_dir / filename

            img.save(image_path)
            return str(image_path)

        except Exception as e:
            print(f"Failed to create fallback image: {e!s}")
            return None


# Global instance
image_service = ImageGenerationService()
