from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.connectors.registry import CONNECTOR_REGISTRY
from app.models import Run, RunStatus, Workflow


def execute_workflow(db: Session, workflow: Workflow, trigger_payload: Dict[str, Any]) -> Run:
    run = Run(
        workflow_id=workflow.id,
        status=RunStatus.running,
        trigger_payload=trigger_payload,
        started_at=datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    context: Dict[str, Any] = {"trigger": trigger_payload, "steps": {}}

    try:
        for step in workflow.steps:
            connector = CONNECTOR_REGISTRY.get(step.connector_type)
            if connector is None:
                raise ValueError(f"Unknown connector_type: {step.connector_type}")

            result = connector.run(step.config, context)
            context["steps"][str(step.order)] = result

        run.status = RunStatus.success
        run.result = context["steps"]
    except Exception as exc:  # noqa: BLE001 - we want to record any failure
        run.status = RunStatus.failed
        run.error = str(exc)
    finally:
        run.finished_at = datetime.utcnow()
        db.add(run)
        db.commit()

    return run
