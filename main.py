import asyncio
from pathlib import Path

import gradio as gr
from gradio_pdf import PDF

from app.agents.blog_generator import BlogGeneratorAgent
from app.agents.paper_analyzer import PaperAnalyzerAgent
from app.agents.poster_generator import PosterGeneratorAgent
from app.agents.presentation_generator import PresentationGeneratorAgent
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
presentation_generator = PresentationGeneratorAgent()

# Global state - Consider refactoring to avoid globals if possible
current_analysis: dict | None = None
current_blog: dict | None = None
current_tldr: dict | None = None
current_poster: dict | None = None
current_presentation: dict | None = None


async def process_paper(pdf_file, url_input, progress=None):
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
            parsed_data = pdf_service.parse_pdf(pdf_content)
            content = parsed_data["text"]
            # Read the PDF content directly from file parsed_pdf_content.txt
            # with open("parsed_pdf_content.txt", encoding="utf-8") as f:
            #     content = f.read()
            source_type = "pdf"
        elif url_input and url_input.strip():
            progress(0.2, desc="Fetching from URL...")
            parsed_data = pdf_service.parse_url(url_input.strip())
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
        return (
            "❌ Please process a paper first.",
            "",
            gr.DownloadButton(visible=False),
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
        return (
            "✅ Blog content generated successfully!",
            blog_preview,
            gr.DownloadButton(visible=True),
        )

    except Exception as e:
        # Consider more specific exception handling
        return (
            f"❌ Error generating blog: {e!s}",
            "",
            gr.DownloadButton(visible=False),
        )


async def generate_social_content(progress=None):
    """Generate social media content from analysis."""
    global current_analysis, current_tldr
    if progress is None:
        progress = gr.Progress()

    if not current_analysis:
        return "❌ Please process a paper first.", "", "", "", None, None, None, None

    try:
        progress(0.3, desc="Generating social media content...")
        current_tldr = await tldr_generator.process(current_analysis)

        progress(1.0, desc="Social content generated!")

        # Prepare image updates - show image if available, hide if not
        linkedin_img_update = gr.Image(
            value=current_tldr.linkedin_image,
            visible=bool(current_tldr.linkedin_image),
        )
        twitter_img_update = gr.Image(
            value=current_tldr.twitter_image,
            visible=bool(current_tldr.twitter_image),
        )
        facebook_img_update = gr.Image(
            value=current_tldr.facebook_image,
            visible=bool(current_tldr.facebook_image),
        )
        instagram_img_update = gr.Image(
            value=current_tldr.instagram_image,
            visible=bool(current_tldr.instagram_image),
        )

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
            linkedin_img_update,
            twitter_img_update,
            facebook_img_update,
            instagram_img_update,
        )

    except Exception as e:
        # Consider more specific exception handling
        error_msg = f"❌ Error generating social content: {e!s}"
        hidden_img = gr.Image(visible=False)
        return (
            error_msg,
            error_msg,
            error_msg,
            error_msg,
            hidden_img,
            hidden_img,
            hidden_img,
            hidden_img,
        )


async def generate_poster_content(template_type, orientation, progress=None):
    """Generate poster content from analysis."""
    global current_analysis, current_poster
    if progress is None:
        progress = gr.Progress()

    if not current_analysis:
        return (
            "❌ Please process a paper first.",
            "",  # For latex_output
            PDF(visible=False),  # For poster_pdf_preview
            gr.DownloadButton(visible=False),  # For download_pdf_btn
            gr.DownloadButton(visible=False),  # For download_latex_btn
        )

    try:
        progress(0.3, desc="Generating poster...")
        current_poster = await poster_generator.process(
            current_analysis,
            template_type,
            orientation,
        )

        progress(0.8, desc="Compiling LaTeX...")

        # Initialize updates for PDF preview and download button
        pdf_preview_update = PDF(visible=False)
        pdf_download_btn_update = gr.DownloadButton(visible=False)

        if current_poster.pdf_path and Path(current_poster.pdf_path).exists():
            pdf_path_str = str(current_poster.pdf_path)
            pdf_preview_update = PDF(
                value=pdf_path_str,
                visible=True,
                label="Generated Poster PDF",
                # height=700 # Optional: Match height if set in create_interface
            )
            pdf_download_btn_update = gr.DownloadButton(
                label="📥 Download PDF",
                value=pdf_path_str,
                visible=True,
            )

        # Get LaTeX download button update
        latex_download_btn_update = (
            await download_latex_code()
        )  # This function already returns a DownloadButton update

        progress(1.0, desc="Poster ready!")
        return (
            "✅ Poster generated successfully!",  # For poster_status
            current_poster.latex_code,  # For latex_output (string updates gr.Code value)
            pdf_preview_update,  # For poster_pdf_preview (PDF component update)
            pdf_download_btn_update,  # For download_pdf_btn (DownloadButton component update)
            latex_download_btn_update,  # For download_latex_btn (DownloadButton component update)
        )

    except Exception as e:
        return (
            f"❌ Error generating poster: {e!s}",
            "",  # For latex_output
            PDF(visible=False),  # For poster_pdf_preview
            gr.DownloadButton(visible=False),  # For download_pdf_btn
            gr.DownloadButton(visible=False),  # For download_latex_btn
        )


