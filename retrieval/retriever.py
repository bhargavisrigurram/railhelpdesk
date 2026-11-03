"""Document retrieval module querying persistent ChromaDB vector store.

Compatible with the course retrieval interface:
Returns structured search results with source citations:
{"rank": int, "chunk_id": str, "text": str, "doc": str, "page": Optional[int], "distance": float}
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb

from ingestion.config import (
    CHROMA_PERSIST_DIRECTORY,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
)
from ingestion.embedder import DocumentEmbedder

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Retrieves document chunks matching user queries."""

    def __init__(
        self,
        persist_dir: Path = CHROMA_PERSIST_DIRECTORY,
        collection_name: str = CHROMA_COLLECTION_NAME,
        embedder: Optional[DocumentEmbedder] = None,
    ):
        self.persist_dir = Path(persist_dir)
        self.collection_name = collection_name
        self.embedder = embedder or DocumentEmbedder(model_name=EMBEDDING_MODEL_NAME)

        logger.info(f"Connecting to persistent ChromaDB at {self.persist_dir} (collection: {self.collection_name})")
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
        if self.collection.count() == 0:
            from ingestion.config import DOCS_DIR
            if DOCS_DIR.exists():
                logger.info("ChromaDB collection is empty. Automatically indexing documents from %s...", DOCS_DIR)
                from ingestion.pipeline import IngestionPipeline
                pipeline = IngestionPipeline(
                    docs_dir=DOCS_DIR,
                    persist_dir=self.persist_dir,
                    collection_name=self.collection_name,
                    embedder=self.embedder,
                )
                pipeline.run(reindex=True)
                self.collection = self.client.get_collection(name=self.collection_name)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve top_k most similar document chunks for a question.

        Returns list of results:
        [
            {
                "rank": 1,
                "chunk_id": "irctc_refund_2026_0005",
                "text": "...",
                "doc": "irctc_refund_rules_jan2026.pdf",
                "page": 3,
                "distance": 0.142,
                "section_title": "Cancellation Charges for RAC or Waitlisted Tickets",
            },
            ...
        ]
        """
        if self.collection.count() == 0:
            logger.warning("ChromaDB collection is empty! Run ingestion first.")
            return []

        query_embedding = self.embedder.embed_query(query)

        where_clause = None
        if filters:
            if len(filters) == 1:
                where_clause = filters
            else:
                where_clause = {"$and": [{k: v} for k, v in filters.items()]}

        k = min(top_k, self.collection.count())
        response = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k,
            where=where_clause,
            include=["documents", "metadatas", "distances"],
        )

        results: List[Dict[str, Any]] = []
        if not response or not response.get("ids") or not response["ids"][0]:
            return results

        ids = response["ids"][0]
        docs = response["documents"][0]
        metas = response["metadatas"][0]
        distances = response["distances"][0] if "distances" in response else [0.0] * len(ids)

        for i in range(len(ids)):
            meta = metas[i] if i < len(metas) else {}
            doc_name = meta.get("doc", "")
            raw_page = meta.get("page", -1)
            is_html = meta.get("is_html", False) or doc_name.endswith(".html")

            # In accordance with project instructions:
            # HTML documents have no page numbers: cite them with page: None (null)
            page_val = None if (is_html or raw_page == -1) else raw_page

            results.append({
                "rank": i + 1,
                "chunk_id": ids[i],
                "text": docs[i],
                "doc": doc_name,
                "page": page_val,
                "distance": float(distances[i]),
                "section_title": meta.get("section_title", ""),
                "section_path": meta.get("section_path", ""),
            })

        return results

    def get_sources_citation(self, results: List[Dict[str, Any]], max_sources: int = 3) -> List[Dict[str, Any]]:
        """Extract unique document sources with page citation for ask() output."""
        sources: List[Dict[str, Any]] = []
        seen = set()

        for r in results:
            doc = r.get("doc")
            page = r.get("page")
            if not doc:
                continue

            key = (doc, page)
            if key not in seen:
                seen.add(key)
                sources.append({"doc": doc, "page": page})
                if len(sources) >= max_sources:
                    break

        return sources

