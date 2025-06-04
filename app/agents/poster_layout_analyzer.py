import base64
import os
from typing import Optional, Tuple

from app.agents.base_agent import BaseAgent


class PosterLayoutAnalyzerAgent(BaseAgent):
    """Agent to analyze poster layout and provide fixes for content that doesn't fit properly"""

    def __init__(self):
        super().__init__("PosterLayoutAnalyzer", model_type="coding")

    async def analyze_poster_layout(
        self,
        poster_image_path: str,
        latex_code: str,
        paper_title: str,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Analyze poster layout from image and provide fixes if content doesn't fit

        Returns:
            - bool: Whether the poster fits properly
            - str: Analysis message
            - Optional[str]: Fixed LaTeX code if needed

        """
        try:
            # Convert image to base64 for vision model
            image_base64 = await self._image_to_base64(poster_image_path)

            if not image_base64:
                return False, "Could not process poster image", None

            # Create analysis prompt
            analysis_prompt = f"""
            You are an expert in academic poster design and LaTeX formatting. 
            Analyze this generated poster image and determine if all content fits properly within the page boundaries.
            
            Paper Title: {paper_title}
            
            Look for the following issues:
            1. Text or content that extends beyond page margins
            2. Overlapping text or sections
            3. Cut-off content at the bottom or sides
            4. Sections that are too cramped or unreadable
            5. Any content that appears to be missing or truncated

            Based on your analysis, provide:
            1. A clear assessment of whether the poster fits properly (YES/NO)
            2. Specific issues you identify (if any)
            3. Recommendations for fixing layout issues
            
            Be detailed and specific about what you observe in the image.
            """

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert academic poster design analyst. Analyze poster layouts for proper formatting and content fit.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": analysis_prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}",
                            },
                        },
                    ],
                },
            ]

            analysis_response = await self.generate_response(messages, temperature=0.3)

            # Check if poster needs fixing
            needs_fixing = (
                "NO" in analysis_response.upper()
                and "fits properly" in analysis_response
            )
            fits_properly = not needs_fixing

            if needs_fixing:
                # Generate fixed LaTeX code
                fixed_latex = await self._generate_fixed_latex(
                    latex_code, analysis_response
                )
                return fits_properly, analysis_response, fixed_latex
            return fits_properly, analysis_response, None

        except Exception as e:
            return False, f"Error analyzing poster layout: {e!s}", None

    async def _image_to_base64(self, image_path: str) -> Optional[str]:
        """Convert image to base64 string"""
        try:
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                return None

            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_string = base64.b64encode(image_data).decode("utf-8")
                return base64_string
        except Exception as e:
            print(f"Error converting image to base64: {e}")
            return None

    async def _generate_fixed_latex(self, original_latex: str, analysis: str) -> str:
        """Generate fixed LaTeX code based on analysis"""
        fix_prompt = f"""
        Based on the poster layout analysis below, fix the LaTeX code to ensure all content fits properly within the page.
        
        Analysis of issues found:
        {analysis}
        
        Original LaTeX Code:
        {original_latex}
        
        Please provide a corrected version of the LaTeX code that addresses the layout issues.
        Focus on:
        1. Reducing font sizes if text is too large
        2. Adjusting section spacing and margins
        3. Making content more concise if needed
        4. Optimizing layout structure
        5. Ensuring proper tikzposter block sizing and positioning
        6. Using appropriate column layouts
        7. Adjusting text wrapping and line spacing
        
        Provide ONLY the corrected LaTeX code starting with \\documentclass and ending with \\end{{document}}.
        Do not include any explanations or markdown formatting.
        MAKE SURE THE ENTIRE POSTER CONTENT FITS PROPERLY ON THE PAGE.
        """

        messages = [
            {
                "role": "system",
                "content": "You are a LaTeX expert specializing in fixing academic poster layouts. Generate clean, compilable LaTeX code that fits properly on the page.",
            },
            {
                "role": "user",
                "content": fix_prompt,
            },
        ]

        fixed_latex = await self.generate_response(messages, temperature=0.2)

        # Clean the response
        fixed_latex = fixed_latex.replace("```latex", "").replace("```", "").strip()

        return fixed_latex

    async def process(self, input_data):
        """Implementation of abstract method from BaseAgent"""
        # This method can be used for batch processing if needed
        return await self.analyze_poster_layout(
            input_data.get("image_path"),
            input_data.get("latex_code"),
            input_data.get("title"),
        )
