# databloom

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![English Docs](https://img.shields.io/badge/README-English-blue)](./README.md)

> 从 pandas DataFrame 一键生成精美的 Excel 报告。18 套主题、9 种图表、智能自动检测、公式表格、定时任务——让数据在 Excel 中绽放。

---

## 目录

- [特性](#特性)
- [安装](#安装)
- [快速上手](#快速上手)
- [内置主题](#内置主题)
- [自定义主题](#自定义主题)
- [API 参考](#api-参考)
- [内置数据集](#内置数据集)
- [开发指南](#开发指南)
- [License](#license)

---

## 特性

- **双重模式**：`quick_report(df)` 一行出报告，或使用 `Report` 构建器精细控制
- **18 套主题**：专业设计的配色方案，覆盖金融、医疗、政府、科技、创意等场景
- **9 种图表**：柱状图、条形图、折线图、饼图、环形图、面积图、散点图、雷达图、股价图——外加柱+线双 Y 轴组合图
- **智能检测**：自动推断列类型、数字格式、对齐方式、图表类型和布局
- **公式表格**：通过 `add_formula_table()` 在表尾追加 SUM/AVERAGE/MAX/MIN 等原生 Excel 公式行
- **定时任务**：`BloomScheduler` 支持每日/每周/每月定时生成报告
- **格式化表格**：交替行配色、智能对齐（数字右对齐、文字左对齐、日期居中）、冻结窗格
- **组合图表**：柱状图+折线图双 Y 轴——量价同图的最佳方案
- **图片插入**：支持本地 PNG/JPG 图片嵌入
- **内置数据集**：5 个商业数据集（财务、销售、HR、供应链）——首次生成后 pickle 缓存
- **主题序列化**：`to_dict()`/`from_dict()` 支持 JSON/YAML 导入导出，团队共享
- **打印设置**：支持 A4 横向/纵向、页边距、宽度适配、标题行重复
- **类型安全**：mypy 严格模式全量标注

---

## 安装

```bash
pip install databloom
```

安装定时任务功能（可选）：

```bash
pip install "databloom[scheduler]"
```

开发环境：

```bash
pip install -e ".[dev]"
```

---

## 快速上手

### Level 1 — 一行出报告

```python
from databloom import quick_report
import pandas as pd

df = pd.DataFrame({
    "产品": ["组件A", "组件B", "组件C"],
    "销量": [15000, 23000, 18000],
    "增长率": [0.12, 0.08, 0.15],
})

quick_report(df, output="./output/report.xlsx")
```

### Level 2 — 声明式构建

```python
from databloom import Report

report = (
    Report(title="月度销售分析", theme="business_blue")
    .set_page_setup(orientation="landscape", fit_to_width=1)
    .add_sheet("概览")
    .add_title("2026年Q3销售概览")
    .add_table(summary_df)
    .add_combo_chart(
        trend_df,
        category_col="月份",
        bar_cols=["营收", "成本"],
        line_cols=["毛利率"],
        bar_title="营收 & 成本",
        line_title="毛利率",
        title="营收 vs 毛利率趋势",
    )
    .add_sheet("明细")
    .add_title("产品销售明细")
    .add_table(detail_df)
    .add_formula_table(
        detail_df,
        formulas={"营收": "SUM", "成本": "SUM"},
        formula_label="合计",
    )
    .build("./output/sales_report.xlsx")
)
```

### Level 3 — 定时任务

```python
from databloom.scheduler import BloomScheduler, ReportConfig

config = ReportConfig(
    title="销售周报",
    theme="business_blue",
    output_path="./output/weekly_sales.xlsx",
    data_factory=lambda: pd.read_sql("SELECT * FROM sales", conn),
)

scheduler = BloomScheduler()
scheduler.weekly(config, day="monday", at="09:00")
scheduler.start()  # 启动调度循环，Ctrl+C 停止
```

---

## 内置主题

| 主题名 | 主色调 | 字体 | 适用场景 |
|--------|--------|------|----------|
| `business_blue` | 深蓝 `#2F5496` | Arial | 企业财报、董事会汇报 |
| `finance_charcoal` | 深灰 `#374151` + 红 | Lato | 银行、证券、保险 |
| `medical_teal` | 青绿 `#0D9488` | Noto Sans | 医疗健康、生命科学 |
| `fresh_green` | 森林绿 `#548235` | Calibri | 环保、农业、可持续发展 |
| `creative_magenta` | 洋红 `#BE185D` | Poppins | 营销、创意、电商 |
| `warm_orange` | 暖橙 `#ED7D31` | Tahoma | 零售、酒店、餐饮 |
| `government_navy` | 海军蓝 `#1E3A5F` | Source Sans 3 | 政府、国企、公共部门 |
| `tech_dark` | 青色 `#00BCD4` 深底 | Segoe UI | 科技公司、数据仪表盘 |
| `minimal_gray` | 低饱和灰 `#555555` | Helvetica | 法律、合规、正式报告 |
| `classic_white` | 黑白 `#000000` | Arial | 传统打印、内部流转 |
| `sunset_coral` | 暖珊瑚粉 `#E07A5F` | Nunito | 生活方式、健康、酒店 |
| `ocean_depths` | 深海蓝 `#006D77` | Roboto | 海运、物流、旅游 |
| `forest_dawn` | 大地棕 `#5E503F` | Lora | 教育、出版、非营利 |
| `slate_pro` | 蓝灰 `#4A5568` | IBM Plex Sans | 工程、SaaS、B2B |
| `amber_academic` | 暖棕 `#A0522D` | Georgia | 学术、研究、人文 |
| `midnight_plum` | 深紫 `#4A235A` | Montserrat | 奢侈品、时尚、高端品牌 |
| `sage_earth` | 灰绿 `#6B705C` | Work Sans | 健康、有机、可持续 |
| `arctic_frost` | 冰蓝 `#318FB5` | Inter | 北欧风格、清爽仪表盘 |

---

## 自定义主题

你可以基于内置主题微调颜色和字体，保存为公司品牌规范：

```python
from databloom import get_theme
import json

# 基于内置主题创建公司品牌主题
theme = get_theme("business_blue")
theme.name = "my_company"
theme.global_font_name = "微软雅黑"
theme.table.header_fill.color = "#1A5276"
theme.accent_color = "#E74C3C"
theme.table.data_font.size = 12  # 深拷贝安全，不影响全局预设

# 导出为 JSON
with open("my_company_theme.json", "w", encoding="utf-8") as f:
    json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)

# 团队成员加载
from databloom.theme.base import Theme

with open("my_company_theme.json", encoding="utf-8") as f:
    company_theme = Theme.from_dict(json.load(f))

report = Report(title="公司月报", theme=company_theme)
```

---

## API 参考

### `quick_report(*dataframes, output, theme, title, chart_type) → bytes | None`

自动分析 DataFrame 结构，选择最佳布局和图表类型。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `*dataframes` | `DataFrame` | — | 一个或多个 DataFrame |
| `output` | `str \| Path \| None` | `None` | 文件路径；`None` 时返回 `bytes` |
| `theme` | `str \| Theme` | `"business_blue"` | 主题名称或实例 |
| `title` | `str` | `"Quick Report"` | 报告标题 |
| `chart_type` | `str` | `"auto"` | 自动检测或指定类型（column/bar/line/pie/doughnut/area/scatter/radar/stock） |

### `Report(title, theme)` — 构建器

| 方法 | 说明 |
|------|------|
| `Report.quick(*dfs, title, theme, chart_type)` | 自动分析 DataFrame，返回可扩展的 `Report` 实例 |
| `.add_sheet(name)` | 创建新工作表 |
| `.add_title(text)` | 大标题（20pt 加粗） |
| `.add_subtitle(text)` | 副标题（13pt） |
| `.add_paragraph(text)` | 正文段落（10pt，自动换行） |
| `.add_table(df, *, title, column_formats, freeze_panes)` | 格式化表格，智能列对齐 |
| `.add_formula_table(df, *, title, formulas, formula_label, freeze_panes)` | 表格 + 底部 SUM/AVERAGE/MAX/MIN 公式行 |
| `.add_chart(df, type, *, category_col, value_cols, title, backend)` | 原生 Excel 图表（9 种类型） |
| `.add_combo_chart(df, *, category_col, bar_cols, line_cols, bar_title, line_title, title)` | 组合图表（柱状图 + 折线图，双 Y 轴） |
| `.add_image(path, *, scale_x, scale_y)` | 插入 PNG/JPG 图片 |
| `.add_spacer(*, rows, height)` | 插入垂直间距 |
| `.set_page_setup(*, orientation, paper, margins, fit_to_width, fit_to_height, print_title_rows)` | 打印页面设置 |
| `.apply_template(template_name, **kwargs)` | 应用预设布局模板 |
| `.build(output=None)` | 渲染并生成文件或返回 bytes |

### `BloomScheduler` — 定时任务

```python
from databloom.scheduler import BloomScheduler, ReportConfig
```

| 方法 | 说明 |
|------|------|
| `scheduler.daily(config, at="09:00")` | 每天指定时间生成报告 |
| `scheduler.weekly(config, day="monday", at="09:00")` | 每周指定日期时间生成 |
| `scheduler.every_hours(config, hours=1)` | 每隔 N 小时生成 |
| `scheduler.every_minutes(config, minutes=30)` | 每隔 N 分钟生成 |
| `scheduler.start()` | 启动调度循环（阻塞，Ctrl+C 停止） |

---

## 内置数据集

```python
from databloom.data import load_dataset, list_datasets

print(list_datasets())
# ['finance_metrics', 'finance_profit', 'hr_workforce', 'sales_orders', 'supply_chain']

df = load_dataset("hr_workforce")  # 200行 × 8列
```

| 数据集 | 数据量 | 说明 |
|--------|--------|------|
| `finance_profit` | 12行 × 13列 | 月度利润表（营收、成本、毛利、费用、净利润） |
| `finance_metrics` | 13行 × 4列 | 四大类财务健康指标（偿债/营运/盈利/成长） |
| `sales_orders` | 60行 × 13列 | 销售订单（10种产品 × 5渠道 × 7区域） |
| `hr_workforce` | 200行 × 8列 | 员工数据（6部门 × 8职级，含绩效/离职/满意度） |
| `supply_chain` | 100行 × 9列 | 采购订单（8家供应商 × 4品类，含合格率/到货周期） |

---

## 开发指南

```bash
# 运行测试
pytest

# 测试覆盖率
pytest --cov=databloom --cov-report=term-missing

# 代码检查
ruff check src/ tests/

# 自动格式化
ruff format src/ tests/

# 类型检查
mypy src/databloom/
```

---

## License

MIT — 详见 [LICENSE](LICENSE)
