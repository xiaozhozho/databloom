# databloom

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> 一个基于 Python 的 Excel 报表快速生成框架。输入 pandas DataFrame，输出专业排版的 xlsx 文件。让数据在 Excel 中绽放。

---

## 目录

- [项目背景](#项目背景)
- [安装与环境](#安装与环境)
- [核心概念](#核心概念)
- [快速上手](#快速上手)
  - [Level 1 — 一行出报告](#level-1--一行出报告)
  - [Level 2 — 声明式构建](#level-2--声明式构建)
  - [Level 3 — 自定义主题](#level-3--自定义主题)
- [案例展示](#案例展示)
  - [案例一：财务分析报告](#案例一财务分析报告)
  - [案例二：HR 人力分析报告](#案例二hr-人力分析报告)
  - [案例三：供应链管理看板](#案例三供应链管理看板)
  - [案例四：多主题仪表盘](#案例四多主题仪表盘)
- [内置数据集](#内置数据集)
- [内置主题](#内置主题)
- [完整 API 参考](#完整-api-参考)
- [开发指南](#开发指南)

---

## 项目背景

在日常数据分析工作中，经常需要将 DataFrame 导出为 Excel 报表发送给业务方或管理层。pandas 自带了 `to_excel()` 方法，但要做带**格式化表格**、**交互式图表**、**多 Sheet 排版**、**分析文字**的专业报表，你需要编写大量 xlsxwriter 样板代码——设置格式、合并单元格、手动计算图表数据范围、调试列宽和颜色。

**databloom 的目标**就是把"包含多个 Sheet、多个图表、专业配色的完整商业报告"从数百行代码压缩到一行或几行链式调用。

你专注于数据分析本身，排版、配色、图表布局交给框架处理。一份包含 120 条订单明细 + KPI 看板 + 6 个图表 + 5 段分析文字的专业报告，用 databloom 不超过 30 行调用代码。

### 技术栈

| 组件 | 用途 | 版本要求 |
|------|------|---------|
| **xlsxwriter** | Excel 文件生成、原生图表、条件格式 | ≥3.1.0 |
| **pandas** | 数据结构、类型检测、分组聚合 | ≥2.0.0 |
| **matplotlib** | 图表渲染（可选，作为图表后端） | ≥3.7.0 |
| **openpyxl** | 生成后验证、读取已有 xlsx | 仅测试使用 |

### 架构概览

```
Theme System  →  Core Engine  →  Elements  →  Layout Engine  →  Smart Facade
  (10套配色)      (xlsxwriter)    (7种元素)     (自动排版)        (用户 API)
                                                        ↓
                    built-in Datasets + Examples
```

架构分为五层，每一层职责单一，互不耦合：

1. **Theme System**（`theme/`）——所有视觉属性定义在 `Theme` 数据类中。10 套内置主题覆盖金融、医疗、政府、创意等关键行业场景。支持 `to_dict()`/`from_dict()` 序列化，可通过 JSON/YAML 在团队间共享。
2. **Core Engine**（`core/`）——`WorkbookManager` 封装 xlsxwriter 工作簿生命周期（文件/内存双模式），`FormatCache` 自动去重 Format 对象避免 xlsxwriter 64K 格式上限，`Grid` 将逻辑布局坐标转换为 Excel 行列号。
3. **Element System**（`elements/`）——所有内容元素继承 `BaseElement` 抽象基类，实现 `measure()` 声明空间需求和 `render()` 写入 Excel。内置 8 种元素：Title、Subtitle、Paragraph、Table、Chart、ComboChart、Image、Spacer。
4. **Layout Engine**（`layout/`）——`LayoutEngine` 管理多 Sheet，`SheetLayout` 管理单 Sheet 内的元素排列。支持顺序放置（`place_row`）和网格放置（`place_grid`），自动处理间距、边距和全宽元素。
5. **Smart Facade**（`facade/`）——用户入口。`Report` 提供流式构建器 API，`quick_report()` 提供一行自动检测。`build(path)` 写入磁盘，`build()` 返回 bytes 用于 Web API。

### 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|---------|
| 0.1.0 | 2025-07 | 初始发布：6套主题、7种元素、4种布局模板、1个预置报告 |
| **0.2.0** | **2025-07** | **当前版本**：主题深拷贝+序列化、4套新主题(共10套)、组合图表(双Y轴)、图表数据写入隐藏Sheet、智能列对齐(数字右对齐/日期居中)、打印页面设置、数据源模块(5个内置数据集)、3个新示例(财务/HR/供应链)、355个测试 |

---

## 安装与环境

```bash
# 安装
pip install databloom

# 开发环境（测试 + 格式化 + 类型检查）
git clone <repo-url> && cd report
pip install -e ".[dev]"
```

依赖：`xlsxwriter>=3.1.0`、`pandas>=2.0.0`、`matplotlib>=3.7.0`（可选，仅 matplotlib 图表后端需要）。

---

## 核心概念

在深入案例之前，理解三个核心概念能让你快速掌握 databloom：

### 1. Report 构建器是链式流

`Report` 对象上的每个方法都返回 `self`，所以你可以用点号连续调用。构建顺序就是报表中元素的出现顺序：

```
Report(title, theme)
  .set_page_setup(...)       # 全局打印设置
  .add_sheet("Sheet1")       # 开始第一个Sheet
  .add_title("标题")          # 大标题
  .add_table(df)             # 数据表格
  .add_chart(df, type="pie") # 图表
  .add_sheet("Sheet2")       # 开始第二个Sheet
  .add_title("第二页")
  ...
  .build("./output.xlsx")    # 生成文件
```

### 2. 主题控制一切视觉

所有颜色、字体、边框、图表色板都存储在 `Theme` 数据类中。10 套预置主题覆盖了从金融到政府的主流行业。通过 `get_theme(name)` 获取的是**深拷贝**——你可以安全地修改它而不影响全局预设。

### 3. 数据集是持久化的

所有内置数据集（财务利润表、HR人力数据、供应链看板等）在首次访问时自动生成并缓存为 pickle 文件。后续加载秒级返回。这保证了示例脚本在任何环境下都能稳定输出相同的数据——非常适合教学、演示和自动化测试。

---

## 快速上手

### Level 1 — 一行出报告

最简单的用法：传入 DataFrame，框架自动分析结构、选择布局、推断图表类型。

```python
from databloom import quick_report
import pandas as pd

df = pd.DataFrame({
    "Product": ["Widget A", "Widget B", "Widget C"],
    "Sales": [15000, 23000, 18000],
    "Growth": [0.12, 0.08, 0.15],
})

# 一行生成——自动选择布局、自动推断图表类型、自动格式化列
quick_report(df, output="./output/report.xlsx")
```

如果传入多个 DataFrame，框架会自动选择 `summary_detail` 模板（概要+图表+明细）布局：

```python
quick_report(kpi_df, detail_df, output="./output/multi.xlsx", theme="tech_dark")
```

自动检测逻辑会分析每列的 dtype：
- `int64`/`float64` → 数字格式（`#,##0` 或 `#,##0.00`），右对齐
- `datetime64` → 日期格式（`yyyy-mm-dd`），居中对齐
- `float64` 且值在 0~1 之间 → 百分比格式（`0.0%`）
- `object`/`string` → 左对齐
- 时间序列列 → 折线图
- 分类列 → 柱状图或条形图
- 多列数值 → 柱状图

### Level 2 — 声明式构建

需要更精细的控制时，使用 `Report` 构建器。支持完整的链式调用。

```python
from databloom import Report

report = (
    Report(title="月度销售分析", theme="business_blue")
    .set_page_setup(orientation="landscape", fit_to_width=1)

    # Sheet 1: 仪表盘
    .add_sheet("仪表盘")
    .add_title("2026年Q3销售概览")
    .add_subtitle("核心指标 | 数据截止：2026-09-30")
    .add_table(kpi_df, title="KPI汇总")

    .add_combo_chart(  # 组合图表：柱状图(营收+成本) + 折线图(毛利率)——v0.2 新增
        trend_df,
        category_col="月份",
        bar_cols=["营收", "成本"],
        line_cols=["毛利率"],
        bar_title="金额（元）",
        line_title="毛利率",
        title="月度经营趋势",
    )

    # Sheet 2: 明细数据
    .add_sheet("明细数据")
    .add_title("产品销售明细")
    .add_table(detail_df, column_formats={"单价": "#,##0.00", "营收": "#,##0.00"})

    # 生成文件
    .build("./output/sales_report.xlsx")
)
```

### Level 3 — 自定义主题

v0.2 新增了主题序列化功能，支持 JSON 导入导出。你可以基于任意内置主题微调颜色和字体，保存为公司内部的主题规范，然后在团队间共享。

```python
from databloom import get_theme
from databloom.theme.base import Theme
import json

# 基于内置主题创建公司品牌主题
theme = get_theme("business_blue")
theme.name = "my_company"
theme.global_font_name = "微软雅黑"          # 中文字体
theme.table.header_fill.color = "#1A5276"     # 深色表头
theme.accent_color = "#E74C3C"                # 品牌红色
theme.table.data_font.size = 11               # 稍大字号

# 保存为 JSON，提交到 Git 或内部文档平台
with open("my_company_theme.json", "w", encoding="utf-8") as f:
    json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)

# 团队成员加载
with open("my_company_theme.json", encoding="utf-8") as f:
    company_theme = Theme.from_dict(json.load(f))

report = Report(title="公司月报", theme=company_theme)
```

---

## 案例展示

以下四个案例从不同业务场景展示了 databloom 的完整能力。每个案例都可以直接运行对应的示例脚本。

| 案例 | 脚本 | Sheet 数 | 数据量 | 关键特性演示 |
|------|------|---------|--------|------------|
| 财务分析报告 | `examples/finance_report.py` | 3 | 12个月 | 组合图表、打印设置、finance_charcoal 主题 |
| HR 人力分析 | `examples/hr_analytics.py` | 3 | 200名员工 | load_dataset()、饼图、条形图、medical_teal 主题 |
| 供应链看板 | `examples/supply_chain.py` | 3 | 100笔采购 | load_dataset()、供应商分析、government_navy 主题 |
| 多主题仪表盘 | `examples/dashboard_fixed.py` | 2 | KPI + 3图表 | 10套主题全量生成、多图表并排布局 |

---

### 案例一：财务分析报告

**脚本**：`python examples/finance_report.py`

演示 v0.2 的**组合图表**、**打印页面设置**、**finance_charcoal 主题**和**智能列对齐**。

#### Sheet 结构

| Sheet | 规模 | 内容 | 关键特性 |
|-------|------|------|---------|
| **利润表** | 22行 × 14列 | 12个月月度营收/成本/毛利/费用/净利润 + 组合图表 | `add_combo_chart()` 柱状图(营收+成本+费用) + 折线图(净利率) 双Y轴 |
| **财务指标** | 42行 × 9列 | 偿债/营运/盈利/成长 4大类13项指标 vs 去年同期 | 数字列右对齐，指标名称左对齐 |
| **分析报告** | 25行 × 9列 | 经营概况 + 盈利能力分析 + 风险提示 + 展望 | `add_paragraph()` 多段文字，`add_spacer()` 间距控制 |

#### 组合图表代码

组合图表是业务分析中最常用的图表类型——柱状图展示"量"（营收、成本），折线图展示"率"（毛利率、净利率），双Y轴避免量级差异导致的视觉失真：

```python
report.add_combo_chart(
    profit_df,
    category_col="月份",
    bar_cols=["营业收入", "营业成本", "费用合计"],  # 左Y轴：金额
    line_cols=["净利率"],                            # 右Y轴：比率
    bar_title="金额（元）",
    line_title="净利率",
    title="月度经营趋势：营收/成本 vs 净利率",
)
```

#### 打印设置

`set_page_setup()` 配置后，在 Excel 中打印预览可看到 A4 横向、宽度适配为 1 页的效果：

```python
report = Report(title="2025年度财务分析报告", theme="finance_charcoal")
report.set_page_setup(
    orientation="landscape",  # 横向
    fit_to_width=1,           # 宽度适配1页
    fit_to_height=0,          # 高度不限页数
)
```

---

### 案例二：HR 人力分析报告

**脚本**：`python examples/hr_analytics.py`

使用 `load_dataset("hr_workforce")` 加载 200 名员工的模拟数据，展示组织人力效能分析。

#### Sheet 结构

| Sheet | 规模 | 内容 |
|-------|------|------|
| **人力概览** | KPI + 汇总表 | 6项核心指标（员工总数、月薪总额、平均月薪、平均绩效、离职率、满意度）+ 按部门汇总 + 按职级汇总 |
| **可视化分析** | 2个图表 + 说明 | 各部门人数分布饼图 + 薪资范围分布条形图 |
| **分析报告** | 2段分析 | 人才结构分析 + 关键发现与5条建议 |

#### 数据集字段

`hr_workforce` 数据集（200条）包含：员工ID、部门（6个部门）、职级（P1-M3共8级）、月薪、入职日期、绩效评分(1-5)、是否离职、满意度(1-10)。

#### 核心代码

```python
from databloom import Report
from databloom.data import load_dataset

df = load_dataset("hr_workforce")  # 200名员工数据

# 维度汇总
dept_summary = df.groupby("部门").agg(
    人数=("员工ID", "count"),
    平均薪资=("月薪(元)", "mean"),
    平均绩效=("绩效评分(1-5)", "mean"),
).reset_index().sort_values("人数", ascending=False)

report = Report(title="2025年度HR人力分析报告", theme="medical_teal")
report.set_page_setup(orientation="landscape", fit_to_width=1)

report.add_sheet("人力概览")
report.add_title("2025年度组织人力概览")
report.add_table(kpi_df, title="核心人力指标")
report.add_table(dept_summary, title="按部门汇总",
    column_formats={"平均薪资": "#,##0.00", "平均绩效": "0.0"})

report.add_sheet("可视化分析")
report.add_chart(dept_summary[["部门", "人数"]], type="pie",
    category_col="部门", value_cols=["人数"], title="各部门人数分布")

report.build("./output/hr_analytics.xlsx")
```

---

### 案例三：供应链管理看板

**脚本**：`python examples/supply_chain.py`

使用 `load_dataset("supply_chain")` 加载 100 笔采购订单数据。

#### Sheet 结构

| Sheet | 规模 | 内容 |
|-------|------|------|
| **采购看板** | KPI + 汇总表 | 5项核心指标（采购总额、平均到货周期、平均合格率、平均库存周转天数、订单总数）+ 按供应商汇总 + 按品类汇总 |
| **可视化分析** | 2个图表 + 说明 | 各供应商采购金额占比饼图 + 各品类平均合格率对比条形图 |
| **分析报告** | 2段分析 | 供应链概览 + 5条优化建议 |

#### 数据集字段

`supply_chain` 数据集（100条）包含：采购单号、供应商（8家）、品类（4类）、采购数量、单价、采购金额、到货周期(天)、合格率、库存周转天数。

#### 核心代码

```python
from databloom import Report
from databloom.data import load_dataset

df = load_dataset("supply_chain")  # 100笔采购订单

supplier_summary = df.groupby("供应商").agg(
    采购金额=("采购金额(元)", "sum"),
    订单数=("采购单号", "count"),
    平均合格率=("合格率", "mean"),
    平均到货周期=("到货周期(天)", "mean"),
).reset_index().sort_values("采购金额", ascending=False)

report = Report(title="2025年度供应链管理看板", theme="government_navy")
report.set_page_setup(orientation="landscape", fit_to_width=1)

report.add_sheet("采购看板")
report.add_table(kpi_df, title="核心供应链指标")
report.add_table(supplier_summary, title="按供应商汇总",
    column_formats={"采购金额": "#,##0.00", "平均合格率": "0.0%", "平均到货周期": "0.0"})

report.add_sheet("可视化分析")
report.add_chart(supplier_summary[["供应商", "采购金额"]],
    type="pie", category_col="供应商", value_cols=["采购金额"],
    title="各供应商采购金额占比")

report.build("./output/supply_chain.xlsx")
```

---

### 案例四：多主题仪表盘

**脚本**：`python examples/dashboard_fixed.py`

一次性为全部 10 套主题生成仪表盘，适合主题选型对比。每个仪表盘包含 KPI 表格 + 3 个并排图表（区域营收柱状图、品类毛利条形图、渠道订单分布饼图）。

这是 v0.2 修复仪表盘多图表重叠 bug 后的正确用法——通过 `full_width=False` 让多个图表真正并排放置：

```python
from databloom.elements.chart import ChartElement

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
```

---

## 内置数据集

v0.2 新增了 `databloom.data` 子包，内置 5 个商业数据集。每个数据集首次访问时自动生成并缓存为本地 pickle 文件，后续加载秒级返回。

```python
from databloom.data import load_dataset, list_datasets

# 列出所有可用数据集（5个）
print(list_datasets())
# ['finance_metrics', 'finance_profit', 'hr_workforce', 'sales_orders', 'supply_chain']

# 加载单个数据集
df = load_dataset("hr_workforce")        # → DataFrame (200行 × 8列)
df = load_dataset("supply_chain")        # → DataFrame (100行 × 9列)

# 强制重新生成（清空缓存）
df = load_dataset("hr_workforce", force_rebuild=True)
```

| 数据集名称 | 数据量 | 类型 | 描述 |
|-----------|--------|------|------|
| `finance_profit` | 12行 × 13列 | DataFrame | 月度利润表（营收/成本/毛利/费用/净利润/利润率） |
| `finance_metrics` | 13行 × 4列 | DataFrame | 财务指标：偿债/营运/盈利/成长4类 vs 去年同期 |
| `sales_orders` | 60行 × 13列 | DataFrame | 销售订单明细：10种产品 × 5个渠道 × 7个区域 |
| `hr_workforce` | 200行 × 8列 | DataFrame | 员工数据：6部门 × 8职级，含绩效/离职/满意度 |
| `supply_chain` | 100行 × 9列 | DataFrame | 采购订单：8家供应商 × 4品类，含合格率/到货周期/库存周转 |

**确定性保证**：所有数据集使用固定的随机种子（`_seed.py`），在任意机器、任意 Python 版本下生成的 pickle 完全一致。适合 CI/CD 流水线中的自动化测试。

---

## 内置主题

databloom 提供 **10 套**经过专业设计的主题。每套主题包含完整的颜色系统（表头/交替行/边框/强调色）、字体层级（标题20pt → 副标题13pt → 正文10pt）和10色图表色板。

| 主题名 | 主色调 | 字体 | 适用场景 | 设计思路 |
|--------|--------|------|----------|---------|
| `business_blue` | 深蓝 `#2F5496` | Arial | 企业财报、董事会汇报 | 最经典的企业色，稳妥不出错 |
| `finance_charcoal` | 深灰 `#374151` + 红 `#DC2626` | Lato | 银行、券商、保险 | 深灰表头传达权威感，红色强调亏损/风险 |
| `medical_teal` | 青绿 `#0D9488` | Noto Sans | 医疗健康、生命科学 | 青绿色传递洁净、可信赖的行业气质 |
| `fresh_green` | 森林绿 `#548235` | Calibri | 环保、农业、可持续发展 | 自然色调，低饱和度不刺眼 |
| `creative_magenta` | 洋红 `#BE185D` | Poppins | 市场营销、创意设计、电商运营 | 高饱和度传达活力与创意 |
| `warm_orange` | 暖橙 `#ED7D31` | Tahoma | 零售、酒店、餐饮 | 温暖亲切，适合消费者面向的报表 |
| `government_navy` | 海军蓝 `#1E3A5F` | Source Sans 3 | 政府、国企、公共部门 | 庄重正式，高对比度利于打印和屏幕阅读 |
| `tech_dark` | 青色 `#00BCD4` 深色背景 | Segoe UI | 科技公司、数据仪表盘 | 现代科技感，深色背景减少屏幕疲劳 |
| `minimal_gray` | 低饱和灰 `#555555` | Helvetica | 法律、合规、正式报告 | 极简主义，让数据本身成为焦点 |
| `classic_white` | 黑白 `#000000` | Arial | 传统打印、内部流转 | 无交替色，适合黑白打印环境 |

**使用方式**：

```python
from databloom import list_themes, get_theme

# 查看所有可用主题（10个）
print(list_themes())

# 获取主题实例（返回深拷贝，安全可改——v0.2 修复）
theme = get_theme("fresh_green")
theme.table.data_font.size = 12  # 不会影响全局预设，其他调用者不受影响
```

**主题对比测试**：运行 `python examples/all_themes.py` 一次性生成全部 10 套主题的预览文件，在 Excel 中打开即可横向对比。

---

## 完整 API 参考

### `quick_report()`

```python
def quick_report(
    *dataframes: pd.DataFrame,
    output: str | Path | None = None,
    theme: str | Theme = "business_blue",
    title: str = "Quick Report",
    chart_type: str = "auto",
) -> bytes | None:
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `*dataframes` | `DataFrame` | — | 一个或多个 DataFrame。传入 3+ 个时发出警告（仅使用前2个）。 |
| `output` | `str \| Path \| None` | `None` | 文件路径；`None` 返回 bytes（适合 Web API）。 |
| `theme` | `str \| Theme` | `"business_blue"` | 主题名称（10选1）或 Theme 实例。 |
| `title` | `str` | `"Quick Report"` | 报告标题。 |
| `chart_type` | `str` | `"auto"` | `"auto"` 自动检测，或显式指定 `column/bar/line/pie/area/scatter`。 |

**返回**：`bytes` 当 `output=None`，否则 `None`（文件写入磁盘）。

---

### `Report` 构建器

```python
class Report:
    def __init__(self, title: str = "Report", theme: str | Theme = "business_blue"):
```

#### Sheet 管理

| 方法 | 参数 | 说明 |
|------|------|------|
| `.add_sheet(name)` | `name: str` | 创建新工作表，后续调用默认作用于此 Sheet。重复名字抛 `ValueError`。 |

#### 文本元素

| 方法 | 参数 | 说明 |
|------|------|------|
| `.add_title(text)` | `text: str` | 主标题（20pt 加粗，主题色） |
| `.add_subtitle(text)` | `text: str` | 副标题（13pt，较浅色） |
| `.add_paragraph(text)` | `text: str` | 正文段落（10pt，自动换行） |

#### 数据元素

| 方法 | 参数 | 说明 |
|------|------|------|
| `.add_table(df, *, title, column_formats, conditional_format_rules)` | 见下方 | 格式化表格。数字列智能右对齐、文字列左对齐、日期列居中。 |
| `.add_chart(df, type, *, category_col, value_cols, title, backend)` | 见下方 | 原生 Excel 图表，6种类型，支持 xlsxwriter/matplotlib 双后端。 |
| `.add_combo_chart(df, *, category_col, bar_cols, line_cols, bar_title, line_title, title)` | 见下方 | 🆕 组合图表：柱状图+折线图双Y轴。 |

**`add_table()` 参数**：
- `df: DataFrame` — 源数据
- `title: str | None` — 可选表头行（合并跨所有列）
- `column_formats: dict[str, str] | None` — 列名 → xlsxwriter 格式字符串（如 `{"营收": "#,##0.00", "毛利率": "0.0%"}`）
- `conditional_format_rules: list[dict] | None` — xlsxwriter 条件格式规则列表

**`add_chart()` 参数**：
- `df: DataFrame` — 源数据
- `type: str` — 图表类型：`column`/`bar`/`line`/`pie`/`area`/`scatter`
- `category_col: str | None` — X轴列名，省略时自动检测
- `value_cols: list[str] | None` — Y轴列名列表，省略时自动检测所有数值列
- `title: str` — 图表标题
- `backend: str` — `"xlsxwriter"`（默认，交互式）或 `"matplotlib"`（静态图片）

**`add_combo_chart()` 参数**：
- `df: DataFrame` — 源数据
- `category_col: str | None` — X轴列名
- `bar_cols: list[str] | None` — 柱状图列名列表（左Y轴）
- `line_cols: list[str] | None` — 折线图列名列表（右Y轴）
- `bar_title: str` — 柱状图轴标签
- `line_title: str` — 折线图轴标签
- `title: str` — 图表标题

#### 布局控制

| 方法 | 参数 | 说明 |
|------|------|------|
| `.add_spacer(*, rows, height)` | `rows: int = 1`, `height: int = 12` | 插入空白间距 |
| `.add_image(path, *, scale_x, scale_y)` | `path: str \| Path` | 插入 PNG/JPG 图片 |
| `.apply_template(template_name, **kwargs)` | 见下方 | 应用预定义布局模板 |

**`apply_template()`** 支持的模板：
- `"simple"` — 标题 → 表格
- `"summary_detail"` — 标题 → 汇总表 → 图表 → 明细表（2 Sheet）
- `"dashboard"` — 标题 → KPI表 → 多图表并排
- `"report"` — 标题 → 副标题 → 段落 → 图表 → 表格 → 页脚

#### 打印与页面设置 🆕

| 方法 | 参数 | 说明 |
|------|------|------|
| `.set_page_setup(*, orientation, paper, margins, fit_to_width, fit_to_height, print_title_rows)` | 见下方 | 应用于所有 Sheet 的打印设置 |

**`set_page_setup()` 参数**：
- `orientation: str` — `"landscape"`（横向）或 `"portrait"`（纵向），默认横向
- `paper: int` — 纸张类型索引：9=A4, 1=Letter, 13=B5，默认 A4
- `margin_left/right/top/bottom: float` — 页边距（英寸），默认 0.7/0.7/0.75/0.75
- `fit_to_width: int` — 宽度适配页数，0=不限，默认 1
- `fit_to_height: int` — 高度适配页数，0=不限，默认 0
- `print_title_rows: int` — 每页重复打印的标题行数，默认 0

#### 生成与输出

| 方法 | 说明 |
|------|------|
| `.build(output=None) → bytes \| None` | 渲染所有 Sheet 并写入文件或返回 bytes |

---

### 数据源模块 🆕

```python
from databloom.data import load_dataset, list_datasets
```

| 函数 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `list_datasets()` | — | `list[str]` | 返回所有可用数据集名称（5个） |
| `load_dataset(name, force_rebuild=False)` | `name: str`, `force_rebuild: bool` | `DataFrame \| dict` | 加载数据集，首次生成并缓存为 pickle |

---

### 主题 API

```python
from databloom import get_theme, list_themes
from databloom.theme.base import Theme
```

| 函数/方法 | 说明 |
|----------|------|
| `list_themes()` | 返回所有内置主题名称（10个） |
| `get_theme(name)` | 返回主题的**深拷贝**（v0.2 修复：安全可改，不污染全局） |
| `theme.to_dict()` | 序列化为字典（可用于 JSON 导出） |
| `Theme.from_dict(data)` | 从字典反序列化（可用于 JSON 导入） |

---
	
## 开发指南

### 环境准备

```bash
git clone <repo-url> && cd report
pip install -e ".[dev]"         # 包含 pytest、ruff、mypy、openpyxl
```

### 运行测试

```bash
pytest                              # 全部 355 个测试
pytest tests/test_data/             # 数据集模块测试（15个）
pytest tests/test_theme/            # 主题相关测试（含序列化）
pytest tests/test_elements/         # 元素测试（含组合图表）
pytest --cov=databloom              # 带覆盖率报告
pytest -m "not slow"                # 排除 matplotlib 慢速测试
```

### 代码规范

```bash
ruff check src/ tests/ examples/    # Lint 检查（零错误）
ruff format src/ tests/ examples/   # 自动格式化
mypy src/databloom/                 # 严格模式类型检查
```

### 运行示例

```bash
python examples/quick_start.py              # 一行出报告
python examples/custom_layout.py            # 声明式构建
python examples/all_themes.py               # 10套主题全量预览
python examples/finance_report.py            # 财务分析报告（组合图表+打印设置）
python examples/hr_analytics.py             # HR人力分析（load_dataset + medical_teal）
python examples/supply_chain.py             # 供应链看板（load_dataset + government_navy）
python examples/dashboard_fixed.py          # 10套主题多图表仪表盘对比
```

### 项目统计

| 指标 | 数值 |
|------|------|
| 版本 | 0.2.0 |
| 测试 | 355 个（全部通过） |
| 覆盖率 | 95% |
| 主题 | 10 套 |
| 元素类型 | 8 种（含 ComboChart） |
| 内置数据集 | 5 个 |
| 示例脚本 | 7 个 |
| 源代码 | ~3,500 行 |
| ruff 错误 | 0 |
| mypy 类型检查 | 严格模式通过 |

---

## License

MIT — 详见 [LICENSE](LICENSE)
