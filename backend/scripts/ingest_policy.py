
import argparse
import hashlib
import logging
import re
from datetime import date
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pdfplumber
from qdrant_client import models

from backend.app.core.config import get_settings
from backend.app.infrastructure.vector_store import (
    add_policy_chunks,
    create_collection,
    get_qdrant_client,
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PDF = PROJECT_ROOT / "data" / "XYZ_Company_Leave_Policy.pdf"

# Initial heuristic for headings such as "3.2 Annual Leave" or
# "Section 4: Sick Leave". Verify this pattern against your actual PDF.
HEADING_PATTERN = re.compile(
    r"^\s*(?:(?:section|clause)\s+)?"
    r"(?P<number>\d+(?:\.\d+)*\.?)"
    r"\s*[:.)\-]?\s+"
    r"(?P<heading>[A-Z][^\n]{1,100})\s*$",
    re.IGNORECASE,
)


_PAGE_NOISE = re.compile(
    r"^(Page \d+ of \d+|.*Leave Policy \(Sample\))$", re.IGNORECASE
)


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text in reading order (tables stay inside their section)."""
    if not pdf_path.is_file():
        raise FileNotFoundError(f"Policy PDF not found: {pdf_path}")

    pages: list[str] = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            lines = [
                line for line in text.splitlines()
                if not _PAGE_NOISE.match(line.strip())
            ]

            if any(line.strip() for line in lines):
                pages.append("\n".join(lines))
            else:
                logger.warning(
                    "Page %d contains no extractable text.", page_number
                )

    extracted = "\n".join(pages).strip()

    if not extracted:
        raise ValueError(
            "No text could be extracted. The PDF may be scanned; "
            "OCR may be required."
        )

    return extracted


def _is_clause(heading: str) -> bool:
    """A long or sentence-like line (e.g. '5.1 The weekly holidays are...')
    is a numbered clause, not a heading: keep it as section content."""
    return len(heading.split()) > 8 or heading.endswith((".", ","))


def split_into_sections(text: str) -> list[dict[str, str]]:
    """
    Split text using headings detected by HEADING_PATTERN.

    Text before the first detected heading is retained under
    an introductory section rather than discarded.
    """
    sections: list[dict[str, str]] = []
    current_number = ""
    current_heading = "Introduction"
    current_lines: list[str] = []

    for line in text.splitlines():
        match = HEADING_PATTERN.match(line.strip())

        if match and not _is_clause(match.group("heading")):
            content = "\n".join(current_lines).strip()

            if content:
                sections.append(
                    {
                        "section_number": current_number,
                        "section_heading": current_heading,
                        "content": content,
                    }
                )

            current_number = match.group("number").rstrip(".")
            current_heading = match.group("heading").strip()
            current_lines = []
        else:
            current_lines.append(line)

    content = "\n".join(current_lines).strip()

    if content:
        sections.append(
            {
                "section_number": current_number,
                "section_heading": current_heading,
                "content": content,
            }
        )

    return sections


def build_policy_chunks(
    text: str,
    *,
    policy_id: str,
    policy_title: str,
    policy_version: str,
    effective_date: str | None,
) -> list[Document]:
    """Create searchable chunks with policy and section metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    documents: list[Document] = []

    for section in split_into_sections(text):
        section_text = section["content"]

        if not section_text.strip():
            continue

        pieces = splitter.split_text(section_text)

        for chunk_index, piece in enumerate(pieces):
            documents.append(
                Document(
                    page_content=piece,
                    metadata={
                        "policy_id": policy_id,
                        "policy_title": policy_title,
                        "policy_version": policy_version,
                        "effective_date": effective_date or "",
                        "section_number": section["section_number"],
                        "section_heading": section["section_heading"],
                        "chunk_index": chunk_index,
                    },
                )
            )

    if not documents:
        raise ValueError("No policy chunks were generated.")

    return documents


def _stable_chunk_id(document: Document) -> str:
    """Generate a deterministic UUID for an identical policy chunk."""
    metadata = document.metadata

    identity = "|".join(
        [
            str(metadata["policy_id"]),
            str(metadata["policy_version"]),
            str(metadata["section_number"]),
            str(metadata["section_heading"]),
            str(metadata["chunk_index"]),
            hashlib.sha256(
                document.page_content.encode("utf-8")
            ).hexdigest(),
        ]
    )

    return str(uuid5(NAMESPACE_URL, identity))


def replace_policy_chunks(
    documents: list[Document],
    policy_id: str,
) -> list[str]:
    """
    Replace existing chunks for this policy ID, then index the new ones.

    Note: deletion happens before insertion. For production-grade
    updates, use versioned collections or staged indexing to avoid
    leaving a policy unavailable if insertion fails.
    """
    settings = get_settings()
    client = get_qdrant_client()

    # Ensure the collection exists before deleting anything.
    create_collection()

    client.create_payload_index(
        collection_name=settings.qdrant_collection,
        field_name="metadata.policy_id",
        field_schema=models.PayloadSchemaType.KEYWORD,
        wait=True,
    )

    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.policy_id",
                        match=models.MatchValue(value=policy_id),
                    )
                ]
            )
        ),
        wait=True,
    )

    ids = [_stable_chunk_id(document) for document in documents]

    return add_policy_chunks(documents, ids=ids)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract and index an HR policy PDF in Qdrant."
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=DEFAULT_PDF,
        help="Path to the policy PDF.",
    )
    parser.add_argument(
        "--policy-id",
        default="leave-policy",
        help="Stable identifier for this policy.",
    )
    parser.add_argument(
        "--title",
        default="XYZ Company Leave Policy",
        help="Policy title.",
    )
    parser.add_argument(
        "--version",
        default="2.0",
        help="Policy version.",
    )
    parser.add_argument(
        "--effective-date",
        default=None,
        help="Effective date in YYYY-MM-DD format.",
    )
    args = parser.parse_args()

    if args.effective_date:
        # Validate the supplied date before indexing.
        date.fromisoformat(args.effective_date)

    logging.basicConfig(level=logging.INFO)

    text = extract_pdf_text(args.pdf)

    documents = build_policy_chunks(
        text,
        policy_id=args.policy_id,
        policy_title=args.title,
        policy_version=args.version,
        effective_date=args.effective_date,
    )

    indexed_ids = replace_policy_chunks(
        documents=documents,
        policy_id=args.policy_id,
    )

    logger.info("Extracted characters: %d", len(text))
    logger.info("Chunks indexed: %d", len(indexed_ids))
    logger.info("Policy ID: %s", args.policy_id)
    logger.info("Policy version: %s", args.version)


if __name__ == "__main__":
    main()
