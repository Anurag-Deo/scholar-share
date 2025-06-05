import asyncio
from pathlib import Path
from typing import Optional

import gradio as gr

from app.agents.blog_generator import BlogGeneratorAgent
from app.agents.paper_analyzer import PaperAnalyzerAgent
from app.agents.poster_generator import PosterGeneratorAgent
from app.agents.tldr_generator import TLDRGeneratorAgent
from app.config.settings import settings
from app.models.schemas import PaperInput
from app.services.devto_service import devto_service
from app.services.pdf_service import pdf_service

# Initialize agents
paper_analyzer = PaperAnalyzerAgent()
blog_generator = BlogGeneratorAgent()
tldr_generator = TLDRGeneratorAgent()
poster_generator = PosterGeneratorAgent()

# Global state - Consider refactoring to avoid globals if possible
current_analysis: Optional[dict] = None
current_blog: Optional[dict] = None
current_tldr: Optional[dict] = None
current_poster: Optional[dict] = None


async def process_paper(pdf_file, url_input, text_input, progress=None):
    """Process paper from various input sources."""
    global current_analysis
    if progress is None:
        progress = gr.Progress()

    try:
        progress(0.1, desc="Processing input...")

        # Determine input source and extract content
        if pdf_file is not None:
            progress(0.2, desc="Parsing PDF...")
            # Replaced open() with Path.open() and async read
            pdf_path = Path(pdf_file.name)
            pdf_content = await asyncio.to_thread(pdf_path.read_bytes)
            # TODO: Uncomment when PDF parsing is implemented
            # parsed_data = pdf_service.parse_pdf(pdf_content)
            # content = parsed_data["text"]
            # Read the PDF content directly from file parsed_pdf_content.txt
            with open("parsed_pdf_content.txt", encoding="utf-8") as f:
                content = f.read()
            source_type = "pdf"
        elif url_input and url_input.strip():
            progress(0.2, desc="Fetching from URL...")
            parsed_data = await pdf_service.parse_url(url_input.strip())
            content = parsed_data["text"]
            source_type = "url"
        elif text_input and text_input.strip():
            content = text_input.strip()
            source_type = "text"
        else:
            return "❌ Please provide a PDF file, URL, or text input.", "", "", ""

        if not content or not content.strip():
            return "❌ No content could be extracted from the input.", "", "", ""

        # Create paper input
        paper_input = PaperInput(content=content, source_type=source_type)

        # Analyze paper
        progress(0.4, desc="Analyzing paper...")
        current_analysis = await paper_analyzer.process(paper_input)
        print(current_analysis)  # Debugging line

        # Generate preview content
        progress(0.7, desc="Generating previews...")

        analysis_summary = f"""
# Paper Analysis Summary

## **Title:** {current_analysis.title}

## **Authors:** {", ".join(current_analysis.authors)}

## **Abstract:**
{current_analysis.abstract}

## **Methodology:**
{current_analysis.methodology}

## **Key Findings:**
{chr(10).join([f"• {finding}" for finding in current_analysis.key_findings])}

## **Results:**
{current_analysis.results}

## **Conclusion:**
{current_analysis.conclusion}

## **Complexity Level:** {current_analysis.complexity_level.title()}

## **Technical Terms:**
{", ".join(current_analysis.technical_terms) if current_analysis.technical_terms else "None identified"}
        """

        progress(1.0, desc="Complete!")

        return (
            "✅ Paper processed successfully!",
            analysis_summary,
            "Ready to generate blog content",
            gr.DownloadButton(visible=True),
        )

    except Exception as e:
        # Consider more specific exception handling
        return (
            f"❌ Error processing paper: {e!s}",
            "",
            "",
            gr.DownloadButton(visible=False),
        )


async def generate_blog_content(progress=None):
    """Generate blog content from analysis."""
    global current_analysis, current_blog
    if progress is None:
        progress = gr.Progress()

    if not current_analysis:
        return "❌ Please process a paper first.", gr.update(
            visible=False,
            interactive=False,
        )

    try:
        progress(0.1, desc="Starting blog generation...")
        await asyncio.sleep(0.5)  # Give time for progress bar to show

        progress(0.3, desc="Generating blog content...")
        await asyncio.sleep(0.3)  # Allow UI to update

        current_blog = await blog_generator.process(current_analysis)

        progress(0.8, desc="Formatting blog content...")
        await asyncio.sleep(0.3)  # Allow UI to update

        blog_preview = f"""# {current_blog.title}

{current_blog.content}

**Tags:** {", ".join(current_blog.tags)}
**Reading Time:** {current_blog.reading_time} minutes"""

        progress(1.0, desc="Blog content generated!")
        return blog_preview, gr.DownloadButton(visible=True)

    except Exception as e:
        # Consider more specific exception handling
        return f"❌ Error generating blog: {e!s}", gr.DownloadButton(visible=False)


