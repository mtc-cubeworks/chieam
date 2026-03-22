"""
Print Assembler Loader
=======================
Auto-registers all entity-specific print data assemblers.
Called once during app startup or on first print request.
"""
from app.infrastructure.print.registry import register_assembler
from app.infrastructure.print.assemblers.purchase_order import PurchaseOrderAssembler
from app.infrastructure.print.assemblers.purchase_request import PurchaseRequestAssembler


_loaded = False


def load_print_assemblers() -> None:
    """Register all known print data assemblers. Idempotent."""
    global _loaded
    if _loaded:
        return

    register_assembler(PurchaseOrderAssembler())
    register_assembler(PurchaseRequestAssembler())

    _loaded = True
