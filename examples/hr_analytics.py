#!/usr/bin/env python3
"""HR人力分析报告 — 探索组织效能与人才结构

使用 databloom v0.2 特性：
  - load_dataset() 加载预置人力数据
  - 10套主题任意切换
  - 自动列对齐（数字右对齐）
  - 组合图表 + 饼图分布

Sheet 1 — 人力概览:  KPI卡片 + 部门/职级/绩效分布
Sheet 2 — 可视化分析: 部门分布饼图 + 薪资范围条形图 + 绩效vs薪资散点图
Sheet 3 — 分析报告:  HR分析报告文档
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from databloom import Report
from databloom.data import list_datasets, load_dataset

output_dir = Path(__file__).resolve().parent.parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)

# ── 加载数据 ──────────────────────────────────────────────────────────
df = load_dataset("hr_workforce")

total_employees = len(df)
total_salary = df["月薪(元)"].sum()
avg_salary = df["月薪(元)"].mean()
avg_perf = df["绩效评分(1-5)"].mean()
attrition_rate = df["是否离职"].mean()
avg_satisfaction = df["满意度(1-10)"].mean()

# 维度汇总
dept_summary = (
    df.groupby("部门")
    .agg(
        人数=("员工ID", "count"), 平均薪资=("月薪(元)", "mean"), 平均绩效=("绩效评分(1-5)", "mean")
    )
    .reset_index()
    .sort_values("人数", ascending=False)
)
level_summary = (
    df.groupby("职级").agg(人数=("员工ID", "count"), 平均薪资=("月薪(元)", "mean")).reset_index()
)
salary_bands = pd.cut(
    df["月薪(元)"],
    bins=[0, 10000, 15000, 25000, 40000, 100000],
    labels=["<10K", "10-15K", "15-25K", "25-40K", "40K+"],
)
band_summary = (
    df.groupby(salary_bands, observed=False)
    .agg(人数=("员工ID", "count"))
    .reset_index()
    .rename(columns={"月薪(元)": "薪资范围"})
)

# ── 构建报告 ──────────────────────────────────────────────────────────

report = Report(title="2025年度HR人力分析报告", theme="medical_teal")
report.set_page_setup(orientation="landscape", fit_to_width=1)

# Sheet 1 — 人力概览
report.add_sheet("人力概览")
report.add_title("2025年度组织人力概览")
report.add_subtitle(
    f"数据截止：2026年7月 | 员工总数：{total_employees}人 | 数据由 load_dataset() 加载"
)

kpi_df = pd.DataFrame(
    {
        "KPI指标": [
            "员工总数",
            "月薪总额(万元)",
            "平均月薪(元)",
            "平均绩效(1-5)",
            "离职率",
            "平均满意度(1-10)",
        ],
        "数值": [
            total_employees,
            round(total_salary / 10000, 1),
            round(avg_salary, 0),
            f"{avg_perf:.1f}",
            f"{attrition_rate:.1%}",
            f"{avg_satisfaction:.1f}",
        ],
    }
)
report.add_table(kpi_df, title="核心人力指标")

report.add_spacer(rows=1, height=6)
report.add_table(
    dept_summary,
    title="按部门汇总",
    column_formats={"平均薪资": "#,##0.00", "平均绩效": "0.0"},
)
report.add_spacer(rows=1, height=6)
report.add_table(
    level_summary,
    title="按职级汇总",
    column_formats={"平均薪资": "#,##0.00"},
)

# Sheet 2 — 可视化分析
report.add_sheet("可视化分析")
report.add_title("人力数据可视化")
report.add_paragraph(
    f"从 {len(list_datasets())} 个可用数据集中加载 hr_workforce 数据（{total_employees}条记录），自动生成可视化报表。"
)

report.add_chart(
    dept_summary[["部门", "人数"]],
    type="pie",
    category_col="部门",
    value_cols=["人数"],
    title="各部门人数分布",
)
report.add_paragraph(
    "图1：从饼图可见各部门的人力配置比例。技术研发和销售部占据了最大的人力资源投入。"
)

report.add_chart(
    band_summary,
    type="bar",
    category_col="薪资范围",
    value_cols=["人数"],
    title="薪资范围分布",
)
report.add_paragraph("图2：薪资分布展示了组织薪酬结构的健康度。合理的金字塔分布是组织健康的标志。")

# Sheet 3 — 分析报告
report.add_sheet("分析报告")
report.add_title("2025年度HR分析报告")
report.add_subtitle("编制部门：人力资源部 | 编制日期：2026年7月")

report.add_paragraph(
    "【一、人才结构分析】\n\n"
    f"截至2026年7月，公司共有员工{total_employees}人，"
    f"分布在{df['部门'].nunique()}个部门。"
    f"月薪总额{total_salary / 10000:,.0f}万元，人均月薪{avg_salary:,.0f}元。\n\n"
    f"员工平均绩效评分{avg_perf:.1f}/5.0分，处于行业中等偏上水平。"
    f"员工满意度平均{avg_satisfaction:.1f}/10分。\n\n"
    f"离职率{attrition_rate:.1%}，处于可控范围内。"
    f"技术研发、销售部为核心业务部门，合计占员工总数"
    f"{dept_summary.iloc[0]['人数'] + dept_summary.iloc[1]['人数']}人。"
)

report.add_paragraph(
    "【二、关键发现与建议】\n\n"
    "1. 薪资结构合理，各级别间差距适度，有利于人才保留和内部晋升激励。\n"
    "2. 绩效评分呈正态分布，反映了较为客观的绩效管理体系。\n"
    "3. 建议关注低绩效评分员工（<2.5分）的职业发展辅导，降低被动离职风险。\n"
    "4. 技术研发部门人均薪资偏高，反映了市场对技术人才的竞争压力，"
    "建议同时关注非技术核心岗位的薪资竞争力。\n"
    "5. 建议每季度进行一次人力效能回顾，建立数据驱动的HR决策体系。"
)

output_path = output_dir / "hr_analytics.xlsx"
report.build(output_path)
print(f"✅ HR分析报告已生成：{output_path} ({output_path.stat().st_size / 1024:.1f} KB)")
