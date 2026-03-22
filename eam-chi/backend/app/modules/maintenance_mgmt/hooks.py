"""
Maintenance Management Module Hooks
=====================================
Registers entity lifecycle hooks with the hook registry.
"""
from app.application.hooks.registry import hook_registry


# =============================================================================
# Before-Save Hooks
# =============================================================================

# Priority matrix: asset criticality × request severity → calculated priority
_PRIORITY_MATRIX = {
    # (criticality, severity) → priority
    ("A", "Critical"): "Emergency",
    ("A", "High"): "Urgent",
    ("A", "Medium"): "High",
    ("A", "Low"): "Medium",
    ("B", "Critical"): "Urgent",
    ("B", "High"): "High",
    ("B", "Medium"): "Medium",
    ("B", "Low"): "Low",
    ("C", "Critical"): "High",
    ("C", "High"): "Medium",
    ("C", "Medium"): "Low",
    ("C", "Low"): "Low",
}


@hook_registry.before_save("maintenance_request")
async def maintenance_request_before_save(doc, ctx):
    """
    MR-1: Auto-calculate priority from asset criticality × request severity.
    MR-4: Detect duplicate open MRs for the same asset.
    """
    from app.services.document import get_value, get_list

    asset_id = getattr(doc, "asset", None) if not isinstance(doc, dict) else doc.get("asset")
    severity = getattr(doc, "severity", None) if not isinstance(doc, dict) else doc.get("severity")

    # --- MR-1: Priority auto-calculation ---
    if asset_id and severity:
        asset_data = await get_value("asset", asset_id, "*", ctx.db)
        if asset_data:
            criticality = asset_data.get("criticality") or "C"
            calculated_priority = _PRIORITY_MATRIX.get(
                (criticality, severity), "Medium"
            )
            if isinstance(doc, dict):
                doc["priority"] = calculated_priority
            else:
                doc.priority = calculated_priority

    # --- MR-4: Duplicate detection ---
    if asset_id:
        doc_id = getattr(doc, "id", None) if not isinstance(doc, dict) else doc.get("id")
        open_mrs = await get_list(
            "maintenance_request",
            {"asset": asset_id},
            db=ctx.db,
        )
        for mr in open_mrs:
            if mr.get("id") == doc_id:
                continue
            state = mr.get("workflow_state", "")
            if state in ("completed", "closed", "cancelled", "Completed", "Closed", "Cancelled"):
                continue
            # Found an open MR for the same asset — flag as potential duplicate
            if isinstance(doc, dict):
                doc["is_duplicate"] = True
                doc["duplicate_of"] = mr.get("id")
            else:
                doc.is_duplicate = True
                doc.duplicate_of = mr.get("id")
            break

    return doc, None


# =============================================================================
# After-Save Hooks
# =============================================================================

@hook_registry.after_save("planned_maintenance_activity")
async def planned_maintenance_activity_after_save(doc, ctx):
    """
    When a PMA is saved, auto-create a MaintenanceCalendar entry
    if one doesn't exist and the PMA has a maintenance_schedule (frequency).
    """
    from app.services.document import get_value, new_doc, save_doc

    pma_id = doc.id if hasattr(doc, 'id') else None
    if not pma_id:
        return

    schedule = getattr(doc, 'maintenance_schedule', None)
    plan_id = getattr(doc, 'maintenance_plan', None)
    activity_id = getattr(doc, 'maintenance_activity', None)

    if not schedule or not plan_id:
        return

    # Check if calendar already exists for this PMA
    existing = await get_value(
        "maintenance_calendar",
        {"planned_maintenance_activity": pma_id},
        "*",
        ctx.db,
    )
    if existing:
        return

    cal = await new_doc("maintenance_calendar", ctx.db,
        planned_maintenance_activity=pma_id,
        maintenance_plan=plan_id,
        maintenance_activity=activity_id,
        frequency=schedule,
    )
    if cal:
        await save_doc(cal, ctx.db)


