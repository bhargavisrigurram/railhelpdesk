# Indian Railways Passenger Help Desk AI — Capstone Project (Version B)

An AI-powered passenger help desk assistant for Indian Railways capable of answering passenger queries regarding official railway rules (cancellation, refunds, Tatkal, advance reservation, chart preparation) using semantic document retrieval, and train timetable queries using read-only text-to-SQL.

---

## Architecture Overview

```
                      +---------------------------------------+
                      |       User Question / Query           |
                      +-------------------+-------------------+
                                          |
                                          v
                              +-----------------------+
                              |   ask(question)       |
                              |   (helpdesk.py)       |
                              +---+---------------+---+
                                  |               |
               Rule / Policy Query|               | Timetable Query
                                  v               v
                   +--------------------+   +---------------------+
                   | DocumentRetriever  |   |    TimetableDB      |
                   | (retrieval/)       |   | (database/db_service|
                   +---------+----------+   +----------+----------+
                             |                         |
                             v                         v
                   +--------------------+   +---------------------+
                   | PersistentChromaDB |   | SQLite Timetable DB |
                   | (chroma_db/)       |   | (mode=ro)           |
                   +--------------------+   +---------------------+
                             ^
                             |
             [ Offline Ingestion Pipeline ]
                     (ingestion/)
                             |
       +---------------------+---------------------+
       |                     |                     |
       v                     v                     v
+--------------+      +--------------+      +--------------+
| Docling PDF  |      |   RapidOCR   |      | BeautifulSoup|
|  Extraction  |      | Scanned PDFs |      |  HTML Parser |
+--------------+      +--------------+      +--------------+
       |                     |                     |
       +---------------------+---------------------+
                             |
                             v
               +---------------------------+
               | Cleaner & Footnote Binder |
               +-------------+-------------+
                             |
                             v
               +---------------------------+
               | Hierarchical Chunker      |
               +-------------+-------------+
                             |
                             v
               +---------------------------+
               | BAAI/bge-small-en-v1.5    |
               | Embedder (384 dims)       |
               +-------------+-------------+
                             |
                             v
               +---------------------------+
               | ChromaDB Persistent Index |
               +---------------------------+
```

---

## Assigned Module: Document Ingestion & Index Building

This repository contains the complete, production-grade implementation of **Document Ingestion & Index Building**:

1. **Multi-Source Extraction**:
   - **Docling Integration (`PDFExtractor`)**: Converts complex digital PDF documents (`irctc_refund_rules_jan2026.pdf`, `rb_cc08_2026_vande_bharat_sleeper_refund.pdf`, `rb_cc08_2025_tatkal.pdf`) into structured AST representations, capturing headings, paragraphs, and markdown tables.
   - **RapidOCR Fallback**: Automatically detects and processes scanned PDF documents lacking a digital text layer (`rb_cc10_2024_advance_reservation.pdf`, `rb_cc10_2025_reservation_charts.pdf`) and scanned Hindi sections with high accuracy using PyMuPDF page rendering.
   - **HTML Extraction (`HTMLExtractor`)**: Parses policy web pages (`indianrail_refund_rules_2015.html`, `pib_2026-03-24_reform_express.html`) with semantic section extraction, ensuring metadata explicitly records `"page": null` as required.

2. **Structure-Preserving Cleaning (`cleaner.py`)**:
   - Cleans formatting artifacts, unicode dashes, and non-printable characters.
   - Standardizes tabular data into clean Markdown tables.
   - Automatically detects footnote markers (`*`, `Note:`, `Explanation:`) immediately following tables and binds them directly into the table chunk so refund conditions are never severed from their charge matrices.

3. **Context-Aware Semantic Chunking (`chunker.py`)**:
   - Builds hierarchical section trees based on document headings.
   - Chunks text with recursive separator splits and configurable token overlap (default: 500 chars / 100 overlap).
   - Injects contextual document and section headers (`Document: <doc>\nSection: <title>`) into each chunk to maximize retrieval relevance.
   - Splits oversized tables row-by-row while automatically repeating the table header row on subsequent chunks.

4. **Normalized Embedding Generation (`embedder.py`)**:
   - Uses `BAAI/bge-small-en-v1.5` (384-dimensional dense embeddings).
   - Generates L2-normalized embeddings for fast cosine similarity.
   - Applies the recommended BGE search query prefix: `"Represent this sentence for searching relevant passages: "`.

