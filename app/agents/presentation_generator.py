import subprocess
import tempfile
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.agents.presentation_planner import PresentationPlannerAgent
from app.agents.presentation_visual_analyzer import PresentationVisualAnalyzerAgent
from app.agents.tikz_diagram_generator import TikzDiagramAgent
from app.models.schemas import PaperAnalysis, PresentationContent, PresentationPlan
from app.services.presentation_pdf_to_image_service import (
    presentation_pdf_to_image_service,
)


class PresentationGeneratorAgent(BaseAgent):
    """Main agent for generating complete research presentations using Beamer"""

    def __init__(self):
        super().__init__("PresentationGenerator", model_type="coding")
        self.template_dir = "app/templates/presentation_templates"
        self.planner = PresentationPlannerAgent()
        self.diagram_generator = TikzDiagramAgent()
        self.visual_analyzer = PresentationVisualAnalyzerAgent()
        self.max_iterations = 1

    async def process(
        self,
        analysis: PaperAnalysis,
        template_type: str = "academic",
        max_slides: int = 15,
    ) -> PresentationContent:
        """Generate complete presentation from paper analysis"""
        try:
            # Step 1: Plan the presentation structure
            print("Planning presentation structure...")
            plan = await self.planner.process(analysis, max_slides)

            # Step 2: Generate TikZ diagrams if needed
            print("Generating diagrams...")
            diagrams = []
            if plan.suggested_diagrams:
                diagrams = await self.diagram_generator.process(
                    plan.suggested_diagrams,
                    analysis,
                )

            # Step 3: Generate Beamer LaTeX code
            print("Generating Beamer presentation...")
            latex_code = await self._generate_beamer_presentation(
                analysis,
                plan,
                diagrams,
                template_type,
            )

            # Step 4: Compile and analyze presentation
            print("Compiling and analyzing presentation...")
            pdf_path, final_latex = await self._compile_and_analyze_presentation(
                latex_code,
                analysis.title,
                plan,
            )

            return PresentationContent(
                title=analysis.title,
                authors=", ".join(analysis.authors),
                institution=None,  # Could be extracted from paper if available
                date=None,
                template_type=template_type,
                slides=plan.slides,
                tikz_diagrams=diagrams,
                latex_code=final_latex,
                pdf_path=pdf_path,
                total_slides=plan.total_slides,
            )

        except Exception as e:
            print(f"Error generating presentation: {e}")
            raise

    async def _generate_beamer_presentation(
        self,
        analysis: PaperAnalysis,
        plan: PresentationPlan,
        diagrams: list,
        template_type: str,
    ) -> str:
        """Generate complete Beamer LaTeX code"""
        # Create diagram code mapping
        diagram_codes = {d.diagram_id: d.tikz_code for d in diagrams}

        beamer_prompt = f"""
        Generate a complete Beamer LaTeX presentation based on this research paper analysis and slide plan.

        Paper Information:
        Title: {analysis.title}
        Authors: {", ".join(analysis.authors)}
        Abstract: {analysis.abstract}
        
        Presentation Plan:
        Total Slides: {plan.total_slides}
        Style: {plan.presentation_style}
        Template: {template_type}

        Slide Details:
        {self._format_slide_plan(plan.slides)}

        Available TikZ Diagrams:
        {self._format_diagram_info(diagrams)}

        Requirements:
        1. Use Beamer document class with appropriate theme
        2. Include all necessary packages (tikz, graphicx, etc.)
        3. Create professional academic presentation
        4. Use consistent formatting and styling
        5. Include proper section breaks and navigation
        6. Integrate TikZ diagrams where appropriate
        7. Use appropriate font sizes and spacing
        8. Follow Beamer best practices
        9. Choose the color scheme such that all the text are readable and visually appealing
        10. If there are too many content on a slide, split it into multiple slides
        11. Ensure all diagrams are properly labeled and referenced in the text
        12. No content should go out of the slide boundaries

        Template Style Guidelines:
        - Academic: Clean, professional, blue color scheme
        - Corporate: Modern, sleek, with company-like styling  
        - Minimal: Simple, clean, minimal visual elements

        Generate complete LaTeX code starting with \\documentclass{{beamer}} and ending with \\end{{document}}.
        Include all slide content, proper formatting, and TikZ diagrams.
        Make sure each slide is well-designed and informative.
        """

        messages = [
            {
                "role": "system",
                "content": "You are a Beamer LaTeX expert specializing in creating professional academic presentations. Generate clean, compilable code.",
            },
            {"role": "user", "content": beamer_prompt},
        ]

        latex_code = await self.generate_response(messages, temperature=0.3)
        return self._clean_latex_code(latex_code)

    def _format_slide_plan(self, slides) -> str:
        """Format slide plan for the prompt"""
        formatted = ""
        for slide in slides:
            formatted += f"""
Slide {slide.slide_number}: {slide.title}
Type: {slide.slide_type}
Content: {slide.content}
TikZ Diagrams: {", ".join(slide.tikz_diagrams) if slide.tikz_diagrams else "None"}
Notes: {slide.notes or "None"}
---"""
        return formatted

    def _format_diagram_info(self, diagrams) -> str:
        """Format diagram information for the prompt"""
        if not diagrams:
            return "No diagrams available"

        formatted = ""
        for diagram in diagrams:
            formatted += f"""
{diagram.diagram_id}: {diagram.title}
Description: {diagram.description}
Type: {diagram.diagram_type}
---"""
        return formatted

    def _clean_latex_code(self, latex_code: str) -> str:
        """Clean and validate Beamer LaTeX code"""
        # Remove markdown code blocks if present
        latex_code = latex_code.replace("```latex", "").replace("```", "")

        # Ensure document structure
        if "\\documentclass" not in latex_code:
            latex_code = "\\documentclass{beamer}\n" + latex_code

        if "\\begin{document}" not in latex_code:
            latex_code += "\n\\begin{document}\n\\end{document}"

        return latex_code.strip()

    async def _compile_latex(self, latex_code: str, title: str) -> str:
        """Compile Beamer LaTeX to PDF"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Clean title for filename
                safe_title = "".join(
                    c for c in title if c.isalnum() or c in (" ", "-", "_")
                ).rstrip()
                safe_title = safe_title.replace(" ", "_")[:50]

                # Write LaTeX file
                tex_file = Path(temp_dir) / f"{safe_title}_presentation.tex"
                tex_file.write_text(latex_code, encoding="utf-8")

                # Compile with pdflatex (multiple passes for references)
                for _ in range(2):
                    result = subprocess.run(
                        ["pdflatex", "-interaction=nonstopmode", str(tex_file)],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        check=False,
                    )

                pdf_file = tex_file.with_suffix(".pdf")
                if pdf_file.exists():
                    # Copy to outputs directory
                    output_path = Path("outputs/presentations")
                    output_path.mkdir(exist_ok=True)

                    final_pdf = output_path / f"{safe_title}_presentation.pdf"
                    final_pdf.write_bytes(pdf_file.read_bytes())

                    return str(final_pdf)
                print(f"PDF compilation failed. LaTeX output: {result.stdout}")
                print(f"LaTeX errors: {result.stderr}")
                return None

        except Exception as e:
            print(f"Error compiling presentation: {e}")
            return None

    async def _compile_and_analyze_presentation(
        self,
        latex_code: str,
        title: str,
        plan: PresentationPlan,
    ) -> tuple[str, str]:
        """Compile presentation and analyze visual quality"""
        current_latex = latex_code
        iteration = 0

        while iteration < self.max_iterations:
            # Compile to PDF
            pdf_path = await self._compile_latex(current_latex, title)

            if not pdf_path:
                print(f"PDF compilation failed on iteration {iteration + 1}")
                break

            # Analyze at least half of the slides for comprehensive quality assessment
            print(f"Analyzing presentation quality (iteration {iteration + 1})...")

            # Calculate pages to analyze (at least half, minimum 1)
            pages_to_analyze = max(1, plan.total_slides // 2)
            if pages_to_analyze < plan.total_slides // 2:
                pages_to_analyze = plan.total_slides // 2 + 1

            print(f"Analyzing {pages_to_analyze} out of {plan.total_slides} slides...")

            # Analyze multiple slides for comprehensive assessment
            all_analyses = []
            improvement_suggestions = []
            slides_analyzed = 0
            quality_threshold = (
                0.7  # Consider presentation good if 70% of slides are good
            )

            for page_num in range(1, min(pages_to_analyze + 1, plan.total_slides + 1)):
                slide_image_path = (
                    await presentation_pdf_to_image_service.convert_pdf_to_image(
                        pdf_path,
                        page_number=page_num,
                        max_width=1024,
                    )
                )

                if slide_image_path:
                    (
                        is_good,
                        analysis,
                        improved_latex,
                    ) = await self.visual_analyzer.analyze_presentation_layout(
                        slide_image_path,
                        current_latex,
                        page_num,
                        plan.total_slides,
                    )

                    all_analyses.append((page_num, is_good, analysis))
                    if improved_latex and not is_good:
                        improvement_suggestions.append(improved_latex)

                    slides_analyzed += 1
                    print(
                        f"Slide {page_num}: {'✅ Good' if is_good else '❌ Needs improvement'}"
                    )
                else:
                    print(f"Could not generate image for slide {page_num}")

            if slides_analyzed == 0:
                print("Could not analyze any slides - using current version")
                return pdf_path, current_latex

            # Determine overall quality based on analyzed slides
            good_slides = sum(1 for _, is_good, _ in all_analyses if is_good)
            quality_ratio = good_slides / slides_analyzed

            print(
                f"Quality assessment: {good_slides}/{slides_analyzed} slides are good ({quality_ratio:.1%})"
            )

            # Consider presentation good if quality meets threshold
            if quality_ratio >= quality_threshold:
                print("Overall presentation quality is satisfactory!")
                return pdf_path, current_latex

            # Apply improvements if available and not at max iterations
            if improvement_suggestions and iteration < self.max_iterations - 1:
                print(f"Applying visual improvements (iteration {iteration + 1})...")
                # Use the most recent improvement suggestion
                current_latex = self._clean_latex_code(improvement_suggestions[-1])
                iteration += 1
            else:
                print("Max iterations reached or no improvements available.")
                return pdf_path, current_latex

        return pdf_path, current_latex

    async def create_template_variants(self, analysis: PaperAnalysis) -> dict:
        """Create presentations with different templates for comparison"""
        templates = ["academic", "corporate", "minimal"]
        presentations = {}

        for template in templates:
            print(f"Generating {template} template presentation...")
            presentation = await self.process(analysis, template_type=template)
            presentations[template] = presentation

        return presentations
