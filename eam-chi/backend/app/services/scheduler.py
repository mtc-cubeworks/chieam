"""
Scheduler Service
==================
APScheduler-based cron job runner for the EAM backend.
Handles frequency-based auto-generation of maintenance requests
from maintenance_calendar entries.

Frequency options (from maintenance_calendar.frequency):
- Weekly: generates every 7 days
- Monthly: generates every 30 days
- Quarterly: generates every 90 days
- Annually: generates every 365 days
- Day of Week: generates on specific day each week
- Day of Month: generates on specific day each month
"""
import logging
import traceback
from datetime import date, datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker

logger = logging.getLogger("scheduler")


async def _log_job(job_id: str, job_name: str, started_at: datetime, status: str,
                   records_created: int = 0, records_updated: int = 0,
                   error_message: str | None = None, error_tb: str | None = None,
                   details: str | None = None, trigger_type: str = "Cron",
                   cron_expression: str | None = None) -> None:
    """Helper to persist a job execution log."""
    try:
        from app.infrastructure.logging.job_logger import log_job_execution
        completed = datetime.now()
        duration = (completed - started_at).total_seconds()
        await log_job_execution(
            job_id=job_id, job_name=job_name, status=status,
            started_at=started_at, completed_at=completed,
            duration_seconds=duration, records_created=records_created,
            records_updated=records_updated, error_message=error_message,
            error_traceback_str=error_tb, details=details,
            trigger_type=trigger_type, cron_expression=cron_expression,
        )
    except Exception as e:
        logger.warning(f"Failed to log job execution: {e}")

scheduler = AsyncIOScheduler()

# Frequency → days between generations
FREQUENCY_DAYS = {
    "Weekly": 7,
    "Monthly": 30,
    "Quarterly": 90,
    "Annually": 365,
}


async def generate_from_calendar():
    """
    Check all maintenance_calendar entries and auto-generate
    maintenance_requests for upcoming due dates based on frequency.
    Runs daily at 1:00 AM.
    """
    from app.services.document import new_doc, save_doc
    from app.services.document_query import _get_model

    logger.info("🕐 Running PM calendar auto-generation job...")
    started_at = datetime.now()

    async with async_session_maker() as db:
        try:
            cal_model = _get_model("maintenance_calendar")
            mr_model = _get_model("maintenance_request")
            pma_model = _get_model("planned_maintenance_activity")
            act_model = _get_model("maintenance_activity")

            if not cal_model or not mr_model:
                logger.warning("Required models not found, skipping")
                return

            # Get all calendar entries with a frequency
            result = await db.execute(
                select(cal_model).where(cal_model.frequency.isnot(None))
            )
            calendars = result.scalars().all()

            if not calendars:
                logger.info("No calendar entries with frequency found")
                return

            today = date.today()
            created = 0

            for cal in calendars:
                freq = cal.frequency
                pma_id = cal.planned_maintenance_activity
                if not pma_id or not freq:
                    continue

                days = FREQUENCY_DAYS.get(freq)
                if not days:
                    continue

                # Find the last MR for this PMA
                last_mr_result = await db.execute(
                    select(mr_model)
                    .where(mr_model.planned_maintenance_activity == pma_id)
                    .order_by(mr_model.due_date.desc())
                    .limit(1)
                )
                last_mr = last_mr_result.scalar_one_or_none()

                if last_mr and last_mr.due_date:
                    last_date = last_mr.due_date
                    next_due = last_date + timedelta(days=days)
                else:
                    # No existing MR, schedule from today
                    next_due = today

                # Only generate if next_due is within the next 7 days
                if next_due <= today + timedelta(days=7):
                    # Get activity name from PMA -> maintenance_activity
                    activity_name = ""
                    if pma_model:
                        pma_result = await db.execute(
                            select(pma_model).where(pma_model.id == pma_id)
                        )
                        pma = pma_result.scalar_one_or_none()
                        if pma:
                            activity_name = pma.maintenance_activity_name or ""
                            if not activity_name and pma.maintenance_activity and act_model:
                                act_result = await db.execute(
                                    select(act_model).where(act_model.id == pma.maintenance_activity)
                                )
                                act = act_result.scalar_one_or_none()
                                if act:
                                    activity_name = act.activity_name or ""

                    # Create WO
                    wo = await new_doc("work_order", db,
                                       workflow_state="Requested",
                                       work_order_type="Preventive Maintenance",
                                       description=f"PM: {activity_name}",
                                       due_date=next_due)
                    if wo:
                        wo = await save_doc(wo, db, commit=False)

                        # Create WOA
                        start_dt = datetime(next_due.year, next_due.month, next_due.day, 8, 0)
                        woa = await new_doc("work_order_activity", db,
                                            workflow_state="Awaiting Resources",
                                            work_order=wo.id,
                                            description=activity_name,
                                            start_date=start_dt,
                                            end_date=start_dt + timedelta(minutes=30))
                        if woa:
                            woa = await save_doc(woa, db, commit=False)

                            # Create MR
                            lead_days = cal.lead_calendar_days or 0
                            mr = await new_doc("maintenance_request", db,
                                               workflow_state="Draft",
                                               due_date=next_due,
                                               description=activity_name,
                                               planned_maintenance_activity=pma_id,
                                               work_order_activity=woa.id)
                            if mr:
                                await save_doc(mr, db, commit=False)
                                created += 1

            await db.commit()
            logger.info(f"✅ Auto-generated {created} maintenance requests")
            await _log_job("pm_calendar_auto_generate", "PM Calendar Auto-Generation",
                           started_at, "Success", records_created=created,
                           cron_expression="0 1 * * *")

        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            await db.rollback()
            await _log_job("pm_calendar_auto_generate", "PM Calendar Auto-Generation",
                           started_at, "Error", error_message=str(e),
                           error_tb=traceback.format_exc(), cron_expression="0 1 * * *")


