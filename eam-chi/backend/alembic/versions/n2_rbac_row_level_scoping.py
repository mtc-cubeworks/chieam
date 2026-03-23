"""Add RBAC row-level data scoping columns

- roles.data_scope (own/team/site/all)
- created_by + modified_by on ALL entity tables
- employee.reports_to (self-referencing FK)

Revision ID: n2_rbac_scope
Revises: m1_merge_gap
Create Date: 2026-06-15 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect as sa_inspect

revision: str = 'n2_rbac_scope'
down_revision: Union[str, None] = 'm1_merge_gap'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All entity tables that inherit from BaseModel
ENTITY_TABLES = [
    "account", "annual_budget", "asset", "asset_class",
    "asset_class_availability", "asset_class_property",
    "asset_maintenance_history", "asset_position", "asset_property",
    "asset_transfer", "bin", "breakdown", "category_of_failure",
    "cause_code", "checklist", "checklist_details",
    "condition_monitoring", "contractor", "corrective_action",
    "cost_code", "currency", "department", "disposed", "email_log",
    "employee", "employee_site", "equipment",
    "equipment_availability", "equipment_availability_details",
    "equipment_group", "equipment_schedule",
    "equipment_schedule_details", "error_log", "failure_analysis",
    "holiday", "incident", "incident_employee", "inspection",
    "inspection_point", "inspection_route", "inventory",
    "inventory_adjustment", "inventory_adjustment_line", "item",
    "item_class", "item_issue", "item_issue_line", "item_return",
    "item_return_line", "job_plan", "job_plan_task", "labor",
    "labor_availability", "labor_availability_details", "labor_group",
    "leave_application", "leave_type", "location", "location_type",
    "maintenance_activity", "maintenance_calendar",
    "maintenance_condition", "maintenance_equipment",
    "maintenance_interval", "maintenance_order",
    "maintenance_order_detail", "maintenance_parts",
    "maintenance_plan", "maintenance_request", "maintenance_trade",
    "manufacturer", "master_data_change", "meter", "meter_reading",
    "model", "note", "note_seen_by", "organization",
    "planned_maintenance_activity", "position", "position_relation",
    "property", "property_type", "purchase_order",
    "purchase_order_line", "purchase_receipt", "purchase_request",
    "purchase_request_line", "purchase_return", "putaway",
    "reason_code", "remedy_code", "request_activity_type",
    "request_for_quotation", "rfq_line", "safety_permit",
    "sales_order", "sales_order_item", "scheduled_job_log",
    "sensor", "sensor_data", "series", "service_contract",
    "service_request", "site", "stock_count", "stock_count_line",
    "stock_count_task", "stock_ledger_entry", "store", "sub_asset",
    "system", "system_type", "tool_checkout", "trade",
    "trade_availability", "trade_labor", "transfer",
    "transfer_receipt", "unit_of_measure", "vendor",
    "vendor_invoice", "vendor_invoice_line", "warranty_claim",
    "work_order", "work_order_activity", "work_order_activity_logs",
    "work_order_checklist", "work_order_checklist_detail",
    "work_order_equipment", "work_order_equipment_actual_hours",
    "work_order_equipment_assignment", "work_order_labor",
    "work_order_labor_actual_hours", "work_order_labor_assignment",
    "work_order_parts", "work_order_parts_reservation",
    "work_schedule", "work_schedule_details", "zone",
]


def _has_column(table_name: str, column_name: str) -> bool:
    """Check if a column already exists in a table."""
    bind = op.get_bind()
    inspector = sa_inspect(bind)
    columns = [c["name"] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    # 1. Add data_scope to roles table
    if not _has_column("roles", "data_scope"):
        op.add_column(
            "roles",
            sa.Column("data_scope", sa.String(20), nullable=False, server_default="all"),
        )

    # 2. Add created_by and modified_by to every entity table
    for table in ENTITY_TABLES:
        if not _has_column(table, "created_by"):
            op.add_column(
                table,
                sa.Column("created_by", sa.String(50), nullable=True),
            )
        if not _has_column(table, "modified_by"):
            op.add_column(
                table,
                sa.Column("modified_by", sa.String(50), nullable=True),
            )

    # 3. Add reports_to to employee table
    if not _has_column("employee", "reports_to"):
        op.add_column(
            "employee",
            sa.Column("reports_to", sa.String(50), sa.ForeignKey("employee.id"), nullable=True),
        )


def downgrade() -> None:
    # 3. Drop reports_to from employee
    op.drop_column("employee", "reports_to")

    # 2. Drop created_by and modified_by from every entity table
    for table in reversed(ENTITY_TABLES):
        op.drop_column(table, "modified_by")
        op.drop_column(table, "created_by")

    # 1. Drop data_scope from roles
    op.drop_column("roles", "data_scope")
