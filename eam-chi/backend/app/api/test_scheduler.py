"""
Test Scheduler API
==================
Manual trigger endpoints for testing scheduler functions.
"""
import logging
from fastapi import APIRouter
from app.services.scheduler import test_scheduler_every_minute, daily_maintenance_interval_check

logger = logging.getLogger("scheduler_test")

router = APIRouter(prefix="/test", tags=["scheduler"])

@router.post("/scheduler/test-minute")
async def test_scheduler_minute():
    """Manually trigger the every-minute test function."""
    try:
        await test_scheduler_every_minute()
        return {"status": "success", "message": "Test scheduler executed successfully"}
    except Exception as e:
        logger.error(f"Test scheduler failed: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/scheduler/interval-check")
async def test_interval_check():
    """Manually trigger the daily maintenance interval check."""
    try:
        await daily_maintenance_interval_check()
        return {"status": "success", "message": "Daily maintenance interval check executed successfully"}
    except Exception as e:
        logger.error(f"Interval check failed: {e}")
        return {"status": "error", "message": str(e)}