async def test_scheduler_every_minute():
    """
    Test function to validate scheduler works.
    Creates a simple log entry every minute.
    """
    from app.services.document import get_list, new_doc, save_doc
    from app.services.document_query import _get_model

    logger.info("⏰ Test scheduler running - creating test record...")
    started_at = datetime.now()

    async with async_session_maker() as db:
        try:
            test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"✅ Scheduler test executed at {test_time}")
            await _log_job("test_scheduler_every_minute", "Test Scheduler (Every Minute)",
                           started_at, "Success", details=f"Test ping at {test_time}",
                           cron_expression="* * * * *")

        except Exception as e:
            logger.error(f"❌ Test scheduler error: {e}")
            await db.rollback()
            await _log_job("test_scheduler_every_minute", "Test Scheduler (Every Minute)",
                           started_at, "Error", error_message=str(e),
                           error_tb=traceback.format_exc(), cron_expression="* * * * *")


async def daily_maintenance_interval_check():
    """
    Check asset property values against maintenance intervals.
    Based on Frappe's daily_maintenance_check function.
    Runs daily at 2:00 AM.
    """
    from app.services.document import new_doc, save_doc, get_list
    from app.services.document_query import _get_model

    logger.info("🔧 Running daily maintenance interval check...")
    started_at = datetime.now()

    async with async_session_maker() as db:
        try:
            # Get models
            interval_model = _get_model("maintenance_interval")
            plan_model = _get_model("maintenance_plan") 
            asset_class_model = _get_model("asset_class")
            asset_model = _get_model("asset")
            asset_prop_model = _get_model("asset_property")
            property_model = _get_model("property")
            mr_model = _get_model("maintenance_request")
            woa_model = _get_model("work_order_activity")

            if not all([interval_model, plan_model, asset_class_model, asset_model, 
                      asset_prop_model, property_model, mr_model, woa_model]):
                logger.warning("Required models not found for interval check")
                return

            # Get all maintenance intervals
            result = await db.execute(select(interval_model))
            intervals = result.scalars().all()

            if not intervals:
                logger.info("No maintenance intervals found")
                return

            created_count = 0
            today = date.today()

            for interval in intervals:
                try:
                    # Get maintenance plan
                    if not interval.maintenance_plan:
                        continue
                    
                    plan_result = await db.execute(
                        select(plan_model).where(plan_model.id == interval.maintenance_plan)
                    )
                    plan = plan_result.scalar_one_or_none()
                    if not plan or not plan.asset_class:
                        continue

                    # Get asset class for lead time
                    lead_time = 7  # default
                    asset_class_result = await db.execute(
                        select(asset_class_model).where(asset_class_model.id == plan.asset_class)
                    )
                    asset_class = asset_class_result.scalar_one_or_none()
                    if asset_class and hasattr(asset_class, 'due_date_lead_time'):
                        try:
                            lead_time = int(asset_class.due_date_lead_time or 7)
                        except (ValueError, TypeError):
                            pass

                    # Get active assets for this asset class
                    assets_result = await db.execute(
                        select(asset_model).where(
                            and_(
                                asset_model.asset_class == plan.asset_class,
                                asset_model.is_active == True
                            )
                        )
                    )
                    assets = assets_result.scalars().all()

                    for asset in assets:
                        # Check required properties
                        if not interval.running_interval_property or not interval.last_interval_property:
                            continue

                        # Get property values
                        running_prop_result = await db.execute(
                            select(asset_prop_model).where(
                                and_(
                                    asset_prop_model.asset == asset.id,
                                    asset_prop_model.property == interval.running_interval_property
                                )
                            )
                        )
                        running_prop = running_prop_result.scalar_one_or_none()

                        last_prop_result = await db.execute(
                            select(asset_prop_model).where(
                                and_(
                                    asset_prop_model.asset == asset.id,
                                    asset_prop_model.property == interval.last_interval_property
                                )
                            )
                        )
                        last_prop = last_prop_result.scalar_one_or_none()

                        if not running_prop or not last_prop:
                            continue

                        # Get property definitions for validation
                        running_def_result = await db.execute(
                            select(property_model).where(property_model.id == interval.running_interval_property)
                        )
                        running_def = running_def_result.scalar_one_or_none()

                        if not running_def:
                            continue

                        # Calculate running interval
                        try:
                            running_value = float(running_prop.property_value or 0)
                            last_value = float(last_prop.property_value or 0)
                            running_interval = running_value - last_value
                        except (ValueError, TypeError):
                            continue

                        # Check if maintenance is due
                        try:
                            interval_value = float(interval.interval or 0)
                            lead_interval = float(interval.lead_interval or 0)
                        except (ValueError, TypeError):
                            continue

                        if running_interval >= (interval_value - lead_interval):
                            # Check if MR already exists
                            existing_result = await db.execute(
                                select(mr_model).where(
                                    and_(
                                        mr_model.asset == asset.id,
                                        mr_model.workflow_state.in_(['Pending Approval', 'Approved', 'Release', 'Draft'])
                                    )
                                )
                            )
                            existing = existing_result.scalar_one_or_none()
                            
                            if existing:
                                continue

                            # Create Work Order Activity
                            woa = await new_doc("work_order_activity", db,
                                workflow_state="Awaiting Resources",
                                description=f"Maintenance for {asset.asset_tag or asset.id}",
                                asset=asset.id,
                                location=asset.location,
                                site=asset.site,
                                department=asset.department)
                            
                            woa = await save_doc(woa, db, commit=False)

                            # Create Maintenance Request
                            due_date = today + timedelta(days=lead_time)
                            mr = await new_doc("maintenance_request", db,
                                workflow_state="Draft",
                                description=f"Maintenance Request for {asset.asset_tag or asset.id} - {asset.description or ''}",
                                planned_maintenance_activity=interval.planned_maintenance_activity,
                                asset=asset.id,
                                location=asset.location,
                                due_date=due_date,
                                site=asset.site,
                                department=asset.department,
                                work_order_activity=woa.id,
                                maintenance_interval_property=interval.last_interval_property,
                                running_interval_value=running_interval)
                            
                            mr = await save_doc(mr, db, commit=False)
                            
                            # Auto-approve the MR (similar to Frappe workflow)
                            mr.workflow_state = "Approved"
                            mr = await save_doc(mr, db, commit=False)
                            
                            created_count += 1
                            logger.info(f"✅ Created maintenance request for asset {asset.id}")

                except Exception as e:
                    logger.error(f"❌ Error processing interval {interval.id}: {e}")
                    continue

            await db.commit()
            logger.info(f"✅ Daily maintenance interval check completed. Created {created_count} maintenance requests")
            await _log_job("daily_maintenance_interval_check", "Daily Maintenance Interval Check",
                           started_at, "Success", records_created=created_count,
                           cron_expression="0 2 * * *")

        except Exception as e:
            logger.error(f"❌ Daily maintenance interval check failed: {e}")
            await db.rollback()
            await _log_job("daily_maintenance_interval_check", "Daily Maintenance Interval Check",
                           started_at, "Error", error_message=str(e),
                           error_tb=traceback.format_exc(), cron_expression="0 2 * * *")