@hook_registry.after_save("sensor_data")
async def sensor_data_after_save(doc, ctx):
    """
    When sensor data is recorded, check MaintenanceConditions.
    If a threshold is breached, auto-create a Maintenance Request
    for condition-based maintenance.
    """
    from app.services.document import get_value, get_list, new_doc, save_doc

    sensor_id = getattr(doc, 'sensor', None)
    value_str = getattr(doc, 'value', None)
    if not sensor_id or not value_str:
        return

    try:
        reading = float(value_str)
    except (ValueError, TypeError):
        return

    # Get sensor -> linked asset
    sensor = await get_value("sensor", sensor_id, "*", ctx.db)
    if not sensor:
        return

    asset_id = sensor.get("asset")
    asset_property_id = sensor.get("asset_property")

    # Update the asset property value with latest reading
    if asset_property_id:
        from app.services.document import get_doc
        prop_doc = await get_doc("asset_property", asset_property_id, ctx.db)
        if prop_doc:
            prop_doc.property_value = value_str
            await save_doc(prop_doc, ctx.db, commit=False)

    # --- Threshold Alerting ---
    # Check sensor min/max thresholds and create alert MRs
    sensor_min = sensor.get("min_threshold")
    sensor_max = sensor.get("max_threshold")
    threshold_breached = False

    if sensor_min is not None:
        try:
            if reading < float(sensor_min):
                threshold_breached = True
        except (ValueError, TypeError):
            pass

    if sensor_max is not None:
        try:
            if reading > float(sensor_max):
                threshold_breached = True
        except (ValueError, TypeError):
            pass

    if threshold_breached and asset_id:
        # Check if an open alert MR already exists for this sensor
        existing_alert = await get_value(
            "maintenance_request",
            {"asset": asset_id, "request_type": "Sensor Alert"},
            "*",
            ctx.db,
        )
        if not existing_alert or existing_alert.get("workflow_state") in (
            "completed", "closed", "cancelled",
        ):
            from datetime import datetime, timedelta
            alert_mr = await new_doc("maintenance_request", ctx.db,
                workflow_state="Draft",
                description=(
                    f"Sensor Alert: {sensor.get('sensor_name', sensor_id)} "
                    f"reading {reading} outside threshold "
                    f"[{sensor_min or '-∞'}, {sensor_max or '∞'}]"
                ),
                asset=asset_id,
                due_date=(datetime.now() + timedelta(days=1)).date(),
                site=sensor.get("site"),
                request_type="Sensor Alert",
            )
            if alert_mr:
                await save_doc(alert_mr, ctx.db)

    # Check maintenance conditions linked to this sensor
    conditions = await get_list(
        "maintenance_condition", {"sensor": sensor_id}, db=ctx.db
    )
    if not conditions:
        return

    for cond in conditions:
        operator = cond.get("comparison_operator")
        threshold_prop_id = cond.get("threshold_property")
        pma_id = cond.get("planned_maintenance_activity")

        if not operator or not threshold_prop_id or not pma_id:
            continue

        # Get threshold value from the property definition
        threshold_prop = await get_value("property", threshold_prop_id, "*", ctx.db)
        if not threshold_prop:
            continue

        try:
            threshold = float(threshold_prop.get("default_value") or 0)
        except (ValueError, TypeError):
            continue

        # Evaluate condition
        breached = False
        if operator == ">" and reading > threshold:
            breached = True
        elif operator == ">=" and reading >= threshold:
            breached = True
        elif operator == "<" and reading < threshold:
            breached = True
        elif operator == "<=" and reading <= threshold:
            breached = True
        elif operator == "==" and reading == threshold:
            breached = True

        if not breached:
            continue

        # Check if an open MR already exists for this sensor/PMA
        existing_mr = await get_value(
            "maintenance_request",
            {
                "planned_maintenance_activity": pma_id,
                "asset": asset_id,
            },
            "*",
            ctx.db,
        )
        if existing_mr and existing_mr.get("workflow_state") not in (
            "completed", "closed", "cancelled",
        ):
            continue

        # Auto-create MR for condition-based maintenance
        from datetime import datetime, timedelta

        mr = await new_doc("maintenance_request", ctx.db,
            workflow_state="Draft",
            description=f"Condition-based: sensor {sensor.get('sensor_name', sensor_id)} "
                        f"reading {reading} {operator} threshold {threshold}",
            planned_maintenance_activity=pma_id,
            asset=asset_id,
            due_date=(datetime.now() + timedelta(days=3)).date(),
            site=sensor.get("site"),
            request_type="Condition Based",
        )
        if mr:
            await save_doc(mr, ctx.db)


