from app.agents.base_agent import BaseAgent
from app.models.schemas import PaperAnalysis, PresentationPlan, SlideContent


class PresentationPlannerAgent(BaseAgent):
    """Agent to plan presentation structure and content based on paper analysis"""

    def __init__(self):
        super().__init__("PresentationPlanner", model_type="heavy")

    async def process(
        self, analysis: PaperAnalysis, max_slides: int = 15
    ) -> PresentationPlan:
        """Create a detailed plan for the presentation slides"""
        planning_prompt = f"""
        You are an expert presentation planner specializing in academic research presentations. 
        Create a detailed slide-by-slide plan for a {max_slides}-slide presentation based on this research paper analysis.

        Paper Analysis:
        Title: {analysis.title}
        Authors: {", ".join(analysis.authors)}
        Abstract: {analysis.abstract}
        Key Findings: {", ".join(analysis.key_findings)}
        Methodology: {analysis.methodology}
        Results: {analysis.results}
        Conclusion: {analysis.conclusion}
        Complexity Level: {analysis.complexity_level}
        Technical Terms: {", ".join(analysis.technical_terms)}

        Create a presentation plan with the following structure:
        1. Title slide
        2. Agenda/Outline
        3. Introduction/Background (1-2 slides)
        4. Problem Statement/Motivation (1 slide)
        5. Methodology (2-3 slides)
        6. Results (3-4 slides)
        7. Key Findings (1-2 slides)
        8. Implications/Discussion (1-2 slides)
        9. Conclusion (1 slide)
        10. Future Work/Q&A (1 slide)

        For each slide, provide:
        - Slide number
        - Title
        - Detailed content description (what should be on the slide)
        - Slide type (title, content, image, diagram, conclusion)
        - Any speaker notes
        - Suggestions for tikz diagrams if applicable

        Also suggest specific diagrams that would enhance the presentation:
        - Flowcharts for methodology
        - Architecture diagrams for systems
        - Comparison charts for results
        - Timeline diagrams for processes
        - Graphs for statistical data

        Try to put the content in the slides in a way that is engaging and informative, while also being concise.
        Don't put too much text on each slide; focus on key points and visuals.
        Understand that the slides are small and too much text will overflow from the slides making them look cluttered.
        

        Respond in this JSON format:
        {{
            "total_slides": {max_slides},
            "slides": [
                {{
                    "slide_number": 1,
                    "title": "Slide Title",
                    "content": "Detailed content description",
                    "slide_type": "title|content|image|diagram|conclusion",
                    "notes": "Speaker notes or additional information",
                    "tikz_diagrams": ["description of tikz diagram if needed"]
                }}
            ],
            "suggested_diagrams": ["List of diagrams to create"],
            "presentation_style": "academic"
        }}

        Make the presentation engaging, well-structured, and appropriate for an academic audience.
        Ensure content flows logically and each slide has a clear purpose.
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert academic presentation planner with deep knowledge of effective presentation design and research communication.",
            },
            {"role": "user", "content": planning_prompt},
        ]

        response = await self.generate_response(messages, temperature=0.4)

        try:
            # Clean and parse JSON response
            import json
            import re

            # Remove markdown code blocks if present
            cleaned_response = re.sub(r"^```json\s*", "", response, flags=re.MULTILINE)
            cleaned_response = re.sub(
                r"\s*```$", "", cleaned_response, flags=re.MULTILINE
            )
            cleaned_response = cleaned_response.strip()

            # Extract JSON from cleaned response
            json_match = re.search(r"\{.*\}", cleaned_response, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())

                # Convert slides data to SlideContent objects
                slides = []
                for slide_data in plan_data.get("slides", []):
                    slides.append(SlideContent(**slide_data))

                return PresentationPlan(
                    total_slides=plan_data.get("total_slides", max_slides),
                    slides=slides,
                    suggested_diagrams=plan_data.get("suggested_diagrams", []),
                    presentation_style=plan_data.get("presentation_style", "academic"),
                )
            raise ValueError("No valid JSON found in response")

        except Exception as e:
            print(f"Error parsing presentation plan: {e}")
            # Fallback plan
            return self._create_fallback_plan(analysis, max_slides)

    def _create_fallback_plan(
        self, analysis: PaperAnalysis, max_slides: int
    ) -> PresentationPlan:
        """Create a basic fallback presentation plan"""
        slides = [
            SlideContent(
                slide_number=1,
                title=analysis.title,
                content=f"Authors: {', '.join(analysis.authors)}",
                slide_type="title",
                notes="Title slide with paper title and authors",
            ),
            SlideContent(
                slide_number=2,
                title="Agenda",
                content="Presentation outline: Introduction, Methodology, Results, Conclusion",
                slide_type="content",
                notes="Overview of presentation structure",
            ),
            SlideContent(
                slide_number=3,
                title="Introduction",
                content=analysis.abstract[:300] + "..."
                if len(analysis.abstract) > 300
                else analysis.abstract,
                slide_type="content",
                notes="Introduction based on paper abstract",
            ),
            SlideContent(
                slide_number=4,
                title="Methodology",
                content=analysis.methodology[:400] + "..."
                if len(analysis.methodology) > 400
                else analysis.methodology,
                slide_type="content",
                notes="Research methodology and approach",
            ),
            SlideContent(
                slide_number=5,
                title="Key Findings",
                content="\n".join(
                    [f"• {finding}" for finding in analysis.key_findings[:3]]
                ),
                slide_type="content",
                notes="Main research findings",
            ),
            SlideContent(
                slide_number=6,
                title="Results",
                content=analysis.results[:400] + "..."
                if len(analysis.results) > 400
                else analysis.results,
                slide_type="content",
                notes="Research results and outcomes",
            ),
            SlideContent(
                slide_number=7,
                title="Conclusion",
                content=analysis.conclusion[:300] + "..."
                if len(analysis.conclusion) > 300
                else analysis.conclusion,
                slide_type="conclusion",
                notes="Conclusions and implications",
            ),
            SlideContent(
                slide_number=8,
                title="Thank You",
                content="Questions & Discussion",
                slide_type="conclusion",
                notes="Q&A slide",
            ),
        ]

        return PresentationPlan(
            total_slides=len(slides),
            slides=slides,
            suggested_diagrams=[
                "Research methodology flowchart",
                "Results comparison chart",
            ],
            presentation_style="academic",
        )