async def sla_monitoring_check():
    """
    Check MRs and WOs for SLA breaches.
    Flags records that have been in intermediate states longer than threshold.
    Runs every 4 hours.
    """
    from app.services.document_query import _get_model

    logger.info("⏱️ Running SLA monitoring check...")
    started_at = datetime.now()

    async with async_session_maker() as db:
        try:
            mr_model = _get_model("maintenance_request")
            wo_model = _get_model("work_order")
            flagged = 0
            today = date.today()

            # Check MRs stuck in intermediate states > 7 days (no due_date or overdue)
            if mr_model:
                result = await db.execute(
                    select(mr_model).where(
                        mr_model.workflow_state.in_(["Draft", "Pending Approval", "Approved"])
                    )
                )
                mrs = result.scalars().all()
                for mr in mrs:
                    due = getattr(mr, "due_date", None)
                    created = getattr(mr, "created_at", None) or getattr(mr, "requested_date", None)
                    if due and hasattr(due, "date"):
                        due = due.date() if callable(getattr(due, "date", None)) else due
                    if due and due < today:
                        mr.is_overdue = True
                        flagged += 1
                    elif created:
                        if hasattr(created, "date"):
                            created = created.date() if callable(getattr(created, "date", None)) else created
                        if isinstance(created, date) and (today - created).days > 7:
                            mr.is_overdue = True
                            flagged += 1

            # Check WOs stuck in in_progress > 30 days
            if wo_model:
                result = await db.execute(
                    select(wo_model).where(
                        wo_model.workflow_state == "in_progress"
                    )
                )
                wos = result.scalars().all()
                for wo in wos:
                    due = getattr(wo, "due_date", None)
                    if due and hasattr(due, "date"):
                        due = due.date() if callable(getattr(due, "date", None)) else due
                    if due and due < today:
                        wo.is_overdue = True
                        flagged += 1

            if flagged:
                await db.commit()
            logger.info(f"⏱️ SLA check complete. Flagged {flagged} overdue record(s)")
            await _log_job("sla_monitoring_check", "SLA Monitoring Check",
                           started_at, "Success", records_updated=flagged,
                           cron_expression="30 */4 * * *")

        except Exception as e:
            logger.error(f"❌ SLA monitoring check failed: {e}")
            await db.rollback()
            await _log_job("sla_monitoring_check", "SLA Monitoring Check",
                           started_at, "Error", error_message=str(e),
                           error_tb=traceback.format_exc(), cron_expression="30 */4 * * *")


