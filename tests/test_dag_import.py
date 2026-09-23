"""
Tests for DAG importability and structure.
Verifies that all DAGs can be parsed by Airflow without errors.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Airflow is installed inside Docker / dedicated CI environment
pytest.importorskip("airflow", reason="apache-airflow is not installed in this environment (runs in Docker)")


class TestDAGImport:
    """Verify DAGs are importable and have correct structure."""

    def test_import_daily_pipeline(self):
        """Daily pipeline DAG should import without errors."""
        from dags.retail_elt_dag import dag

        assert dag is not None
        assert dag.dag_id == "retail_daily_pipeline"

    def test_import_incremental_dag(self):
        """Incremental DAG should import without errors."""
        from dags.incremental_sales_dag import dag

        assert dag is not None
        assert dag.dag_id == "retail_incremental_sales"

    def test_import_backfill_dag(self):
        """Backfill DAG should import without errors."""
        from dags.backfill_dag import dag

        assert dag is not None
        assert dag.dag_id == "retail_backfill"

    def test_import_quality_dag(self):
        """Quality monitor DAG should import without errors."""
        from dags.data_quality_dag import dag

        assert dag is not None
        assert dag.dag_id == "retail_data_quality_monitor"

    def test_daily_pipeline_task_count(self):
        """Daily pipeline should have expected number of tasks."""
        from dags.retail_elt_dag import dag

        task_ids = [t.task_id for t in dag.tasks]
        # Should have: 2 ingestion + 3 transform + 4 marts + snapshot + test_marts + quality
        assert len(task_ids) >= 10

    def test_daily_pipeline_has_task_groups(self):
        """Daily pipeline should use task groups."""
        from dags.retail_elt_dag import dag

        group_ids = [g for g in dag.task_group.children.keys()]
        assert "ingestion" in group_ids
        assert "transformation" in group_ids
        assert "marts" in group_ids

    def test_backfill_is_manual_only(self):
        """Backfill DAG should have no schedule (manual trigger only)."""
        from dags.backfill_dag import dag

        assert dag.schedule_interval is None

    def test_daily_pipeline_has_retries(self):
        """Daily pipeline default_args should include retries."""
        from dags.retail_elt_dag import dag

        assert dag.default_args.get("retries", 0) >= 1

    def test_daily_pipeline_has_sla(self):
        """Daily pipeline should have SLA configured."""
        from dags.retail_elt_dag import dag

        assert dag.default_args.get("sla") is not None

    def test_all_dags_have_owner(self):
        """All DAGs should have an owner set."""
        from dags.retail_elt_dag import dag as daily
        from dags.incremental_sales_dag import dag as incr
        from dags.backfill_dag import dag as backfill
        from dags.data_quality_dag import dag as quality

        for d in [daily, incr, backfill, quality]:
            assert d.default_args.get("owner") == "data-engineering"

    def test_all_dags_have_tags(self):
        """All DAGs should have at least one tag."""
        from dags.retail_elt_dag import dag as daily
        from dags.incremental_sales_dag import dag as incr
        from dags.backfill_dag import dag as backfill
        from dags.data_quality_dag import dag as quality

        for d in [daily, incr, backfill, quality]:
            assert len(d.tags) > 0
            assert "retail" in d.tags
