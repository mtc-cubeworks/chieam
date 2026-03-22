"""add_phase3_phase4_tables

Revision ID: i4d5e6f7g8h9
Revises: h3c4d5e6f7g8
Create Date: 2025-01-15 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'i4d5e6f7g8h9'
down_revision: str = 'h3c4d5e6f7g8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Failure Analysis (RCA) ---
    op.create_table(
        'failure_analysis',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('work_order', sa.String(50), sa.ForeignKey('work_order.name'), nullable=True),
        sa.Column('incident', sa.String(50), sa.ForeignKey('incident.name'), nullable=True),
        sa.Column('asset', sa.String(50), sa.ForeignKey('asset.name'), nullable=True),
        sa.Column('category_of_failure', sa.String(50), sa.ForeignKey('category_of_failure.name'), nullable=True),
        sa.Column('cause_code', sa.String(100), nullable=True),
        sa.Column('remedy_code', sa.String(100), nullable=True),
        sa.Column('analysis_method', sa.String(50), nullable=True),
        sa.Column('root_cause_description', sa.Text, nullable=True),
        sa.Column('contributing_factors', sa.Text, nullable=True),
        sa.Column('analysis_date', sa.Date, nullable=True),
        sa.Column('analyst', sa.String(50), sa.ForeignKey('employee.name'), nullable=True),
        sa.Column('site', sa.String(50), sa.ForeignKey('site.name'), nullable=True),
        sa.Column('workflow_state', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # --- Corrective Action (CAPA) ---
    op.create_table(
        'corrective_action',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('failure_analysis', sa.String(50), sa.ForeignKey('failure_analysis.name'), nullable=True),
        sa.Column('action_type', sa.String(50), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('priority', sa.String(20), nullable=True),
        sa.Column('assigned_to', sa.String(50), sa.ForeignKey('employee.name'), nullable=True),
        sa.Column('due_date', sa.Date, nullable=True),
        sa.Column('completion_date', sa.Date, nullable=True),
        sa.Column('verification_date', sa.Date, nullable=True),
        sa.Column('verified_by', sa.String(50), sa.ForeignKey('employee.name'), nullable=True),
        sa.Column('verification_notes', sa.Text, nullable=True),
        sa.Column('work_order', sa.String(50), sa.ForeignKey('work_order.name'), nullable=True),
        sa.Column('workflow_state', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # --- Inspection Route ---
    op.create_table(
        'inspection_route',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('route_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('frequency', sa.String(50), nullable=True),
        sa.Column('site', sa.String(50), sa.ForeignKey('site.name'), nullable=True),
        sa.Column('department', sa.String(50), sa.ForeignKey('department.name'), nullable=True),
        sa.Column('assigned_to', sa.String(50), sa.ForeignKey('employee.name'), nullable=True),
        sa.Column('estimated_duration', sa.Float, nullable=True),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # --- Inspection Point ---
    op.create_table(
        'inspection_point',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('inspection_route', sa.String(50), sa.ForeignKey('inspection_route.name'), nullable=False),
        sa.Column('sequence', sa.Integer, nullable=True),
        sa.Column('asset', sa.String(50), sa.ForeignKey('asset.name'), nullable=True),
        sa.Column('location', sa.String(50), sa.ForeignKey('location.name'), nullable=True),
        sa.Column('measurement_type', sa.String(50), nullable=True),
        sa.Column('parameter_name', sa.String(200), nullable=True),
        sa.Column('expected_value', sa.String(100), nullable=True),
        sa.Column('tolerance', sa.Float, nullable=True),
        sa.Column('unit_of_measure', sa.String(50), nullable=True),
        sa.Column('instructions', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # --- Job Plan ---
    op.create_table(
        'job_plan',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('job_plan_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('work_order_type', sa.String(50), nullable=True),
        sa.Column('asset_class', sa.String(50), sa.ForeignKey('asset_class.name'), nullable=True),
        sa.Column('craft', sa.String(100), nullable=True),
        sa.Column('estimated_hours', sa.Float, nullable=True),
        sa.Column('estimated_cost', sa.Float, nullable=True),
        sa.Column('safety_procedures', sa.Text, nullable=True),
        sa.Column('checklist', sa.String(50), sa.ForeignKey('checklist.name'), nullable=True),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # --- Job Plan Task ---
    op.create_table(
        'job_plan_task',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('job_plan', sa.String(50), sa.ForeignKey('job_plan.name'), nullable=False),
        sa.Column('sequence', sa.Integer, nullable=True),
        sa.Column('task_description', sa.Text, nullable=False),
        sa.Column('craft_required', sa.String(100), nullable=True),
        sa.Column('estimated_hours', sa.Float, nullable=True),
        sa.Column('item', sa.String(50), sa.ForeignKey('item.name'), nullable=True),
        sa.Column('quantity', sa.Float, nullable=True),
        sa.Column('instructions', sa.Text, nullable=True),
        sa.Column('safety_notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # --- Safety Permit ---
    op.create_table(
        'safety_permit',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('permit_type', sa.String(50), nullable=False),
        sa.Column('work_order', sa.String(50), sa.ForeignKey('work_order.name'), nullable=True),
        sa.Column('asset', sa.String(50), sa.ForeignKey('asset.name'), nullable=True),
        sa.Column('location', sa.String(50), sa.ForeignKey('location.name'), nullable=True),
        sa.Column('requested_by', sa.String(50), sa.ForeignKey('employee.name'), nullable=True),
        sa.Column('approved_by', sa.String(50), sa.ForeignKey('employee.name'), nullable=True),
        sa.Column('valid_from', sa.DateTime, nullable=True),
        sa.Column('valid_to', sa.DateTime, nullable=True),
        sa.Column('hazards_identified', sa.Text, nullable=True),
        sa.Column('precautions', sa.Text, nullable=True),
        sa.Column('emergency_procedures', sa.Text, nullable=True),
        sa.Column('site', sa.String(50), sa.ForeignKey('site.name'), nullable=True),
        sa.Column('workflow_state', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # --- Service Contract ---
    op.create_table(
        'service_contract',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('vendor', sa.String(50), sa.ForeignKey('vendor.name'), nullable=False),
        sa.Column('contract_type', sa.String(50), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('start_date', sa.Date, nullable=True),
        sa.Column('end_date', sa.Date, nullable=True),
        sa.Column('annual_value', sa.Float, nullable=True),
        sa.Column('total_contract_value', sa.Float, nullable=True),
        sa.Column('payment_terms', sa.String(100), nullable=True),
        sa.Column('sla_response_hours', sa.Float, nullable=True),
        sa.Column('sla_resolution_hours', sa.Float, nullable=True),
        sa.Column('auto_renew', sa.Boolean, default=False),
        sa.Column('renewal_notice_days', sa.Integer, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('workflow_state', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # --- Warranty Claim ---
    op.create_table(
        'warranty_claim',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('asset', sa.String(50), sa.ForeignKey('asset.name'), nullable=False),
        sa.Column('vendor', sa.String(50), sa.ForeignKey('vendor.name'), nullable=True),
        sa.Column('work_order', sa.String(50), sa.ForeignKey('work_order.name'), nullable=True),
        sa.Column('claim_date', sa.Date, nullable=True),
        sa.Column('warranty_start', sa.Date, nullable=True),
        sa.Column('warranty_end', sa.Date, nullable=True),
        sa.Column('failure_description', sa.Text, nullable=True),
        sa.Column('claim_amount', sa.Float, nullable=True),
        sa.Column('credited_amount', sa.Float, nullable=True),
        sa.Column('vendor_reference', sa.String(100), nullable=True),
        sa.Column('resolution_notes', sa.Text, nullable=True),
        sa.Column('workflow_state', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # --- Meter ---
    op.create_table(
        'meter',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('meter_name', sa.String(200), nullable=True),
        sa.Column('meter_type', sa.String(50), nullable=False),
        sa.Column('asset', sa.String(50), sa.ForeignKey('asset.name'), nullable=False),
        sa.Column('unit_of_measure', sa.String(50), nullable=True),
        sa.Column('last_reading', sa.Float, nullable=True),
        sa.Column('last_reading_date', sa.DateTime, nullable=True),
        sa.Column('rollover_point', sa.Float, nullable=True),
        sa.Column('average_daily_usage', sa.Float, nullable=True),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # --- Meter Reading ---
    op.create_table(
        'meter_reading',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('meter', sa.String(50), sa.ForeignKey('meter.name'), nullable=False),
        sa.Column('reading_value', sa.Float, nullable=False),
        sa.Column('reading_date', sa.DateTime, nullable=True),
        sa.Column('delta', sa.Float, nullable=True),
        sa.Column('work_order', sa.String(50), sa.ForeignKey('work_order.name'), nullable=True),
        sa.Column('recorded_by', sa.String(50), sa.ForeignKey('employee.name'), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('meter_reading')
    op.drop_table('meter')
    op.drop_table('warranty_claim')
    op.drop_table('service_contract')
    op.drop_table('safety_permit')
    op.drop_table('job_plan_task')
    op.drop_table('job_plan')
    op.drop_table('inspection_point')
    op.drop_table('inspection_route')
    op.drop_table('corrective_action')
    op.drop_table('failure_analysis')