@hook_registry.after_save("maintenance_order_detail")
async def maintenance_order_detail_after_save(doc, ctx):
    """
    When an MO detail is saved, copy MR description to the detail
    if not already set.
    """
    from app.services.document import get_value, save_doc

    mr_id = getattr(doc, 'maintenance_request', None)
    description = getattr(doc, 'description', None)

    if not mr_id or description:
        return

    mr = await get_value("maintenance_request", mr_id, "*", ctx.db)
    if mr and mr.get("description"):
        doc.description = mr["description"]
        await save_doc(doc, ctx.db)


# =============================================================================
# Workflow Hooks - All routed through central workflow_router
# =============================================================================

@hook_registry.workflow("maintenance_request")
async def maintenance_request_workflow_hook(ctx):
    from app.modules.maintenance_mgmt.workflow_router import route_workflow
    return await route_workflow("maintenance_request", ctx.doc, ctx.action, ctx.db, ctx.user)


@hook_registry.workflow("maintenance_order")
async def maintenance_order_workflow_hook(ctx):
    from app.modules.maintenance_mgmt.workflow_router import route_workflow
    return await route_workflow("maintenance_order", ctx.doc, ctx.action, ctx.db, ctx.user)


# =============================================================================
# MW-5: Condition Monitoring — threshold alerting workflow
# =============================================================================

@hook_registry.after_save("condition_monitoring")
async def condition_monitoring_after_save(doc, ctx):
    """
    MW-5: When a condition monitoring reading is saved, evaluate thresholds
    and auto-create a maintenance request if critical threshold is breached.
    """
    from app.services.document import new_doc, save_doc, get_value
    from datetime import datetime, timedelta

    reading_value = getattr(doc, "reading_value", None)
    critical_threshold = getattr(doc, "critical_threshold", None)
    warning_threshold = getattr(doc, "warning_threshold", None)
    asset_id = getattr(doc, "asset", None)

    if reading_value is None or not asset_id:
        return None

    try:
        reading = float(reading_value)
    except (ValueError, TypeError):
        return None

    alert_status = "Normal"
    if critical_threshold is not None:
        try:
            if reading >= float(critical_threshold):
                alert_status = "Critical"
        except (ValueError, TypeError):
            pass

    if alert_status == "Normal" and warning_threshold is not None:
        try:
            if reading >= float(warning_threshold):
                alert_status = "Warning"
        except (ValueError, TypeError):
            pass

    # Update alert status
    if getattr(doc, "alert_status", None) != alert_status:
        doc.alert_status = alert_status
        await save_doc(doc, ctx.db, commit=False)

    # Auto-create MR on critical threshold breach
    if alert_status == "Critical" and not getattr(doc, "maintenance_request", None):
        mr = await new_doc("maintenance_request", ctx.db,
            workflow_state="Draft",
            description=f"Critical condition alert: reading {reading} exceeds threshold {critical_threshold}",
            asset=asset_id,
            due_date=(datetime.now() + timedelta(days=1)).date(),
            site=getattr(doc, "site", None),
            request_type="Condition Based",
        )
        if mr:
            await save_doc(mr, ctx.db, commit=False)
            doc.maintenance_request = mr.id
            await save_doc(doc, ctx.db)

    return None


