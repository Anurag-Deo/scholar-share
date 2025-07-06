import json
import re

from app.agents.base_agent import BaseAgent
from app.models.schemas import PaperAnalysis, PaperInput


class PaperAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("PaperAnalyzer", model_type="heavy")

    async def process(self, input_data: PaperInput) -> PaperAnalysis:
        """Analyze research paper and extract key information"""
        analysis_prompt = f"""
        You are an expert research paper analyzer. Analyze the following research paper content and extract key information in JSON format.

        Paper Content:
        {input_data.content}

        Please provide a detailed analysis in the following JSON structure:
        {{
            "title": "Paper title",
            "authors": ["Author 1", "Author 2"],
            "abstract": "Paper abstract",
            "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
            "methodology": "Detailed description of methodology",
            "results": "Summary of key results",
            "conclusion": "Main conclusions",
            "complexity_level": "beginner/intermediate/advanced",
            "technical_terms": ["term1", "term2"],
            "figures_tables": [
                {{"type": "figure", "description": "Description", "content": "Content if available"}},
                {{"type": "table", "description": "Description", "content": "Content if available"}}
            ]
        }}

        Focus on extracting the most important and impactful findings. Be thorough but concise.
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert research paper analyzer with deep knowledge across multiple academic fields.",
            },
            {"role": "user", "content": analysis_prompt},
        ]

        response = await self.generate_response(messages, temperature=0.3)
        # print(f"Raw response: {response}")  # Debugging line

        try:
            # Extract JSON from response by removing markdown code blocks
            # Remove ```json at the start and ``` at the end
            cleaned_response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
            cleaned_response = re.sub(r'\s*```$', '', cleaned_response, flags=re.MULTILINE)
            cleaned_response = cleaned_response.strip()
            print(f"Cleaned response: {cleaned_response}")  # Debugging line

            # Extract JSON from cleaned response
            json_match = re.search(r"\{.*\}", cleaned_response, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
                return PaperAnalysis(**analysis_data)
            raise ValueError("No valid JSON found in response")
        except Exception:
            # Fallback parsing
            return self._fallback_parse(response, input_data.content)

    def _fallback_parse(self, response: str, content: str) -> PaperAnalysis:
        """Fallback parsing if JSON extraction fails"""
        lines = content.split("\n")
        title = next(
            (line.strip() for line in lines if len(line.strip()) > 10), "Untitled Paper"
        )

        return PaperAnalysis(
            title=title,
            authors=["Unknown Author"],
            abstract=content[:500] + "..." if len(content) > 500 else content,
            key_findings=["Analysis in progress"],
            methodology="To be analyzed",
            results="To be analyzed",
            conclusion="To be analyzed",
            complexity_level="intermediate",
            technical_terms=[],
            figures_tables=[],
        )
