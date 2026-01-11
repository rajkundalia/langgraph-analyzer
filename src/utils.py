"""
Utility Functions for LangGraph Research Paper Analyzer

Helper functions for PDF processing, text formatting, file I/O,
and other common operations used throughout the workflow.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime


def load_pdf_text(pdf_path: str) -> Tuple[str, str]:
    """
    Extract text content from a PDF file.

    Uses PyPDF to read PDF files and extract text content. Handles
    multi-page documents and basic text cleaning.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Tuple of (extracted_text, paper_title)

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If PDF cannot be read or contains no text

    Example:
        >>> text, title = load_pdf_text("data/papers/attention.pdf")
        >>> print(f"Loaded: {title} ({len(text)} characters)")
    """

    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("pypdf is required. Install with: pip install pypdf")

    # Validate file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    print(f"\n📄 Loading PDF: {pdf_path}")

    try:
        # Read PDF
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)

        print(f"   Pages found: {num_pages}")

        # Extract text from all pages
        text_content = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)

        if not text_content:
            raise ValueError("PDF contains no extractable text")

        full_text = "\n\n".join(text_content)

        # Clean the text
        full_text = clean_text(full_text)

        # Extract title from filename or first page
        paper_title = extract_paper_title(pdf_path, reader)

        print(f"   ✓ Extracted {len(full_text)} characters")
        print(f"   ✓ Title: {paper_title}\n")

        return full_text, paper_title

    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text.

    Performs basic text cleaning:
    - Remove excessive whitespace
    - Normalize line breaks
    - Remove special characters that interfere with LLM processing

    Args:
        text: Raw extracted text

    Returns:
        Cleaned text string
    """

    # Replace multiple newlines with double newline
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Replace multiple spaces with single space
    text = re.sub(r' {2,}', ' ', text)

    # Remove non-printable characters except newlines and tabs
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def extract_paper_title(pdf_path: str, reader) -> str:
    """
    Extract paper title from PDF.

    Tries multiple strategies:
    1. First line of first page
    2. Filename (cleaned)
    3. Default placeholder

    Args:
        pdf_path: Path to PDF file
        reader: PdfReader instance

    Returns:
        Extracted or inferred paper title
    """

    try:
        # Strategy 1: Try to get title from first page
        first_page_text = reader.pages[0].extract_text()
        if first_page_text:
            # Take first non-empty line
            lines = [line.strip() for line in first_page_text.split('\n') if line.strip()]
            if lines:
                title = lines[0]
                # Clean up if it's reasonable length
                if 10 < len(title) < 200:
                    return title
    except:
        pass

    # Strategy 2: Use filename
    filename = Path(pdf_path).stem
    # Clean up filename (replace underscores/hyphens with spaces, capitalize)
    title = filename.replace('_', ' ').replace('-', ' ')
    title = ' '.join(word.capitalize() for word in title.split())

    return title


def save_report(report_text: str, paper_title: str, output_dir: str = "outputs") -> str:
    """
    Save analysis report to file.

    Creates output directory if needed and saves the report with a
    timestamped, sanitized filename.

    Args:
        report_text: Final analysis report content
        paper_title: Title of analyzed paper
        output_dir: Directory to save report (default: "outputs")

    Returns:
        Path to saved file

    Example:
        path = save_report(report, "Attention Is All You Need")
        print(f"Saved to: {path}")
    """

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create sanitized filename from paper title
    safe_title = sanitize_filename(paper_title)

    # Add timestamp to make unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_title}_{timestamp}.txt"

    filepath = os.path.join(output_dir, filename)

    # Write report
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"\n💾 Report saved to: {filepath}")

    return filepath


