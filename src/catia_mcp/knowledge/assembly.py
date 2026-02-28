"""CATIA Assembly Design knowledge — constraints, methods, BOM management."""

KNOWLEDGE: dict = {
    "id": "assembly",
    "title": "装配设计 (Assembly Design)",
    "summary": "装配方法论：约束类型、自上而下/自下而上设计、BOM 管理、干涉检查",
    "sections": {
        "concepts": {
            "title": "装配核心概念",
            "content": (
                "CATIA 装配设计使用 .CATProduct 文档，包含：\n"
                "• 组件 (Component) — 指向 .CATPart 或子 .CATProduct 的引用\n"
                "• 约束 (Constraint) — 定义组件之间的位置关系\n"
                "• 产品结构 (Product Structure) — 层级化的零部件树\n\n"
                "装配的工作原理：\n"
                "1. 装配文件不复制零件数据，只保存引用和位置矩阵\n"
                "2. 修改零件文件后，装配自动更新\n"
                "3. 同一零件可以被多次引用 (实例化)\n"
                "4. 子装配可以嵌套任意层级"
            ),
        },
        "design_approaches": {
            "title": "装配设计方法",
            "content": {
                "Bottom-Up (自下而上)": (
                    "先独立设计每个零件，然后装配在一起。\n"
                    "优点：零件可独立修改和复用\n"
                    "缺点：装配时可能发现干涉\n"
                    "适用：标准件、成熟设计"
                ),
                "Top-Down (自上而下)": (
                    "在装配环境中设计零件，引用其他零件的几何。\n"
                    "优点：确保零件完美配合\n"
                    "缺点：零件间依赖性高，修改需谨慎\n"
                    "适用：全新设计、紧密配合的零件组"
                ),
                "Mixed (混合方法)": (
                    "实际工程中最常用。基础结构自上而下，标准件和独立零件自下而上。"
                ),
            },
        },
        "constraints": {
            "title": "装配约束详解",
            "content": {
                "Coincidence (重合)": (
                    "最常用的约束。使几何元素重合/对齐。\n"
                    "• 面-面：两平面重合 (共面)\n"
                    "• 轴-轴：两轴共线 (同轴)\n"
                    "• 点-点：两点重合\n"
                    "• 面-轴：面的法线与轴共线\n"
                    "移除自由度：3个 (平面重合) 或 4个 (轴重合)"
                ),
                "Contact (接触)": (
                    "两平面面对面接触 (法线方向相反)。\n"
                    "与 Coincidence 的区别：Contact 确保面朝向相对。\n"
                    "移除自由度：1个 (法线方向上的移动)"
                ),
                "Offset (偏移)": (
                    "两平面保持固定距离。\n"
                    "参数：偏移距离 (mm)\n"
                    "偏移=0 等效于 Coincidence\n"
                    "移除自由度：1个"
                ),
                "Angle (角度)": (
                    "两平面/轴之间保持固定角度。\n参数：角度 (度)\n移除自由度：1个 (旋转)"
                ),
                "Fix (固定)": (
                    "将组件固定在当前位置，移除所有自由度。\n"
                    "通常用于第一个/基础组件。\n"
                    "移除自由度：6个 (全部)"
                ),
                "Fix Together (固定在一起)": ("两个组件固定相对位置。\n不需要几何元素选择。"),
            },
        },
        "degrees_of_freedom": {
            "title": "自由度 (Degrees of Freedom)",
            "content": (
                "3D 空间中，一个未约束的刚体有 6 个自由度：\n"
                "• 3 个平移 (X, Y, Z)\n"
                "• 3 个旋转 (绕X, 绕Y, 绕Z)\n\n"
                "装配约束的目标是将所有组件的自由度降为 0。\n\n"
                "常见约束组合（以轴+孔配合为例）：\n"
                "1. Coincidence (轴-轴) → 移除 4 DOF → 剩余：沿轴平移 + 绕轴旋转\n"
                "2. Contact (面-面) → 移除 1 DOF → 剩余：绕轴旋转\n"
                "3. 如果旋转无所谓（圆形对称），可以不再约束\n\n"
                "检查方法：右键组件 → 'Degrees of Freedom'，绿色=完全约束"
            ),
        },
        "manipulation": {
            "title": "组件操作",
            "content": {
                "Move (移动)": "手动平移/旋转组件到大致位置",
                "Snap (吸附)": "快速对齐两个几何元素",
                "Explode (爆炸图)": "将装配分解展示，便于查看内部结构",
                "Replace (替换)": "用另一个零件替换当前组件",
                "Reuse Pattern": "重用零件中的阵列到装配层级",
                "Flexible (柔性)": "允许子装配中的组件在上层装配中移动",
            },
        },
        "bom": {
            "title": "BOM (物料清单) 管理",
            "content": (
                "装配的 BOM 从产品结构自动生成：\n\n"
                "BOM 信息包括：\n"
                "• 零件号 (Part Number)\n"
                "• 名称 (Name)\n"
                "• 描述 (Description)\n"
                "• 数量 (Quantity)\n"
                "• 材料 (Material)\n"
                "• 质量 (Mass)\n\n"
                "设置零件属性：\n"
                "  在 Product 节点上右键 → Properties → Product 标签页\n"
                "  或通过 COM: product.PartNumber = 'xxx'\n\n"
                "导出 BOM：File → Save As → 选择 .xls 或 .csv 格式"
            ),
        },
        "interference": {
            "title": "干涉检查",
            "content": (
                "检查装配中零件是否有碰撞/穿透：\n\n"
                "Analyze → Clash Detection:\n"
                "• Clash (碰撞) — 两个零件实体重叠\n"
                "• Contact (接触) — 两个零件表面接触\n"
                "• Clearance (间隙) — 两个零件之间的最小距离\n\n"
                "自动化干涉检查通过 DMU Space Analysis 工作台完成。"
            ),
        },
    },
}
