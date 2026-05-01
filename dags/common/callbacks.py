"""
Retail ELT Platform — DAG Callback Functions
=============================================
Shared failure, success, and SLA miss callbacks
used across all Airflow DAGs.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


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

    error_msg = (
        f"🔴 TASK FAILED | DAG: {dag_id} | Task: {task_id} | "
        f"Execution: {execution_date} | Error: {exception}"
    )
    logger.error(error_msg)

    # In production, send alert:
    # slack_alert(error_msg)
    # pagerduty_trigger(dag_id, task_id, exception)


def on_success_callback(context):
    """Called when the entire DAG succeeds."""
    dag_id = context.get("dag").dag_id
    execution_date = context.get("execution_date")

    logger.info(
        f"✅ DAG SUCCESS | DAG: {dag_id} | Execution: {execution_date} | "
        f"Completed at: {datetime.now().isoformat()}"
    )


def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """
    Called when a task misses its SLA deadline.
    Critical for pipeline observability.
    """
    sla_msg = (
        f"⚠️ SLA MISS | DAG: {dag.dag_id} | "
        f"Tasks: {[t.task_id for t in task_list]} | "
        f"Blocking: {[t.task_id for t in blocking_tis]}"
    )
    logger.warning(sla_msg)

    # In production:
    # slack_alert(sla_msg, channel="#data-alerts", severity="warning")
