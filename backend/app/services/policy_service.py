
from datetime import date
from typing import Any

from backend.app.core.config import get_settings
from backend.app.infrastructure.vector_store import get_qdrant_client
from backend.app.schemas.policy import (
    PolicyResponse,
    PolicySectionResponse,
    PolicySectionsResponse,
)


def _scroll_all_points() -> list[dict[str, Any]]:
    """Read all policy chunks from Qdrant, handling pagination."""
    settings = get_settings()
    client = get_qdrant_client()

    points: list[dict[str, Any]] = []
    offset = None

    while True:
        batch, next_offset = client.scroll(
            collection_name=settings.qdrant_collection,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        for point in batch:
            payload = point.payload or {}

            # LangChain Qdrant stores metadata inside the metadata payload.
            metadata = payload.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}

            content = payload.get("page_content", "")

            points.append(
                {
                    "id": str(point.id),
                    "content": content if isinstance(content, str) else "",
                    "metadata": metadata,
                }
            )

        if next_offset is None:
            break

        offset = next_offset

    return points


def _parse_date(value: Any) -> date | None:
    """Parse an ISO-formatted date without failing the whole response."""
    if not value:
        return None

    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _get_policy_metadata(
    points: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Build one metadata record per policy ID."""
    policies: dict[str, dict[str, Any]] = {}

    for point in points:
        metadata = point["metadata"]
        policy_id = metadata.get("policy_id")

        if not policy_id:
            continue

        policy_id = str(policy_id)

        if policy_id not in policies:
            policies[policy_id] = {
                "policy_id": policy_id,
                "title": str(
                    metadata.get("policy_title", "Untitled policy")
                ),
                "version": str(
                    metadata.get("policy_version", "Unknown")
                ),
                "effective_date": _parse_date(
                    metadata.get("effective_date")
                ),
                "sections": set(),
            }

        section_number = str(metadata.get("section_number", ""))
        section_heading = str(
            metadata.get("section_heading", "Untitled section")
        )

        policies[policy_id]["sections"].add(
            (section_number, section_heading)
        )

    return policies


def list_policies() -> list[PolicyResponse]:
    """List distinct policies represented in the Qdrant collection."""
    points = _scroll_all_points()
    policies = _get_policy_metadata(points)

    return [
        PolicyResponse(
            policy_id=item["policy_id"],
            title=item["title"],
            version=item["version"],
            effective_date=item["effective_date"],
            section_count=len(item["sections"]),
        )
        for item in sorted(
            policies.values(),
            key=lambda item: item["title"].lower(),
        )
    ]


def get_policy_sections(policy_id: str) -> PolicySectionsResponse | None:
    """
    Reconstruct a policy's sections from its stored chunks.

    Multiple chunks with the same section metadata are combined.
    For accurate ordering, ingestion should store a chunk_index.
    """
    if not policy_id or not policy_id.strip():
        raise ValueError("Policy ID cannot be empty.")

    points = _scroll_all_points()

    policy_points = [
        point
        for point in points
        if str(point["metadata"].get("policy_id", "")) == policy_id
    ]

    if not policy_points:
        return None

    metadata_records = _get_policy_metadata(policy_points)
    policy = metadata_records.get(policy_id)

    if policy is None:
        return None

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}

    for point in policy_points:
        metadata = point["metadata"]
        key = (
            str(metadata.get("section_number", "")),
            str(metadata.get("section_heading", "Untitled section")),
        )

        grouped.setdefault(key, []).append(point)

    sections: list[PolicySectionResponse] = []

    for (section_number, heading), chunks in grouped.items():
        # Sort by chunk_index if ingestion supplied it.
        chunks.sort(
            key=lambda point: (
                int(point["metadata"].get("chunk_index", 0)),
                point["id"],
            )
        )

        # Remove repeated identical chunk text.
        unique_texts: list[str] = []
        seen_texts: set[str] = set()

        for chunk in chunks:
            content = chunk["content"].strip()

            if content and content not in seen_texts:
                seen_texts.add(content)
                unique_texts.append(content)

        sections.append(
            PolicySectionResponse(
                section_number=section_number,
                heading=heading,
                content="\n\n".join(unique_texts),
            )
        )

    sections.sort(
        key=lambda section: (
            section.section_number,
            section.heading.lower(),
        )
    )

    return PolicySectionsResponse(
        policy_id=policy_id,
        title=policy["title"],
        version=policy["version"],
        effective_date=policy["effective_date"],
        sections=sections,
    )
