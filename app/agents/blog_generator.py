from app.agents.base_agent import BaseAgent
from app.models.schemas import BlogContent, PaperAnalysis


class BlogGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("BlogGenerator", model_type="heavy")

    async def process(self, analysis: PaperAnalysis) -> BlogContent:
        """Generate beginner-friendly blog content from paper analysis"""
        blog_prompt = f"""
        You are an expert computer scientist specializes in the area of machine learning. Transform this research paper analysis into an engaging, highly technical yet beginner-friendly blog post.

        Paper Analysis:
        Title: {analysis.title}
        Authors: {", ".join(analysis.authors)}
        Abstract: {analysis.abstract}
        Key Findings: {", ".join(analysis.key_findings)}
        Methodology: {analysis.methodology}
        Results: {analysis.results}
        Conclusion: {analysis.conclusion}
        Complexity Level: {analysis.complexity_level}

        Create a blog post that:
        1. Use technical language and explain complex concepts in simple terms
        2. Uses analogies to explain technical terms
        3. Has an engaging introduction that hooks the reader
        4. Clearly explains the significance of the research
        5. Includes practical implications of the findings
        6. Is optimized for SEO with proper structure and headings
        7. Must explain the key findings and methodology in great detail.
        8. Use markdown formatting for code snippets, equations, and figures

        Structure the blog post with:
        - Catchy title
        - Engaging introduction
        - Main sections with clear headings
        - Conclusion with key takeaways
        - Suggested tags for DEV.to

        Make it interesting for a general audience while maintaining scientific accuracy.
        Don't include any other information except the blog post content. No additional headers or ending text in the response.
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert computer scientist expert in machine learning and artificial intelligence also you are expert in blog writing, who excels at making complex research accessible to everyone.",
            },
            {"role": "user", "content": blog_prompt},
        ]

        response = await self.generate_response(messages, temperature=0.7)

        # Extract title, content, and tags
        title = self._extract_title(response)
        content = self._clean_content(response)
        tags = self._extract_tags(response, analysis)
        meta_description = self._generate_meta_description(analysis)
        reading_time = self._calculate_reading_time(content)

        return BlogContent(
            title=title,
            content=content,
            tags=tags,
            meta_description=meta_description,
            reading_time=reading_time,
        )

    def _extract_title(self, content: str) -> str:
        """Extract title from blog content"""
        lines = content.split("\n")
        for line in lines:
            if line.strip().startswith("#") and not line.strip().startswith("##"):
                return line.strip().replace("#", "").strip()
        return "Research Insights: Latest Findings"

    def _clean_content(self, content: str) -> str:
        """Clean and format blog content"""
        # Remove title from content if it's duplicated
        lines = content.split("\n")
        cleaned_lines = []
        title_found = False

        for line in lines:
            if (
                line.strip().startswith("#")
                and not line.strip().startswith("##")
                and not title_found
            ):
                title_found = True
                continue
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

    def _extract_tags(self, content: str, analysis: PaperAnalysis) -> list:
        """Extract relevant tags for the blog post"""
        base_tags = ["research", "science", "academic"]

        # Add complexity-based tags
        if analysis.complexity_level == "beginner":
            base_tags.extend(["beginners", "explained"])
        elif analysis.complexity_level == "advanced":
            base_tags.extend(["advanced", "technical"])

        # Add field-specific tags based on content
        content_lower = content.lower()
        field_tags = {
            "ai": ["ai", "machinelearning", "artificialintelligence", "deeplearning", "neuralnetworks", "automation", "computervision", "nlp", "generativeai"],
            "machine learning": ["machinelearning", "ml", "datascience", "supervisedlearning", "unsupervisedlearning", "reinforcementlearning", "featureengineering", "modeloptimization"],
            "computer science": ["computerscience", "programming", "technology", "softwareengineering", "algorithms", "datastructures", "computationaltheory", "systemsdesign"],
            "data science": ["datascience", "bigdata", "datamining", "datavisualization", "statistics", "predictiveanalytics", "dataengineering"],
            "cybersecurity": ["cybersecurity", "infosec", "ethicalhacking", "cryptography", "networksecurity", "applicationsecurity", "securityengineering"],
            "software development": ["softwaredevelopment", "coding", "devops", "agile", "testing", "debugging", "versioncontrol", "softwarearchitecture"],
            "cloud computing": ["cloudcomputing", "aws", "azure", "googlecloud", "serverless", "containers", "kubernetes", "cloudsecurity"],
        }

        for field, tags in field_tags.items():
            if field in content_lower:
                base_tags.extend(tags[:2])
                break

        return list(set(base_tags))[:10]  # Limit to 10 tags

    def _generate_meta_description(self, analysis: PaperAnalysis) -> str:
        """Generate SEO meta description"""
        if analysis.key_findings:
            finding = analysis.key_findings[0]
            return f"Discover how {finding[:100]}... Latest research insights explained in simple terms."
        return f"Explore the latest research findings from {analysis.title[:50]}... explained for everyone."

    def _calculate_reading_time(self, content: str) -> int:
        """Calculate estimated reading time in minutes"""
        word_count = len(content.split())
        return max(1, word_count // 200)  # Assuming 200 words per minute
