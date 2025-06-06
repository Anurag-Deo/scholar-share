from app.agents.base_agent import BaseAgent
from app.models.schemas import PaperAnalysis, TikzDiagram


class TikzDiagramAgent(BaseAgent):
    """Agent to create TikZ-based diagrams and infographics for presentations"""

    def __init__(self):
        super().__init__("TikzDiagramGenerator", model_type="coding")

    async def process(
        self, diagram_descriptions: list[str], analysis: PaperAnalysis
    ) -> list[TikzDiagram]:
        """Generate TikZ diagrams based on descriptions and paper content"""
        diagrams = []
        for i, description in enumerate(diagram_descriptions):
            diagram = await self._create_single_diagram(description, analysis, i + 1)
            if diagram:
                diagrams.append(diagram)

        return diagrams

    async def _create_single_diagram(
        self, description: str, analysis: PaperAnalysis, diagram_num: int
    ) -> TikzDiagram:
        """Create a single TikZ diagram"""
        tikz_prompt = f"""
        Create a TikZ diagram for a research presentation based on this description and paper content.

        Diagram Description: {description}

        Paper Context:
        Title: {analysis.title}
        Methodology: {analysis.methodology}
        Key Findings: {", ".join(analysis.key_findings)}
        Results: {analysis.results}
        Technical Terms: {", ".join(analysis.technical_terms)}

        Generate clean, professional TikZ code that:
        1. Is suitable for academic presentations
        2. Uses appropriate colors and styling
        3. Is well-commented for clarity
        4. Fits within slide dimensions
        5. Uses clear, readable fonts
        6. Follows TikZ best practices

        Common diagram types to consider:
        - Flowcharts for processes/methodology
        - Block diagrams for system architecture  
        - Graphs and charts for data visualization
        - Timeline diagrams for sequential processes
        - Comparison diagrams for before/after scenarios
        - Network diagrams for connections/relationships

        Provide ONLY the TikZ code within a tikzpicture environment, without document structure.
        Use appropriate TikZ libraries like shapes, arrows, positioning, etc.

        Example format:
        \\begin{{tikzpicture}}[node distance=2cm, auto]
        % Your TikZ code here
        \\end{{tikzpicture}}

        Make the diagram informative, visually appealing, and directly relevant to the research content.
        """

        messages = [
            {
                "role": "system",
                "content": "You are a TikZ expert specializing in creating academic diagrams and visualizations. Generate clean, professional TikZ code.",
            },
            {"role": "user", "content": tikz_prompt},
        ]

        response = await self.generate_response(messages, temperature=0.3)

        # Clean the TikZ code
        tikz_code = self._clean_tikz_code(response)

        # Determine diagram type from description
        diagram_type = self._determine_diagram_type(description)

        return TikzDiagram(
            diagram_id=f"diagram_{diagram_num}",
            title=f"Diagram {diagram_num}",
            description=description,
            tikz_code=tikz_code,
            diagram_type=diagram_type,
        )

    def _clean_tikz_code(self, code: str) -> str:
        """Clean and validate TikZ code"""
        # Remove markdown code blocks if present
        code = code.replace("```latex", "").replace("```tikz", "").replace("```", "")

        # Ensure tikzpicture environment
        if "\\begin{tikzpicture}" not in code:
            # Wrap content in tikzpicture if not present
            code = f"\\begin{{tikzpicture}}[node distance=2cm, auto]\n{code}\n\\end{{tikzpicture}}"

        return code.strip()

    def _determine_diagram_type(self, description: str) -> str:
        """Determine diagram type from description"""
        description_lower = description.lower()

        if any(
            word in description_lower
            for word in ["flow", "process", "step", "workflow"]
        ):
            return "flowchart"
        if any(
            word in description_lower
            for word in ["architecture", "system", "structure", "framework"]
        ):
            return "architecture"
        if any(
            word in description_lower
            for word in ["timeline", "sequence", "chronological", "time"]
        ):
            return "timeline"
        if any(
            word in description_lower
            for word in ["comparison", "vs", "versus", "compare", "before", "after"]
        ):
            return "comparison"
        if any(
            word in description_lower
            for word in ["graph", "chart", "plot", "data", "statistics"]
        ):
            return "graph"
        if any(
            word in description_lower
            for word in ["network", "connection", "relationship", "link"]
        ):
            return "network"
        return "general"

    async def create_methodology_flowchart(
        self, analysis: PaperAnalysis
    ) -> TikzDiagram:
        """Create a specific methodology flowchart"""
        return await self._create_single_diagram(
            f"Methodology flowchart showing the research process: {analysis.methodology}",
            analysis,
            1,
        )

    async def create_results_comparison(self, analysis: PaperAnalysis) -> TikzDiagram:
        """Create a results comparison diagram"""
        return await self._create_single_diagram(
            f"Results comparison chart based on: {analysis.results}",
            analysis,
            2,
        )

    async def create_architecture_diagram(self, analysis: PaperAnalysis) -> TikzDiagram:
        """Create a system architecture diagram"""
        return await self._create_single_diagram(
            f"System architecture diagram for the proposed approach in: {analysis.methodology}",
            analysis,
            3,
        )
