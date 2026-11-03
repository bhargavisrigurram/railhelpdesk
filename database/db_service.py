"""Read-only SQLite timetable database query service.

Adheres to project requirement:
Run all SQL on a read-only connection:
sqlite3.connect("file:database/rail_timetable.db?mode=ro", uri=True)
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from ingestion.config import DATABASE_PATH

logger = logging.getLogger(__name__)

FORBIDDEN_SQL_KEYWORDS = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "REPLACE", "PRAGMA"]


class TimetableDB:
    """Read-only interface to rail_timetable.db."""

    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

    def get_connection(self) -> sqlite3.Connection:
        """Create a read-only SQLite connection."""
        uri_path = f"file:{self.db_path.resolve().as_posix()}?mode=ro"
        conn = sqlite3.connect(uri_path, uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, sql: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """Safely execute a read-only SELECT query."""
        sql_clean = sql.strip().strip(";")
        first_word = sql_clean.split()[0].upper() if sql_clean else ""

        if first_word != "SELECT" and first_word != "WITH":
            raise PermissionError(f"Modification queries are forbidden on read-only timetable: {first_word}")

        # Check for harmful statements
        for keyword in FORBIDDEN_SQL_KEYWORDS:
            if keyword in sql_clean.upper().split():
                raise PermissionError(f"Statement contains forbidden keyword: {keyword}")

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql_clean, params)
            else:
                cursor.execute(sql_clean)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_train_by_number(self, train_number: str) -> Optional[Dict[str, Any]]:
        """Lookup train by train number."""
        sql = "SELECT number, name, type_code, from_station_code, to_station_code, departure, arrival, duration_min, distance_km FROM trains WHERE number = ?"
        rows = self.execute_query(sql, (train_number,))
        return rows[0] if rows else None

    def count_trains_by_type(self, type_code: str) -> int:
        """Count trains by type code."""
        sql = "SELECT COUNT(*) as count FROM trains WHERE type_code = ?"
        rows = self.execute_query(sql, (type_code,))
        return rows[0]["count"] if rows else 0

    def find_trains_between_stations(self, from_code: str, to_code: str) -> List[Dict[str, Any]]:
        """Find trains stopping at from_code then to_code in sequence order."""
        sql = """
        SELECT t.number, t.name, a.departure, b.arrival
        FROM stops a
        JOIN stops b ON b.train_number = a.train_number AND b.stop_sequence > a.stop_sequence
        JOIN trains t ON t.number = a.train_number
        WHERE a.station_code = ? AND b.station_code = ?
        ORDER BY a.departure;
        """
        return self.execute_query(sql, (from_code, to_code))

    def get_schedule_stop(self, train_number: str, station_code: str) -> Optional[Dict[str, Any]]:
        """Get departure and arrival for a train at a specific station."""
        sql = "SELECT train_number, station_code, day, arrival, departure FROM schedules WHERE train_number = ? AND station_code = ?"
        rows = self.execute_query(sql, (train_number, station_code))
        return rows[0] if rows else None