5. **Persistent ChromaDB Indexing (`indexer.py`)**:
   - Stores chunks in a persistent ChromaDB instance (`./chroma_db`) under collection `rail_helpdesk_docs`.
   - Uses `cosine` space distance metric.
   - Deduplicates chunks based on deterministic hash IDs (`{doc}_{chunk_index:04d}`).
   - Automatically re-indexes if collection is empty or `--reindex` is specified.

---

## Directory Structure

```
├── .env.example                               # Template for environment configuration
├── .gitignore                                 # Git ignore rules for caches, venvs, and databases
├── README.md                                  # Project overview and setup instructions
├── SOURCES.md                                 # Source attribution for railway documents & database
├── requirements.txt                           # Project dependencies
├── ingest.py                                  # CLI tool to run the ingestion & indexing pipeline
├── helpdesk.py                                # Main interface providing ask(question)
├── run_questions.py                           # Batch evaluation runner for question sets
│
├── documents/                                 # Official Railway circulars, gazettes, and HTML pages
│   ├── indianrail_refund_rules_2015.html
│   ├── irctc_refund_rules_jan2026.pdf
│   ├── pib_2026-03-24_reform_express.html
│   ├── rb_cc08_2025_tatkal.pdf
│   ├── rb_cc08_2026_vande_bharat_sleeper_refund.pdf
│   ├── rb_cc10_2024_advance_reservation.pdf
│   └── rb_cc10_2025_reservation_charts.pdf
│
├── database/                                  # Timetable SQLite database & schema documentation
│   ├── db_service.py                          # Read-only SQLite query engine with security checks
│   ├── rail_timetable.db                      # SQLite timetable snapshot (8,990 stations, 5,208 trains)
│   └── schema.md                              # Schema details and SQL conventions
│
├── ingestion/                                 # Document Ingestion & Index Building module
│   ├── __init__.py
│   ├── cleaner.py                             # Text & table cleaning and footnote binding
│   ├── chunker.py                             # Semantic, hierarchical chunker with table handling
│   ├── config.py                              # Centralized configuration & environment loader
│   ├── embedder.py                            # BGE-small embedding model wrapper
│   ├── html_extractor.py                      # HTML document extractor
│   ├── indexer.py                             # Persistent ChromaDB indexing & management
│   ├── pdf_extractor.py                       # Docling & RapidOCR PDF parsing
│   └── pipeline.py                            # End-to-end ingestion orchestrator
│
├── retrieval/                                 # Dense retrieval & citation module
│   ├── __init__.py
│   └── retriever.py                           # ChromaDB similarity search & citation builder
│
└── tests/                                     # Automated test suite (21 unit & integration tests)
    ├── test_chunker.py                        # Tests for chunking & table splitting
    ├── test_cleaner.py                        # Tests for cleaning & footnote binding
    ├── test_extraction.py                     # Tests for Docling, RapidOCR, and HTML extraction
    ├── test_helpdesk.py                       # Tests for helpdesk query routing & safety
    ├── test_indexer.py                        # Tests for ChromaDB indexing lifecycle
    └── test_retrieval.py                      # Tests for retriever interface & source formatting
```

---

## Installation & Setup

### 1. Prerequisites
- Python 3.10 to 3.13
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/bhargavisrigurram/railhelpdesk.git
cd railhelpdesk
```

### 3. Create and Activate Virtual Environment
```bash
# On Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables (Optional)
Copy `.env.example` to `.env` to customize settings:
```bash
cp .env.example .env
```

---

## Running Document Ingestion

To extract, clean, chunk, embed, and index all 7 documents into persistent ChromaDB:

```bash
python ingest.py --reindex
```

### CLI Ingestion Options:
- `--docs-dir <path>`: Directory containing PDFs and HTML files (default: `documents`)
- `--persist-dir <path>`: Directory where ChromaDB files are saved (default: `./chroma_db`)
- `--collection <name>`: ChromaDB collection name (default: `rail_helpdesk_docs`)
- `--chunk-size <int>`: Max chunk size in characters (default: `500`)
- `--chunk-overlap <int>`: Overlap between adjacent chunks (default: `100`)
- `--reindex`: Wipe existing collection and re-index all documents from scratch

---

## Running the Help Desk & Evaluations