async def daily_reorder_check():
    """
    Scan all inventory items and auto-generate Purchase Requests
    for items below their reorder point.
    Runs daily at 3:00 AM.
    """
    from app.services.document import new_doc, save_doc
    from app.services.document_query import _get_model

    logger.info("📦 Running daily reorder point check...")
    started_at = datetime.now()

    async with async_session_maker() as db:
        try:
            item_model = _get_model("item")
            pr_model = _get_model("purchase_request")
            prl_model = _get_model("purchase_request_line")

            if not item_model:
                logger.warning("Item model not found")
                return

            # Get items with reorder_point set
            result = await db.execute(
                select(item_model).where(
                    and_(
                        item_model.reorder_point.isnot(None),
                        item_model.reorder_point > 0,
                    )
                )
            )
            items = result.scalars().all()

            created = 0
            for item in items:
                actual = getattr(item, "actual_qty_on_hand", 0) or 0
                reorder_point = getattr(item, "reorder_point", 0) or 0
                reorder_qty = getattr(item, "reorder_qty", 0) or reorder_point

                if actual >= reorder_point:
                    continue

                # Check for open PRs for this item
                if prl_model:
                    existing = await db.execute(
                        select(prl_model).where(
                            and_(
                                prl_model.item == item.id,
                                prl_model.workflow_state.notin_(
                                    ["fully_received", "cancelled", "closed"]
                                ),
                            )
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                # Create PR
                qty_needed = max(reorder_qty, reorder_point - actual)
                pr = await new_doc("purchase_request", db,
                    workflow_state="Draft",
                    description=f"Auto-reorder: {item.item_name or item.id}",
                    request_type="Inventory Reorder",
                )
                if pr:
                    await save_doc(pr, db, commit=False)
                    prl = await new_doc("purchase_request_line", db,
                        purchase_request=pr.id,
                        item=item.id,
                        item_name=getattr(item, "item_name", None),
                        qty_required=int(qty_needed),
                        unit_of_measure=getattr(item, "uom", None),
                    )
                    if prl:
                        await save_doc(prl, db, commit=False)
                    created += 1

            if created:
                await db.commit()
            logger.info(f"📦 Reorder check complete. Created {created} purchase request(s)")
            await _log_job("daily_reorder_check", "Daily Inventory Reorder Check",
                           started_at, "Success", records_created=created,
                           cron_expression="0 3 * * *")

        except Exception as e:
            logger.error(f"❌ Daily reorder check failed: {e}")
            await db.rollback()
            await _log_job("daily_reorder_check", "Daily Inventory Reorder Check",
                           started_at, "Error", error_message=str(e),
                           error_tb=traceback.format_exc(), cron_expression="0 3 * * *")


async def overdue_wo_check():
    """
    Flag overdue Work Orders and auto-escalate if needed.
    Runs daily at 6:00 AM.
    """
    from app.services.document_query import _get_model

    logger.info("🚨 Running overdue WO check...")
    started_at = datetime.now()

    async with async_session_maker() as db:
        try:
            wo_model = _get_model("work_order")
            if not wo_model:
                return

            today = date.today()
            result = await db.execute(
                select(wo_model).where(
                    and_(
                        wo_model.workflow_state.in_(["in_progress", "approved"]),
                        wo_model.due_date.isnot(None),
                        wo_model.due_date < today,
                    )
                )
            )
            overdue_wos = result.scalars().all()
            flagged = 0

            for wo in overdue_wos:
                if not getattr(wo, "is_overdue", False):
                    wo.is_overdue = True
                    flagged += 1

            if flagged:
                await db.commit()
            logger.info(f"🚨 Overdue WO check complete. Flagged {flagged} work order(s)")
            await _log_job("overdue_wo_check", "Overdue Work Order Check",
                           started_at, "Success", records_updated=flagged,
                           cron_expression="0 6 * * *")

        except Exception as e:
            logger.error(f"❌ Overdue WO check failed: {e}")
            await db.rollback()
            await _log_job("overdue_wo_check", "Overdue Work Order Check",
                           started_at, "Error", error_message=str(e),
                           error_tb=traceback.format_exc(), cron_expression="0 6 * * *")


async def daily_kpi_calculation():
    """Daily KPI calculation - computes MTBF, MTTR, PM Compliance for the trailing 30 days."""
    started_at = datetime.now()
    try:
        async with async_session_maker() as db:
            from app.services.kpi import calculate_all_kpis

            end = datetime.now()
            start = end - timedelta(days=30)
            result = await calculate_all_kpis(db, start_date=start, end_date=end)
            kpis = result.get("kpis", {})

            logger.info(
                f"KPI calculation complete — "
                f"MTBF: {kpis.get('mtbf', {}).get('mtbf_hours', 'N/A')}h, "
                f"MTTR: {kpis.get('mttr', {}).get('mttr_hours', 'N/A')}h, "
                f"PM Compliance: {kpis.get('pm_compliance', {}).get('compliance_pct', 'N/A')}%"
            )
            await _log_job("daily_kpi_calculation", "Daily KPI Calculation",
                           started_at, "Success", cron_expression="0 7 * * *")
    except Exception as e:
        logger.error(f"KPI calculation failed: {e}")
        await _log_job("daily_kpi_calculation", "Daily KPI Calculation",
                       started_at, "Error", error_message=str(e),
                       error_tb=traceback.format_exc(), cron_expression="0 7 * * *")


def start_scheduler():
    """Start the APScheduler with all maintenance jobs."""
    # Daily maintenance interval check - runs at 2:00 AM (like Frappe)
    scheduler.add_job(
        daily_maintenance_interval_check,
        CronTrigger(hour=2, minute=0),
        id="daily_maintenance_interval_check",
        name="Daily Maintenance Interval Check",
        replace_existing=True,
    )
    
    # PM calendar auto-generation - runs daily at 1:00 AM
    scheduler.add_job(
        generate_from_calendar,
        CronTrigger(hour=1, minute=0),
        id="pm_calendar_auto_generate",
        name="PM Calendar Auto-Generation",
        replace_existing=True,
    )

    # SLA monitoring - runs every 4 hours
    scheduler.add_job(
        sla_monitoring_check,
        CronTrigger(hour="*/4", minute=30),
        id="sla_monitoring_check",
        name="SLA Monitoring Check",
        replace_existing=True,
    )

    # Daily reorder point check - runs at 3:00 AM
    scheduler.add_job(
        daily_reorder_check,
        CronTrigger(hour=3, minute=0),
        id="daily_reorder_check",
        name="Daily Inventory Reorder Check",
        replace_existing=True,
    )

    # Overdue WO check - runs daily at 6:00 AM
    scheduler.add_job(
        overdue_wo_check,
        CronTrigger(hour=6, minute=0),
        id="overdue_wo_check",
        name="Overdue Work Order Check",
        replace_existing=True,
    )

    # Daily KPI calculation - runs at 7:00 AM
    scheduler.add_job(
        daily_kpi_calculation,
        CronTrigger(hour=7, minute=0),
        id="daily_kpi_calculation",
        name="Daily KPI Calculation",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("📅 Scheduler started:")
    logger.info("  - PM calendar: Daily at 1:00 AM")
    logger.info("  - Interval check: Daily at 2:00 AM")
    logger.info("  - Reorder check: Daily at 3:00 AM")
    logger.info("  - SLA monitoring: Every 4 hours at :30")
    logger.info("  - Overdue WO check: Daily at 6:00 AM")
    logger.info("  - KPI calculation: Daily at 7:00 AM")


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("📅 Scheduler stopped")
