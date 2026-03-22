"""add_remaining_coverage_fields_and_tables

Revision ID: k6f7g8h9i0j1
Revises: j5e6f7g8h9i0
Create Date: 2026-03-22 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'k6f7g8h9i0j1'
down_revision: str = 'j5e6f7g8h9i0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================================
    # WA-1, WA-3: Work Order Activity — sequencing & completion criteria
    # =========================================================================
    with op.batch_alter_table('work_order_activity') as batch_op:
        batch_op.add_column(sa.Column('sequence', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('predecessor', sa.String(50), sa.ForeignKey('work_order_activity.id'), nullable=True))
        batch_op.add_column(sa.Column('dependency_type', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('acceptance_criteria', sa.Text, nullable=True))
        batch_op.add_column(sa.Column('completion_status', sa.String(50), nullable=True))

    # =========================================================================
    # LA-2, LA-3, LA-4: Work Order Labor — shift, rate, labor type
    # =========================================================================
    with op.batch_alter_table('work_order_labor') as batch_op:
        batch_op.add_column(sa.Column('shift', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('rate', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('rate_type', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('overtime_multiplier', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('labor_type', sa.String(50), nullable=True))

    # =========================================================================
    # PR-1, PR-2: Item Return — reason tracking & inspection
    # =========================================================================
    with op.batch_alter_table('item_return') as batch_op:
        batch_op.add_column(sa.Column('return_reason', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('return_reason_notes', sa.Text, nullable=True))
        batch_op.add_column(sa.Column('inspection_required', sa.Boolean, nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('inspection_status', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('inspection_notes', sa.Text, nullable=True))

    # =========================================================================
    # PI-1, PI-3: Item Issue — WO linkage & destination
    # =========================================================================
    with op.batch_alter_table('item_issue') as batch_op:
        batch_op.add_column(sa.Column('work_order', sa.String(50), sa.ForeignKey('work_order.id'), nullable=True))
        batch_op.add_column(sa.Column('issue_destination', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('require_wo', sa.Boolean, nullable=True, server_default='false'))

    # =========================================================================
    # PQ-1: Purchase Request — budget validation
    # =========================================================================
    with op.batch_alter_table('purchase_request') as batch_op:
        batch_op.add_column(sa.Column('budget_code', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('budget_amount', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('total_amount', sa.Float, nullable=True))

    # =========================================================================
    # PO-3: Vendor — performance tracking fields
    # =========================================================================
    with op.batch_alter_table('vendor') as batch_op:
        batch_op.add_column(sa.Column('contact_name', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('contact_email', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('contact_phone', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('address', sa.Text, nullable=True))
        batch_op.add_column(sa.Column('vendor_type', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('delivery_rating', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('quality_rating', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('overall_rating', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('total_orders', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('on_time_deliveries', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('rejected_deliveries', sa.Integer, nullable=True))

    # =========================================================================
    # PO-4, PO-5: Purchase Order — amendment trail & blanket/contract
    # =========================================================================
    with op.batch_alter_table('purchase_order') as batch_op:
        batch_op.add_column(sa.Column('amendment_number', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('amendment_reason', sa.Text, nullable=True))
        batch_op.add_column(sa.Column('original_po', sa.String(50), sa.ForeignKey('purchase_order.id'), nullable=True))
        batch_op.add_column(sa.Column('po_type', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('blanket_limit', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('released_amount', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('contract_start', sa.Date, nullable=True))
        batch_op.add_column(sa.Column('contract_end', sa.Date, nullable=True))
        batch_op.add_column(sa.Column('payment_terms', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('delivery_terms', sa.String(100), nullable=True))

    # =========================================================================
    # SC-1, SC-2: Stock Count — variance & blind count
    # =========================================================================
    with op.batch_alter_table('stock_count') as batch_op:
        batch_op.add_column(sa.Column('variance_threshold_pct', sa.Float, nullable=True))
        batch_op.add_column(sa.Column('auto_adjust', sa.Boolean, nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('blind_count', sa.Boolean, nullable=True, server_default='false'))

    # =========================================================================
    # SC-3: Stock Count Task — multi-counter
    # =========================================================================
    with op.batch_alter_table('stock_count_task') as batch_op:
        batch_op.add_column(sa.Column('counter_number', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('recount_required', sa.Boolean, nullable=True, server_default='false'))

    # =========================================================================
    # IV-4: Inventory — lot tracking
    # =========================================================================
    with op.batch_alter_table('inventory') as batch_op:
        batch_op.add_column(sa.Column('lot_number', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('expiry_date', sa.Date, nullable=True))

    # =========================================================================
    # IV-1, IV-4, IV-6: Item — reorder, lot, cycle count
    # =========================================================================
    with op.batch_alter_table('item') as batch_op:
        batch_op.add_column(sa.Column('reorder_point', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('reorder_quantity', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('minimum_stock', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('maximum_stock', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('is_lot_tracked', sa.Boolean, nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('cycle_count_frequency', sa.String(50), nullable=True))

    # =========================================================================
    # MW-5: Condition Monitoring (new table)
    # =========================================================================
    op.create_table(
        'condition_monitoring',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('workflow_state', sa.String(50), nullable=True),
        sa.Column('asset', sa.String(50), sa.ForeignKey('asset.id'), nullable=False),
        sa.Column('sensor', sa.String(50), sa.ForeignKey('sensor.id'), nullable=True),
        sa.Column('monitoring_type', sa.String(100), nullable=True),
        sa.Column('reading_value', sa.Float, nullable=True),
        sa.Column('reading_unit', sa.String(50), nullable=True),
        sa.Column('reading_timestamp', sa.DateTime, nullable=True),
        sa.Column('baseline_value', sa.Float, nullable=True),
        sa.Column('warning_threshold', sa.Float, nullable=True),
        sa.Column('critical_threshold', sa.Float, nullable=True),
        sa.Column('alert_status', sa.String(50), nullable=True),
        sa.Column('trend_direction', sa.String(50), nullable=True),
        sa.Column('analysis_notes', sa.Text, nullable=True),
        sa.Column('maintenance_request', sa.String(50), sa.ForeignKey('maintenance_request.id'), nullable=True),
        sa.Column('site', sa.String(50), sa.ForeignKey('site.id'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # =========================================================================
    # MW-11: Asset Transfer (new table)
    # =========================================================================
    op.create_table(
        'asset_transfer',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('workflow_state', sa.String(50), nullable=True),
        sa.Column('asset', sa.String(50), sa.ForeignKey('asset.id'), nullable=False),
        sa.Column('transfer_type', sa.String(100), nullable=True),
        sa.Column('from_site', sa.String(50), sa.ForeignKey('site.id'), nullable=True),
        sa.Column('to_site', sa.String(50), sa.ForeignKey('site.id'), nullable=True),
        sa.Column('from_location', sa.String(50), sa.ForeignKey('location.id'), nullable=True),
        sa.Column('to_location', sa.String(50), sa.ForeignKey('location.id'), nullable=True),
        sa.Column('from_department', sa.String(50), sa.ForeignKey('department.id'), nullable=True),
        sa.Column('to_department', sa.String(50), sa.ForeignKey('department.id'), nullable=True),
        sa.Column('transferred_by', sa.String(50), sa.ForeignKey('employee.id'), nullable=True),
        sa.Column('received_by', sa.String(50), sa.ForeignKey('employee.id'), nullable=True),
        sa.Column('transfer_date', sa.DateTime, nullable=True),
        sa.Column('received_date', sa.DateTime, nullable=True),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # =========================================================================
    # MW-18: Master Data Change (new table)
    # =========================================================================
    op.create_table(
        'master_data_change',
        sa.Column('name', sa.String(50), primary_key=True),
        sa.Column('workflow_state', sa.String(50), nullable=True),
        sa.Column('entity_type', sa.String(100), nullable=True),
        sa.Column('entity_id', sa.String(50), nullable=True),
        sa.Column('change_type', sa.String(100), nullable=True),
        sa.Column('field_name', sa.String(100), nullable=True),
        sa.Column('old_value', sa.Text, nullable=True),
        sa.Column('new_value', sa.Text, nullable=True),
        sa.Column('requested_by', sa.String(50), sa.ForeignKey('employee.id'), nullable=True),
        sa.Column('approved_by', sa.String(50), sa.ForeignKey('employee.id'), nullable=True),
        sa.Column('requested_date', sa.DateTime, nullable=True),
        sa.Column('approved_date', sa.DateTime, nullable=True),
        sa.Column('justification', sa.Text, nullable=True),
        sa.Column('rejection_reason', sa.Text, nullable=True),
        sa.Column('site', sa.String(50), sa.ForeignKey('site.id'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('master_data_change')
    op.drop_table('asset_transfer')
    op.drop_table('condition_monitoring')

    with op.batch_alter_table('item') as batch_op:
        batch_op.drop_column('cycle_count_frequency')
        batch_op.drop_column('is_lot_tracked')
        batch_op.drop_column('maximum_stock')
        batch_op.drop_column('minimum_stock')
        batch_op.drop_column('reorder_quantity')
        batch_op.drop_column('reorder_point')

    with op.batch_alter_table('inventory') as batch_op:
        batch_op.drop_column('expiry_date')
        batch_op.drop_column('lot_number')

    with op.batch_alter_table('stock_count_task') as batch_op:
        batch_op.drop_column('recount_required')
        batch_op.drop_column('counter_number')

    with op.batch_alter_table('stock_count') as batch_op:
        batch_op.drop_column('blind_count')
        batch_op.drop_column('auto_adjust')
        batch_op.drop_column('variance_threshold_pct')

    with op.batch_alter_table('purchase_order') as batch_op:
        batch_op.drop_column('delivery_terms')
        batch_op.drop_column('payment_terms')
        batch_op.drop_column('contract_end')
        batch_op.drop_column('contract_start')
        batch_op.drop_column('released_amount')
        batch_op.drop_column('blanket_limit')
        batch_op.drop_column('po_type')
        batch_op.drop_column('original_po')
        batch_op.drop_column('amendment_reason')
        batch_op.drop_column('amendment_number')

    with op.batch_alter_table('vendor') as batch_op:
        batch_op.drop_column('rejected_deliveries')
        batch_op.drop_column('on_time_deliveries')
        batch_op.drop_column('total_orders')
        batch_op.drop_column('overall_rating')
        batch_op.drop_column('quality_rating')
        batch_op.drop_column('delivery_rating')
        batch_op.drop_column('vendor_type')
        batch_op.drop_column('address')
        batch_op.drop_column('contact_phone')
        batch_op.drop_column('contact_email')
        batch_op.drop_column('contact_name')

    with op.batch_alter_table('purchase_request') as batch_op:
        batch_op.drop_column('total_amount')
        batch_op.drop_column('budget_amount')
        batch_op.drop_column('budget_code')

    with op.batch_alter_table('item_issue') as batch_op:
        batch_op.drop_column('require_wo')
        batch_op.drop_column('issue_destination')
        batch_op.drop_column('work_order')

    with op.batch_alter_table('item_return') as batch_op:
        batch_op.drop_column('inspection_notes')
        batch_op.drop_column('inspection_status')
        batch_op.drop_column('inspection_required')
        batch_op.drop_column('return_reason_notes')
        batch_op.drop_column('return_reason')

    with op.batch_alter_table('work_order_labor') as batch_op:
        batch_op.drop_column('labor_type')
        batch_op.drop_column('overtime_multiplier')
        batch_op.drop_column('rate_type')
        batch_op.drop_column('rate')
        batch_op.drop_column('shift')

    with op.batch_alter_table('work_order_activity') as batch_op:
        batch_op.drop_column('completion_status')
        batch_op.drop_column('acceptance_criteria')
        batch_op.drop_column('dependency_type')
        batch_op.drop_column('predecessor')
        batch_op.drop_column('sequence')