### Interactive Python Interface
```python
from helpdesk import ask

response = ask("What is the gazette notification number for the Vande Bharat Sleeper refund rules?")
print(response)
# Output:
# {
#   "answer": "G.S.R. 41(E), dated 16 January 2026. It amended the Railway Passengers (Cancellation of Ticket and Refund of Fare) Rules, 2015...",
#   "sources": [{"doc": "rb_cc08_2026_vande_bharat_sleeper_refund.pdf", "page": 1}, ...],
#   "sql": null,
#   "dont_know": false
# }
```

### Running Batch Evaluations
Run evaluation on question sets (e.g. `questions/sample_questions.json`):
```bash
python run_questions.py questions/sample_questions.json sample_results.json
```

The output file matches the required grading format with `id`, `question`, `answer`, `sources`, `sql`, and `dont_know`.

---

## Running Tests

The test suite validates all modules including PDF extraction, RapidOCR scanned document parsing, HTML extraction, text cleaning, chunking, ChromaDB indexing, retrieval citations, and timetable queries:

```bash
pytest tests -v
```

All 21 automated tests pass successfully:
- `tests/test_cleaner.py`: 3 passed (whitespace normalization, markdown tables, footnote binding)
- `tests/test_chunker.py`: 5 passed (recursive split, overlap, table headers, metadata, HTML null page)
- `tests/test_extraction.py`: 4 passed (Docling extraction, RapidOCR scanned OCR, HTML parsing, error handling)
- `tests/test_indexer.py`: 2 passed (index lifecycle, duplicate handling, empty chunk skipping)
- `tests/test_retrieval.py`: 2 passed (similarity search, citation metadata formatting)
- `tests/test_helpdesk.py`: 5 passed (timetable lookup, aggregation, read-only safety, fare out-of-scope)

---

## Troubleshooting & Key Quirks

1. **Scanned Documents**:
   - `rb_cc10_2024_advance_reservation.pdf` and `rb_cc10_2025_reservation_charts.pdf` are scanned images without a native PDF text layer.
   - The ingestion module automatically falls back to `RapidOCR` via PyMuPDF rendering to extract the text without manual intervention.

2. **HTML Documents**:
   - `indianrail_refund_rules_2015.html` and `pib_2026-03-24_reform_express.html` do not have physical page numbers.
   - Citations for these documents are strictly assigned `"page": null` in the JSON response.

3. **Read-Only Database Connection**:
   - All SQL queries against `database/rail_timetable.db` run with SQLite URI `mode=ro`.
   - Any query attempting `INSERT`, `UPDATE`, `DELETE`, or `DROP` is blocked and safely declined.

4. **Offline Embedding & HuggingFace**:
   - Once `BAAI/bge-small-en-v1.5` is downloaded to `~/.cache/huggingface/`, the ingestion and query pipeline can run completely offline by setting `HF_HUB_OFFLINE=1`.

---

## Summary of Files Created / Modified

- `ingestion/config.py`: Centralized configuration, document metadata mappings, and environment settings.
- `ingestion/cleaner.py`: Whitespace normalization, markdown table formatting, and table-footnote binding.
- `ingestion/pdf_extractor.py`: Hybrid Docling + RapidOCR PDF parser for digital and scanned circulars.
- `ingestion/html_extractor.py`: BeautifulSoup HTML parser with section tracking and `"page": null` citations.
- `ingestion/chunker.py`: Hierarchical context-aware chunker with table header replication.
- `ingestion/embedder.py`: BGE-small dense embedding generator with L2 normalization.
- `ingestion/indexer.py`: Persistent ChromaDB indexing with deduplication and metadata serialization.
- `ingestion/pipeline.py`: End-to-end ingestion pipeline runner.
- `ingest.py`: CLI command for full or incremental document indexing.
- `retrieval/retriever.py`: Vector retriever with source citation builder and auto-indexing fallback.
- `database/db_service.py`: Read-only SQLite query service for the train timetable.
- `helpdesk.py`: Core `ask(question)` interface implementing multi-source routing.
- `run_questions.py`: Capstone evaluation runner script.
- `tests/`: 6 comprehensive test suites covering all functionalities.
- `requirements.txt`: Pinned top-level dependencies.
- `.env.example`: Environment variable template.
- `.gitignore`: Clean ignore patterns for environments, caches, and vector DB files.