async def generate_presentation_content(template_type, slide_count, progress=None):
    """Generate presentation content from analysis."""
    global current_analysis, current_presentation
    if progress is None:
        progress = gr.Progress()

    if not current_analysis:
        return (
            "❌ Please process a paper first.",
            "",  # For beamer_output
            PDF(visible=False),  # For presentation_pdf_preview
            gr.DownloadButton(visible=False),  # For download_presentation_pdf_btn
            gr.DownloadButton(visible=False),  # For download_beamer_btn
        )

    try:
        progress(0.2, desc="Planning presentation structure...")

        # Generate presentation using the PresentationGeneratorAgent
        current_presentation = await presentation_generator.process(
            current_analysis,
            template_type=template_type,
            max_slides=slide_count,
        )

        progress(0.8, desc="Compiling Beamer LaTeX...")

        # Initialize updates for PDF preview and download button
        pdf_preview_update = PDF(visible=False)
        pdf_download_btn_update = gr.DownloadButton(visible=False)

        if (
            current_presentation.pdf_path
            and Path(current_presentation.pdf_path).exists()
        ):
            pdf_path_str = str(current_presentation.pdf_path)
            pdf_preview_update = PDF(
                value=pdf_path_str,
                visible=True,
                label="Generated Presentation PDF",
            )
            pdf_download_btn_update = gr.DownloadButton(
                label="📥 Download PDF",
                value=pdf_path_str,
                visible=True,
            )

        # Get Beamer LaTeX download button update
        beamer_download_btn_update = await download_presentation_beamer()

        progress(1.0, desc="Presentation ready!")
        return (
            "✅ Presentation generated successfully!",  # For presentation_status
            current_presentation.latex_code,  # For beamer_output (string updates gr.Code value)
            pdf_preview_update,  # For presentation_pdf_preview (PDF component update)
            pdf_download_btn_update,  # For download_presentation_pdf_btn (DownloadButton component update)
            beamer_download_btn_update,  # For download_beamer_btn (DownloadButton component update)
        )

    except Exception as e:
        return (
            f"❌ Error generating presentation: {e!s}",
            "",  # For beamer_output
            PDF(visible=False),  # For presentation_pdf_preview
            gr.DownloadButton(visible=False),  # For download_presentation_pdf_btn
            gr.DownloadButton(visible=False),  # For download_beamer_btn
        )


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


async def download_latex_code():
    """Generate downloadable LaTeX code as a file."""
    if not current_poster:
        return gr.DownloadButton(visible=False)

    try:
        # Save LaTeX code to outputs directory
        output_path = Path("outputs/posters/poster_latex.tex")
        output_path.write_text(current_poster.latex_code, encoding="utf-8")

        return gr.DownloadButton(
            label="📥 Download LaTeX",
            value=str(output_path),
            visible=True,
        )

    except OSError:
        return gr.DownloadButton(visible=False)


async def download_presentation_beamer():
    """Generate downloadable Beamer LaTeX code as a file."""
    if not current_presentation:
        return gr.DownloadButton(visible=False)

    try:
        # Save Beamer code to outputs directory
        output_path = Path("outputs/presentations/presentation_beamer.tex")
        output_path.write_text(current_presentation.latex_code, encoding="utf-8")

        return gr.DownloadButton(
            label="📥 Download Beamer LaTeX",
            value=str(output_path),
            visible=True,
        )

    except OSError:
        return gr.DownloadButton(visible=False)


# Configuration functions
def update_api_keys(
    heavy_model_key,
    light_model_key,
    coding_model_key,
    devto_key,
    mistral_key,
):
    """Update API keys with runtime overrides."""
    # Update settings with new keys
    settings.set_override("HEAVY_MODEL_API_KEY", heavy_model_key)
    settings.set_override("LIGHT_MODEL_API_KEY", light_model_key)
    settings.set_override("CODING_MODEL_API_KEY", coding_model_key)
    settings.set_override("IMAGE_GEN_API_KEY", image_gen_key)
    settings.set_override("DEEPINFRA_API_KEY", deepinfra_key)
    settings.set_override("DEVTO_API_KEY", devto_key)
    settings.set_override("MISTRAL_API_KEY", mistral_key)

    # Get status of overrides
    status = settings.get_overrides_status()

    # Create status message
    overridden_keys = [key for key, is_overridden in status.items() if is_overridden]

    if overridden_keys:
        status_msg = (
            f"✅ Configuration updated! Overridden keys: {', '.join(overridden_keys)}"
        )
    else:
        status_msg = "ℹ Configuration cleared. Using environment variables."

    return status_msg


