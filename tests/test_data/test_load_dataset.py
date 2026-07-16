"""Tests for databloom.data sub-package."""

from __future__ import annotations

import pandas as pd

from databloom.data import list_datasets, load_dataset


class TestListDatasets:
    """Tests for list_datasets."""

    def test_returns_list(self) -> None:
        names = list_datasets()
        assert isinstance(names, list)
        assert len(names) >= 5

    def test_returns_sorted(self) -> None:
        names = list_datasets()
        assert names == sorted(names)

    def test_includes_finance(self) -> None:
        assert "finance_profit" in list_datasets()
        assert "finance_metrics" in list_datasets()

    def test_includes_sales(self) -> None:
        assert "sales_orders" in list_datasets()

    def test_includes_hr(self) -> None:
        assert "hr_workforce" in list_datasets()

    def test_includes_supply_chain(self) -> None:
        assert "supply_chain" in list_datasets()


class TestLoadDataset:
    """Tests for load_dataset."""

    def test_finance_profit(self) -> None:
        df = load_dataset("finance_profit")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 12
        assert "月份" in df.columns
        assert "营业收入" in df.columns
        assert "净利率" in df.columns

    def test_finance_metrics(self) -> None:
        df = load_dataset("finance_metrics")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 13
        assert "指标类别" in df.columns

    def test_sales_orders(self) -> None:
        df = load_dataset("sales_orders")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 60
        assert "订单编号" in df.columns
        assert "营收" in df.columns

    def test_hr_workforce(self) -> None:
        df = load_dataset("hr_workforce")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 200
        assert "员工ID" in df.columns
        assert "部门" in df.columns
        assert "月薪(元)" in df.columns

    def test_supply_chain(self) -> None:
        df = load_dataset("supply_chain")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100
        assert "采购单号" in df.columns
        assert "供应商" in df.columns
        assert "合格率" in df.columns

    def test_load_twice_is_identical(self) -> None:
        df1 = load_dataset("supply_chain")
        df2 = load_dataset("supply_chain")
        pd.testing.assert_frame_equal(df1, df2)

    def test_force_rebuild(self) -> None:
        df = load_dataset("supply_chain", force_rebuild=True)
        assert len(df) == 100

    def test_unknown_dataset_raises(self) -> None:
        import pytest
        with pytest.raises(KeyError, match="Unknown dataset"):
            load_dataset("nonexistent_dataset")
