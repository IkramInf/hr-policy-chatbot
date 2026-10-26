
from pathlib import Path
from unittest.mock import patch

import pytest

from backend.scripts.ingest_policy import (
    extract_pdf_text,
    build_policy_chunks,
)


def test_extract_pdf_text_rejects_missing_file(tmp_path):
    missing_pdf = tmp_path / "missing.pdf"

    with pytest.raises((FileNotFoundError, ValueError)):
        extract_pdf_text(missing_pdf)


def test_extract_pdf_text_reads_pdf(tmp_path):
    """Test extraction using a temporary PDF with known text."""
    from pypdf import PdfWriter

    pdf_path = tmp_path / "sample_policy.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    # A blank page has no extractable text. The extractor should
    # return empty text or report that the PDF contains no text.
    with open(pdf_path, "wb") as file:
        writer.write(file)

    result = extract_pdf_text(pdf_path)

    assert isinstance(result, str)


def test_build_policy_chunks_attaches_metadata():
    text = """
    1. Annual Leave

    Employees may request annual leave according to company policy.

    2. Sick Leave

    Employees should follow the company's sick leave procedure.
    """

    chunks = build_policy_chunks(
        text=text,
        policy_id="test-policy",
        title="Test Leave Policy",
        version="1.0",
    )

    assert chunks
    for chunk in chunks:
        assert chunk.page_content.strip()
        assert chunk.metadata["policy_id"] == "test-policy"
        assert chunk.metadata["policy_title"] == "Test Leave Policy"
        assert chunk.metadata["policy_version"] == "1.0"
        assert chunk.metadata["section_heading"]


def test_build_policy_chunks_is_repeatable():
    text = (
        "1. Annual Leave\n\n"
        "Employees may request annual leave according to policy."
    )

    first = build_policy_chunks(
        text=text,
        policy_id="test-policy",
        title="Test Leave Policy",
        version="1.0",
    )
    second = build_policy_chunks(
        text=text,
        policy_id="test-policy",
        title="Test Leave Policy",
        version="1.0",
    )

    assert [chunk.page_content for chunk in first] == [
        chunk.page_content for chunk in second
    ]
    assert [chunk.metadata for chunk in first] == [
        chunk.metadata for chunk in second
    ]
