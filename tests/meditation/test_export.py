"""Tests for admin export utilities."""

from __future__ import annotations

from datetime import datetime

from fastapi.responses import StreamingResponse

from hushai.meditation.admin.export import (
    export_to_csv,
    export_to_excel,
    get_export_response,
)


class TestExportToCsv:
    def test_empty_data(self):
        resp = export_to_csv([], "test.csv")
        assert isinstance(resp, StreamingResponse)
        assert resp.media_type == "text/csv"
        assert "attachment" in resp.headers.get("Content-Disposition", "")

    def test_with_data(self):
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
        resp = export_to_csv(data, "users.csv")
        assert isinstance(resp, StreamingResponse)
        assert resp.media_type == "text/csv"


class TestExportToExcel:
    def test_empty_data(self):
        resp = export_to_excel([], "test.xlsx")
        assert isinstance(resp, StreamingResponse)
        assert (
            resp.media_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    def test_with_data(self):
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
        resp = export_to_excel(data, "users.xlsx")
        assert isinstance(resp, StreamingResponse)
        assert (
            resp.media_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    def test_with_datetime(self):
        data = [
            {"name": "Alice", "created": datetime(2024, 1, 15, 10, 30, 0)},
        ]
        resp = export_to_excel(data, "with_date.xlsx")
        assert isinstance(resp, StreamingResponse)

    def test_with_list_value(self):
        data = [
            {"name": "Alice", "tags": ["a", "b", "c"]},
        ]
        resp = export_to_excel(data, "with_list.xlsx")
        assert isinstance(resp, StreamingResponse)

    def test_with_none_value(self):
        data = [
            {"name": "Alice", "note": None},
        ]
        resp = export_to_excel(data, "with_none.xlsx")
        assert isinstance(resp, StreamingResponse)


class TestGetExportResponse:
    def test_csv_format(self):
        data = [{"id": 1, "name": "test"}]
        resp = get_export_response(data, "export", "csv")
        assert isinstance(resp, StreamingResponse)
        assert resp.media_type == "text/csv"
        assert "export_" in resp.headers.get("Content-Disposition", "")
        assert ".csv" in resp.headers.get("Content-Disposition", "")

    def test_xlsx_format(self):
        data = [{"id": 1, "name": "test"}]
        resp = get_export_response(data, "export", "xlsx")
        assert isinstance(resp, StreamingResponse)
        assert (
            resp.media_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert "export_" in resp.headers.get("Content-Disposition", "")
        assert ".xlsx" in resp.headers.get("Content-Disposition", "")

    def test_default_is_csv(self):
        data = [{"id": 1}]
        resp = get_export_response(data, "export", "unknown")
        assert resp.media_type == "text/csv"
