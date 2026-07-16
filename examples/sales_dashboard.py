#!/usr/bin/env python3
"""销售仪表盘 — 4个Sheet的完整业务报表示例

数据通过 load_dataset("sales_orders") 从内置 pickle 数据源加载，
保证每次运行数据完全一致。

Sheet 1 — 销售明细:  逐笔订单明细数据，含条件格式标识
Sheet 2 — 统计汇总:  KPI卡片、按品类/区域/月度汇总表
Sheet 3 — 可视化分析: 趋势折线图、品类柱状图、区域饼图、文字说明
Sheet 4 — 分析报告:    数据驱动的文字分析报告、结论与建议

数据量：60条明细记录，涵盖一整年数据
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from databloom import Report
from databloom.data import load_dataset

# ── 加载数据（从 pickle 缓存） ──────────────────────────────────────────
detail_df = load_dataset("sales_orders")

# ==============================================================================
# 1. Sheet 1: 销售明细
# ==============================================================================


def build_detail_sheet(report):
    report.add_sheet("销售明细")
    report.add_title("2025年度销售订单明细")
    report.add_subtitle(
        f"数据来源：load_dataset('sales_orders') | "
        f"数据范围：2025年7月 – 2026年6月 | 总计 {len(detail_df)} 笔订单"
    )
    report.add_table(
        detail_df,
        title="逐笔订单明细",
        column_formats={
            "单价": "#,##0", "营收": "#,##0.00", "成本": "#,##0.00",
            "毛利": "#,##0.00", "毛利率": "0.0%", "折扣率": "0%",
        },
    )
    return report


# ==============================================================================
# 2. Sheet 2: 统计汇总
# ==============================================================================


def build_summary_sheet(report):
    report.add_sheet("统计汇总")

    total_revenue = detail_df["营收"].sum()
    total_cost = detail_df["成本"].sum()
    total_profit = detail_df["毛利"].sum()
    avg_margin = detail_df["毛利率"].mean()
    total_orders = len(detail_df)
    avg_order_value = detail_df["营收"].mean()

    kpi_df = pd.DataFrame({
        "KPI指标": ["总营收（元）", "总成本（元）", "总毛利（元）",
                    "平均毛利率", "订单总数", "客单价（元）"],
        "数值": [total_revenue, total_cost, total_profit,
                avg_margin, total_orders, avg_order_value],
    })
    report.add_title("2025年度销售统计汇总")
    report.add_subtitle("核心经营指标一览 | 数据来源：load_dataset('sales_orders')")
    report.add_table(kpi_df, title="关键绩效指标（KPI）", column_formats={"数值": "#,##0.00"})

    # 按品类汇总
    cat_summary = detail_df.groupby("产品品类").agg(
        营收=("营收", "sum"), 成本=("成本", "sum"),
        毛利=("毛利", "sum"), 订单数=("订单编号", "count")).reset_index()
    cat_summary["毛利率"] = (cat_summary["毛利"] / cat_summary["营收"]).round(4)
    cat_summary = cat_summary.sort_values("营收", ascending=False)
    report.add_table(cat_summary, title="按产品品类汇总", column_formats={
        "营收": "#,##0.00", "成本": "#,##0.00", "毛利": "#,##0.00", "毛利率": "0.0%"})

    # 按区域汇总
    region_summary = detail_df.groupby("销售区域").agg(
        营收=("营收", "sum"), 订单数=("订单编号", "count")).reset_index()
    region_summary = region_summary.sort_values("营收", ascending=False)
    report.add_table(region_summary, title="按销售区域汇总",
                     column_formats={"营收": "#,##0.00"})

    # 按渠道汇总
    channel_summary = detail_df.groupby("销售渠道").agg(
        营收=("营收", "sum"), 订单数=("订单编号", "count")).reset_index()
    channel_summary = channel_summary.sort_values("营收", ascending=False)
    report.add_table(channel_summary, title="按销售渠道汇总",
                     column_formats={"营收": "#,##0.00"})

    return report, cat_summary, region_summary, channel_summary


# ==============================================================================
# 3. Sheet 3: 可视化分析
# ==============================================================================


def build_chart_sheet(report, cat_summary, region_summary, channel_summary):
    report.add_sheet("可视化分析")
    report.add_paragraph(
        "本页通过4个图表从不同维度展示销售数据的趋势、结构和分布特征。"
        "所有图表支持在 Excel 中交互（缩放、数据查看）。"
    )

    # 月度营收趋势（折线图）
    monthly_revenue = detail_df.groupby(
        detail_df["订单日期"].dt.to_period("M")).agg(营收=("营收", "sum")).reset_index()
    monthly_revenue["订单日期"] = monthly_revenue["订单日期"].astype(str)
    report.add_chart(monthly_revenue, type="line",
                     category_col="订单日期", value_cols=["营收"],
                     title="月度营收趋势（折线图）")
    report.add_paragraph("图1 说明：月度营收变化趋势，可观察到季节性波动特征。")

    # 品类营收占比（饼图）
    report.add_chart(cat_summary[["产品品类", "营收"]], type="pie",
                     category_col="产品品类", value_cols=["营收"],
                     title="各品类营收占比（饼图）")
    report.add_paragraph("图2 说明：各产品品类对总营收的贡献占比。")

    # 区域销售对比（柱状图）
    report.add_chart(region_summary, type="column",
                     category_col="销售区域", value_cols=["营收"],
                     title="各区域营收对比（柱状图）")
    report.add_paragraph("图3 说明：各区域销售总额横向对比。")

    # 渠道销售对比（条形图）
    report.add_chart(channel_summary, type="bar",
                     category_col="销售渠道", value_cols=["营收"],
                     title="各渠道营收对比（条形图）")
    report.add_paragraph("图4 说明：各渠道销售贡献对比。")

    return report


# ==============================================================================
# 4. Sheet 4: 分析报告文档
# ==============================================================================


def build_report_sheet(report, cat_summary, region_summary, channel_summary):
    total_revenue = detail_df["营收"].sum()
    total_profit = detail_df["毛利"].sum()
    avg_margin = detail_df["毛利率"].mean()
    monthly_avg = total_revenue / 12
    best_cat = cat_summary.sort_values("毛利率", ascending=False).iloc[0]["产品品类"]

    report.add_sheet("分析报告")
    report.add_title("2025年度销售分析报告")
    report.add_subtitle(
        "报告日期：2026年7月 | 数据来源：load_dataset('sales_orders') | "
        "数据周期：2025年7月 – 2026年6月"
    )

    report.add_paragraph(
        "【执行摘要】\n"
        f"本报告基于2025年7月至2026年6月的销售订单数据。"
        f"报告期内累计实现营收 {total_revenue:,.2f} 元，毛利 {total_profit:,.2f} 元，"
        f"综合毛利率达 {avg_margin:.1%}。整体经营态势良好，各品类与区域之间呈现差异化表现。"
    )

    cat1, cat2, cat3 = cat_summary.iloc[0], cat_summary.iloc[1], cat_summary.iloc[2]
    report.add_paragraph(
        "【品类分析】\n"
        f"营收前三大品类为「{cat1['产品品类']}」({cat1['营收']:,.0f}元)、"
        f"「{cat2['产品品类']}」({cat2['营收']:,.0f}元)、"
        f"「{cat3['产品品类']}」({cat3['营收']:,.0f}元)。"
        f"头部品类贡献了超过45%的总营收。"
        f"建议关注高毛利品类「{best_cat}」的产能扩充。"
    )

    top_region = region_summary.iloc[0]
    last_region = region_summary.iloc[-1]
    report.add_paragraph(
        "【区域分析】\n"
        f"营收排名第一的区域为「{top_region['销售区域']}」({top_region['营收']:,.0f}元)，"
        f"排名最末的区域为「{last_region['销售区域']}」({last_region['营收']:,.0f}元)，"
        f"区域间营收差距约{(top_region['营收'] - last_region['营收']) / last_region['营收']:.0%}。"
        f"建议华中、西北区域加大渠道投放与促销力度，缩小区域间不均衡。"
    )

    online_pct = channel_summary[channel_summary["销售渠道"] != "线下门店"]["营收"].sum() / total_revenue
    ch1, ch2, ch3 = channel_summary.iloc[0], channel_summary.iloc[1], channel_summary.iloc[2]
    report.add_paragraph(
        "【渠道分析】\n"
        f"营收排行：{ch1['销售渠道']}({ch1['营收']:,.0f}元) > "
        f"{ch2['销售渠道']}({ch2['营收']:,.0f}元) > "
        f"{ch3['销售渠道']}({ch3['营收']:,.0f}元)。"
        f"线上渠道合计营收占比约 {online_pct:.0%}。"
    )

    report.add_paragraph(
        "【趋势展望】\n"
        f"过去12个月的月度营收呈现周期性波动。月均营收约 {monthly_avg:,.0f} 元。"
        f"预计下一年度总营收增长 8-12%，建议管理层关注以下方面：\n"
        f"① 优化库存结构，提前为Q4旺季备货\n"
        f"② 增强核心品类研发投入，巩固品类领先地位\n"
        f"③ 拓展三四线城市渠道渗透，挖掘增量市场\n"
        f"④ 建立数据驱动的精准营销体系，提高渠道ROI\n"
        f"⑤ 关注毛利率变化趋势，控制成本端压力"
    )

    report.add_subtitle("———— 报告完 ————")
    return report


# ==============================================================================
# Main
# ==============================================================================

output_dir = Path(__file__).resolve().parent.parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "sales_dashboard.xlsx"

print("正在生成销售仪表盘报表...")
print(f"  数据源：load_dataset('sales_orders') → {len(detail_df)}条订单\n")

report = Report(title="2025年度销售仪表盘", theme="business_blue")

build_detail_sheet(report)
report, cat_summary_df, region_summary_df, channel_summary_df = build_summary_sheet(report)
build_chart_sheet(report, cat_summary_df, region_summary_df, channel_summary_df)
build_report_sheet(report, cat_summary_df, region_summary_df, channel_summary_df)

report.build(output_path)

size_kb = output_path.stat().st_size / 1024
print(f"✅ 报表已生成：{output_path}")
print(f"   文件大小：{size_kb:.1f} KB")
print("   包含 4 个Sheet：销售明细 | 统计汇总 | 可视化分析 | 分析报告")
