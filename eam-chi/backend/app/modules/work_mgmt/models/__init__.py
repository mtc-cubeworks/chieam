# Work Management Models
from .category_of_failure import CategoryOfFailure
from .work_order import WorkOrder
from .work_order_activity import WorkOrderActivity
from .work_order_activity_logs import WorkOrderActivityLogs
from .work_order_checklist import WorkOrderChecklist
from .work_order_checklist_detail import WorkOrderChecklistDetail
from .work_order_equipment import WorkOrderEquipment
from .work_order_equipment_actual_hours import WorkOrderEquipmentActualHours
from .work_order_equipment_assignment import WorkOrderEquipmentAssignment
from .work_order_labor import WorkOrderLabor
from .work_order_labor_actual_hours import WorkOrderLaborActualHours
from .work_order_labor_assignment import WorkOrderLaborAssignment
from .work_order_parts import WorkOrderParts
from .work_order_parts_reservation import WorkOrderPartsReservation

__all__ = [
    "CategoryOfFailure",
    "WorkOrder",
    "WorkOrderActivity",
    "WorkOrderActivityLogs",
    "WorkOrderChecklist",
    "WorkOrderChecklistDetail",
    "WorkOrderEquipment",
    "WorkOrderEquipmentActualHours",
    "WorkOrderEquipmentAssignment",
    "WorkOrderLabor",
    "WorkOrderLaborActualHours",
    "WorkOrderLaborAssignment",
    "WorkOrderParts",
    "WorkOrderPartsReservation",
]
