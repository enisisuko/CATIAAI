"""CATIA fundamentals — workbenches, object model, coordinate systems, navigation."""

KNOWLEDGE: dict = {
    "id": "fundamentals",
    "title": "CATIA 基础知识",
    "summary": "CATIA 的核心概念、工作台、对象模型、坐标系和基本导航",
    "sections": {
        "overview": {
            "title": "CATIA 概述",
            "content": (
                "CATIA (Computer Aided Three-dimensional Interactive Application) 是达索系统 "
                "(Dassault Systèmes) 开发的 CAD/CAM/CAE 商业软件。它被广泛用于航空航天、"
                "汽车、船舶和工业设备设计。\n\n"
                "CATIA 的核心设计哲学：\n"
                "1. 基于特征 (Feature-Based): 每个设计操作是一个'特征'，按顺序记录在规格树中\n"
                "2. 参数化 (Parametric): 所有尺寸可作为参数修改，自动更新整个模型\n"
                "3. 关联性 (Associative): 零件、装配和图纸之间保持关联，一处修改全局更新\n"
                "4. 基于历史 (History-Based): 特征树记录完整建模过程，可回溯修改任何步骤"
            ),
        },
        "workbenches": {
            "title": "工作台 (Workbenches)",
            "content": {
                "Part Design": "零件设计 — 基于草图创建实体特征 (拉伸、旋转、倒角等)",
                "Sketcher": "草图绘制 — 2D 轮廓绘制和约束",
                "Assembly Design": "装配设计 — 组装零件并添加约束",
                "Drafting": "工程图 — 从 3D 模型生成 2D 工程图",
                "Generative Shape Design (GSD)": "创成式曲面设计 — 创建和操作曲面",
                "Wireframe & Surface": "线框和曲面 — 基本线框和曲面操作",
                "Sheet Metal Design": "钣金设计 — 钣金件的展开和折弯",
                "FreeStyle": "自由曲面 — 高级曲面造型 (A级曲面)",
                "DMU Kinematics": "数字样机运动学 — 运动仿真",
                "Machining": "加工 — 数控加工编程",
                "Structure Design": "结构设计 — 钢结构和框架设计",
                "Functional Molded Part": "功能模塑件 — 注塑件设计",
            },
        },
        "object_model": {
            "title": "CATIA 对象模型 (Object Model)",
            "content": (
                "CATIA 的 COM 自动化基于层级对象模型：\n\n"
                "Application (CATIA应用程序)\n"
                "├── Documents (文档集合)\n"
                "│   ├── PartDocument (.CATPart)\n"
                "│   │   ├── Part (零件对象)\n"
                "│   │   │   ├── Bodies (实体集合)\n"
                "│   │   │   │   └── Body (实体)\n"
                "│   │   │   │       ├── Sketches (草图集合)\n"
                "│   │   │   │       └── Shapes (形状/特征集合)\n"
                "│   │   │   ├── HybridBodies (几何体集合/开放体)\n"
                "│   │   │   ├── Parameters (参数集合)\n"
                "│   │   │   ├── Relations (关系/公式集合)\n"
                "│   │   │   └── OriginElements (原点元素：XY/YZ/XZ平面)\n"
                "│   │   └── Product (产品属性)\n"
                "│   ├── ProductDocument (.CATProduct)\n"
                "│   │   └── Product\n"
                "│   │       ├── Products (子产品/组件集合)\n"
                "│   │       └── Constraints (装配约束)\n"
                "│   └── DrawingDocument (.CATDrawing)\n"
                "│       └── DrawingRoot\n"
                "│           └── Sheets (图纸集合)\n"
                "│               └── Views (视图集合)\n"
                "├── ActiveDocument (当前活动文档)\n"
                "├── SystemService (系统服务)\n"
                "└── ActiveWindow (活动窗口/查看器)"
            ),
        },
        "coordinate_system": {
            "title": "坐标系与参考平面",
            "content": (
                "CATIA 使用右手笛卡尔坐标系：\n\n"
                "三个基准平面 (Reference Planes)：\n"
                "• XY 平面 — 水平平面 (俯视方向)\n"
                "• YZ 平面 — 正面平面 (前视方向)\n"
                "• XZ 平面 — 侧面平面 (侧视方向)\n\n"
                "三个轴：\n"
                "• X 轴 — 红色，水平向右\n"
                "• Y 轴 — 绿色，水平向前\n"
                "• Z 轴 — 蓝色，垂直向上\n\n"
                "原点 (Origin)：三个平面的交点 (0, 0, 0)\n\n"
                "注意：草图中只有 H (水平) 和 V (垂直) 两个方向，"
                "具体对应哪个全局轴取决于草图所在的平面。"
            ),
        },
        "document_types": {
            "title": "文档类型",
            "content": {
                ".CATPart": "零件文档 — 包含单个 3D 零件的几何数据、特征树和参数",
                ".CATProduct": "装配文档 — 包含多个零件的装配关系和约束",
                ".CATDrawing": "图纸文档 — 包含从 3D 模型生成的 2D 工程图",
                ".CATProcess": "工艺文档 — 包含加工工艺信息",
                ".CATAnalysis": "分析文档 — 包含有限元分析数据",
                ".CATMaterial": "材料库文档 — 包含材料属性定义",
                ".catalog": "目录文件 — 标准件库和目录",
                ".STEP/.STP": "通用 3D 交换格式 (ISO 10303)",
                ".IGES/.IGS": "早期通用 3D 交换格式",
                ".STL": "网格格式 (用于 3D 打印)",
            },
        },
        "specification_tree": {
            "title": "规格树 (Specification Tree)",
            "content": (
                "规格树是 CATIA 的核心 UI 元素，它以树形结构展示模型的完整建模历史。\n\n"
                "规格树的关键概念：\n"
                "1. 顺序依赖 — 特征按创建顺序排列，后面的特征可能依赖前面的\n"
                "2. 父子关系 — 草图是特征的父对象（如 Sketch.1 是 Pad.1 的父对象）\n"
                "3. 可编辑 — 双击任何特征可以回到该特征编辑\n"
                "4. 可重排序 — 特征可以拖动重新排序（但需注意依赖关系）\n"
                "5. 可隐藏/显示 — 右键可控制特征的可见性\n"
                "6. 状态指示器：\n"
                "   • 绿色对号 ✓ — 特征正常\n"
                "   • 黄色感叹号 ⚠ — 特征有警告\n"
                "   • 红色叉号 ✗ — 特征有错误（需修复）\n"
                "   • 灰色 — 特征被停用 (Deactivated)\n\n"
                "典型零件的规格树结构：\n"
                "Part1\n"
                "├── xy plane / yz plane / zx plane\n"
                "├── PartBody\n"
                "│   ├── Sketch.1\n"
                "│   ├── Pad.1 (基于 Sketch.1)\n"
                "│   ├── Sketch.2\n"
                "│   ├── Pocket.1 (基于 Sketch.2)\n"
                "│   ├── EdgeFillet.1\n"
                "│   └── Hole.1\n"
                "├── Geometrical Set.1\n"
                "│   ├── Point.1\n"
                "│   └── Line.1\n"
                "└── Parameters\n"
                "    ├── Length = 100mm\n"
                "    └── Width = 50mm"
            ),
        },
        "units": {
            "title": "单位系统",
            "content": (
                "CATIA 默认使用国际单位制 (SI)：\n\n"
                "• 长度: mm (毫米)\n"
                "• 角度: deg (度)\n"
                "• 质量: kg (千克)\n"
                "• 时间: s (秒)\n"
                "• 温度: °C (摄氏度)\n\n"
                "可在 Tools → Options → General → Parameters and Measure 中修改单位。\n\n"
                "在自动化中，所有长度参数默认以 mm 为单位传递，"
                "角度以 deg 为单位。注意：CATIA 内部计算可能使用不同单位，"
                "但 COM API 返回的值通常已转换为用户设定的单位。"
            ),
        },
        "navigation": {
            "title": "3D 视图导航",
            "content": {
                "旋转": "按住鼠标中键拖动",
                "平移": "按住鼠标中键 + 右键拖动 (或 Ctrl+中键)",
                "缩放": "按住鼠标中键 + 右键 → 上下拖动 (或滚轮)",
                "适合窗口": "Ctrl+Shift+F 或 View → Fit All In",
                "前视图": "Ctrl+KP7 或点击罗盘的 Front",
                "俯视图": "Ctrl+KP9",
                "侧视图": "Ctrl+KP3",
                "等轴测": "Ctrl+KP5",
                "选择": "左键点击对象",
                "多选": "Ctrl + 左键点击",
                "框选": "从左到右画框 = 完全包含；从右到左画框 = 交叉选择",
            },
        },
    },
}
