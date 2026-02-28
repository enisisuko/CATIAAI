"""CATIA troubleshooting knowledge — common problems and solutions."""

KNOWLEDGE: dict = {
    "id": "troubleshooting",
    "title": "故障排除 (Troubleshooting)",
    "summary": "CATIA 常见问题诊断与解决：特征错误、性能优化、文件修复、许可证问题",
    "sections": {
        "feature_errors": {
            "title": "特征错误诊断",
            "content": {
                "Update Error (更新错误)": (
                    "症状：特征显示红色 ✗ 或黄色 ⚠\n"
                    "原因：依赖的几何体发生了变化\n"
                    "解决步骤：\n"
                    "1. 右键错误特征 → 'Edit' 查看定义\n"
                    "2. 检查引用的元素是否仍然有效\n"
                    "3. 重新选择丢失的引用 (Replace)\n"
                    "4. 或 Deactivate 该特征暂时跳过\n"
                    "5. 最后 Update All (Ctrl+U)"
                ),
                "Invalid Sketch (无效草图)": (
                    "原因：草图未封闭、自交叉或过约束\n"
                    "解决：双击草图进入编辑 → 检查绿色/红色状态 → 修复"
                ),
                "Impossible Operation (不可能的操作)": (
                    "原因：几何条件不满足（如孔深超过实体厚度）\n"
                    "解决：检查参数值是否合理"
                ),
                "Boolean Failure (布尔运算失败)": (
                    "原因：两个实体没有足够的重叠\n"
                    "解决：确保布尔体与目标体有交集"
                ),
                "Fillet/Chamfer Failure": (
                    "原因：圆角/倒角半径太大，导致自交叉\n"
                    "解决：减小半径，或先做大面的圆角"
                ),
                "Shell Failure": (
                    "原因：壁厚太大或几何太复杂\n"
                    "解决：减小壁厚，简化内部结构"
                ),
                "Pattern Failure": (
                    "原因：阵列实例落在实体外部\n"
                    "解决：检查方向和间距参数"
                ),
            },
        },
        "performance": {
            "title": "性能优化",
            "content": [
                "1. 减少特征数量 — 合并可以合并的操作",
                "2. 简化草图 — 不要在一个草图中放太多元素",
                "3. 使用 Power Copy 代替重复建模",
                "4. 关闭不需要的文档窗口",
                "5. 设置 LOD (Level of Detail) — Tools → Options → Display",
                "6. 大装配使用 CGR 格式 (轻量化表示)",
                "7. 用 Design Mode / Visualization Mode 切换",
                "8. 定期清理 Undo 历史 — 减少内存占用",
                "9. 禁用自动更新 — 手动 Ctrl+U 批量更新",
                "10. 使用 Product Cache 加速大装配加载",
            ],
        },
        "file_issues": {
            "title": "文件问题",
            "content": {
                "File Corrupted": (
                    "解决方案：\n"
                    "1. 尝试从备份恢复 (.CATPartbak)\n"
                    "2. 用 CATIA 的 Desk → Repair 工具\n"
                    "3. 导出为 STEP 再重新导入\n"
                    "4. 使用 CATDUA (CATIA Data Utility for Administration)"
                ),
                "Missing Links": (
                    "装配中零件链接断开。\n"
                    "解决：Edit → Links → 选择 Broken → 指向正确文件"
                ),
                "Cannot Save": (
                    "原因：文件被锁、磁盘满、权限不足\n"
                    "解决：另存为新文件名 (Save As)"
                ),
                "Version Compatibility": (
                    "高版本文件无法在低版本打开。\n"
                    "解决：用高版本导出 STEP/IGES/V4 格式"
                ),
            },
        },
        "display_issues": {
            "title": "显示问题",
            "content": {
                "Model Not Visible": "按 Ctrl+Shift+F (Fit All In) 居中显示全部",
                "Strange Colors": "View → Render Style → 切换渲染模式",
                "Slow Rotation": "降低显示精度：Tools → Options → Display → Performance",
                "Missing Faces": "可能是曲面错误，检查 Join/Heal 操作",
                "Z-Fighting": "两个面重叠闪烁，偏移其中一个微小距离",
            },
        },
        "automation_errors": {
            "title": "自动化常见错误",
            "content": {
                "CATIA.Application not found": (
                    "确保 CATIA 正在运行。\n"
                    "如果使用 GetObject 失败，改用 CreateObject。\n"
                    "检查 CATIA 是否以管理员权限运行。"
                ),
                "Index out of range": (
                    "COM 集合索引从 1 开始，不是 0。\n"
                    "检查 .Count 属性确认集合大小。"
                ),
                "Reference is Nothing": (
                    "创建引用失败。\n"
                    "确保原始对象存在且可访问。\n"
                    "某些对象需要先 Update 才能创建引用。"
                ),
                "Sketch edit mode conflict": (
                    "不能同时编辑两个草图。\n"
                    "确保 CloseEdition() 被调用。"
                ),
                "Part.Update fails": (
                    "模型中有错误的特征。\n"
                    "逐个检查特征，或用 Deactivate 跳过错误特征。"
                ),
            },
        },
    },
}
