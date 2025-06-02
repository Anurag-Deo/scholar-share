import base64
from typing import Any
from mistralai import Mistral
from app.config.settings import settings


class PDFParsingError(Exception):
    """Custom exception for PDF parsing errors."""


class URLParsingError(Exception):
    """Custom exception for URL parsing errors."""


class PDFService:
    def __init__(self):
        self.mistral_api_key = settings.MISTRAL_API_KEY
        self.client = Mistral(api_key=self.mistral_api_key)

    def _format_ocr_response(self, ocr_response) -> dict[str, Any]:
        """Format the OCR response into a standardized dictionary."""
        images = []
        tables = []
        full_text_parts = []

        # Handle different response structures
        if hasattr(ocr_response, "pages"):
            pages = ocr_response.pages
        elif isinstance(ocr_response, dict) and "pages" in ocr_response:
            pages = ocr_response["pages"]
        elif hasattr(ocr_response, "data") and hasattr(ocr_response.data, "pages"):
            pages = ocr_response.data.pages
        else:
            # If no pages found, try to extract content directly
            print(f"Unexpected response structure: {type(ocr_response)}")
            print(
                f"Response attributes: {dir(ocr_response) if hasattr(ocr_response, '__dict__') else 'No attributes'}"
            )
            return {
                "text": str(ocr_response) if ocr_response else "",
                "images": [],
                "tables": [],
                "metadata": {"raw_response": str(ocr_response)},
            }

        for page in pages:
            # Extract images
            if hasattr(page, "images") and page.images:
                for img in page.images:
                    if hasattr(img, "image_base64") and img.image_base64:
                        images.append(img.image_base64)

            # Extract text/markdown
            text_content = None
            if hasattr(page, "markdown") and page.markdown:
                text_content = page.markdown
            elif hasattr(page, "text") and page.text:
                text_content = page.text
            elif hasattr(page, "content") and page.content:
                text_content = page.content

            if text_content:
                full_text_parts.append(text_content)

                # Extract tables from markdown
                if "|" in text_content:  # Simple check for table presence
                    lines = text_content.split("\n")
                    current_table = []
                    in_table = False

                    for line in lines:
                        stripped_line = line.strip()
                        if stripped_line.startswith("|") and stripped_line.endswith(
                            "|"
                        ):
                            if not in_table:
                                in_table = True
                                current_table = []
                            current_table.append(line)
                        else:
                            if in_table and current_table:
                                # Only add table if it has more than just header separator
                                if len(current_table) > 2:
                                    tables.append("\n".join(current_table))
                                current_table = []
                                in_table = False

                    # Don't forget the last table
                    if current_table and len(current_table) > 2:
                        tables.append("\n".join(current_table))

        return {
            "text": "\n\n".join(full_text_parts),
            "images": images,
            "tables": tables,
            "metadata": {
                "page_count": len(pages) if pages else 0,
                "image_count": len(images),
                "table_count": len(tables),
            },
        }

    def parse_pdf(self, pdf_content: bytes) -> dict[str, Any]:
        """Parse PDF using Mistral OCR API synchronously."""
        try:
            # Encode PDF content to base64
            pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")
            data_url = f"data:application/pdf;base64,{pdf_base64}"

            # Make the OCR request
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": data_url,
                },
                include_image_base64=True,
            )

            print(f"OCR Response type: {type(ocr_response)}")
            # print(f"OCR Response: {ocr_response}")

            # Format and return the response
            formatted_response = self._format_ocr_response(ocr_response)
            # Save the text content to a file
            with open("parsed_pdf_content.txt", "w", encoding="utf-8") as f:
                f.write(formatted_response["text"])
            return formatted_response

        except Exception as e:
            print(f"Error in parse_pdf: {e}")
            print(f"Error type: {type(e)}")
            raise PDFParsingError(f"PDF parsing failed: {str(e)}") from e

    def parse_url(self, url: str) -> dict[str, Any]:
        """Parse PDF from URL using Mistral OCR API synchronously."""
        try:
            # Make the OCR request
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": url,
                },
                include_image_base64=True,
            )

            print(f"OCR Response type: {type(ocr_response)}")
            # print(f"OCR Response: {ocr_response}")

            # Format and return the response
            formatted_response = self._format_ocr_response(ocr_response)
            return formatted_response

        except Exception as e:
            print(f"Error in parse_url: {e}")
            print(f"Error type: {type(e)}")
            raise URLParsingError(f"URL parsing failed: {str(e)}") from e


# Usage example
pdf_service = PDFService()

# Example (use in a route or script):
# with open("sample.pdf", "rb") as f:
#     pdf_content = f.read()
#     result = pdf_service.parse_pdf(pdf_content)
#     print(result)