def clear_api_keys():
    """Clear all API key overrides."""
    settings.clear_overrides()
    return "🔄 All API key overrides cleared. Using environment variables."


def get_current_config_status():
    """Get current configuration status."""
    status = settings.get_overrides_status()
    overridden_keys = [key for key, is_overridden in status.items() if is_overridden]

    if overridden_keys:
        return f"🔧 Active overrides: {', '.join(overridden_keys)}"
    return "📋 Using environment variables (no overrides active)"


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
                    # text_input = gr.Textbox(
                    #     label="Or Paste Paper Text",
                    #     lines=5,
                    #     placeholder="Paste your research paper content here...",
                    # )

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
                    blog_status_output = gr.Textbox(
                        label="Generation status",
                        interactive=False,
                    )
                    blog_output = gr.Markdown(
                        label="Generated Blog Content",
                        max_height=600,
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
                    gr.Markdown("### LinkedIn")
                    linkedin_output = gr.Textbox(
                        label="LinkedIn Post",
                        lines=5,
                        show_copy_button=True,
                    )
                    linkedin_image = gr.Image(
                        label="LinkedIn Image",
                        show_label=True,
                        show_download_button=True,
                        visible=False,
                    )

                    gr.Markdown("### Twitter")
                    twitter_output = gr.Textbox(
                        label="Twitter Thread",
                        lines=5,
                        show_copy_button=True,
                    )
                    twitter_image = gr.Image(
                        label="Twitter Image",
                        show_label=True,
                        show_download_button=True,
                        visible=False,
                    )

                with gr.Column():
                    gr.Markdown("### Facebook")
                    facebook_output = gr.Textbox(
                        label="Facebook Post",
                        lines=5,
                        show_copy_button=True,
                    )
                    facebook_image = gr.Image(
                        label="Facebook Image",
                        show_label=True,
                        show_download_button=True,
                        visible=False,
                    )

                    gr.Markdown("### Instagram")
                    instagram_output = gr.Textbox(
                        label="Instagram Caption",
                        lines=5,
                        show_copy_button=True,
                    )
                    instagram_image = gr.Image(
                        label="Instagram Image",
                        show_label=True,
                        show_download_button=True,
                        visible=False,
                    )

        with gr.Tab("🎨 Poster Generation"):
            gr.Markdown("## Generate Academic Conference Poster")

            with gr.Row():
                with gr.Column():
                    template_dropdown = gr.Dropdown(
                        choices=["ieee", "acm", "nature"],
                        value="ieee",
                        label="Poster Template Style",
                    )
                    orientation_dropdown = gr.Dropdown(
                        choices=["landscape", "portrait"],
                        value="landscape",
                        label="Poster Orientation",
                    )
                    generate_poster_btn = gr.Button(
                        "🎨 Generate Poster",
                        variant="primary",
                    )

                with gr.Column():
                    poster_status = gr.Textbox(label="Status", interactive=False)

            # Modified layout for poster output and download buttons
            with gr.Row():
                with gr.Column(
                    scale=1,
                ):  # Column for PDF Preview and its Download Button
                    poster_pdf_preview = PDF(  # Changed from gr.File to PDF for preview
                        label="Generated Poster PDF",
                        visible=False,
                        # height=700  # Optional: Uncomment and set a height for the PDF preview
                    )
                    download_pdf_btn = gr.DownloadButton(  # Moved here
                        label="📥 Download PDF",
                        visible=False,
                    )
                with gr.Column(
                    scale=1,
                ):  # Column for LaTeX Code and its Download Button
                    latex_output = gr.Code(
                        label="LaTeX Code",
                        language="latex",
                    )
                    download_latex_btn = gr.DownloadButton(  # Moved here
                        label="📥 Download LaTeX",
                        visible=False,
                    )

        with gr.Tab("📊 Presentation Generation"):
            gr.Markdown("## Generate Beamer LaTeX Presentations")

            with gr.Row():
                with gr.Column():
                    presentation_template_dropdown = gr.Dropdown(
                        choices=["academic", "corporate", "minimal"],
                        value="academic",
                        label="Presentation Template Style",
                    )
                    slide_count_slider = gr.Slider(
                        minimum=8,
                        maximum=20,
                        value=12,
                        step=1,
                        label="Number of Slides",
                    )
                    generate_presentation_btn = gr.Button(
                        "📊 Generate Presentation",
                        variant="primary",
                    )

                with gr.Column():
                    presentation_status = gr.Textbox(label="Status", interactive=False)

            # Layout for presentation output and download buttons
            with gr.Row():
                with gr.Column(
                    scale=1,
                ):  # Column for PDF Preview and its Download Button
                    presentation_pdf_preview = PDF(
                        label="Generated Presentation PDF",
                        visible=False,
                    )
                    download_presentation_pdf_btn = gr.DownloadButton(
                        label="📥 Download PDF",
                        visible=False,
                    )
                with gr.Column(
                    scale=1,
                ):  # Column for Beamer Code and its Download Button
                    beamer_output = gr.Code(
                        label="Beamer LaTeX Code",
                        language="latex",
                    )
                    download_beamer_btn = gr.DownloadButton(
                        label="📥 Download Beamer LaTeX",
                        visible=False,
                    )

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

        with gr.Tab("⚙️ Configuration"):
            gr.Markdown("## API Key Configuration")
            gr.Markdown("""
            Override API keys from environment variables. This is useful when your environment keys expire or you want to use different keys temporarily.
            Leave fields empty to use environment variables.
            """)

            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Language Models")
                    heavy_model_key_input = gr.Textbox(
                        label="Heavy Model API Key (GPT-4, etc.)",
                        type="password",
                        placeholder="Enter key to override environment variable...",
                    )
                    light_model_key_input = gr.Textbox(
                        label="Light Model API Key (GPT-4-mini/nano, etc.)",
                        type="password",
                        placeholder="Enter key to override environment variable...",
                    )
                    coding_model_key_input = gr.Textbox(
                        label="Coding Model API Key (Claude)",
                        type="password",
                        placeholder="Enter key to override environment variable...",
                    )
                    mistral_key_input = gr.Textbox(
                        label="Mistral API Key",
                        type="password",
                        placeholder="Enter key to override environment variable...",
                    )

                with gr.Column():
                    gr.Markdown("### Other Services")
                    # image_gen_key_input = gr.Textbox(
                    #     label="Image Generation API Key (DALL-E, etc.)",
                    #     type="password",
                    #     placeholder="Enter key to override environment variable...",
                    # )
                    # deepinfra_key_input = gr.Textbox(
                    #     label="DeepInfra API Key",
                    #     type="password",
                    #     placeholder="Enter key to override environment variable...",
                    # )
                    devto_key_input = gr.Textbox(
                        label="DEV.to API Key",
                        type="password",
                        placeholder="Enter key to override environment variable...",
                    )

            with gr.Row():
                update_config_btn = gr.Button(
                    "💾 Update Configuration", variant="primary"
                )
                clear_config_btn = gr.Button(
                    "🔄 Clear All Overrides", variant="secondary"
                )

            config_status = gr.Textbox(
                label="Configuration Status",
                interactive=False,
                value=get_current_config_status(),
            )

        # Event handlers
        process_btn.click(
            fn=process_paper,
            inputs=[pdf_input, url_input],
            # inputs=[pdf_input, url_input, text_input],
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
            outputs=[blog_status_output, blog_output, download_blog_btn],
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
                linkedin_image,
                twitter_image,
                facebook_image,
                instagram_image,
            ],
        )

        generate_poster_btn.click(
            fn=generate_poster_content,
            inputs=[template_dropdown, orientation_dropdown],
            outputs=[
                poster_status,
                latex_output,
                poster_pdf_preview,  # Maps to the PDF component
                download_pdf_btn,  # Maps to the PDF download button
                download_latex_btn,  # Maps to the LaTeX download button
            ],
        )

        generate_presentation_btn.click(
            fn=generate_presentation_content,
            inputs=[presentation_template_dropdown, slide_count_slider],
            outputs=[
                presentation_status,
                beamer_output,
                presentation_pdf_preview,  # Maps to the PDF component
                download_presentation_pdf_btn,  # Maps to the PDF download button
                download_beamer_btn,  # Maps to the Beamer download button
            ],
        )

        publish_draft_btn.click(
            fn=publish_draft,
            outputs=[publish_status],
        )

        publish_now_btn.click(
            fn=publish_now,
            outputs=[publish_status],
        )

        update_config_btn.click(
            fn=update_api_keys,
            inputs=[
                heavy_model_key_input,
                light_model_key_input,
                coding_model_key_input,
                devto_key_input,
                mistral_key_input,
            ],
            outputs=[config_status],
        )

        clear_config_btn.click(
            fn=clear_api_keys,
            outputs=[config_status],
        )

    return app


if __name__ == "__main__":
    # Create output directories using pathlib
    Path("outputs/posters").mkdir(parents=True, exist_ok=True)
    Path("outputs/blogs").mkdir(parents=True, exist_ok=True)
    Path("outputs/presentations").mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(parents=True, exist_ok=True)

    # Launch the application
    app_instance = create_interface()
    app_instance.launch(
        server_name=settings.HOST,
        server_port=settings.PORT,
        debug=settings.DEBUG,
        share=False,
    )
