"""Tests for the BloomScheduler module."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pandas as pd
import pytest

from databloom.scheduler import BloomScheduler, ReportConfig


class TestReportConfig:
    """Tests for the ReportConfig dataclass."""

    def test_default_values(self) -> None:
        config = ReportConfig()
        assert config.title == "Scheduled Report"
        assert config.theme == "business_blue"
        assert config.output_path == "./output/scheduled_report.xlsx"
        assert config.data_factory is None
        assert config.chart_type == "auto"
        assert config.on_complete is None
        assert config.on_error is None
        assert config.auto_create_dir is True

    def test_custom_values(self) -> None:
        config = ReportConfig(
            title="My Report",
            theme="tech_dark",
            output_path="/tmp/report.xlsx",
            chart_type="column",
            auto_create_dir=False,
        )
        assert config.title == "My Report"
        assert config.theme == "tech_dark"
        assert config.output_path == "/tmp/report.xlsx"
        assert config.chart_type == "column"
        assert config.auto_create_dir is False

    def test_path_object(self) -> None:
        config = ReportConfig(output_path=Path("/tmp/out.xlsx"))
        assert config.output_path == Path("/tmp/out.xlsx")

    def test_on_complete_callback(self) -> None:
        results: list[Path] = []
        config = ReportConfig(
            on_complete=lambda p: results.append(p),
        )
        assert results == []
        assert config.on_complete is not None
        config.on_complete(Path("/tmp/test.xlsx"))
        assert results == [Path("/tmp/test.xlsx")]

    def test_on_error_callback(self) -> None:
        errors: list[Exception] = []
        config = ReportConfig(
            on_error=lambda e: errors.append(e),
        )
        exc = ValueError("test")
        assert config.on_error is not None
        config.on_error(exc)
        assert errors == [exc]


class TestBloomSchedulerImport:
    """Tests for the import guard when schedule is not installed."""

    def test_import_error_when_schedule_missing(self) -> None:
        """BloomScheduler raises ImportError with helpful message when
        schedule is not installed."""
        with mock.patch.dict("sys.modules", {"schedule": None}):
            with pytest.raises(ImportError) as exc_info:
                BloomScheduler()
            assert "schedule is required" in str(exc_info.value)
            assert "databloom[scheduler]" in str(exc_info.value)


class TestBloomSchedulerJobRegistration:
    """Tests for job scheduling methods using the real schedule library."""

    @pytest.fixture(autouse=True)
    def _clear_schedule(self) -> None:
        """Clear the global schedule default_scheduler between tests."""
        import schedule

        schedule.clear()

    @pytest.fixture
    def scheduler(self) -> BloomScheduler:
        return BloomScheduler()

    @pytest.fixture
    def config(self) -> ReportConfig:
        return ReportConfig(
            title="Test Report",
            output_path="/tmp/test.xlsx",
        )

    def test_daily_registers_job(self, scheduler: BloomScheduler, config: ReportConfig) -> None:
        scheduler.daily(config, at="08:00")
        assert scheduler.job_count == 1

    def test_weekly_registers_job(self, scheduler: BloomScheduler, config: ReportConfig) -> None:
        scheduler.weekly(config, day="monday", at="09:00")
        assert scheduler.job_count == 1

    def test_monthly_registers_job(self, scheduler: BloomScheduler, config: ReportConfig) -> None:
        scheduler.monthly(config, day=15, at="07:00")
        assert scheduler.job_count == 1

    def test_every_hours_registers_job(
        self, scheduler: BloomScheduler, config: ReportConfig
    ) -> None:
        scheduler.every_hours(config, hours=4)
        assert scheduler.job_count == 1

    def test_every_minutes_registers_job(
        self, scheduler: BloomScheduler, config: ReportConfig
    ) -> None:
        scheduler.every_minutes(config, minutes=15)
        assert scheduler.job_count == 1

    def test_multiple_jobs(self, scheduler: BloomScheduler, config: ReportConfig) -> None:
        scheduler.daily(config, at="09:00")
        scheduler.weekly(config, day="friday", at="18:00")
        scheduler.monthly(config, day=1, at="07:00")
        assert scheduler.job_count == 3

    def test_monthly_invalid_day_low(self, scheduler: BloomScheduler, config: ReportConfig) -> None:
        with pytest.raises(ValueError, match="Monthly day must be 1-28"):
            scheduler.monthly(config, day=0)

    def test_monthly_invalid_day_high(
        self, scheduler: BloomScheduler, config: ReportConfig
    ) -> None:
        with pytest.raises(ValueError, match="Monthly day must be 1-28"):
            scheduler.monthly(config, day=29)

    def test_monthly_days_1_and_28_valid(
        self, scheduler: BloomScheduler, config: ReportConfig
    ) -> None:
        scheduler.monthly(config, day=1)
        scheduler.monthly(config, day=28)
        assert scheduler.job_count == 2


class TestBloomSchedulerReportGeneration:
    """Tests for _generate_report with various inputs."""

    @pytest.fixture
    def mock_schedule(self) -> mock.MagicMock:
        mock_sched = mock.MagicMock()
        mock_sched.jobs = []
        return mock_sched

    @pytest.fixture
    def scheduler(self, mock_schedule: mock.MagicMock) -> BloomScheduler:
        with mock.patch.dict("sys.modules", {"schedule": mock_schedule}):
            return BloomScheduler()

    @pytest.fixture
    def temp_dir(self, tmp_path: Path) -> Path:
        return tmp_path

    def test_generate_report_empty(self, scheduler: BloomScheduler, temp_dir: Path) -> None:
        """Generate a report with no data_factory — creates minimal empty report."""
        output = temp_dir / "empty.xlsx"
        config = ReportConfig(title="Empty", output_path=output)
        scheduler._generate_report(config)
        assert output.exists()

    def test_generate_report_with_single_dataframe(
        self, scheduler: BloomScheduler, temp_dir: Path
    ) -> None:
        """Generate a report from a DataFrame factory that returns one DataFrame."""
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        output = temp_dir / "single_df.xlsx"
        config = ReportConfig(
            title="Single DF",
            output_path=output,
            data_factory=lambda: df,
        )
        scheduler._generate_report(config)
        assert output.exists()

    def test_generate_report_with_list_of_dataframes(
        self, scheduler: BloomScheduler, temp_dir: Path
    ) -> None:
        """Generate a report from a factory that returns a list of DataFrames."""
        df1 = pd.DataFrame({"X": [10, 20]})
        df2 = pd.DataFrame({"Y": [30, 40]})
        output = temp_dir / "multi_df.xlsx"
        config = ReportConfig(
            title="Multi DF",
            output_path=output,
            data_factory=lambda: [df1, df2],
        )
        scheduler._generate_report(config)
        assert output.exists()

    def test_generate_report_with_tuple_of_dataframes(
        self, scheduler: BloomScheduler, temp_dir: Path
    ) -> None:
        """Generate a report from a factory that returns a tuple of DataFrames."""
        df1 = pd.DataFrame({"A": [1, 2]})
        df2 = pd.DataFrame({"B": [3, 4]})
        output = temp_dir / "tuple_df.xlsx"
        config = ReportConfig(
            title="Tuple DF",
            output_path=output,
            data_factory=lambda: (df1, df2),
        )
        scheduler._generate_report(config)
        assert output.exists()

    def test_on_complete_callback_called(
        self, scheduler: BloomScheduler, temp_dir: Path
    ) -> None:
        """Verify on_complete callback fires with the output path."""
        results: list[Path] = []
        output = temp_dir / "callback.xlsx"
        config = ReportConfig(
            title="Callback",
            output_path=output,
            on_complete=lambda p: results.append(p),
        )
        scheduler._generate_report(config)
        assert len(results) == 1
        assert results[0] == output

    def test_on_error_callback_called(
        self, scheduler: BloomScheduler, temp_dir: Path
    ) -> None:
        """Verify on_error callback is fired when data_factory raises."""
        errors: list[Exception] = []

        def bad_factory() -> pd.DataFrame:
            raise RuntimeError("factory failure")

        config = ReportConfig(
            title="Error",
            output_path=temp_dir / "error.xlsx",
            data_factory=bad_factory,
            on_error=lambda e: errors.append(e),
        )
        scheduler._generate_report(config)
        assert len(errors) == 1
        assert isinstance(errors[0], RuntimeError)
        assert str(errors[0]) == "factory failure"

    def test_auto_create_dir_disabled_no_parent(
        self, scheduler: BloomScheduler, temp_dir: Path
    ) -> None:
        """When auto_create_dir is False and parent directory exists,
        the report is generated normally."""
        output = temp_dir / "report.xlsx"
        config = ReportConfig(
            title="No Dir Create",
            output_path=output,
            auto_create_dir=False,
        )
        scheduler._generate_report(config)
        assert output.exists()

    def test_auto_create_dir_enabled(
        self, scheduler: BloomScheduler, temp_dir: Path
    ) -> None:
        """When auto_create_dir is True, parent dirs are created automatically."""
        nested = temp_dir / "sub1" / "sub2" / "report.xlsx"
        config = ReportConfig(
            title="Auto Dir",
            output_path=nested,
            auto_create_dir=True,
        )
        scheduler._generate_report(config)
        assert nested.exists()

    def test_non_dataframe_return_from_factory(
        self, scheduler: BloomScheduler, temp_dir: Path
    ) -> None:
        """Factory returning a non-DataFrame value generates empty report."""
        output = temp_dir / "non_df.xlsx"
        config = ReportConfig(
            title="Non DF",
            output_path=output,
            data_factory=lambda: {"not": "a dataframe"},  # type: ignore[return-value]
        )
        scheduler._generate_report(config)
        assert output.exists()

    def test_error_without_callback_does_not_propagate(
        self, scheduler: BloomScheduler, temp_dir: Path
    ) -> None:
        """Without an on_error callback, exceptions are printed but not raised."""

        def bad_factory() -> pd.DataFrame:
            raise RuntimeError("factory failure")

        config = ReportConfig(
            title="No Callback",
            output_path=temp_dir / "noerr.xlsx",
            data_factory=bad_factory,
        )
        # Should not raise — error is caught and traceback is printed
        scheduler._generate_report(config)
        # The output file was not created because the factory failed
        assert not (temp_dir / "noerr.xlsx").exists()


class TestBloomSchedulerMonthlyGate:
    """Tests for the _generate_report_monthly day-of-month gate."""

    @pytest.fixture
    def mock_schedule(self) -> mock.MagicMock:
        mock_sched = mock.MagicMock()
        mock_sched.jobs = []
        return mock_sched

    @pytest.fixture
    def scheduler(self, mock_schedule: mock.MagicMock, tmp_path: Path) -> BloomScheduler:
        with mock.patch.dict("sys.modules", {"schedule": mock_schedule}):
            return BloomScheduler()

    def test_generate_report_monthly_matching_day(
        self, scheduler: BloomScheduler, tmp_path: Path
    ) -> None:
        """When today matches the configured day, report is generated."""
        output = tmp_path / "monthly_ok.xlsx"
        config = ReportConfig(title="Monthly OK", output_path=output)

        from datetime import datetime

        today = datetime.now().day
        scheduler._generate_report_monthly(config, today)
        assert output.exists()

    def test_generate_report_monthly_non_matching_day(
        self, scheduler: BloomScheduler, tmp_path: Path
    ) -> None:
        """When today does NOT match, report is NOT generated."""
        output = tmp_path / "monthly_skip.xlsx"
        config = ReportConfig(title="Monthly Skip", output_path=output)

        from datetime import datetime

        today = datetime.now().day
        # Pick a day that is NOT today
        non_today = today % 28 + 1  # wraps to 1-28, guaranteed different
        scheduler._generate_report_monthly(config, non_today)
        assert not output.exists()
