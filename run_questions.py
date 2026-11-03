#!/usr/bin/env python3
"""Official runner script for Indian Railways Passenger Help Desk capstone evaluation.

Usage:
    python run_questions.py <questions_file.json> <results_file.json>
"""

import sys
import json
import logging
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from helpdesk import ask

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_questions")


def run_questions(questions_path: str, results_path: str):
    """Load questions, invoke ask(question) for each, and output results list."""
    q_file = Path(questions_path)
    r_file = Path(results_path)

    if not q_file.exists():
        logger.error(f"Questions file not found: {q_file}")
        sys.exit(1)

    logger.info(f"Loading questions from: {q_file}")
    with open(q_file, "r", encoding="utf-8") as f:
        questions_data = json.load(f)

    if not isinstance(questions_data, list):
        logger.error("Expected JSON questions file to contain a list of objects.")
        sys.exit(1)

    results = []
    total = len(questions_data)
    logger.info(f"Evaluating {total} questions...")

    for i, item in enumerate(questions_data):
        q_id = item.get("id", f"Q{i+1:02d}")
        q_text = item.get("question", "")
        logger.info(f"[{i+1}/{total}] Processing {q_id}: {q_text[:70]}...")

        output = ask(q_text)

        result_entry = {
            "id": q_id,
            "question": q_text,
            "answer": output.get("answer", ""),
            "sources": output.get("sources", []),
            "sql": output.get("sql"),
            "dont_know": output.get("dont_know", False),
        }
        results.append(result_entry)

    r_file.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Writing {len(results)} results to: {r_file}")
    with open(r_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info("Evaluation complete.")


def main():
    if len(sys.argv) < 3:
        print("Usage: python run_questions.py <questions.json> <results.json>")
        sys.exit(1)

    questions_path = sys.argv[1]
    results_path = sys.argv[2]
    run_questions(questions_path, results_path)


if __name__ == "__main__":
    main()

