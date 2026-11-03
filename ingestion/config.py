"""Configuration settings for document ingestion, retrieval, and help desk."""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = Path(os.getenv("DOCUMENTS_DIR", str(BASE_DIR / "documents")))
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "database" / "rail_timetable.db")))
CHROMA_PERSIST_DIRECTORY = Path(os.getenv("CHROMA_PERSIST_DIRECTORY", str(BASE_DIR / "chroma_db")))

# ChromaDB Settings
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "rail_helpdesk_docs")
HNSW_SPACE = "cosine"

# Embedding Model Settings
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "
EMBEDDING_DIM = 384

# Chunking Settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# LLM / Gemini Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

# Known Document Titles / Keys
DOC_METADATA_MAP = {
    "indianrail_refund_rules_2015.html": {
        "key": "refund_rules_2015",
        "title": "Revised Refund Rules w.e.f. 12.11.2015 (Indian Railways)",
        "is_html": True,
        "date": "2015-11-12",
    },
    "irctc_refund_rules_jan2026.pdf": {
        "key": "irctc_refund_2026",
        "title": "IRCTC Refund Rules and TDR Filing (updated Jan 2026)",
        "is_html": False,
        "date": "2026-01-19",
    },
    "rb_cc10_2024_advance_reservation.pdf": {
        "key": "rb_cc10_2024",
        "title": "Railway Board Commercial Circular No. 10 of 2024 (Advance Reservation Period 60 Days)",
        "is_html": False,
        "date": "2024-10-16",
    },
    "rb_cc08_2025_tatkal.pdf": {
        "key": "rb_cc08_2025",
        "title": "Railway Board Commercial Circular No. 08 of 2025 (Modification in Tatkal Scheme)",
        "is_html": False,
        "date": "2025-06-10",
    },
    "rb_cc10_2025_reservation_charts.pdf": {
        "key": "rb_cc10_2025",
        "title": "Railway Board Commercial Circular No. 10 of 2025 (Preparation of First Reservation Charts)",
        "is_html": False,
        "date": "2025-07-02",
    },
    "rb_cc08_2026_vande_bharat_sleeper_refund.pdf": {
        "key": "rb_cc08_2026",
        "title": "Railway Board Commercial Circular No. 08 of 2026 and Gazette G.S.R. 41(E) (Vande Bharat Sleeper Refund Rules)",
        "is_html": False,
        "date": "2026-01-19",
    },
    "pib_2026-03-24_reform_express.html": {
        "key": "pib_reform_express_2026",
        "title": "PIB Press Release: Indian Railways Announces Five New Reforms Under 'Reform Express'",
        "is_html": True,
        "date": "2026-03-24",
    },
}
