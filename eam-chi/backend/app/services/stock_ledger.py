"""
Stock Ledger Entry Service
============================
Creates stock ledger entries to maintain an audit trail of all inventory movements.
Called after any inventory-mutating operation (issue, return, receipt, adjustment, transfer).
"""
from typing import Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.document import new_doc, save_doc, get_value


async def create_stock_ledger_entry(
    db: AsyncSession,
    *,
    item: str,
    voucher_type: str,
    voucher_no: str,
    qty_in: int = 0,
    qty_out: int = 0,
    unit_cost: float = 0,
    store: Optional[str] = None,
    bin_id: Optional[str] = None,
    serial_no: Optional[str] = None,
    site: Optional[str] = None,
) -> Any:
    """
    Create a Stock Ledger Entry to record an inventory movement.

    Uses the actual model fields: qty_in, qty_out, value_in, value_out,
    balance_qty, balance_value, voucher_type, voucher_no.
    """
    try:
        value_in = round(qty_in * unit_cost, 2) if qty_in else 0
        value_out = round(qty_out * unit_cost, 2) if qty_out else 0

        # Get current balance from item master for running total
        current_qty = await get_value("item", item, "actual_qty_on_hand", db) or 0
        balance_qty = int(current_qty)
        balance_value = round(balance_qty * unit_cost, 2)

        entry = await new_doc("stock_ledger_entry", db,
            item=item,
            serial_no=serial_no,
            store=store,
            bin=bin_id,
            posting_datetime=datetime.now(),
            qty_in=qty_in,
            qty_out=qty_out,
            value_in=value_in,
            value_out=value_out,
            balance_qty=balance_qty,
            balance_value=balance_value,
            voucher_type=voucher_type,
            voucher_no=voucher_no,
            site=site,
        )
        if entry:
            await save_doc(entry, db, commit=False)
        return entry
    except Exception:
        # Stock ledger is supplementary - don't block the main transaction
        return None


async def ledger_for_issue(
    db: AsyncSession,
    item_issue_id: str,
    item_id: str,
    qty: int,
    unit_cost: float = 0,
    store: Optional[str] = None,
    serial_no: Optional[str] = None,
    site: Optional[str] = None,
) -> Any:
    return await create_stock_ledger_entry(
        db=db, item=item_id,
        voucher_type="Item Issue", voucher_no=item_issue_id,
        qty_out=abs(qty), unit_cost=unit_cost,
        store=store, serial_no=serial_no, site=site,
    )


async def ledger_for_return(
    db: AsyncSession,
    item_return_id: str,
    item_id: str,
    qty: int,
    unit_cost: float = 0,
    store: Optional[str] = None,
    serial_no: Optional[str] = None,
    site: Optional[str] = None,
) -> Any:
    return await create_stock_ledger_entry(
        db=db, item=item_id,
        voucher_type="Item Return", voucher_no=item_return_id,
        qty_in=abs(qty), unit_cost=unit_cost,
        store=store, serial_no=serial_no, site=site,
    )


async def ledger_for_receipt(
    db: AsyncSession,
    receipt_id: str,
    item_id: str,
    qty: int,
    unit_cost: float = 0,
    store: Optional[str] = None,
    serial_no: Optional[str] = None,
    site: Optional[str] = None,
) -> Any:
    return await create_stock_ledger_entry(
        db=db, item=item_id,
        voucher_type="Purchase Receipt", voucher_no=receipt_id,
        qty_in=abs(qty), unit_cost=unit_cost,
        store=store, serial_no=serial_no, site=site,
    )


async def ledger_for_adjustment(
    db: AsyncSession,
    adjustment_id: str,
    item_id: str,
    qty_change: int,
    unit_cost: float = 0,
    store: Optional[str] = None,
    site: Optional[str] = None,
) -> Any:
    qi = qty_change if qty_change > 0 else 0
    qo = abs(qty_change) if qty_change < 0 else 0
    return await create_stock_ledger_entry(
        db=db, item=item_id,
        voucher_type="Inventory Adjustment", voucher_no=adjustment_id,
        qty_in=qi, qty_out=qo, unit_cost=unit_cost,
        store=store, site=site,
    )


async def ledger_for_purchase_return(
    db: AsyncSession,
    return_id: str,
    item_id: str,
    qty: int,
    unit_cost: float = 0,
    store: Optional[str] = None,
    site: Optional[str] = None,
) -> Any:
    return await create_stock_ledger_entry(
        db=db, item=item_id,
        voucher_type="Purchase Return", voucher_no=return_id,
        qty_out=abs(qty), unit_cost=unit_cost,
        store=store, site=site,
    )
