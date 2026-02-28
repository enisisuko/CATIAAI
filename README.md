# CATIA MCP Server

通过 MCP (Model Context Protocol) 将云端大模型连接到 CATIA V5/V6，实现 AI 驱动的 CAD 自动化。

采用 **CLINE 风格 Agent 思维链路**，让 AI 像工程师一样思考、规划、执行 CATIA 操作。

## 架构

```
Cloud LLM (Claude/GPT/etc.)
        │
        │  MCP Protocol (stdio/SSE)
        ▼
┌──────────────────────────────────────────────┐
│           CATIA MCP Server (本软件)            │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │  pycatia  │  │ pywinauto│  │   Agent    │ │
│  │  COM API  │  │ Smart UI │  │  Workflow  │ │
│  │ (推荐后端) │  │ (智能UI)  │  │ (思维链路)  │ │
│  └────┬─────┘  └────┬─────┘  └────────────┘ │
│       │              │                       │
│  ┌────┴─────┐  ┌────┴──────┐                │
│  │ pyautogui│  │ pywin32   │                │
│  │ (屏幕截图) │  │ (直接COM) │                │
│  └──────────┘  └───────────┘                │
└──────────────────────────────────────────────┘
         │              │
         ▼              ▼
    CATIA V5/V6    Screen/UI
```

## 集成的开源项目

| 开源项目 | 版本 | 用途 |
|---------|------|------|
| [pycatia](https://github.com/evereux/pycatia) | ≥0.9.0 | CATIA V5 COM 自动化 (推荐后端) |
| [pywinauto](https://github.com/pywinauto/pywinauto) | ≥0.6.0 | Windows UI 智能自动化 |
| [FastMCP](https://github.com/modelcontextprotocol/python-sdk) | ≥1.0.0 | MCP 协议服务器框架 |
| [pyautogui](https://github.com/asweigart/pyautogui) | ≥0.9.54 | 屏幕截图/坐标点击 |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | ≥2.0.0 | 配置管理 |

## 功能模块 (94 MCP Tools + Resources + Prompts)

| 模块 | 工具数 | 功能 |
|------|--------|------|
| **System** | 15 | 连接管理, 文档操作, 特征树, 参数, 宏, 撤销/重做 |
| **Sketcher** | 10 | 线/圆/矩形/弧/样条/点, 约束, 倒角, 裁剪 |
| **Part Design** | 12 | 拉伸/凹槽/旋转/倒角/圆角/壳体/孔/阵列/镜像 |
| **Assembly** | 8 | 插入组件, 约束 (重合/接触/偏移/角度/固定), BOM |
| **Drawing** | 7 | 视图 (主/投影/剖/局部/等轴测), 标注, 注释 |
| **Surface** | 10 | 拉伸/旋转/扫掠/填充/放样/偏移/混合/修剪/分割/连接 |
| **Measurement** | 3 | 距离/角度/属性(面积/体积/重心) |
| **Vision/UI** | 13 | 截图, 点击, 拖拽, 打字, 快捷键, 滚轮, 图像匹配 |
| **Smart UI** ★ | 8 | pywinauto: 菜单点击, 工具栏, 对话框交互, 规格树读取 |
| **Agent** ★ | 5 | 任务规划, 状态分析, 下一步建议, 设计验证, 宏生成 |

★ = 新增模块

### MCP Resources (只读上下文)
- `catia://status` — 连接状态
- `catia://document/info` — 文档信息
- `catia://document/tree` — 特征树
- `catia://document/parameters` — 参数列表
- `catia://help/tools` — 工具参考手册
- `catia://help/workflow/{name}` — 工作流指南

### MCP Prompts (Agent 提示词模板)
- `catia_agent_system` — Agent 系统提示词 (CLINE 风格思维链)
- `design_part` — 零件设计引导
- `modify_part` — 修改零件引导
- `create_assembly` — 装配设计引导
- `create_drawing` — 工程图引导
- `troubleshoot_catia` — 故障排除引导

## Agent 思维链路 (CLINE 风格)

```
用户: "创建一个带4个安装孔的轴承座"
                │
                ▼
    ┌─── plan_catia_task ───┐
    │ 分析任务 → 生成执行计划  │
    └───────┬───────────────┘
            │ 1. connect_catia
            │ 2. new_part
            │ 3. create_sketch + geometry
            │ 4. create_pad
            │ 5. create_hole + pattern
            │ 6. create_fillet
            ▼
    ┌─── analyze_current_state ───┐
    │ 检查当前状态，确认进度       │
    └───────┬─────────────────────┘
            ▼
    ┌─── validate_design ───┐
    │ 验证设计完整性         │
    └───────┬───────────────┘
            ▼
    ┌─── suggest_next_step ───┐
    │ 建议: save_document     │
    └─────────────────────────┘
```

## 快速开始

### 安装依赖

```bash
# 开发环境 (Linux/macOS — mock 模式)
pip install -e ".[dev]"

# Windows 完整安装 (含 CATIA 自动化)
pip install -e ".[dev,windows]"
```

### 运行 MCP 服务器

```bash
python main.py
# 或
catia-mcp
```

### 运行测试

```bash
pytest tests/ -v    # 122 tests
```

### 代码检查

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## 连接优先级

在 Windows 上运行时，连接优先级为：
1. **pycatia** (推荐) — 最完整的 CATIA Python API 封装
2. **win32com** (备用) — 直接 COM 自动化
3. **Mock** (开发/测试) — 非 Windows 或无 CATIA 时自动启用

## 配置

通过环境变量或 `.env` 文件配置：

```env
CATIA_MCP_LOG_LEVEL=INFO
CATIA_MCP_USE_PYCATIA=true
CATIA_MCP_VISION_ENABLED=true
CATIA_MCP_TRANSPORT=stdio
CATIA_MCP_MOCK_MODE=false
```

## 技术栈

- **Python 3.11+** — 核心语言
- **MCP SDK (FastMCP)** — Model Context Protocol
- **pycatia** — CATIA V5 COM 自动化
- **pywinauto** — Windows UI 智能自动化
- **pyautogui** — 屏幕捕获和基础 UI 自动化
- **Pydantic** — 数据验证和配置
- **pytest** — 测试框架
- **ruff** — 代码质量
