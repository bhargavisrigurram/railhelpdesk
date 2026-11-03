#!/usr/bin/env python3
"""CLI script to run the Railway Help Desk document ingestion pipeline."""

import argparse
import logging
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ingestion.config import (
    DOCUMENTS_DIR,
    CHROMA_PERSIST_DIRECTORY,
    CHROMA_COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL_NAME,
)
from ingestion.pipeline import IngestionPipeline


def setup_logging(verbose: bool = False):
    """Configure console logging format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Ingest Indian Railways documents into persistent ChromaDB index."
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default=str(DOCUMENTS_DIR),
        help=f"Directory containing PDF and HTML documents (default: {DOCUMENTS_DIR})",
    )
    parser.add_argument(
        "--persist-dir",
        type=str,
        default=str(CHROMA_PERSIST_DIRECTORY),
        help=f"ChromaDB persistence directory (default: {CHROMA_PERSIST_DIRECTORY})",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=CHROMA_COLLECTION_NAME,
        help=f"ChromaDB collection name (default: {CHROMA_COLLECTION_NAME})",
    )
    parser.add_argument(
        "--reindex",
        action="store_true",
        help="Clear existing collection before indexing.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        help=f"Target chunk size in characters (default: {CHUNK_SIZE})",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=CHUNK_OVERLAP,
        help=f"Chunk overlap in characters (default: {CHUNK_OVERLAP})",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable detailed debug logging.",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    logger = logging.getLogger("ingest")
    logger.info("Initializing Railway Document Ingestion Pipeline...")

    try:
        pipeline = IngestionPipeline(
            docs_dir=Path(args.docs_dir),
            persist_dir=Path(args.persist_dir),
            collection_name=args.collection,
            model_name=EMBEDDING_MODEL_NAME,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )

        results = pipeline.run(reindex=args.reindex)

        print("\n" + "=" * 60)
        print("INGESTION PIPELINE SUMMARY")
        print("=" * 60)
        print(f"Status:             {results.get('status')}")
        print(f"Total documents:    {results.get('total_documents')}")
        print(f"Total chunks:       {results.get('total_chunks')}")
        print(f"Records in index:   {results.get('collection_count')}")
        print(f"Duration:           {results.get('duration_seconds')} seconds")
        print("-" * 60)
        print("Per-document statistics:")
        for doc_name, stats in results.get("doc_stats", {}).items():
            print(f"  • {doc_name:<45}: {stats.get('chunks', 0):>3} chunks ({stats.get('status')})")
        print("=" * 60 + "\n")

        if results.get("status") == "success":
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Fatal error during ingestion: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

