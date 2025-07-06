from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

# --- FIX: Import the BaseAgent to inherit from it ---
from app.agents.base_agent import BaseAgent
from app.services.html_export_service import html_export_service
from app.models.schemas import PaperAnalysis, PresentationOutput

# Define the directory for presentation templates
TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "presentation_templates"

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=select_autoescape(["html"])
)


# --- FIX: Inherit from BaseAgent ---
class PresentationGeneratorAgent(BaseAgent):
    """
    An agent that generates a presentation from a paper analysis.
    It prompts an LLM to create HTML slides and then uses services
    to export the final presentation to PDF and PPTX formats.
    """

    def __init__(self):
        super().__init__("PresentationGenerator", model_type="heavy")

    async def process(
        self,
        analysis: PaperAnalysis,
        template_type: str = "base_theme",
        max_slides: int = 12,
    ) -> PresentationOutput:
        # 1. Prompt the LLM for RAW slide markup using a detailed instruction set.
        prompt = f"""
You are an expert slide-deck designer using Reveal.js.
Your task is to create the raw HTML for a slide presentation based on the provided paper data.

Theme constraints (already defined in CSS – DO NOT restate):
  – brand primary colour  : #004d99
  – brand accent colour   : #ffa726
  – heading / body fonts  : Inter, sans-serif

Your response must contain ONLY the HTML <section> blocks. Do not include <html>, <head>, or <body> tags.

RULES:
1. Produce at most {max_slides} <section> blocks.
2. The first slide must have `data-layout="cover"` and prominently feature the paper's title and authors.
3. All subsequent slides must start with an `<h2>` heading.
4. Use `<ul>` and `<li>` for bullet points. Limit bullet points to a maximum of 6 per slide.

PAPER DATA:
- Title: {analysis.title}
- Authors: {", ".join(analysis.authors)}
- Abstract: {analysis.abstract}
- Key Findings: {", ".join(analysis.key_findings)}
- Methodology: {analysis.methodology}
- Results: {analysis.results}
- Conclusion: {analysis.conclusion}
"""
        # --- FIX: Use the inherited self.generate_response() method ---
        # This is the correct, standardized way to call the LLM within an agent.
        messages = [
            {
                "role": "system",
                "content": "You are an expert slide-deck designer using Reveal.js. Your task is to create the raw HTML for a slide presentation based on the provided paper data.",
            },
            {"role": "user", "content": prompt},
        ]
        raw_sections = await self.generate_response(
            messages,
            # model_type="heavy",  # Using a powerful model for creative content generation
            temperature=0.7,
            # max_tokens=4000,
        )

        # 2. Inject the generated HTML sections into the base theme template.
        tpl = env.get_template("base_theme.html")
        html_code = tpl.render(title=analysis.title, content=raw_sections)

        # 3. Define output paths and ensure the directory exists.
        out_dir = Path("outputs/presentations")
        out_dir.mkdir(parents=True, exist_ok=True)
        html_path = out_dir / "presentation.html"
        html_path.write_text(html_code, encoding="utf-8")

        # 4. Use the export service to convert the final HTML to PDF and PPTX.
        pdf_path = out_dir / "presentation.pdf"
        ppt_path = out_dir / "presentation.pptx"
        await html_export_service.html_to_pdf(html_path, pdf_path)
        await html_export_service.html_to_ppt(html_path, ppt_path)

        # 5. Return all relevant paths and the generated HTML code.
        return PresentationOutput(
            html_code=html_code,
            html_path=html_path,
            pdf_path=pdf_path,
            ppt_path=ppt_path,
        )
    

# TODO: Currently the HTML is contaning &lt; and &gt; instead of < and >. This is because the LLM is generating HTML entities instead of raw HTML.
