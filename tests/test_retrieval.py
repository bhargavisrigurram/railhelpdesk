"""Tests for the retrieval interface and citation extraction."""

import pytest
import numpy as np
from pathlib import Path

from ingestion.indexer import ChromaIndexer
from retrieval.retriever import DocumentRetriever


def test_retriever_interface(tmp_path: Path):
    persist_dir = tmp_path / "test_retrieval_db"
    indexer = ChromaIndexer(persist_dir=persist_dir, collection_name="retrieval_col")

    chunks = [
        {
            "chunk_id": "c1",
            "doc": "irctc_refund_rules_jan2026.pdf",
            "page": 3,
            "text": "Cancellation charges for RAC or Waitlisted tickets: clerkage Rs 60.",
            "section_title": "RAC and Waitlist",
            "section_path": "Refunds > RAC",
            "split_method": "whole_section",
        },
        {
            "chunk_id": "c2",
            "doc": "indianrail_refund_rules_2015.html",
            "page": None,
            "text": "Table of revised refund charges effective 12.11.2015.",
            "section_title": "2015 Table",
            "section_path": "Rules > 2015 Table",
            "split_method": "whole_section",
        },
    ]

    # Use a dummy embedder for unit testing the retriever structure
    class MockEmbedder:
        def embed_query(self, q):
            return np.ones(384, dtype=np.float32)

    embeddings = np.ones((2, 384), dtype=np.float32)
    indexer.index_chunks(chunks, embeddings)

    retriever = DocumentRetriever(
        persist_dir=persist_dir,
        collection_name="retrieval_col",
        embedder=MockEmbedder(),
    )

    results = retriever.retrieve("clerkage charges", top_k=2)
    assert len(results) == 2

    # Check structure
    r0 = results[0]
    assert "rank" in r0
    assert "chunk_id" in r0
    assert "doc" in r0
    assert "text" in r0
    assert "page" in r0

    # Ensure HTML document has page: None
    html_res = next(r for r in results if r["doc"].endswith(".html"))
    assert html_res["page"] is None

    # Test sources citation generator
    citations = retriever.get_sources_citation(results)
    assert len(citations) == 2
    assert {"doc": "irctc_refund_rules_jan2026.pdf", "page": 3} in citations
    assert {"doc": "indianrail_refund_rules_2015.html", "page": None} in citations

