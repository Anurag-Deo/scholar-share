import os
import subprocess
import tempfile

from app.agents.base_agent import BaseAgent
from app.models.schemas import PaperAnalysis, PosterContent


class PosterGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("PosterGenerator", model_type="heavy")
        self.template_dir = "app/templates/poster_templates"

    async def process(
        self, analysis: PaperAnalysis, template_type: str = "ieee"
    ) -> PosterContent:
        """Generate academic conference poster"""
        # Generate LaTeX content
        latex_prompt = f"""
        Generate LaTeX code for an academic conference poster using the {template_type} style.
        
        Paper Details:
        Title: {analysis.title}
        Authors: {", ".join(analysis.authors)}
        Abstract: {analysis.abstract}
        Methodology: {analysis.methodology}
        Results: {analysis.results}
        Conclusion: {analysis.conclusion}
        Key Findings: {", ".join(analysis.key_findings)}
        
        Requirements:
        - Use tikzposter or beamerposter package
        - Professional academic layout
        - Clear sections: Abstract, Methodology, Results, Conclusion
        - Include space for figures/tables
        - Use appropriate fonts and colors for {template_type} style
        - Make it visually appealing and readable
        
        Generate complete LaTeX code that can be compiled directly.
        """

        messages = [
            {
                "role": "system",
                "content": "You are a LaTeX expert specializing in academic poster design. Generate clean, compilable LaTeX code.",
            },
            {"role": "user", "content": latex_prompt},
        ]

        latex_code = await self.generate_response(messages, temperature=0.3)
        latex_code = self._clean_latex_code(latex_code)

        # Compile to PDF
        pdf_path = await self._compile_latex(latex_code, analysis.title)

        return PosterContent(
            template_type=template_type,
            title=analysis.title,
            authors=", ".join(analysis.authors),
            abstract=analysis.abstract,
            methodology=analysis.methodology,
            results=analysis.results,
            conclusion=analysis.conclusion,
            figures=[],  # Will be populated if figures are detected
            latex_code=latex_code,
            pdf_path=pdf_path,
        )

    def _clean_latex_code(self, latex_code: str) -> str:
        """Clean and validate LaTeX code"""
        # Remove markdown code block markers if present
        latex_code = latex_code.replace("```", "")

        # Ensure document structure
        if "\\documentclass" not in latex_code:
            latex_code = "\\documentclass[a0paper,portrait]{tikzposter}\n" + latex_code

        if "\\begin{document}" not in latex_code:
            latex_code += "\n\\begin{document}\n\\maketitle\n\\end{document}"

        return latex_code.strip()

    async def _compile_latex(self, latex_code: str, title: str) -> str:
        """Compile LaTeX to PDF"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create LaTeX file
                tex_file = os.path.join(temp_dir, "poster.tex")
                with open(tex_file, "w", encoding="utf-8") as f:
                    f.write(latex_code)

                # Compile with pdflatex
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "poster.tex"],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                pdf_file = os.path.join(temp_dir, "poster.pdf")

                if os.path.exists(pdf_file):
                    # Move to outputs directory
                    output_dir = "outputs/posters"
                    os.makedirs(output_dir, exist_ok=True)

                    safe_title = "".join(
                        c for c in title if c.isalnum() or c in (" ", "-", "_")
                    ).rstrip()
                    output_path = os.path.join(output_dir, f"{safe_title}_poster.pdf")

                    import shutil

                    shutil.copy2(pdf_file, output_path)
                    return output_path
                # Compilation failed, try with simpler template
                return await self._generate_fallback_poster(latex_code, title)

        except Exception as e:
            print(f"LaTeX compilation error: {e}")
            return await self._generate_fallback_poster(latex_code, title)

    async def _generate_fallback_poster(self, latex_code: str, title: str) -> str:
        """Generate a simple fallback poster if LaTeX compilation fails"""
        try:
            # Create a simple HTML poster as fallback
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .poster {{ width: 800px; margin: 0 auto; }}
                    .title {{ font-size: 24px; font-weight: bold; text-align: center; margin-bottom: 20px; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ccc; }}
                    .section h3 {{ color: #333; }}
                </style>
            </head>
            <body>
                <div class="poster">
                    <div class="title">{title}</div>
                    <div class="section">
                        <h3>LaTeX Code Generated</h3>
                        <pre>{latex_code[:500]}...</pre>
                    </div>
                    <div class="section">
                        <p>Note: PDF compilation failed. LaTeX code is available for manual compilation.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            output_dir = "outputs/posters"
            os.makedirs(output_dir, exist_ok=True)

            safe_title = "".join(
                c for c in title if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            output_path = os.path.join(output_dir, f"{safe_title}_poster.html")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return output_path

        except Exception as e:
            print(f"Fallback poster generation error: {e}")
            return "outputs/posters/poster_generation_failed.txt"
