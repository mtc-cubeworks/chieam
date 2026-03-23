"""add_remaining_gap_fields_and_tables

Revision ID: j5e6f7g8h9i0
Revises: i4d5e6f7g8h9
Create Date: 2026-03-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'j5e6f7g8h9i0'
down_revision: str = 'i4d5e6f7g8h9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================================
    # AR-1, AR-2, AR-3, AR-5, AR-6, AR-7: Asset field additions
    # =========================================================================
    with op.batch_alter_table('asset') as batch_op:
        batch_op.add_column(sa.Column('lifecycle_state', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('parent_asset', sa.String(50), sa.ForeignKey('asset.id'), nullable=True))
        batch_op.add_column(sa.Column('functional_location', sa.String(50), sa.ForeignKey('location.id'), nullable=True))
        batch_op.add_column(sa.Column('criticality', sa.String(10), nullable=True))
        batch_op.add_column(sa.Column('risk_score', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('warranty_start', sa.Date, nullable=True))
        batch_op.add_column(sa.Column('warranty_end', sa.Date, nullable=True))
        batch_op.add_column(sa.Column('warranty_vendor', sa.String(50), sa.ForeignKey('vendor.id'), nullable=True))
        batch_op.add_column(sa.Column('manufacturer', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('manufacturer_part_number', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('rated_capacity', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('rated_power', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('weight', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('technical_specs', sa.Text, nullable=True))
        batch_op.add_column(sa.Column('depreciation_method', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('useful_life_years', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('salvage_value', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('accumulated_depreciation', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('commissioning_date', sa.Date, nullable=True))

    # =========================================================================
    # IN-1, IN-4, IN-5: Incident field additions
    # =========================================================================
    with op.batch_alter_table('incident') as batch_op:
        batch_op.add_column(sa.Column('incident_subtype', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('osha_recordable', sa.Boolean, nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('regulatory_status', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('reporting_deadline', sa.Date, nullable=True))
        batch_op.add_column(sa.Column('failure_analysis', sa.String(50), sa.ForeignKey('failure_analysis.id'), nullable=True))

    # =========================================================================
    # WO-2, WO-3, WO-4, WO-5, WO-8, WO-9, WO-10: Work Order field additions
    # =========================================================================
    with op.batch_alter_table('work_order') as batch_op:
        batch_op.add_column(sa.Column('job_plan', sa.String(50), sa.ForeignKey('job_plan.id'), nullable=True))
        batch_op.add_column(sa.Column('scheduled_start', sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column('scheduled_end', sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column('actual_start', sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column('actual_end', sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column('estimated_cost', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('approval_level', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('approved_by', sa.String(50), sa.ForeignKey('employee.id'), nullable=True))
        batch_op.add_column(sa.Column('total_labor_cost', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('total_equipment_cost', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('total_parts_cost', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('total_cost', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('safety_permit', sa.String(50), sa.ForeignKey('safety_permit.id'), nullable=True))
        batch_op.add_column(sa.Column('loto_required', sa.Boolean, nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('technician_findings', sa.Text, nullable=True))
        batch_op.add_column(sa.Column('work_performed', sa.Text, nullable=True))
        batch_op.add_column(sa.Column('recommendations', sa.Text, nullable=True))
        batch_op.add_column(sa.Column('follow_up_work_order', sa.String(50), sa.ForeignKey('work_order.id'), nullable=True))
        batch_op.add_column(sa.Column('parent_work_order', sa.String(50), sa.ForeignKey('work_order.id'), nullable=True))

    # =========================================================================
    # MR-2, MR-6: Maintenance Request field additions
    # =========================================================================
    with op.batch_alter_table('maintenance_request') as batch_op:
        batch_op.add_column(sa.Column('sla_response_due', sa.Date, nullable=True))
        batch_op.add_column(sa.Column('sla_resolution_due', sa.Date, nullable=True))
        batch_op.add_column(sa.Column('sla_status', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('is_overdue', sa.Boolean, nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('request_category', sa.String(100), nullable=True))

    # =========================================================================
    # MW-17: Vendor Invoice + Lines (3-way matching)
    # =========================================================================
    op.create_table(
        'vendor_invoice',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('workflow_state', sa.String(50), nullable=True),
        sa.Column('vendor', sa.String(50), sa.ForeignKey('vendor.id'), nullable=False),
        sa.Column('purchase_order', sa.String(50), sa.ForeignKey('purchase_order.id'), nullable=True),
        sa.Column('invoice_number', sa.String(100), nullable=True),
        sa.Column('invoice_date', sa.Date, nullable=True),
        sa.Column('due_date', sa.Date, nullable=True),
        sa.Column('total_amount', sa.Float, nullable=True),
        sa.Column('tax_amount', sa.Float, nullable=True),
        sa.Column('currency', sa.String(50), sa.ForeignKey('currency.id'), nullable=True),
        sa.Column('payment_terms', sa.String(100), nullable=True),
        sa.Column('match_status', sa.String(50), nullable=True),
        sa.Column('match_variance', sa.Float, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('site', sa.String(50), sa.ForeignKey('site.id'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'vendor_invoice_line',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('vendor_invoice', sa.String(50), sa.ForeignKey('vendor_invoice.id'), nullable=False),
        sa.Column('purchase_order_line', sa.String(50), sa.ForeignKey('purchase_order_line.id'), nullable=True),
        sa.Column('item', sa.String(50), sa.ForeignKey('item.id'), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('quantity_invoiced', sa.Float, nullable=True),
        sa.Column('unit_price', sa.Float, nullable=True),
        sa.Column('line_total', sa.Float, nullable=True),
        sa.Column('row_number', sa.Integer, nullable=True),
        sa.Column('match_status', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # =========================================================================
    # MW-14: Tool / Equipment Checkout
    # =========================================================================
    op.create_table(
        'tool_checkout',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('workflow_state', sa.String(50), nullable=True),
        sa.Column('tool', sa.String(50), sa.ForeignKey('asset.id'), nullable=False),
        sa.Column('checked_out_to', sa.String(50), sa.ForeignKey('employee.id'), nullable=True),
        sa.Column('work_order', sa.String(50), sa.ForeignKey('work_order.id'), nullable=True),
        sa.Column('checkout_date', sa.DateTime, nullable=True),
        sa.Column('expected_return_date', sa.Date, nullable=True),
        sa.Column('actual_return_date', sa.DateTime, nullable=True),
        sa.Column('condition_at_checkout', sa.String(50), nullable=True),
        sa.Column('condition_at_return', sa.String(50), nullable=True),
        sa.Column('calibration_due_date', sa.Date, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('site', sa.String(50), sa.ForeignKey('site.id'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('tool_checkout')
    op.drop_table('vendor_invoice_line')
    op.drop_table('vendor_invoice')

    with op.batch_alter_table('maintenance_request') as batch_op:
        batch_op.drop_column('request_category')
        batch_op.drop_column('is_overdue')
        batch_op.drop_column('sla_status')
        batch_op.drop_column('sla_resolution_due')
        batch_op.drop_column('sla_response_due')

    with op.batch_alter_table('work_order') as batch_op:
        batch_op.drop_column('parent_work_order')
        batch_op.drop_column('follow_up_work_order')
        batch_op.drop_column('recommendations')
        batch_op.drop_column('work_performed')
        batch_op.drop_column('technician_findings')
        batch_op.drop_column('loto_required')
        batch_op.drop_column('safety_permit')
        batch_op.drop_column('total_cost')
        batch_op.drop_column('total_parts_cost')
        batch_op.drop_column('total_equipment_cost')
        batch_op.drop_column('total_labor_cost')
        batch_op.drop_column('approved_by')
        batch_op.drop_column('approval_level')
        batch_op.drop_column('estimated_cost')
        batch_op.drop_column('actual_end')
        batch_op.drop_column('actual_start')
        batch_op.drop_column('scheduled_end')
        batch_op.drop_column('scheduled_start')
        batch_op.drop_column('job_plan')

    with op.batch_alter_table('incident') as batch_op:
        batch_op.drop_column('failure_analysis')
        batch_op.drop_column('reporting_deadline')
        batch_op.drop_column('regulatory_status')
        batch_op.drop_column('osha_recordable')
        batch_op.drop_column('incident_subtype')

    with op.batch_alter_table('asset') as batch_op:
        batch_op.drop_column('commissioning_date')
        batch_op.drop_column('accumulated_depreciation')
        batch_op.drop_column('salvage_value')
        batch_op.drop_column('useful_life_years')
        batch_op.drop_column('depreciation_method')
        batch_op.drop_column('technical_specs')
        batch_op.drop_column('weight')
        batch_op.drop_column('rated_power')
        batch_op.drop_column('rated_capacity')
        batch_op.drop_column('manufacturer_part_number')
        batch_op.drop_column('manufacturer')
        batch_op.drop_column('warranty_vendor')
        batch_op.drop_column('warranty_end')
        batch_op.drop_column('warranty_start')
        batch_op.drop_column('risk_score')
        batch_op.drop_column('criticality')
        batch_op.drop_column('functional_location')
        batch_op.drop_column('parent_asset')
        batch_op.drop_column('lifecycle_state')
