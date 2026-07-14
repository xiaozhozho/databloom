# Excel报表框架 - 开发计划 (code-plan.md)

## 1. 项目概述

### 1.1 目标
使用 Python + xlsxwriter + pandas 开发一个快速制作精美 Excel 报表的框架，通过传入 pandas.DataFrame 即可快速生成精美的 Excel 报表。

### 1.2 核心需求
- **使用方式**：两者兼顾 —— 简单场景一行代码自动生成，复杂场景声明式 API 精确控制
- **报表内容**：表格 + 图表混合，支持条件格式、颜色标识
- **布局控制**：自由网格布局，每个元素可指定位置和行列占用
- **多Sheet**：支持一个工作簿内多个 Sheet，每个 Sheet 独立布局
- **图表引擎**：xlsxwriter 内置图表 + matplotlib 生成图片，两者结合
- **样式主题**：内置多套精心设计的配色主题，可一键切换
- **Python 版本**：3.10+，使用现代 Python 特性
- **测试框架**：pytest
- **项目定位**：可发布的 pip 包

---

## 2. 项目名称

`excelreport`（暂定）

---

## 3. 技术栈

| 类别 | 技术 | 用途 |
|------|------|------|
| 运行时 | Python 3.10+ | 主语言 |
| Excel 生成 | xlsxwriter | 底层 Excel 写入 |
| 数据处理 | pandas | DataFrame 处理与数据检测 |
| 图表生成 | matplotlib | 复杂图表渲染为图片 |
| 图表生成 | xlsxwriter (内置) | 原生 Excel 交互式图表 |
| 项目管理 | hatchling / setuptools | 构建系统 |
| 代码质量 | ruff | Lint & Format |
| 类型检查 | mypy | 静态类型检查 |
| 测试 | pytest + pytest-mock + pytest-cov | 单元测试、覆盖率 |
| 版本管理 | git | 代码版本控制 |

---

## 4. 功能模块

### 4.1 Core Engine（核心引擎）
对 xlsxwriter 的薄封装，隐藏底层细节。

**职责：**
- 统一的 Workbook/Sheet 创建与管理
- 单元格坐标计算（行号、列号、A1 表示法等）
- 合并单元格、冻结窗格、打印设置等底层操作
- 不包含任何样式逻辑

**关键类：**
- `WorkbookManager`：管理 xlsxwriter Workbook 生命周期
- `Grid`：网格坐标计算引擎，将逻辑布局转换为 Excel 行列坐标

### 4.2 Element System（元素系统）
将报表内容抽象为独立"元素"，每个元素可独立渲染到指定位置。

**职责：**
- 定义 `BaseElement` 抽象基类
- 各元素类型实现自己的渲染、测量逻辑
- 元素可组合、可扩展

**元素类型：**
| 元素 | 说明 |
|------|------|
| `TableElement` | 将 DataFrame 渲染为格式化表格，支持条件格式、色阶 |
| `ChartElement` | 图表元素，支持 xlsxwriter 原生图表和 matplotlib 图片两种模式 |
| `TitleElement` | 报表主标题 |
| `SubtitleElement` | 副标题 / 描述文字 |
| `ParagraphElement` | 正文段落 |
| `ImageElement` | 插入外部图片 |
| `SpacerElement` | 空白占位 |

**元素接口（BaseElement）：**
- `measure()`：返回元素所需的行高、列宽
- `render(workbook, sheet, position)`：将元素渲染到指定位置
- `needs_full_width()`：是否需要占满整行宽度

### 4.3 Layout Engine（布局引擎）
负责将元素放置到 Sheet 上，计算精确坐标。

**职责：**
- 网格系统：用户声明行/列的区域占用，引擎计算精确的 Excel 坐标
- 自动计算行高列宽，处理元素之间的间距
- 支持多 Sheet，每个 Sheet 有独立的布局
- 提供内置布局模板

**关键类：**
- `LayoutEngine`：核心布局计算，元素放置
- `SheetLayout`：单个 Sheet 上的布局定义

**内置布局模板：**
- `summary_detail`：标题 → 摘要表 → 图表 → 明细数据表
- `dashboard`：标题 → 多图表网格 → KPI 卡片
- `report`：标题 → 段落 → 图表 → 数据表 → 页脚
- `simple`：标题 → 单个数据表

