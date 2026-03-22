"""
Document Service
================
Backward-compatible facade that re-exports from the split modules:
- document_query.py  (read-only operations)
- document_mutation.py (write operations)

Usage remains unchanged:
    from app.services.document import get_doc, new_doc, save_doc, get_meta, get_value

Last Updated: 2026-02-09
"""
# Re-export query operations
from app.services.document_query import (  # noqa: F401
    get_meta,
    get_doc,
    get_value,
    get_list,
    _get_model,
    _record_to_dict,
)

# Re-export mutation operations
from app.services.document_mutation import (  # noqa: F401
    new_doc,
    save_doc,
    insert_doc,
    delete_doc,
    apply_workflow_state,
)
