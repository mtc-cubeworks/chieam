"""
Export Service
==============
Handles exporting entity records to XLSX/CSV format.
Split from import_export.py for SRP compliance (BE#4).
"""
from __future__ import annotations

import csv
import io
from typing import Any, Iterable

from openpyxl import Workbook

from app.meta.registry import EntityMeta


def get_export_fields(meta: EntityMeta) -> list[str]:
    # Export should include `id` so exports can be used as re-import templates.
    fields = [
        f.name
        for f in meta.fields
        if not f.hidden and f.name not in {"created_at", "updated_at"}
    ]
    if "id" in fields:
        fields.remove("id")
        fields.insert(0, "id")
    return fields


async def export_records(
    db: Any,
    meta: EntityMeta,
    records: Iterable[Any],
    format: str = "xlsx",
) -> bytes:
    """Export records to XLSX or CSV format."""
    fields = get_export_fields(meta)

    if format == "xlsx":
        wb = Workbook()
        ws = wb.active
        ws.title = meta.label or meta.name

        # Write header row
        ws.append(fields)

        # Write data rows
        for record in records:
            row = []
            for field in fields:
                value = getattr(record, field, None)
                # Convert datetime objects to strings for Excel compatibility
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                row.append(value)
            ws.append(row)

        bio = io.BytesIO()
        wb.save(bio)
        return bio.getvalue()
    else:
        # CSV format
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = {}
            for field in fields:
                row[field] = getattr(record, field, None)
            writer.writerow(row)
        return output.getvalue().encode("utf-8")
