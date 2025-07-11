import os
import subprocess
import tempfile

from app.agents.base_agent import BaseAgent
from app.agents.poster_layout_analyzer import PosterLayoutAnalyzerAgent
from app.models.schemas import PaperAnalysis, PosterContent
from app.services.pdf_to_image_service import pdf_to_image_service


class PosterGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("PosterGenerator", model_type="coding")
        self.template_dir = "app/templates/poster_templates"
        self.layout_analyzer = PosterLayoutAnalyzerAgent()
        self.max_fix_attempts = 2  # Maximum attempts to fix layout issues

    async def process(
        self,
        analysis: PaperAnalysis,
        template_type: str = "ieee",
        orientation: str = "landscape",
    ) -> PosterContent:
        """Generate academic conference poster"""
        # tikzdocumentation
        tikzdocumentation = ""
        with open(
            os.path.join(self.template_dir, "tikzposter.md"),
            encoding="utf-8",
        ) as f:
            tikzdocumentation = f.read()
        # Generate LaTeX content
        latex_prompt = f"""
        Generate LaTeX code for an academic conference poster using the {template_type} style.
        The poster should be suitable for a {orientation} orientation and include the following sections:
        
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
        Use the tikzposter package for a modern academic poster design.
        The poster should be structured with clear sections and headings.
        Poster should be aesthetically pleasing with good theme and color choices. Given the documentation below, try to make the poster visually appealing and professional.
        MAKE SURE THAT NONE OF THE SECTIONS ARE EMPTY OR MISSING OR GOES OUT OF THE POSTER.
        For you reference here is the documentation for the tikzposter package:
        {tikzdocumentation}
        
        Make sure you give your ouptut just a tex code block starting with ```latex and ending with ```.
        Do not include any other text or explanations.
        Here is an example of a simple poster template:
        ```latex
        # Your code goes here
        ```

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

        # Compile to PDF and analyze layout
        pdf_path, final_latex_code = await self._compile_and_analyze_poster(
            latex_code,
            analysis.title,
            analysis,
        )

        return PosterContent(
            template_type=template_type,
            title=analysis.title,
            authors=", ".join(analysis.authors),
            abstract=analysis.abstract,
            methodology=analysis.methodology,
            results=analysis.results,
            conclusion=analysis.conclusion,
            figures=[],  # Will be populated if figures are detected
            latex_code=final_latex_code,
            pdf_path=pdf_path,
        )

    def _clean_latex_code(self, latex_code: str) -> str:
        """Clean and validate LaTeX code"""
        # Remove markdown code block markers if present
        latex_code = latex_code.replace("```latex", "").replace("```", "")

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

    async def _compile_and_analyze_poster(
        self,
        latex_code: str,
        title: str,
        analysis: PaperAnalysis,
    ) -> tuple[str, str]:
        """
        Compile LaTeX to PDF and analyze layout, fixing issues if needed.

        Returns:
            tuple: (pdf_path, final_latex_code)

        """
        current_latex = latex_code
        attempt = 0

        while attempt <= self.max_fix_attempts:
            # Compile to PDF
            pdf_path = await self._compile_latex(current_latex, title)

            if not pdf_path:
                print(f"PDF compilation failed on attempt {attempt + 1}")
                break

            # Convert PDF to image for analysis (optimized resolution for vision model)
            poster_image_path = await pdf_to_image_service.convert_pdf_to_image(
                pdf_path,
                max_width=800,  # Optimized for vision model token costs
            )

            if not poster_image_path:
                print("Could not convert PDF to image for analysis")
                return pdf_path, current_latex

            # Analyze poster layout
            (
                fits_properly,
                analysis_message,
                fixed_latex,
            ) = await self.layout_analyzer.analyze_poster_layout(
                poster_image_path,
                current_latex,
                title,
            )

            print(f"Poster layout analysis (attempt {attempt + 1}): {analysis_message}")

            if fits_properly:
                print("Poster layout is satisfactory!")
                return pdf_path, current_latex

            if fixed_latex and attempt < self.max_fix_attempts:
                print(f"Applying layout fixes (attempt {attempt + 1})...")
                current_latex = self._clean_latex_code(fixed_latex)
                attempt += 1
            else:
                print(
                    "Max fix attempts reached or no fix available. Using current version.",
                )
                return pdf_path, current_latex

        # If we reach here, return the last attempt
        return pdf_path, current_latex
