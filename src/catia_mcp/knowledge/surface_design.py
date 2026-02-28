"""CATIA Surface Design knowledge — GSD concepts, techniques, and workflows."""

KNOWLEDGE: dict = {
    "id": "surface_design",
    "title": "曲面设计 (Generative Shape Design)",
    "summary": "曲面建模技术：创建方法、操作技巧、实体化、A级曲面基础",
    "sections": {
        "concepts": {
            "title": "曲面设计核心概念",
            "content": (
                "CATIA GSD (Generative Shape Design) 用于创建和操作曲面。\n\n"
                "曲面 vs 实体：\n"
                "• 曲面是没有厚度的'皮'（0厚度几何）\n"
                "• 实体是有体积的封闭几何\n"
                "• 曲面需要加厚 (Thick Surface) 才能变成实体\n\n"
                "曲面存放位置：\n"
                "• Geometrical Set (几何体集) — 开放体，包含线框和曲面\n"
                "• Ordered Geometrical Set — 有序几何体集，特征有依赖顺序\n"
                "• HybridBody — 混合体\n\n"
                "曲面的连续性等级：\n"
                "• G0 (位置连续) — 两面共享边，但可能有棱角\n"
                "• G1 (切线连续) — 两面在边处切线方向一致，平滑过渡\n"
                "• G2 (曲率连续) — 两面在边处曲率一致，视觉完美\n"
                "• G3 (曲率变化率连续) — 最高级，用于 A 级曲面"
            ),
        },
        "creation_methods": {
            "title": "曲面创建方法",
            "content": {
                "Extrude (拉伸曲面)": "将曲线沿方向拉伸生成曲面。参数：曲线、方向、长度。",
                "Revolve (旋转曲面)": "将曲线绕轴线旋转生成曲面。参数：曲线、轴、角度。",
                "Sweep (扫掠曲面)": (
                    "沿引导线扫掠轮廓生成曲面。\n"
                    "类型：\n"
                    "  • Explicit — 明确的轮廓和引导线\n"
                    "  • Line — 直线型截面（等截面扫掠）\n"
                    "  • Circle — 圆形截面扫掠\n"
                    "  • Conic — 圆锥截面扫掠\n"
                    "扫掠是最灵活的曲面创建方法之一。"
                ),
                "Fill (填充曲面)": (
                    "用曲面填充由曲线围成的边界。\n支持指定切线连续性和通过点约束。"
                ),
                "Loft / Multi-sections Surface (多截面曲面)": (
                    "通过多个截面曲线生成曲面。\n"
                    "参数：多个截面、可选引导线、可选脊线\n"
                    "是创建复杂过渡形状的主要方法。"
                ),
                "Blend (混合曲面)": "在两条曲线之间创建光滑过渡曲面。支持 G0/G1/G2 连续。",
                "Offset (偏移曲面)": "创建等距偏移曲面。参数：源曲面、偏移距离。",
            },
        },
        "operations": {
            "title": "曲面操作",
            "content": {
                "Split (分割)": "用一个曲面或平面切割另一个曲面，保留一侧。",
                "Trim (修剪)": "相互修剪两个曲面，保留选定部分。",
                "Join (连接)": "将多个相邻曲面连接为一个曲面。",
                "Healing (修复)": "修复曲面之间的小间隙和不连续。",
                "Disassemble (分解)": "将连接的曲面分解为单独的面。",
                "Boundary (边界)": "提取曲面的边界曲线。",
                "Extract (提取)": "从实体中提取面或边。",
                "Near / Far (远近)": "在两个结果中选择保留哪一侧。",
            },
        },
        "wireframe": {
            "title": "线框元素",
            "content": {
                "Point (点)": "坐标点、曲线上的点、面上的点、中心点。",
                "Line (直线)": "两点直线、点和方向、角度线、切线、法线。",
                "Plane (平面)": "三点平面、偏移平面、角度平面、法线平面、曲面切平面。",
                "Circle (圆)": "中心半径圆、三点圆、中心轴圆。",
                "Spline (样条)": "通过控制点的光滑曲线。",
                "Helix (螺旋线)": "参数：起点、轴、螺距、高度。用于弹簧和螺纹。",
                "Intersection (交线)": "两个曲面/平面的交线。",
                "Projection (投影)": "将曲线投影到曲面上。",
                "Reflect Line (反射线)": "曲面上的光照反射线（用于质量检查）。",
            },
        },
        "surface_to_solid": {
            "title": "曲面转实体",
            "content": (
                "曲面设计完成后，需要将曲面转换为实体：\n\n"
                "方法：\n"
                "1. Thick Surface (加厚) — 给曲面添加厚度变成实体\n"
                "2. Close Surface (封闭曲面) — 将开放曲面封闭后实体化\n"
                "3. Sew Surface (缝合) — 将曲面缝合到现有实体上\n"
                "4. Split by Surface — 用曲面切割实体\n\n"
                "注意事项：\n"
                "• 加厚要求曲面不能自交叉\n"
                "• 封闭曲面要求曲面边界完全封闭\n"
                "• 缝合要求曲面边界与实体的面完全匹配"
            ),
        },
        "quality_check": {
            "title": "曲面质量检查",
            "content": {
                "Connect Checker": "检查两个曲面之间的连续性等级 (G0/G1/G2)。",
                "Curvature Analysis": "显示曲率分布（斑马线/刺猬图）。",
                "Draft Analysis": "分析拔模角度分布。",
                "Surfacic Curvature": "曲面高斯曲率和主曲率分析。",
                "Reflect Line": "反射线分析曲面光顺度。",
                "Deviation Analysis": "测量曲面与参考之间的偏差。",
            },
        },
    },
}