async def generate_social_content(progress=None):
    """Generate social media content from analysis."""
    global current_analysis, current_tldr
    if progress is None:
        progress = gr.Progress()

    if not current_analysis:
        return "❌ Please process a paper first.", "", "", ""

    try:
        progress(0.3, desc="Generating social media content...")
        current_tldr = await tldr_generator.process(current_analysis)

        progress(1.0, desc="Social content generated!")

        return (
            current_tldr.linkedin_post,
            "\n\n".join(
                [
                    f"Tweet {i + 1}: {tweet}"
                    for i, tweet in enumerate(current_tldr.twitter_thread)
                ],
            ),
            current_tldr.facebook_post,
            current_tldr.instagram_caption,
        )

    except Exception as e:
        # Consider more specific exception handling
        error_msg = f"❌ Error generating social content: {e!s}"
        return error_msg, error_msg, error_msg, error_msg


async def generate_poster_content(template_type, progress=None):
    """Generate poster content from analysis."""
    global current_analysis, current_poster
    if progress is None:
        progress = gr.Progress()

    if not current_analysis:
        return "❌ Please process a paper first.", ""

    try:
        progress(0.3, desc="Generating poster...")
        current_poster = await poster_generator.process(current_analysis, template_type)

        progress(0.8, desc="Compiling LaTeX...")

        poster_info = f"""
        **Poster Generated Successfully!**
        
        **Template:** {template_type.upper()}
        **PDF Path:** {current_poster.pdf_path if current_poster.pdf_path else "Compilation in progress..."}
        
        **LaTeX Code Preview:**
        ```
        {current_poster.latex_code[:300]}...
        ```
        """

        progress(1.0, desc="Poster ready!")
        return poster_info, current_poster.latex_code

    except Exception as e:
        # Consider more specific exception handling
        return f"❌ Error generating poster: {e!s}", ""


async def publish_to_devto(publish_now):
    """Publish blog content to DEV.to."""
    global current_blog

    if not current_blog:
        return "❌ Please generate blog content first."

    try:
        result = await devto_service.publish_article(current_blog, publish_now)

        if result["success"]:
            status = "Published" if result.get("published") else "Saved as Draft"
            return f"✅ Article {status} successfully!\nURL: {result.get('url', 'N/A')}"
        # Removed unnecessary else
        return f"❌ Publication failed: {result.get('error', 'Unknown error')}"

    except Exception as e:
        # Consider more specific exception handling
        return f"❌ Error publishing to DEV.to: {e!s}"


def publish_draft():
    """Sync wrapper for publishing as draft."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create a task
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, publish_to_devto(False))
                return future.result()
        else:
            return loop.run_until_complete(publish_to_devto(False))
    except RuntimeError:
        # If no event loop, create one
        return asyncio.run(publish_to_devto(False))


def publish_now():
    """Sync wrapper for publishing immediately."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create a task
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, publish_to_devto(True))
                return future.result()
        else:
            return loop.run_until_complete(publish_to_devto(True))
    except RuntimeError:
        # If no event loop, create one
        return asyncio.run(publish_to_devto(True))


async def download_analysis_summary():
    """Generate downloadable analysis summary as markdown file."""
    global current_analysis

    if not current_analysis:
        return None

    try:
        # Create comprehensive analysis summary
        markdown_content = f"""# Paper Analysis Summary

## Title
{current_analysis.title}

## Authors
{", ".join(current_analysis.authors)}

## Abstract
{current_analysis.abstract}

## Methodology
{current_analysis.methodology}

## Key Findings
{chr(10).join([f"- {finding}" for finding in current_analysis.key_findings])}

## Results
{current_analysis.results}

## Conclusion
{current_analysis.conclusion}

## Complexity Level
{current_analysis.complexity_level.title()}

## Technical Terms
{", ".join(current_analysis.technical_terms) if current_analysis.technical_terms else "None identified"}

## Figures and Tables
{chr(10).join([f"- {fig.get('description', 'Figure/Table')}: {fig.get('caption', 'No caption')}" for fig in current_analysis.figures_tables]) if current_analysis.figures_tables else "None identified"}

---
*Generated by ScholarShare - AI Research Dissemination Platform*
"""

        # Save to outputs directory
        output_path = Path("outputs/analysis_summary.md")
        output_path.write_text(markdown_content, encoding="utf-8")

        return str(output_path)

    except Exception:
        return None


async def download_blog_markdown():
    """Generate downloadable blog content as markdown file."""
    if not current_blog:
        return None

    try:
        # Create comprehensive blog markdown
        markdown_content = f"""# {current_blog.title}

{current_blog.content}

---

**Tags:** {", ".join(current_blog.tags)}
**Reading Time:** {current_blog.reading_time} minutes
**Meta Description:** {current_blog.meta_description}

---
*Generated by ScholarShare - AI Research Dissemination Platform*
"""

        # Save to outputs directory
        output_path = Path("outputs/blogs/blog_content.md")
        output_path.write_text(markdown_content, encoding="utf-8")

        return str(output_path)

    except OSError:
        return None


