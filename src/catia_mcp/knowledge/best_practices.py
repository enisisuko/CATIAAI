"""CATIA best practices — design patterns, naming conventions, industry standards."""

KNOWLEDGE: dict = {
    "id": "best_practices",
    "title": "最佳实践 (Best Practices)",
    "summary": "设计模式、命名规范、参数化策略、行业标准、团队协作规范",
    "sections": {
        "naming_conventions": {
            "title": "命名规范",
            "content": (
                "良好的命名是高效协作的基础：\n\n"
                "【零件命名】\n"
                "• 格式：项目号-类型-序号_描述\n"
                "• 示例：PRJ001-PRT-001_BearingHousing\n\n"
                "【特征命名】\n"
                "• 有意义的名称替代默认名：\n"
                "  ✗ Pad.1, Pocket.2, Sketch.3\n"
                "  ✓ BasePlate, MountingSlot, BoltHoleSketch\n"
                "• 在规格树中右键 → Properties → 修改名称\n\n"
                "【参数命名】\n"
                "• 使用描述性名称：Length, Width, BoltDiameter\n"
                "• 避免：a, b, x1, param1\n"
                "• 格式建议：PascalCase 或 snake_case\n\n"
                "【装配命名】\n"
                "• 按功能分组：Chassis_Assembly, Gearbox_Assembly\n"
                "• 实例编号：Bolt_M8x30_01, Bolt_M8x30_02"
            ),
        },
        "parametric_design": {
            "title": "参数化设计策略",
            "content": (
                "参数化设计让模型可以通过修改参数快速变更：\n\n"
                "【参数层级】\n"
                "1. 主参数 (Master Parameters) — 用户直接控制\n"
                "   例：总长 TotalLength = 200mm\n"
                "2. 派生参数 (Derived) — 通过公式自动计算\n"
                "   例：壁厚 WallThick = TotalLength * 0.05\n"
                "3. 特征参数 — 由主参数驱动\n\n"
                "【公式 (Formulas)】\n"
                "通过 Tools → Formula 或 f(x) 按钮创建：\n"
                "  WallThick = TotalLength * 0.05\n"
                "  HoleSpacing = (TotalLength - 2 * EdgeDist) / (NumHoles - 1)\n"
                "  Radius = if(Diameter > 100mm, 5mm, 3mm)\n\n"
                "【设计表 (Design Table)】\n"
                "用 Excel 表格驱动多组参数配置：\n"
                "  Tools → Design Table → Create from Excel\n"
                "  每行一组配置，每列一个参数\n"
                "  实现一个模型生成多个变体。\n\n"
                "【Power Copy / User Feature】\n"
                "将参数化的特征组封装为可复用的模板：\n"
                "  Insert → Instantiate From Document → 选择模板零件"
            ),
        },
        "modeling_guidelines": {
            "title": "建模准则",
            "content": [
                "1. 先规划再建模 — 想清楚基础形状和特征顺序",
                "2. 草图完全约束 — 始终保持草图绿色",
                "3. 利用对称性 — 对称零件建一半后镜像",
                "4. 最少特征原则 — 能一步完成的不分两步",
                "5. 保持特征独立 — 减少特征间的交叉引用",
                "6. 使用参考几何 — 创建辅助平面和轴线便于后续操作",
                "7. 圆角/倒角最后做 — 它们最容易因修改而出错",
                "8. 给特征有意义的名称 — 方便他人理解你的设计意图",
                "9. 定期保存和备份 — 养成 Ctrl+S 习惯",
                "10. 建模历史可读 — 让另一个工程师能看懂你的规格树",
                "11. 避免引用 Body 以外的几何 — 减少跨 Body 依赖",
                "12. 使用公布元素 (Published Elements) — 稳定装配引用",
            ],
        },
        "assembly_guidelines": {
            "title": "装配设计准则",
            "content": [
                "1. 固定基础零件 — 第一个插入的零件应 Fix",
                "2. 按功能分子装配 — 大装配分层级组织",
                "3. 使用 Published Elements — 避免直接引用几何面",
                "4. 检查自由度 — 每个零件的 DOF 应该为 0 或合理值",
                "5. 使用 Flexible 子装配 — 需要时允许内部移动",
                "6. 做干涉检查 — 装配完成后跑 Clash Detection",
                "7. 管理替换件 — 用 Replace 更新零件版本",
                "8. BOM 信息完整 — 每个零件设好 Part Number 和属性",
            ],
        },
        "drawing_guidelines": {
            "title": "工程图准则",
            "content": [
                "1. 选择合适的投影方向 — 主视图应最能体现零件形状",
                "2. 用足够但不多余的视图 — 完全描述形状即可",
                "3. 尺寸标注完整 — 制造所需的每个尺寸都应标注",
                "4. 避免重复标注 — 同一尺寸不出现两次",
                "5. 从基准标注 — 保证尺寸链的合理性",
                "6. 标注公差 — 关键配合面给出公差",
                "7. 加注粗糙度 — 标明表面加工要求",
                "8. 填写标题栏 — 材料、数量、比例等信息完整",
            ],
        },
        "data_management": {
            "title": "数据管理",
            "content": (
                "【文件组织】\n"
                "推荐的项目文件夹结构：\n"
                "  Project/\n"
                "  ├── Parts/          — 零件文件\n"
                "  ├── Assemblies/     — 装配文件\n"
                "  ├── Drawings/       — 图纸文件\n"
                "  ├── Templates/      — 模板文件\n"
                "  ├── Standards/      — 标准件库\n"
                "  ├── Import_Export/  — 导入导出文件\n"
                "  └── Archives/       — 归档\n\n"
                "【版本管理】\n"
                "• 使用 PLM 系统 (ENOVIA, Teamcenter) 管理正式版本\n"
                "• 小团队可用文件命名管理：PartName_v1, PartName_v2\n"
                "• 始终保留上一版本的备份\n\n"
                "【文件传输】\n"
                "• 使用 'Send To' 功能打包所有关联文件\n"
                "• 跨平台交换用 STEP AP214 格式\n"
                "• 3D 打印用 STL 或 3MF 格式"
            ),
        },
        "industry_tips": {
            "title": "行业特定技巧",
            "content": {
                "航空航天": (
                    "• 大量使用曲面设计 (GSD/FreeStyle)\n"
                    "• 严格的公差和 GD&T 标注\n"
                    "• 复合材料铺层设计 (Composites Design)\n"
                    "• 与 FEA 分析紧密集成"
                ),
                "汽车": (
                    "• A 级曲面质量要求 (G2/G3 连续)\n"
                    "• 大型装配管理 (数万零件)\n"
                    "• 钣金设计和模具设计\n"
                    "• 人机工程学分析"
                ),
                "工业设备": (
                    "• 参数化设计族（系列零件）\n"
                    "• 标准件库的大量使用\n"
                    "• 焊接结构设计\n"
                    "• 液压/气动管路布局"
                ),
            },
        },
    },
}
