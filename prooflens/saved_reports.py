from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import tempfile
from typing import Any


class SavedReportStore:
    def __init__(self, db_path: Path | str = "prooflens_saved_reports.sqlite3") -> None:
        self._db_path = Path(db_path)
        default_path = Path("prooflens_saved_reports.sqlite3")
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._ensure_schema()
        except sqlite3.OperationalError:
            if self._db_path != default_path:
                raise
            fallback_path = Path(tempfile.gettempdir()) / "prooflens_saved_reports.sqlite3"
            fallback_path.parent.mkdir(parents=True, exist_ok=True)
            self._db_path = fallback_path
            self._ensure_schema()

    def save_report(self, report: dict[str, Any]) -> int:
        sanitized_report = _sanitize_report(report)
        with sqlite3.connect(self._db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO saved_reports (
                    input_type,
                    scenario_family,
                    selected_university,
                    overall_verdict,
                    confidence_level,
                    report_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(sanitized_report.get("input_type", "pasted_text")),
                    str(sanitized_report.get("scenario_family", "")),
                    sanitized_report.get("selected_university"),
                    str(sanitized_report.get("overall_verdict", "Dogrulanamadi")),
                    str(
                        sanitized_report.get("overall_confidence_level")
                        or sanitized_report.get("confidence_level", "Dusuk guven")
                    ),
                    json.dumps(sanitized_report, ensure_ascii=True),
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def list_reports(self, limit: int = 20) -> list[dict[str, Any]]:
        with sqlite3.connect(self._db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT
                    id,
                    created_at,
                    input_type,
                    scenario_family,
                    selected_university,
                    overall_verdict,
                    confidence_level
                FROM saved_reports
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_report(self, report_id: int) -> dict[str, Any] | None:
        with sqlite3.connect(self._db_path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                """
                SELECT
                    id,
                    created_at,
                    input_type,
                    scenario_family,
                    selected_university,
                    overall_verdict,
                    confidence_level,
                    report_json
                FROM saved_reports
                WHERE id = ?
                """,
                (report_id,),
            ).fetchone()

        if row is None:
            return None

        data = dict(row)
        data["report"] = json.loads(data.pop("report_json"))
        return data

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self._db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS saved_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    input_type TEXT NOT NULL,
                    scenario_family TEXT NOT NULL,
                    selected_university TEXT NULL,
                    overall_verdict TEXT NOT NULL,
                    confidence_level TEXT NOT NULL,
                    report_json TEXT NOT NULL
                )
                """
            )
            connection.commit()


def _sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    blocked_keys = {
        "ocr_text",
        "raw_screenshot",
        "raw_screenshot_bytes",
        "image_bytes",
        "upload_bytes",
    }
    for key, value in report.items():
        if key in blocked_keys:
            continue
        sanitized[key] = value
    return sanitized
