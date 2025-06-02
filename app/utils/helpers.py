import hashlib
import re
import tempfile
from typing import List


def clean_filename(filename: str) -> str:
    """Clean filename for safe file operations"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Remove extra spaces and limit length
    filename = re.sub(r"\s+", "_", filename.strip())
    return filename[:100]  # Limit length


def generate_content_hash(content: str) -> str:
    """Generate hash for content deduplication"""
    return hashlib.md5(content.encode()).hexdigest()


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text"""
    # Simple keyword extraction (can be enhanced with NLP)
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    # Remove common words
    stop_words = {
        "this",
        "that",
        "with",
        "have",
        "will",
        "from",
        "they",
        "been",
        "said",
        "each",
        "which",
        "their",
        "time",
        "would",
        "there",
        "could",
        "other",
    }
    keywords = [word for word in words if word not in stop_words]
    # Return most frequent words
    from collections import Counter

    return [word for word, count in Counter(keywords).most_common(max_keywords)]


def format_authors(authors: List[str]) -> str:
    """Format author list for display"""
    if not authors:
        return "Unknown Author"
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    return f"{', '.join(authors[:-1])}, and {authors[-1]}"


def estimate_reading_time(text: str, wpm: int = 200) -> int:
    """Estimate reading time in minutes"""
    word_count = len(text.split())
    return max(1, round(word_count / wpm))


def create_temp_file(content: str, suffix: str = ".txt") -> str:
    """Create temporary file with content"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name


def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return url_pattern.match(url) is not None


def sanitize_html(text: str) -> str:
    """Basic HTML sanitization"""
    # Remove script tags and their content
    text = re.sub(
        r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE
    )
    # Remove other potentially dangerous tags
    dangerous_tags = ["script", "iframe", "object", "embed", "form"]
    for tag in dangerous_tags:
        text = re.sub(
            f"<{tag}[^>]*>.*?</{tag}>", "", text, flags=re.DOTALL | re.IGNORECASE
        )
    return text


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break

        # Try to break at sentence boundary
        chunk = text[start:end]
        last_period = chunk.rfind(".")
        last_newline = chunk.rfind("\n")

        break_point = max(last_period, last_newline)
        if break_point > start + chunk_size // 2:  # Only if break point is reasonable
            end = start + break_point + 1

        chunks.append(text[start:end])
        start = end - overlap

    return chunks


def format_social_media_content(content: str, platform: str) -> str:
    """Format content for specific social media platforms"""
    if platform.lower() == "twitter":
        # Split into tweets if too long
        if len(content) <= 280:
            return content
        # Simple tweet splitting (can be enhanced)
        sentences = content.split(". ")
        tweets = []
        current_tweet = ""

        for sentence in sentences:
            if len(current_tweet + sentence) <= 250:  # Leave room for thread numbering
                pass  # This block is empty as per the markdown structure

        if current_tweet:
            tweets.append(current_tweet.strip())
        return "\n\n".join(tweets)

    if platform.lower() == "linkedin":
        # LinkedIn allows longer content, but add professional formatting
        if len(content) > 1300:
            content = content[:1297] + "..."
        return content

    if platform.lower() == "facebook":
        # Facebook formatting with engagement hooks
        if not content.endswith("?"):
            content += "\n\nWhat do you think about this research? Share your thoughts!"
        return content

    return content
