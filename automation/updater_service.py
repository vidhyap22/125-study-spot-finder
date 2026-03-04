# updater_service.py
from pathlib import Path
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
# Import your already-existing update function(s)
# e.g. from your_data_module import update_all_context
from automation.update_tasks import update_data

_scheduler = BackgroundScheduler()
_JOB_ID = "global_update_job"


def _ensure_scheduler_started():
    if not _scheduler.running:
        _scheduler.start()


def is_running() -> bool:
    if not _scheduler.running:
        return False
    return _scheduler.get_job(_JOB_ID) is not None


def start(interval_sec: int = 300, run_immediately: bool = True) -> dict:
    """
    Start (or restart) the backend timer.
    """
    if interval_sec <= 0:
        raise ValueError("interval_sec must be > 0")

    _ensure_scheduler_started()

    if run_immediately:
        update_data()

    _scheduler.add_job(
        func=update_data,
        trigger=IntervalTrigger(seconds=interval_sec),
        id=_JOB_ID,
        replace_existing=True,
        max_instances=1,      # prevents overlapping runs
        coalesce=True,        # missed runs collapse into one
        misfire_grace_time=30
    )

    return {"running": True, "interval_sec": interval_sec}


def stop() -> dict:
    """
    Stop the backend timer.
    """
    try:
        _scheduler.remove_job(_JOB_ID)
    except Exception:
        pass

    return {"running": False}


def status() -> dict:
    return {"running": is_running()}