### 4.4 Theme System（主题系统）
管理系统内所有的视觉样式定义。

**职责：**
- 定义 `Theme` 数据类，包含所有可配置的样式属性
- 内置多套精心设计的主题
- 支持局部样式覆盖

**内置主题：**
| 主题名 | 风格描述 |
|--------|----------|
| `business_blue` | 专业商务蓝，深蓝表头 + 浅灰交替行 |
| `fresh_green` | 清新自然绿，适合环保/健康/农业场景 |
| `tech_dark` | 科技深色，深底白字，适合科技/数据场景 |
| `warm_orange` | 暖橙活力，适合营销/创意/零售场景 |
| `minimal_gray` | 极简灰，低饱和配色，适合正式报告 |
| `classic_white` | 经典白底，传统表格风格 |

**主题属性：**
- 表头颜色（背景、字体）
- 数据行颜色（奇偶行背景、边框）
- 标题/副标题字体族、字号、颜色
- 图表配色方案（系列色板）
- 全局字体族
- 数字格式模板

### 4.5 Smart Facade（智能门面）
面向用户的顶层 API，提供两种使用方式。

**职责：**
- 声明式 API（`Report` Builder）：链式调用构建报表
- 智能 API（`quick_report()`）：一行代码自动生成

**使用示例：**

```python
# 方式一：声明式 API
from excelreport import Report

report = (
    Report(title="月度销售分析", theme="business_blue")
    .add_sheet("概览")
    .add_title("2026年7月销售概览")
    .add_table(summary_df)
    .add_chart(trend_df, type="line", title="销售趋势")
    .add_sheet("明细")
    .add_title("销售明细数据")
    .add_table(detail_df)
    .build("./output/销售分析报告.xlsx")  # 指定路径，未指定则返回bytes
)

# 方式二：智能快速生成
from excelreport import quick_report

quick_report(df, output="./output/report.xlsx")
```

**设计决策：** `build(path)` 入参指定路径写入文件；未传入则返回 bytes，方便 Web API 场景使用。

### 4.6 Utils（工具模块）
- `inspection.py`：DataFrame 特征检测
  - 列类型识别（数值、日期、文本、分类）
  - 数据分布分析（是否适合图表、建议图表类型）
  - 自动推断报表元素和布局

---

## 5. 项目结构

```
report/
├── pyproject.toml              # 项目元数据、依赖、构建配置
├── LICENSE
├── README.md
├── .gitignore
├── CLAUDE.md                   # Claude Code 指引
├── src/
│   └── excelreport/
│       ├── __init__.py         # 公共 API 导出
│       ├── core/
│       │   ├── __init__.py
│       │   ├── workbook.py     # Workbook/Sheet 封装
│       │   └── grid.py         # 网格坐标计算引擎
│       ├── elements/
│       │   ├── __init__.py
│       │   ├── base.py         # BaseElement 抽象基类
│       │   ├── table.py        # TableElement
│       │   ├── chart.py        # ChartElement (xlsxwriter + matplotlib)
│       │   ├── text.py         # TitleElement, SubtitleElement, ParagraphElement
│       │   └── image.py        # ImageElement
│       ├── layout/
│       │   ├── __init__.py
│       │   ├── engine.py       # 布局引擎：元素放置、碰撞检测
│       │   └── templates.py    # 内置布局模板
│       ├── theme/
│       │   ├── __init__.py
│       │   ├── base.py         # Theme 数据类
│       │   └── presets.py      # 内置主题定义
│       ├── facade/
│       │   ├── __init__.py
│       │   ├── report.py       # Report Builder（声明式API）
│       │   └── quick.py        # quick_report() 智能生成
│       └── utils/
│           ├── __init__.py
│           └── inspection.py   # DataFrame 特征检测
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures（示例DataFrame、临时路径等）
│   ├── test_core/
│   │   ├── __init__.py
│   │   ├── test_workbook.py
│   │   └── test_grid.py
│   ├── test_elements/
│   │   ├── __init__.py
│   │   ├── test_table.py
│   │   ├── test_chart.py
│   │   ├── test_text.py
│   │   └── test_image.py
│   ├── test_layout/
│   │   ├── __init__.py
│   │   ├── test_engine.py
│   │   └── test_templates.py
│   ├── test_theme/
│   │   ├── __init__.py
│   │   ├── test_base.py
│   │   └── test_presets.py
│   └── test_facade/
│       ├── __init__.py
│       ├── test_report.py
│       └── test_quick.py
└── examples/
    ├── quick_start.py
    ├── custom_layout.py
    └── all_themes.py
```

