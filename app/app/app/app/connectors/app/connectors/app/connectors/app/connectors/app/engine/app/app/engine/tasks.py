from datetime import datetime, timedelta
from typing import Any, Dict

from app.database import SessionLocal
from app.engine.executor import execute_workflow
from app.models import TriggerType, Workflow
from app.worker import celery_app


@celery_app.task(name="app.engine.tasks.run_workflow_task")
def run_workflow_task(workflow_id: int, trigger_payload: Dict[str, Any]) -> None:
    db = SessionLocal()
    try:
        workflow = db.query(Workflow).get(workflow_id)
        if workflow and workflow.is_active:
            execute_workflow(db, workflow, trigger_payload)
    finally:
        db.close()


@celery_app.task(name="app.engine.tasks.poll_cron_workflows")
def poll_cron_workflows() -> None:
    """Runs every minute (see beat_schedule in worker.py). Checks every
    active cron-triggered workflow and fires the ones that are due,
    based on trigger_config = {"interval_seconds": N, "next_run": iso}.
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        workflows = (
            db.query(Workflow)
            .filter(Workflow.trigger_type == TriggerType.cron, Workflow.is_active.is_(True))
            .all()
        )
        for wf in workflows:
            cfg = wf.trigger_config or {}
            interval = cfg.get("interval_seconds", 300)
            next_run_str = cfg.get("next_run")
            next_run = datetime.fromisoformat(next_run_str) if next_run_str else now

            if now >= next_run:
                execute_workflow(db, wf, {"fired_at": now.isoformat(), "source": "cron"})
                cfg["next_run"] = (now + timedelta(seconds=interval)).isoformat()
                wf.trigger_config = cfg
                db.add(wf)
                db.commit()
    finally:
        db.close()
