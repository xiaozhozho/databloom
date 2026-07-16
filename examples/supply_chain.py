#!/usr/bin/env python3
"""供应链管理看板 — 探索采购效率与供应商质量

使用 databloom v0.2 特性：
  - load_dataset() 加载预置供应链数据
  - 10套主题任意切换
  - 组合图表

Sheet 1 — 采购看板:  KPI + 供应商/品类汇总
Sheet 2 — 可视化分析: 供应商金额饼图 + 品类合格率条形图
Sheet 3 — 分析报告:  供应链分析文档
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from databloom import Report
from databloom.data import load_dataset

output_dir = Path(__file__).resolve().parent.parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)

# ── 加载数据 ──────────────────────────────────────────────────────────
df = load_dataset("supply_chain")

total_amount = df["采购金额(元)"].sum()
avg_lead_time = df["到货周期(天)"].mean()
avg_quality = df["合格率"].mean()
avg_turnover = df["库存周转天数"].mean()

supplier_summary = (
    df.groupby("供应商")
    .agg(
        采购金额=("采购金额(元)", "sum"),
        订单数=("采购单号", "count"),
        平均合格率=("合格率", "mean"),
        平均到货周期=("到货周期(天)", "mean"),
    )
    .reset_index()
    .sort_values("采购金额", ascending=False)
)
category_summary = (
    df.groupby("品类")
    .agg(
        采购金额=("采购金额(元)", "sum"),
        订单数=("采购单号", "count"),
        平均合格率=("合格率", "mean"),
    )
    .reset_index()
    .sort_values("采购金额", ascending=False)
)

# ── 构建报告 ──────────────────────────────────────────────────────────

report = Report(title="2025年度供应链管理看板", theme="government_navy")
report.set_page_setup(orientation="landscape", fit_to_width=1)

# Sheet 1 — 采购看板
report.add_sheet("采购看板")
report.add_title("2025年度供应链采购看板")
report.add_subtitle(
    f"数据来源：load_dataset('supply_chain') | {len(df)}笔采购订单 | {df['供应商'].nunique()}家供应商 | {df['品类'].nunique()}个品类"
)

kpi_df = pd.DataFrame(
    {
        "KPI指标": [
            "采购总额(万元)",
            "平均到货周期(天)",
            "平均合格率",
            "平均库存周转天数",
            "订单总数",
        ],
        "数值": [
            round(total_amount / 10000, 1),
            f"{avg_lead_time:.1f}",
            f"{avg_quality:.1%}",
            f"{avg_turnover:.1f}",
            len(df),
        ],
    }
)
report.add_table(kpi_df, title="核心供应链指标")

report.add_spacer(rows=1, height=6)
report.add_table(
    supplier_summary,
    title="按供应商汇总",
    column_formats={"采购金额": "#,##0.00", "平均合格率": "0.0%", "平均到货周期": "0.0"},
)
report.add_spacer(rows=1, height=6)
report.add_table(
    category_summary,
    title="按品类汇总",
    column_formats={"采购金额": "#,##0.00", "平均合格率": "0.0%"},
)

# Sheet 2 — 可视化分析
report.add_sheet("可视化分析")
report.add_title("供应链数据可视化")

report.add_chart(
    supplier_summary[["供应商", "采购金额"]],
    type="pie",
    category_col="供应商",
    value_cols=["采购金额"],
    title="各供应商采购金额占比",
)
report.add_paragraph("图1：各供应商采购金额分布。供应商集中度是供应链风险管理的关键指标。")

report.add_chart(
    category_summary[["品类", "平均合格率"]],
    type="bar",
    category_col="品类",
    value_cols=["平均合格率"],
    title="各品类平均合格率对比",
)
report.add_paragraph("图2：合格率反映了各品类的质量水平，是供应商选择和考核的核心指标。")

# Sheet 3 — 分析报告
report.add_sheet("分析报告")
report.add_title("2025年度供应链分析报告")
report.add_subtitle("编制日期：2026年7月")

top_supplier = supplier_summary.iloc[0]
worst_supplier = supplier_summary.iloc[-1]

report.add_paragraph(
    "【一、供应链概览】\n\n"
    f"年度采购总额{total_amount / 10000:,.0f}万元，覆盖{df['供应商'].nunique()}家供应商、{df['品类'].nunique()}个品类。"
    f"平均到货周期{avg_lead_time:.1f}天，平均合格率{avg_quality:.1%}，平均库存周转{avg_turnover:.1f}天。\n\n"
    f"最大供应商{top_supplier['供应商']}，采购金额{top_supplier['采购金额'] / 10000:,.0f}万元，"
    f"合格率{top_supplier['平均合格率']:.1%}。"
    f"合格率最低供应商为{worst_supplier['供应商']}（{worst_supplier['平均合格率']:.1%}），建议纳入重点关注。"
)

report.add_paragraph(
    "【二、优化建议】\n\n"
    "1. 供应商集中度：前3大供应商占比较高，建议适度分散采购风险。\n"
    "2. 到货周期波动：部分品类到货周期标准差较大，建议建立安全库存机制。\n"
    "3. 合格率管控：对合格率低于90%的供应商启动改进计划或替代方案。\n"
    "4. 库存周转：关注库存周转天数偏高品类，推进精益库存管理。\n"
    "5. 数字化：建议引入供应商绩效评分卡，实现供应商管理的量化决策。"
)

output_path = output_dir / "supply_chain.xlsx"
report.build(output_path)
print(f"✅ 供应链看板已生成：{output_path} ({output_path.stat().st_size / 1024:.1f} KB)")
