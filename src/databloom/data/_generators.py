"""Built-in dataset generators.

Each function returns one or more DataFrames using deterministic
random seeds.  The datasets/ directory caches results as pickle files
so generation only happens once.

Adding a new dataset:
1. Write a `_gen_<name>() -> pd.DataFrame | dict[str, pd.DataFrame]` function.
2. Register it in `_GENERATORS` below.
3. Optionally add an entry in `_seed.py` for reproducible seeding.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_DATASETS_DIR = Path(__file__).resolve().parent / "datasets"
_DATASETS_DIR.mkdir(parents=True, exist_ok=True)


def _stash(name: str, data: Any) -> None:
    """Save *data* as a pickle file in the datasets/ directory."""
    path = _DATASETS_DIR / f"{name}.pkl"
    with open(path, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


def _unstash(name: str) -> Any | None:
    """Load a dataset from its pickle file, or return None."""
    path = _DATASETS_DIR / f"{name}.pkl"
    if not path.exists():
        return None
    with open(path, "rb") as f:
        return pickle.load(f)




# ── Finance ────────────────────────────────────────────────────────────


def _gen_finance_profit() -> pd.DataFrame:
    """12-month profit statement (Chinese accounting format)."""
    import random

    from databloom.data._seed import SEEDS

    seed = SEEDS["finance_profit"]
    random.seed(seed)
    np.random.seed(seed)

    months = [f"{m}月" for m in range(1, 13)]
    base_revenue = np.linspace(800, 1500, 12) * 10000
    noise = np.random.normal(0, 50000, 12)
    revenue = (base_revenue + noise).round(0)

    cost_ratio = 0.55 + np.sin(np.linspace(0, np.pi * 2, 12)) * 0.05
    cost = (revenue * cost_ratio).round(0)
    gross_profit = (revenue - cost).round(0)
    gross_margin = (gross_profit / revenue).round(4)

    selling_expense = (revenue * 0.12).round(0)
    admin_expense = (revenue * 0.08).round(0)
    rd_expense = (revenue * 0.03).round(0)
    total_opex = (selling_expense + admin_expense + rd_expense).round(0)

    operating_profit = (gross_profit - total_opex).round(0)
    operating_margin = (operating_profit / revenue).round(4)

    net_profit = (operating_profit * np.random.uniform(0.72, 0.82, 12)).round(0)
    net_margin = (net_profit / revenue).round(4)

    return pd.DataFrame({
        "月份": months,
        "营业收入": revenue, "营业成本": cost,
        "毛利润": gross_profit, "毛利率": gross_margin,
        "销售费用": selling_expense, "管理费用": admin_expense,
        "研发费用": rd_expense, "费用合计": total_opex,
        "营业利润": operating_profit, "营业利润率": operating_margin,
        "净利润": net_profit, "净利率": net_margin,
    })


def _gen_finance_metrics() -> pd.DataFrame:
    """13 financial health indicators (solvency / operations / profitability / growth)."""

    def _metric(val: float, unit: str = "%") -> str:
        return f"{val:.1f}{unit}"

    return pd.DataFrame({
        "指标类别": [
            "偿债能力", "偿债能力", "偿债能力",
            "营运能力", "营运能力", "营运能力",
            "盈利能力", "盈利能力", "盈利能力", "盈利能力",
            "成长能力", "成长能力", "成长能力",
        ],
        "指标名称": [
            "流动比率", "速动比率", "资产负债率",
            "应收账款周转率", "存货周转率", "总资产周转率",
            "净资产收益率(ROE)", "总资产报酬率(ROA)", "毛利率", "净利率",
            "营收增长率", "净利润增长率", "总资产增长率",
        ],
        "2025年实际": [
            _metric(1.85), _metric(1.42), _metric(42.3),
            _metric(8.2, "次"), _metric(6.5, "次"), _metric(1.2, "次"),
            _metric(15.8), _metric(8.9), _metric(38.2), _metric(12.6),
            _metric(18.5), _metric(22.3), _metric(10.8),
        ],
        "2024年同期": [
            _metric(1.72), _metric(1.30), _metric(45.1),
            _metric(7.8, "次"), _metric(6.1, "次"), _metric(1.1, "次"),
            _metric(14.2), _metric(7.8), _metric(36.8), _metric(10.9),
            _metric(15.2), _metric(18.1), _metric(9.5),
        ],
    })


# ── Sales dashboard ────────────────────────────────────────────────────


def _gen_sales_orders() -> pd.DataFrame:
    """60 sales orders across 10 products, 5 categories, 7 regions, 5 channels."""
    import random

    from databloom.data._seed import SEEDS

    seed = SEEDS["sales_orders"]
    random.seed(seed)
    np.random.seed(seed)

    products = [
        "智屏电视-55寸", "智屏电视-65寸", "智能手表-Pro", "智能手表-Lite",
        "蓝牙耳机-X3", "蓝牙耳机-X5", "平板电脑-10寸", "平板电脑-12寸",
        "笔记本电脑-14寸", "笔记本电脑-16寸",
    ]
    categories = {
        "智屏电视-55寸": "大家电", "智屏电视-65寸": "大家电",
        "智能手表-Pro": "可穿戴", "智能手表-Lite": "可穿戴",
        "蓝牙耳机-X3": "音频设备", "蓝牙耳机-X5": "音频设备",
        "平板电脑-10寸": "平板", "平板电脑-12寸": "平板",
        "笔记本电脑-14寸": "电脑", "笔记本电脑-16寸": "电脑",
    }
    regions = ["华北", "华东", "华南", "华中", "西南", "西北", "东北"]
    channels = ["官方商城", "天猫旗舰店", "京东自营", "线下门店", "抖音直播"]

    N = 60
    dates = pd.date_range("2025-07-01", periods=12, freq="ME").repeat(N // 12).tolist()
    if len(dates) < N:
        dates += [dates[-1]] * (N - len(dates))

    records = []
    for i in range(N):
        prod = random.choice(products)
        cat = categories[prod]
        region = random.choice(regions)
        channel = random.choice(channels)
        price = random.choice([2999, 4999, 899, 599, 199, 299, 2499, 3499, 5999, 7999])
        qty = random.randint(1, 15)
        revenue = price * qty
        cost = revenue * random.uniform(0.55, 0.72)
        profit = revenue - cost
        discount = random.choice([0, 5, 10, 10, 10, 15, 20]) / 100
        records.append({
            "订单日期": dates[i], "订单编号": f"ORD-{20250001 + i:06d}",
            "产品名称": prod, "产品品类": cat, "销售区域": region,
            "销售渠道": channel, "单价": price, "数量": qty,
            "营收": round(revenue, 2), "成本": round(cost, 2),
            "毛利": round(profit, 2), "毛利率": round(profit / revenue, 4),
            "折扣率": discount,
        })

    return pd.DataFrame(records)


# ── HR workforce ───────────────────────────────────────────────────────


def _gen_hr_workforce() -> pd.DataFrame:
    """200 employees across 6 departments with performance & attrition data."""
    import random

    from databloom.data._seed import SEEDS

    seed = SEEDS["hr_workforce"]
    random.seed(seed)
    np.random.seed(seed)

    departments = {
        "技术研发": 50, "市场营销": 35, "销售部": 40,
        "人力资源": 15, "财务部": 20, "运营部": 40,
    }
    levels = ["P1", "P2", "P3", "P4", "P5", "M1", "M2", "M3"]

    records = []
    for emp_id in range(1, 201):
        dept = random.choices(list(departments.keys()), weights=list(departments.values()), k=1)[0]
        level = random.choices(
            levels, weights=[8, 15, 20, 25, 15, 10, 5, 2], k=1
        )[0]
        level_base = {"P1": 6000, "P2": 9000, "P3": 13000, "P4": 18000,
                       "P5": 25000, "M1": 22000, "M2": 32000, "M3": 45000}
        salary = round(level_base[level] * random.uniform(0.85, 1.25), 0)
        hire_days_offset = random.randint(0, 2555)  # up to ~7 years
        hire_date = pd.Timestamp("2026-07-01") - pd.Timedelta(days=int(hire_days_offset))

        # Performance: out of 5
        perf_mean = 3.2 if dept == "销售部" else 3.5
        performance = min(5.0, max(1.0, round(np.random.normal(perf_mean, 0.8), 1)))

        # Attrition risk: higher for low performers & low salary
        attrition_base = max(0, (4.0 - performance) * 0.15 + (salary < 12000) * 0.1)
        is_resigned = random.random() < attrition_base

        records.append({
            "员工ID": f"EMP-{emp_id:05d}",
            "部门": dept,
            "职级": level,
            "月薪(元)": salary,
            "入职日期": hire_date,
            "绩效评分(1-5)": performance,
            "是否离职": is_resigned,
            "满意度(1-10)": round(max(1, min(10, np.random.normal(6.8, 1.5))), 1),
        })

    return pd.DataFrame(records)


# ── Supply chain ───────────────────────────────────────────────────────


def _gen_supply_chain() -> pd.DataFrame:
    """100 procurement orders with supplier quality & delivery metrics."""
    import random

    from databloom.data._seed import SEEDS

    seed = SEEDS["supply_chain"]
    random.seed(seed)
    np.random.seed(seed)

    suppliers = {
        "华东精工": {"category": "电子元器件", "base_quality": 0.97, "base_lead": 12},
        "华南制造": {"category": "电子元器件", "base_quality": 0.94, "base_lead": 9},
        "北方钢铁": {"category": "金属材料", "base_quality": 0.96, "base_lead": 18},
        "西南矿业": {"category": "金属材料", "base_quality": 0.92, "base_lead": 22},
        "绿源包装": {"category": "包装材料", "base_quality": 0.99, "base_lead": 5},
        "恒达化工": {"category": "化工原料", "base_quality": 0.93, "base_lead": 15},
        "星联电子": {"category": "电子元器件", "base_quality": 0.95, "base_lead": 10},
        "昌泰包装": {"category": "包装材料", "base_quality": 0.98, "base_lead": 6},
    }

    records = []
    for order_id in range(1, 101):
        supplier = random.choice(list(suppliers.keys()))
        info = suppliers[supplier]
        quantity = random.randint(100, 5000)
        unit_price = round(random.uniform(5, 500), 2)
        amount = round(quantity * unit_price, 2)

        lead_time = max(1, round(np.random.normal(info["base_lead"], 3)))
        quality = max(0.80, min(1.0, np.random.normal(info["base_quality"], 0.04)))

        # Inventory turnover days
        inv_turnover = round(max(15, np.random.normal(45, 20)), 1)

        records.append({
            "采购单号": f"PO-{order_id:04d}",
            "供应商": supplier,
            "品类": info["category"],
            "采购数量": quantity,
            "单价(元)": unit_price,
            "采购金额(元)": amount,
            "到货周期(天)": lead_time,
            "合格率": round(quality, 4),
            "库存周转天数": inv_turnover,
        })

    return pd.DataFrame(records).sort_values("采购单号").reset_index(drop=True)


# ── Registry ───────────────────────────────────────────────────────────


_GENERATORS: dict[str, Any] = {
    "finance_profit": _gen_finance_profit,
    "finance_metrics": _gen_finance_metrics,
    "sales_orders": _gen_sales_orders,
    "hr_workforce": _gen_hr_workforce,
    "supply_chain": _gen_supply_chain,
}


# Lazy import to break circular dependency
def load_dataset(name: str, force_rebuild: bool = False) -> Any:
    """Load a built-in dataset, generating and caching it on first access.

    Args:
        name: Dataset identifier (e.g. ``"finance_profit"``).
        force_rebuild: If ``True``, regenerate even when a cached pickle exists.

    Returns:
        A ``pd.DataFrame`` or ``dict[str, pd.DataFrame]``.

    Raises:
        KeyError: If *name* is not a known dataset.
    """
    if name not in _GENERATORS:
        available = ", ".join(sorted(_GENERATORS))
        raise KeyError(f"Unknown dataset {name!r}. Available: {available}")

    if not force_rebuild:
        cached = _unstash(name)
        if cached is not None:
            return cached

    data = _GENERATORS[name]()
    _stash(name, data)
    return data


def list_datasets() -> list[str]:
    """Return the names of all available built-in datasets."""
    return sorted(_GENERATORS)