def sanitize_filename(filename: str, max_length: int = 50) -> str:
    """
    Sanitize string for use as filename.

    Removes special characters and limits length.

    Args:
        filename: Original filename/title
        max_length: Maximum filename length

    Returns:
        Sanitized filename safe for filesystem
    """

    # Remove special characters, keep alphanumeric and spaces
    sanitized = re.sub(r'[^\w\s-]', '', filename)

    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')

    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)

    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # Remove trailing underscore
    sanitized = sanitized.rstrip('_')

    return sanitized.lower()


def format_section_header(title: str, width: int = 70) -> str:
    """
    Format a section header with consistent styling.

    Args:
        title: Section title
        width: Total width of header

    Returns:
        Formatted header string
    """

    return f"\n{'=' * width}\n{title.upper().center(width)}\n{'=' * width}\n"


def truncate_text(text: str, max_length: int = 8000,
                  add_ellipsis: bool = True) -> str:
    """
    Truncate text to maximum length for LLM context.

    Ensures text fits within token limits while preserving readability.

    Args:
        text: Text to truncate
        max_length: Maximum character length
        add_ellipsis: Whether to add "..." indicator

    Returns:
        Truncated text
    """

    if len(text) <= max_length:
        return text

    truncated = text[:max_length]

    if add_ellipsis:
        truncated += "\n\n[Text truncated for analysis...]"

    return truncated


def get_user_approval() -> bool:
    """
    Get yes/no approval from user via console input.

    Handles various input formats (yes/y, no/n, etc.) and validates input.

    Returns:
        True if user approved, False otherwise

    Example:
        >>> if get_user_approval():
        ...     save_report()
    """

    print("\n" + "=" * 70)
    print("🔍 HUMAN REVIEW REQUIRED")
    print("=" * 70)
    print("\nPlease review the synthesized report above.")

    while True:
        response = input("\n👉 Approve this report? (yes/no): ").strip().lower()

        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("   ⚠️  Invalid input. Please enter 'yes' or 'no'")


def print_welcome_banner():
    """Display welcome banner when starting the analyzer."""

    print("\n" + "=" * 70)
    print("🤖 LANGGRAPH MULTI-AGENT RESEARCH PAPER ANALYZER")
    print("=" * 70)
    print("\nThis tool uses coordinated AI agents to analyze research papers:")
    print("  • Claims Extractor - Identifies key claims")
    print("  • Methodology Analyzer - Evaluates research methods")
    print("  • Limitations Finder - Identifies weaknesses")
    print("  • Synthesizer - Creates comprehensive report")
    print("  • Human Review - Your approval gate")
    print("\n" + "=" * 70 + "\n")


def print_completion_summary(approved: bool, output_path: Optional[str] = None):
    """
    Display completion summary after workflow finishes.

    Args:
        approved: Whether report was approved
        output_path: Path where report was saved (if approved)
    """

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    if approved:
        print("\n✅ Status: APPROVED")
        if output_path:
            print(f"📄 Report saved to: {output_path}")
        print("\nThe multi-agent analysis has been completed and saved.")
    else:
        print("\n❌ Status: REJECTED")
        print("\nThe report was not approved. No files saved.")

    print("\nThank you for using LangGraph Multi-Agent Analyzer!")
    print("=" * 70 + "\n")


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of token count for text.

    Uses simple heuristic: ~4 characters per token on average.

    Args:
        text: Text to estimate

    Returns:
        Estimated token count
    """

    return len(text) // 4


def check_dependencies() -> bool:
    """
    Check if all required dependencies are installed.

    Returns:
        True if all dependencies available, False otherwise
    """

    required = {
        'langgraph': 'langgraph',
        'langchain': 'langchain',
        'langchain_ollama': 'langchain-ollama',
        'pypdf': 'pypdf'
    }

    missing = []

    for package_name, install_name in required.items():
        try:
            __import__(package_name)
        except ImportError:
            missing.append(install_name)

    if missing:
        print("\n❌ Missing required packages:")
        for pkg in missing:
            print(f"   • {pkg}")
        print("\nInstall with: pip install " + " ".join(missing))
        return False

    return True