"""
Retail ELT Platform — DAG Callback Functions
=============================================
Shared failure, success, and SLA miss callbacks
used across all Airflow DAGs. Uses structured logging
for consistent observability.
"""

import sys
import os

sys.path.insert(0, "/opt/airflow")

from src.logger import get_logger

logger = get_logger(__name__)


def on_failure_callback(context):
    """
    Called when a task fails. Logs structured failure info
    and would trigger alerts in production (Slack, PagerDuty, email).
    """
    task_instance = context.get("task_instance")
    dag_id = context.get("dag").dag_id
    task_id = task_instance.task_id
    execution_date = context.get("execution_date")
    exception = context.get("exception")

    logger.error(
        f"Task failed: {dag_id}.{task_id}",
        extra={
            "pipeline_name": dag_id,
            "task_name": task_id,
            "status": "FAILED",
            "error": str(exception),
        },
    )

    # In production, send alert:
    # slack_alert(error_msg)
    # pagerduty_trigger(dag_id, task_id, exception)


def on_success_callback(context):
    """Called when the entire DAG succeeds."""
    dag_id = context.get("dag").dag_id
    execution_date = context.get("execution_date")

    logger.info(
        f"DAG completed successfully: {dag_id}",
        extra={
            "pipeline_name": dag_id,
            "status": "SUCCESS",
        },
    )


def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """
    Called when a task misses its SLA deadline.
    Critical for pipeline observability.
    """
    logger.warning(
        f"SLA miss detected: {dag.dag_id}",
        extra={
            "pipeline_name": dag.dag_id,
            "status": "SLA_MISS",
            "tasks": [t.task_id for t in task_list],
            "blocking_tasks": [t.task_id for t in blocking_tis],
        },
    )

    # In production:
    # slack_alert(sla_msg, channel="#data-alerts", severity="warning")
