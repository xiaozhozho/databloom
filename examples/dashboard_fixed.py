#!/usr/bin/env python3
"""仪表盘布局修复示例 — 展示 v0.2 修复后的多图表并排布局

v0.2 修复内容：
- ChartElement 新增 full_width=False 参数
- layout_dashboard 模板解除了图表重叠bug
- 多个图表可真正并排放置在同一行
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from databloom import Report, list_themes

output_dir = Path(__file__).resolve().parent.parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)

# ── 简洁的内联数据（仪表盘场景用聚合数据，不需 pickle 持久化） ────────
kpi_df = pd.DataFrame({
    "KPI": ["总营收(万元)", "总成本(万元)", "毛利(万元)", "毛利率", "订单数", "客单价(元)"],
    "数值": ["1,586", "987", "599", "37.7%", "60", "26,450"],
})

chart1 = pd.DataFrame({"区域": ["华东", "华南", "华北", "华中", "西南"], "营收": [450, 320, 280, 180, 120]})
chart2 = pd.DataFrame({"品类": ["手机", "家电", "服装", "美妆", "食品", "家居"], "毛利": [180, 120, 150, 95, 35, 60]})
chart3 = pd.DataFrame({"渠道": ["天猫", "京东", "抖音", "拼多多", "线下"], "订单数": [220, 180, 160, 140, 100]})

# ── 为每套主题生成一个仪表盘 ───────────────────────────────────────────
print("Building dashboard with 3 side-by-side charts ...")
print(f"  Total themes to demonstrate: {len(list_themes())}\n")

for theme_name in list_themes():
    filename = f"dashboard_{theme_name}.xlsx"
    print(f"  Generating {filename} ...")

    report = (
        Report(title=f"Dashboard — {theme_name}", theme=theme_name)
        .set_page_setup(orientation="landscape", fit_to_width=1)
        .add_sheet("仪表盘")
        .add_title(f"经营仪表盘 — {theme_name.replace('_', ' ').title()}")
        .add_subtitle("核心KPI概览")
        .add_table(kpi_df, title="关键绩效指标")
    )

    from databloom.elements.chart import ChartElement

    report.add_sheet("图表看板")
    report.add_title("多维度数据可视化")

    for idx, (df, chart_type, chart_title) in enumerate([
        (chart1, "column", "区域营收对比"),
        (chart2, "bar", "品类毛利排名"),
        (chart3, "pie", "渠道订单分布"),
    ]):
        report._engine.place(
            ChartElement(df, chart_type=chart_type, title=chart_title, full_width=False),
            row=report._engine.current_sheet()._next_row,
            col=idx,
        )

    report.build(output_dir / filename)

print(f"\n✅ All {len(list_themes())} dashboard reports generated in {output_dir}/")
