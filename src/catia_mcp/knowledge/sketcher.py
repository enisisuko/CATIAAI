"""CATIA Sketcher knowledge — 2D sketching, constraints, profiles, best practices."""

KNOWLEDGE: dict = {
    "id": "sketcher",
    "title": "草图绘制 (Sketcher)",
    "summary": "2D 草图绘制技术：几何元素、约束系统、全约束草图、轮廓创建技巧",
    "sections": {
        "concepts": {
            "title": "草图核心概念",
            "content": (
                "草图 (Sketch) 是 CATIA 中所有基于轮廓的 3D 特征的基础。\n\n"
                "关键概念：\n"
                "1. 草图是 2D 的 — 所有几何元素都在一个平面上\n"
                "2. 草图需要支撑面 — 可以是参考平面或已有的面\n"
                "3. 草图包含几何元素和约束\n"
                "4. 草图应当'完全约束' (Fully Constrained) — 绿色显示\n"
                "5. 草图的 H 轴 (水平) 和 V 轴 (垂直) 取决于支撑面的方向\n"
                "6. 草图中的原点与 3D 空间中的原点投影对应\n\n"
                "草图颜色含义：\n"
                "• 白色 — 未约束 (Under-Constrained)\n"
                "• 绿色 — 完全约束 (Fully Constrained) ✓\n"
                "• 紫色/红色 — 过约束 (Over-Constrained) ✗\n"
                "• 棕色 — 无法求解 (Inconsistent)"
            ),
        },
        "geometry_elements": {
            "title": "几何元素",
            "content": {
                "点 (Point)": "基本元素，用于定位或作为参考。可在交点、端点处创建。",
                "线段 (Line)": "两点之间的直线段。参数：起点(x1,y1)，终点(x2,y2)。",
                "无限线 (Infinite Line)": "用于辅助的无限延伸线（构造几何）。",
                "圆 (Circle)": "完整圆。参数：圆心(cx,cy)，半径(r)。",
                "弧 (Arc)": (
                    "圆弧。参数：圆心，半径，起始角，结束角。"
                    "有三点弧和圆心弧两种创建方式。"
                ),
                "椭圆 (Ellipse)": "椭圆或椭圆弧。参数：中心，长轴，短轴。",
                "矩形 (Rectangle)": "实际是4条线段+约束。参数：角点(x,y)，宽，高。",
                "样条 (Spline)": "通过控制点的光滑曲线。支持 B-Spline。参数：控制点列表。",
                "圆锥曲线 (Conic)": "抛物线、双曲线等。",
                "轮廓 (Profile)": "连续绘制的线段和弧的组合，自动在端点处连接。",
                "轴线 (Axis)": "用于旋转特征 (Shaft/Groove) 的旋转轴。",
                "构造几何 (Construction)": (
                    "辅助线，不参与轮廓生成。"
                    "切换：右键 → Construction/Standard。"
                ),
            },
        },
        "constraints": {
            "title": "约束系统",
            "content": (
                "约束分为几何约束和尺寸约束两大类。\n\n"
                "【几何约束 (Geometric Constraints)】\n"
                "• 固定 (Fix) — 将元素锁定在当前位置\n"
                "• 重合 (Coincidence) — 两点重合、点在线上、点在圆上\n"
                "• 相切 (Tangent) — 两曲线在交点处相切\n"
                "• 垂直 (Perpendicular) — 两线段互相垂直\n"
                "• 平行 (Parallel) — 两线段平行\n"
                "• 水平 (Horizontal) — 线段水平\n"
                "• 垂直方向 (Vertical) — 线段垂直\n"
                "• 同心 (Concentric) — 两圆/弧同心\n"
                "• 等长/等半径 (Equal) — 两线段等长或两圆等半径\n"
                "• 对称 (Symmetry) — 相对于轴线对称\n"
                "• 中点 (Midpoint) — 点在线段中点上\n\n"
                "【尺寸约束 (Dimensional Constraints)】\n"
                "• 距离 (Distance) — 两元素间的距离\n"
                "• 长度 (Length) — 线段长度\n"
                "• 角度 (Angle) — 两线段之间的角度\n"
                "• 半径 (Radius) — 圆或弧的半径\n"
                "• 直径 (Diameter) — 圆的直径\n"
                "• 半径/半径约束 — 椭圆的半轴\n\n"
                "约束自由度 (DOF):\n"
                "• 未约束的点有 2 个 DOF (x, y)\n"
                "• 未约束的线段有 4 个 DOF (两个端点)\n"
                "• 未约束的圆有 3 个 DOF (圆心x, 圆心y, 半径)\n"
                "• 目标是让所有 DOF = 0 (完全约束)"
            ),
        },
        "operations": {
            "title": "草图操作",
            "content": {
                "镜像 (Mirror)": "选择元素和轴线，创建镜像副本。",
                "偏移 (Offset)": "创建等距偏移曲线。",
                "修剪 (Trim)": "在交点处修剪多余部分。Quick Trim 是最常用的。",
                "延伸 (Extend)": "将线段延伸到另一个元素。",
                "倒圆角 (Fillet)": "在两条线交点处创建圆弧过渡。",
                "倒角 (Chamfer)": "在两条线交点处创建斜切。",
                "投影 (Project)": "将 3D 边投影到草图平面上。",
                "相交 (Intersect)": "计算 3D 元素与草图平面的交线。",
            },
        },
        "best_practices": {
            "title": "草图最佳实践",
            "content": [
                "1. 始终追求完全约束 (绿色) — 未约束的草图在修改时会产生不可预测的变化",
                "2. 先画大致形状，后添加精确约束 — 不要一开始就输入精确坐标",
                "3. 从原点开始 — 将草图的关键特征锚定到原点，方便后续操作",
                "4. 使用构造几何 — 辅助线帮助定位，但不会被特征使用",
                "5. 保持草图简单 — 复杂轮廓拆分为多个简单草图，用多个特征组合",
                "6. 利用对称 — 对称的形状只画一半，用镜像约束完成",
                "7. 避免过约束 — 出现紫色/红色立即删除多余约束",
                "8. 使用标准矩形工具 — 比手动画 4 条线更可靠（自动添加约束）",
                "9. 注意草图方向 — 创建特征前确认拉伸方向是否正确",
                "10. 封闭轮廓 — Pad/Pocket 等特征需要封闭轮廓",
                "11. 避免自交叉 — 轮廓不能与自身交叉",
                "12. 参数化命名 — 给关键尺寸命名 (如 'Length', 'Width') 方便后续引用",
            ],
        },
        "common_errors": {
            "title": "草图常见错误",
            "content": {
                "Open Profile": "轮廓未封闭。解决：检查端点是否重合，用修剪或延伸连接。",
                "Self-intersecting": "轮廓自交叉。解决：删除交叉部分重新绘制。",
                "Over-constrained": "约束过多。解决：删除紫色/红色的约束，一次一个。",
                "Inconsistent": "约束矛盾。解决：检查是否有冲突的尺寸约束。",
                "Zero-length element": "元素长度为0。解决：删除该元素。",
                "Sketch not planar": "草图不在平面上。通常是支撑面选择问题。",
            },
        },
        "automation_tips": {
            "title": "草图自动化技巧",
            "content": (
                "通过 API 自动化草图时的关键要点：\n\n"
                "1. 创建草图的步骤：\n"
                "   a. 选择支撑平面 (XY/YZ/XZ 或面)\n"
                "   b. 调用 Sketches.Add(reference) 创建\n"
                "   c. 打开编辑模式 OpenEdition()\n"
                "   d. 通过 Factory2D 创建几何元素\n"
                "   e. 关闭编辑 CloseEdition()\n\n"
                "2. Factory2D 创建方法：\n"
                "   • CreateLine(x1, y1, x2, y2)\n"
                "   • CreateClosedCircle(cx, cy, radius)\n"
                "   • CreateCircle(cx, cy, radius, start, end)\n"
                "   • CreatePoint(x, y)\n"
                "   • CreateSpline(points_array)\n\n"
                "3. 约束通过 Constraints 集合添加：\n"
                "   • AddMonoEltCst(type, element)\n"
                "   • AddBiEltCst(type, element1, element2)\n\n"
                "4. 坐标单位始终是 mm\n"
                "5. 角度始终是 弧度 (radians) 在 API 级别"
            ),
        },
    },
}