---

## 6. 开发计划（分阶段）

### Phase 1：项目基础设施搭建
**目标：** 搭好骨架，确保开发流程跑通

| 任务 | 说明 |
|------|------|
| 1.1 | 初始化 git 仓库，创建 `.gitignore` |
| 1.2 | 创建 `pyproject.toml`，配置项目元数据、依赖、构建系统 |
| 1.3 | 配置 ruff（lint & format）、mypy（类型检查） |
| 1.4 | 配置 pytest，创建基础 `conftest.py` 和 fixtures |
| 1.5 | 创建项目目录结构（空包） |
| 1.6 | 编写 README.md 框架 |

### Phase 2：Theme System（主题系统）
**目标：** 先完成样式基础设施，后续所有模块依赖它

| 任务 | 说明 |
|------|------|
| 2.1 | 定义 `Theme` 数据类，包含所有样式属性 |
| 2.2 | 实现 6 套内置主题（business_blue, fresh_green, tech_dark, warm_orange, minimal_gray, classic_white） |
| 2.3 | 编写主题单元测试 |

### Phase 3：Core Engine（核心引擎）
**目标：** xlsxwriter 封装，提供稳定的底层接口

| 任务 | 说明 |
|------|------|
| 3.1 | 实现 `WorkbookManager`：工作簿/工作表创建管理 |
| 3.2 | 实现 `Grid`：网格坐标计算（逻辑网格 → Excel 行列坐标） |
| 3.3 | 编写核心引擎单元测试 |

### Phase 4：Element System（元素系统）
**目标：** 实现所有报表元素

| 任务 | 说明 |
|------|------|
| 4.1 | 实现 `BaseElement` 抽象基类和接口 |
| 4.2 | 实现 `TitleElement`、`SubtitleElement`、`ParagraphElement` |
| 4.3 | 实现 `TableElement`（DataFrame → 格式化表格，条件格式、色阶） |
| 4.4 | 实现 `ChartElement`（xlsxwriter 原生图表 + matplotlib 图片两种模式） |
| 4.5 | 实现 `ImageElement` |
| 4.6 | 编写元素单元测试 |

### Phase 5：Layout Engine（布局引擎）
**目标：** 元素放置与布局计算

| 任务 | 说明 |
|------|------|
| 5.1 | 实现 `LayoutEngine`：元素放置、间距计算、碰撞检测 |
| 5.2 | 实现 `SheetLayout`：单 Sheet 布局管理 |
| 5.3 | 实现 4 套内置布局模板 |
| 5.4 | 编写布局引擎单元测试 |

### Phase 6：Smart Facade（用户接口层）
**目标：** 顶层的用户友好 API

| 任务 | 说明 |
|------|------|
| 6.1 | 实现 `Report` Builder：链式声明式 API |
| 6.2 | 实现 `quick_report()`：智能快速生成 |
| 6.3 | 实现 `DataFrame` 特征检测工具 |
| 6.4 | 编写门面层单元测试 + 集成测试 |

### Phase 7：收尾打磨
**目标：** 示例、文档、质量保障

| 任务 | 说明 |
|------|------|
| 7.1 | 编写 3 个示例脚本（quick_start, custom_layout, all_themes） |
| 7.2 | 编写 CLAUDE.md |
| 7.3 | 补充 README.md |
| 7.4 | 测试覆盖率检查，确保 ≥ 80% |

---

## 7. 验证方式

- **单元测试**：每个模块独立测试，mock xlsxwriter 调用
- **集成测试**：使用临时文件路径，生成真实 xlsx 文件后用 openpyxl/pandas 回读验证
- **类型检查**：`mypy src/excelreport/` 零错误
- **Lint**：`ruff check src/ tests/` 零警告
- **示例脚本**：手动运行 examples/ 下脚本，检查输出的 xlsx 文件视觉效果