# Create Gradio Interface
def create_interface():
    with gr.Blocks(
        title="ScholarShare - AI Research Dissemination",
        theme=gr.themes.Soft(),
    ) as app:
        gr.Markdown("""
        # 🎓 ScholarShare - AI-Powered Research Dissemination Platform
        
        Transform complex research papers into accessible, multi-format content for broader audience engagement.
        """)

        with gr.Tab("📄 Paper Input & Analysis"):
            gr.Markdown("## Upload and Analyze Research Paper")

            with gr.Row():
                with gr.Column():
                    pdf_input = gr.File(
                        label="Upload PDF Paper",
                        file_types=[".pdf"],
                        type="filepath",
                    )
                    url_input = gr.Textbox(
                        label="Or Enter Paper URL (arXiv, etc.)",
                        placeholder="https://arxiv.org/pdf/...",
                    )
                    text_input = gr.Textbox(
                        label="Or Paste Paper Text",
                        lines=5,
                        placeholder="Paste your research paper content here...",
                    )

                    process_btn = gr.Button("🔍 Analyze Paper", variant="primary")

                with gr.Column():
                    status_output = gr.Textbox(label="Status", interactive=False)
                    analysis_output = gr.Markdown(
                        label="Paper Analysis",
                        max_height=400,
                        show_copy_button=True,
                    )
                    download_analysis_btn = gr.DownloadButton(
                        label="📥 Download Analysis as Markdown",
                        visible=False,
                    )

        with gr.Tab("📝 Blog Generation"):
            gr.Markdown("## Generate Beginner-Friendly Blog Content")

            with gr.Row():
                with gr.Column():
                    blog_status = gr.Textbox(label="Blog Status", interactive=False)
                    generate_blog_btn = gr.Button(
                        "✍️ Generate Blog Content",
                        variant="primary",
                    )
                    download_blog_btn = gr.DownloadButton(
                        label="📥 Download Blog as Markdown",
                        visible=False,  # Changed from True to False initially
                    )

                with gr.Column():
                    blog_output = gr.Markdown(
                        label="Generated Blog Content",
                        max_height=400,
                        show_copy_button=True,
                    )

        with gr.Tab("📱 Social Media Content"):
            gr.Markdown("## Generate Platform-Specific Social Media Content")

            with gr.Row():
                generate_social_btn = gr.Button(
                    "📱 Generate Social Content",
                    variant="primary",
                )

            with gr.Row():
                with gr.Column():
                    linkedin_output = gr.Textbox(label="LinkedIn Post", lines=5)
                    twitter_output = gr.Textbox(label="Twitter Thread", lines=5)

                with gr.Column():
                    facebook_output = gr.Textbox(label="Facebook Post", lines=5)
                    instagram_output = gr.Textbox(label="Instagram Caption", lines=5)

        with gr.Tab("🎨 Poster Generation"):
            gr.Markdown("## Generate Academic Conference Poster")

            with gr.Row():
                with gr.Column():
                    template_dropdown = gr.Dropdown(
                        choices=["ieee", "acm", "nature"],
                        value="ieee",
                        label="Poster Template Style",
                    )
                    generate_poster_btn = gr.Button(
                        "🎨 Generate Poster",
                        variant="primary",
                    )

                with gr.Column():
                    poster_output = gr.Markdown(label="Poster Information")

            with gr.Row():
                latex_output = gr.Code(label="LaTeX Code", language="latex")

        with gr.Tab("🚀 Publishing"):
            gr.Markdown("## Publish Content to Platforms")

            with gr.Column():
                gr.Markdown("### DEV.to Publishing")
                with gr.Row():
                    publish_draft_btn = gr.Button("💾 Save as Draft")
                    publish_now_btn = gr.Button("🚀 Publish Now", variant="primary")

                publish_status = gr.Textbox(
                    label="Publishing Status",
                    interactive=False,
                )

        # Event handlers
        process_btn.click(
            fn=process_paper,
            inputs=[pdf_input, url_input, text_input],
            outputs=[
                status_output,
                analysis_output,
                blog_status,
                download_analysis_btn,
            ],
        )

        download_analysis_btn.click(
            fn=download_analysis_summary,
            outputs=[download_analysis_btn],
        )

        generate_blog_btn.click(
            fn=generate_blog_content,
            outputs=[blog_output, download_blog_btn],
        )

        download_blog_btn.click(
            fn=download_blog_markdown,
            outputs=[download_blog_btn],
        )

        generate_social_btn.click(
            fn=generate_social_content,
            outputs=[
                linkedin_output,
                twitter_output,
                facebook_output,
                instagram_output,
            ],
        )

        generate_poster_btn.click(
            fn=generate_poster_content,
            inputs=[template_dropdown],
            outputs=[poster_output, latex_output],
        )

        publish_draft_btn.click(
            fn=publish_draft,
            outputs=[publish_status],
        )

        publish_now_btn.click(
            fn=publish_now,
            outputs=[publish_status],
        )

    return app


if __name__ == "__main__":
    # Create output directories using pathlib
    Path("outputs/posters").mkdir(parents=True, exist_ok=True)
    Path("outputs/blogs").mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(parents=True, exist_ok=True)

    # Launch the application
    app_instance = create_interface()
    app_instance.launch(
        server_name=settings.HOST,
        server_port=settings.PORT,
        debug=settings.DEBUG,
        share=False,
    )