# =============================================================================
# XW-4: WO Parts Shortage → Auto-generate PR
# =============================================================================

@hook_registry.after_save("work_order_parts")
async def wo_parts_auto_pr(doc, ctx):
    """
    XW-4: When WO parts are saved and quantity_required > quantity_on_hand,
    auto-generate a Purchase Request for the shortage.
    """
    from app.services.document import get_value, new_doc, save_doc

    item_id = getattr(doc, "item", None)
    qty_required = float(getattr(doc, "quantity_required", 0) or 0)

    if not item_id or qty_required <= 0:
        return None

    # Check current inventory
    item_data = await get_value("item", item_id, "*", ctx.db)
    if not item_data:
        return None

    qty_on_hand = float(item_data.get("actual_qty_on_hand", 0) or 0)
    reserved = float(getattr(doc, "quantity_reserved", 0) or 0)
    shortage = qty_required - (qty_on_hand - reserved)

    if shortage <= 0:
        return None

    # Check if PR already exists for this WO part
    wo_activity_id = getattr(doc, "work_order_activity", None)
    if not wo_activity_id:
        return None

    from app.services.document import get_list
    wo_activity = await get_value("work_order_activity", wo_activity_id, "*", ctx.db)
    wo_id = wo_activity.get("work_order") if wo_activity else None

    # Create PR for shortage
    pr = await new_doc("purchase_request", ctx.db,
        workflow_state="Draft",
        pr_description=f"Auto-PR for WO parts shortage: {item_data.get('item_name', item_id)}",
        site=wo_activity.get("site") if wo_activity else None,
    )
    if pr:
        await save_doc(pr, ctx.db, commit=False)
        pr_line = await new_doc("purchase_request_line", ctx.db,
            purchase_request=pr.id,
            item=item_id,
            item_name=item_data.get("item_name"),
            qty_required=int(shortage),
            unit_of_measure=item_data.get("uom"),
            row_number=1,
        )
        if pr_line:
            await save_doc(pr_line, ctx.db)

    return None


# =============================================================================
# MW-18: Master Data Change workflow
# =============================================================================

@hook_registry.workflow("master_data_change")
async def master_data_change_workflow_hook(ctx):
    """
    MW-18: When a master data change is approved and action is 'apply',
    apply the change to the target entity.
    """
    from app.services.document import get_doc, save_doc

    doc = ctx.doc
    action = ctx.action

    if action in ("apply", "Apply"):
        entity_type = getattr(doc, "entity_type", None)
        entity_id = getattr(doc, "entity_id", None)
        field_name = getattr(doc, "field_name", None)
        new_value = getattr(doc, "new_value", None)

        if entity_type and entity_id and field_name:
            target_doc = await get_doc(entity_type, entity_id, ctx.db)
            if target_doc and hasattr(target_doc, field_name):
                setattr(target_doc, field_name, new_value)
                await save_doc(target_doc, ctx.db, commit=False)

                from datetime import datetime
                doc.approved_date = datetime.now()
                await save_doc(doc, ctx.db)

                return {
                    "status": "success",
                    "message": f"Change applied: {entity_type}.{field_name} updated for {entity_id}",
                }
            return {"status": "error", "message": f"Target entity {entity_type}/{entity_id} not found or field {field_name} does not exist"}
        return {"status": "error", "message": "entity_type, entity_id, and field_name are required"}

    return {"status": "success", "message": f"Master data change workflow '{action}' allowed"}


def register_hooks():
    """Called by the module loader. Hooks are already registered via decorators above."""
    # Import server action modules to trigger their @server_actions.register decorators
    import app.modules.maintenance_mgmt.apis.maintenance_request_actions  # noqa: F401
    # MW-7: FMEA server actions (5-Why, Fishbone, RPN)
    import app.modules.maintenance_mgmt.services.fmea_service  # noqa: F401
    # MR-5/MW-9: Notification hooks
    import app.modules.maintenance_mgmt.services.notification_service  # noqa: F401
