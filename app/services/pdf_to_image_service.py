import os
from typing import Optional

try:
    import fitz  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdf2image

    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

from PIL import Image


class PDFToImageService:
    """Service to convert PDF files to images for analysis using Python packages"""

    @staticmethod
    async def convert_pdf_to_image(
        pdf_path: str,
        output_path: Optional[str] = None,
        max_width: int = 800,
    ) -> Optional[str]:
        """
        Convert PDF to PNG image using Python packages (PyMuPDF or pdf2image).

        Args:
            pdf_path: Path to the PDF file
            output_path: Optional output path for the image. If None, creates one based on PDF name
            max_width: Maximum width for the output image (to control token costs)

        Returns:
            Path to the generated image file, or None if conversion failed

        """
        try:
            if not os.path.exists(pdf_path):
                print(f"PDF file not found: {pdf_path}")
                return None

            # Generate output path if not provided
            if output_path is None:
                pdf_dir = os.path.dirname(pdf_path)
                pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
                output_path = os.path.join(pdf_dir, f"{pdf_name}_image.png")

            # Try PyMuPDF first (faster and lighter)
            if PYMUPDF_AVAILABLE:
                success = await PDFToImageService._convert_with_pymupdf(
                    pdf_path,
                    output_path,
                    max_width,
                )
                if success:
                    return output_path

            # Fallback to pdf2image
            if PDF2IMAGE_AVAILABLE:
                success = await PDFToImageService._convert_with_pdf2image(
                    pdf_path,
                    output_path,
                    max_width,
                )
                if success:
                    return output_path

            print(
                "No PDF conversion libraries available. Install PyMuPDF or pdf2image."
            )
            return None

        except Exception as e:
            print(f"Error converting PDF to image: {e}")
            return None

    @staticmethod
    async def _convert_with_pymupdf(
        pdf_path: str,
        output_path: str,
        max_width: int,
    ) -> bool:
        """Convert using PyMuPDF (fitz) - fast and lightweight"""
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)

            if len(doc) == 0:
                print("PDF has no pages")
                return False

            # Get first page
            page = doc[0]

            # Calculate appropriate zoom to achieve max_width
            page_rect = page.rect
            zoom = min(max_width / page_rect.width, 2.0)  # Max zoom of 2.0

            # Create transformation matrix
            mat = fitz.Matrix(zoom, zoom)

            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Save as PNG
            pix.save(output_path)

            # Clean up
            doc.close()

            return True

        except Exception as e:
            print(f"PyMuPDF conversion error: {e}")
            return False

    @staticmethod
    async def _convert_with_pdf2image(
        pdf_path: str,
        output_path: str,
        max_width: int,
    ) -> bool:
        """Convert using pdf2image library"""
        try:
            # Calculate DPI to achieve desired width
            # Standard A4 width is ~8.27 inches, so DPI = max_width / 8.27
            target_dpi = min(int(max_width / 8.27), 150)  # Max 150 DPI

            # Convert first page only
            images = pdf2image.convert_from_path(
                pdf_path,
                dpi=target_dpi,
                first_page=1,
                last_page=1,
                fmt="PNG",
            )

            if not images:
                print("No images generated from PDF")
                return False

            # Get the first (and only) image
            image = images[0]

            # Resize if still too wide
            if image.width > max_width:
                ratio = max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # Save the image
            image.save(output_path, "PNG", optimize=True)

            return True

        except Exception as e:
            print(f"pdf2image conversion error: {e}")
            return False

    @staticmethod
    async def get_available_converters() -> list[str]:
        """Get list of available PDF conversion methods"""
        available = []
        if PYMUPDF_AVAILABLE:
            available.append("PyMuPDF")
        if PDF2IMAGE_AVAILABLE:
            available.append("pdf2image")
        return available


# Global instance
pdf_to_image_service = PDFToImageService()
