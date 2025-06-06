import base64
import os
from typing import Optional, Tuple

from app.agents.base_agent import BaseAgent


class PresentationVisualAnalyzerAgent(BaseAgent):
    """Agent to analyze presentation layout and visual elements for quality assurance"""

    def __init__(self):
        super().__init__("PresentationVisualAnalyzer", model_type="light")

    async def analyze_presentation_layout(
        self,
        presentation_image_path: str,
        latex_code: str,
        slide_number: int,
        total_slides: int,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Analyze presentation slide layout and provide feedback

        Returns:
            tuple: (is_layout_good, analysis_feedback, suggested_fixes)

        """
        try:
            # Convert image to base64 for vision model
            image_base64 = await self._image_to_base64(presentation_image_path)
            if not image_base64:
                return False, "Could not process presentation image", None

            analysis_prompt = f"""
            Analyze this presentation slide (slide {slide_number} of {total_slides}) for layout quality and visual appeal.

            Look for the following aspects:
            1. Text readability and font sizes
            2. Content overflow or text cut-off
            3. Proper spacing and margins
            4. Visual hierarchy and organization
            5. Color scheme and contrast
            6. Diagram/image clarity and positioning
            7. Overall professional appearance
            8. Slide balance and composition

            Specific issues to check:
            - Is all text clearly visible and readable?
            - Are there any overlapping elements?
            - Is the content well-organized and not cramped?
            - Are diagrams and images properly sized and positioned?
            - Is the slide visually appealing and professional?
            - Does the slide follow good presentation design principles?

            Provide a detailed assessment including:
            1. Overall quality rating (Excellent/Good/Fair/Poor)
            2. Specific issues identified (if any)
            3. Recommendations for improvement
            4. Whether the slide needs to be regenerated

            There are a lot of cases where the sentences are not fitting in the slide, it looks like it is the end of the sentence, but some part of the sentence is cut off. Make sure to find those cases and provide feedback on them. THESE FEEDBACKS SHOULD BE WRITTEN IN CAPITAL.

            Be thorough in your analysis and provide actionable feedback.
            """

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert presentation design analyst with deep knowledge of visual design principles and academic presentation standards.",
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

            # Determine if layout needs improvement
            needs_improvement = any(
                keyword in analysis_response.lower()
                for keyword in [
                    "poor",
                    "fair",
                    "cramped",
                    "overflow",
                    "cut-off",
                    "overlapping",
                    "unreadable",
                    "too small",
                    "needs improvement",
                    "regenerate",
                ]
            )

            layout_is_good = not needs_improvement

            if needs_improvement:
                # Generate specific fixes
                fixed_latex = await self._generate_layout_fixes(
                    latex_code, analysis_response
                )
                return layout_is_good, analysis_response, fixed_latex

            return layout_is_good, analysis_response, None

        except Exception as e:
            return False, f"Error analyzing presentation layout: {e!s}", None

    async def _image_to_base64(self, image_path: str) -> Optional[str]:
        """Convert image to base64 string"""
        try:
            if not os.path.exists(image_path):
                print(f"Presentation image not found: {image_path}")
                return None

            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_string = base64.b64encode(image_data).decode("utf-8")
                return base64_string
        except Exception as e:
            print(f"Error converting presentation image to base64: {e}")
            return None

    async def _generate_layout_fixes(self, original_latex: str, analysis: str) -> str:
        """Generate improved LaTeX code based on visual analysis"""
        fix_prompt = f"""
        Based on the presentation layout analysis below, improve the Beamer LaTeX code to fix visual and layout issues.
        
        Visual Analysis Feedback:
        {analysis}
        
        Original LaTeX Code:
        {original_latex}
        
        Please provide an improved version that addresses the identified issues. Focus on:
        1. Improving text readability (font sizes, spacing)
        2. Fixing content overflow or cut-off issues
        3. Better spacing and margins
        4. Improved visual hierarchy
        5. Better positioning of elements
        6. Professional color scheme
        7. Proper slide layout and composition
        
        Beamer-specific improvements:
        - Use appropriate frame options for content fitting
        - Adjust font sizes with \\tiny, \\small, \\large, etc.
        - Use proper column layouts for better organization
        - Apply appropriate themes and color schemes
        - Use proper spacing commands (\\vspace, \\hspace)
        - Ensure TikZ diagrams fit properly on slides
        
        Provide ONLY the corrected Beamer LaTeX code.
        Do not include explanations or markdown formatting.
        """

        messages = [
            {
                "role": "system",
                "content": "You are a Beamer LaTeX expert specializing in presentation layout optimization and visual design improvements.",
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

    async def analyze_diagram_quality(
        self,
        diagram_image_path: str,
        tikz_code: str,
    ) -> Tuple[bool, str, Optional[str]]:
        """Analyze the quality of TikZ diagrams in presentations"""
        try:
            image_base64 = await self._image_to_base64(diagram_image_path)
            if not image_base64:
                return False, "Could not process diagram image", None

            diagram_prompt = """
            Analyze this TikZ diagram for clarity, readability, and visual appeal in a presentation context.

            Check for:
            1. Clarity and readability of text and labels
            2. Appropriate sizing for presentation slides
            3. Good color choices and contrast
            4. Proper spacing between elements
            5. Professional appearance
            6. Clear visual hierarchy
            7. Effective use of shapes and arrows

            Provide feedback on:
            - Overall diagram quality
            - Specific improvements needed
            - Whether the diagram enhances understanding
            - Recommendations for better visual design
            """

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert in diagram design and TikZ visualization for academic presentations.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": diagram_prompt,
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

            analysis = await self.generate_response(messages, temperature=0.3)

            needs_improvement = any(
                keyword in analysis.lower()
                for keyword in [
                    "poor",
                    "unclear",
                    "hard to read",
                    "too small",
                    "cramped",
                    "needs improvement",
                    "confusing",
                    "messy",
                ]
            )

            is_good = not needs_improvement

            if needs_improvement:
                improved_tikz = await self._improve_tikz_diagram(tikz_code, analysis)
                return is_good, analysis, improved_tikz

            return is_good, analysis, None

        except Exception as e:
            return False, f"Error analyzing diagram: {e!s}", None

    async def _improve_tikz_diagram(self, original_tikz: str, analysis: str) -> str:
        """Improve TikZ diagram code based on analysis"""
        improvement_prompt = f"""
        Improve this TikZ diagram code based on the visual analysis feedback.
        
        Analysis Feedback:
        {analysis}
        
        Original TikZ Code:
        {original_tikz}
        
        Create an improved version that:
        - Has better readability and clarity
        - Uses appropriate sizing for presentations
        - Has good color choices and contrast
        - Is well-organized and professional
        - Follows TikZ best practices
        
        Provide only the improved TikZ code within tikzpicture environment.
        """

        messages = [
            {
                "role": "system",
                "content": "You are a TikZ expert focused on creating clear, professional diagrams for presentations.",
            },
            {
                "role": "user",
                "content": improvement_prompt,
            },
        ]

        improved_tikz = await self.generate_response(messages, temperature=0.2)

        # Clean the response
        improved_tikz = (
            improved_tikz.replace("```latex", "")
            .replace("```tikz", "")
            .replace("```", "")
            .strip()
        )

        return improved_tikz

    async def process(self, input_data):
        """Implementation of abstract method from BaseAgent"""
        return await self.analyze_presentation_layout(
            input_data.get("image_path"),
            input_data.get("latex_code"),
            input_data.get("slide_number", 1),
            input_data.get("total_slides", 1),
        )
