# CATIA MCP Server

通过 MCP (Model Context Protocol) 将云端大模型连接到 CATIA V5/V6，实现 AI 驱动的 CAD 自动化。

## 架构

```
Cloud LLM (Claude/GPT/etc.)
        │
        │  MCP Protocol (stdio/SSE)
        ▼
┌──────────────────────────────┐
│   CATIA MCP Server (本软件)   │
│                              │
│  ┌────────────┐ ┌──────────┐ │
│  │ CATIA COM  │ │ Vision/  │ │
│  │ Automation │ │ Screen   │ │
│  │ (pywin32)  │ │ (pyauto) │ │
│  └─────┬──────┘ └────┬─────┘ │
└────────┼─────────────┼───────┘
         │             │
         ▼             ▼
    CATIA V5/V6    Screen/UI
```

## 功能模块 (60+ MCP Tools)

| 模块 | 工具数 | 功能 |
|------|--------|------|
| **System** | 13 | 连接管理, 文档操作, 特征树, 参数, 宏, 撤销/重做 |
| **Sketcher** | 10 | 线/圆/矩形/弧/样条/点, 约束, 倒角, 裁剪 |
| **Part Design** | 12 | 拉伸/凹槽/旋转/倒角/圆角/壳体/孔/阵列/镜像 |
| **Assembly** | 8 | 插入组件, 约束 (重合/接触/偏移/角度/固定), BOM |
| **Drawing** | 7 | 视图 (主/投影/剖/局部/等轴测), 标注, 注释 |
| **Surface** | 10 | 拉伸/旋转/扫掠/填充/放样/偏移/混合/修剪/分割/连接 |
| **Measurement** | 3 | 距离/角度/属性(面积/体积/重心) |
| **Vision/UI** | 12 | 截图, 点击, 拖拽, 打字, 快捷键, 滚轮, 图像匹配 |

## 快速开始

### 安装依赖

```bash
pip install -e ".[dev]"
```

### 运行 MCP 服务器

```bash
# stdio 模式 (用于 LLM 客户端集成)
python main.py

# 或使用入口点
catia-mcp
```

### 运行测试

```bash
pytest tests/ -v
```

### 代码检查

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## 技术栈

- **Python 3.11+** - 核心语言
- **MCP SDK (FastMCP)** - Model Context Protocol 服务器
- **pywin32** - Windows COM 自动化 (CATIA API)
- **pyautogui** - 屏幕捕获和 UI 自动化
- **Pydantic** - 数据验证
- **pytest** - 测试框架
- **ruff** - 代码质量检查

## 工作模式

- **Windows + CATIA**: 通过 COM 自动化直接操作 CATIA
- **Mock 模式**: 无 CATIA 时自动切换到模拟模式，用于开发和测试

## 打包为 EXE

```bash
pip install pyinstaller
pyinstaller --onefile main.py --name catia-mcp
```
