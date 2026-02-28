"""CATIA scripting knowledge — VBA, CATScript, COM automation guide."""

KNOWLEDGE: dict = {
    "id": "scripting",
    "title": "CATIA 脚本与自动化",
    "summary": "VBA/CATScript/Python 自动化编程：COM 对象模型、常用 API、代码模板",
    "sections": {
        "languages": {
            "title": "脚本语言选择",
            "content": {
                "CATScript": (
                    "CATIA 内置脚本语言，基于 VBScript 语法。\n"
                    "运行方式：Tools → Macro → Macros → Run\n"
                    "文件扩展名：.CATScript\n"
                    "特点：无需安装额外软件，直接在 CATIA 中运行。"
                ),
                "VBA (Visual Basic for Applications)": (
                    "通过 CATIA 内置的 VBA 编辑器。\n"
                    "运行方式：Tools → Macro → Visual Basic Editor\n"
                    "特点：支持调试、窗体 (UserForm)、对象浏览器。"
                ),
                "VBScript": (
                    "Windows 脚本宿主运行的 VB 脚本。\n"
                    "外部运行：wscript.exe / cscript.exe\n"
                    "文件扩展名：.vbs\n"
                    "特点：可从外部驱动 CATIA (Out-of-process)。"
                ),
                "Python (pycatia)": (
                    "通过 pycatia 库访问 CATIA COM API。\n"
                    "安装：pip install pycatia\n"
                    "特点：现代语言特性，丰富的第三方库生态。\n"
                    "推荐用于复杂自动化任务。"
                ),
            },
        },
        "com_basics": {
            "title": "COM 自动化基础",
            "content": (
                "CATIA 通过 COM (Component Object Model) 暴露自动化接口。\n\n"
                "【连接 CATIA】\n"
                "VBScript:\n"
                "  Set CATIA = GetObject(, \"CATIA.Application\")\n"
                "  ' 或创建新实例\n"
                "  Set CATIA = CreateObject(\"CATIA.Application\")\n\n"
                "Python (pycatia):\n"
                "  from pycatia import catia\n"
                "  caa = catia()\n\n"
                "Python (win32com):\n"
                "  import win32com.client\n"
                "  catia = win32com.client.Dispatch('CATIA.Application')\n\n"
                "【基本操作模式】\n"
                "1. 获取 Application 对象\n"
                "2. 通过 Application 访问 Documents\n"
                "3. 打开/创建文档\n"
                "4. 通过文档访问 Part/Product/DrawingRoot\n"
                "5. 操作对象属性和方法\n"
                "6. 调用 Part.Update() 刷新模型"
            ),
        },
        "common_patterns": {
            "title": "常用代码模板",
            "content": {
                "创建新零件": (
                    "Dim documents As Documents\n"
                    "Set documents = CATIA.Documents\n"
                    "Dim partDoc As PartDocument\n"
                    "Set partDoc = documents.Add(\"Part\")\n"
                    "Dim part As Part\n"
                    "Set part = partDoc.Part"
                ),
                "创建草图并拉伸": (
                    "Dim body As Body\n"
                    "Set body = part.Bodies.Item(1)\n"
                    "' 获取 XY 平面引用\n"
                    "Dim xyPlane As Plane\n"
                    "Set xyPlane = part.OriginElements.PlaneXY\n"
                    "Dim ref As Reference\n"
                    "Set ref = part.CreateReferenceFromObject(xyPlane)\n"
                    "' 创建草图\n"
                    "Dim sketch As Sketch\n"
                    "Set sketch = body.Sketches.Add(ref)\n"
                    "' 开始绘制\n"
                    "Dim factory As Factory2D\n"
                    "Set factory = sketch.OpenEdition()\n"
                    "factory.CreateClosedCircle 0, 0, 25\n"
                    "sketch.CloseEdition\n"
                    "' 拉伸\n"
                    "Dim shapeFactory As ShapeFactory\n"
                    "Set shapeFactory = part.ShapeFactory\n"
                    "Dim pad As Pad\n"
                    "Set pad = shapeFactory.AddNewPad(sketch, 50)\n"
                    "part.Update"
                ),
                "遍历特征树": (
                    "Dim body As Body\n"
                    "Set body = part.Bodies.Item(1)\n"
                    "Dim shapes As Shapes\n"
                    "Set shapes = body.Shapes\n"
                    "For i = 1 To shapes.Count\n"
                    "    Dim shape As Shape\n"
                    "    Set shape = shapes.Item(i)\n"
                    "    MsgBox shape.Name\n"
                    "Next"
                ),
                "读写参数": (
                    "Dim params As Parameters\n"
                    "Set params = part.Parameters\n"
                    "' 读取\n"
                    "Dim length As Parameter\n"
                    "Set length = params.Item(\"PartBody\\\\Pad.1\\\\FirstLimit\\\\Length\")\n"
                    "MsgBox \"Length = \" & length.Value\n"
                    "' 修改\n"
                    "length.Value = 100\n"
                    "part.Update"
                ),
                "导出 STEP": (
                    "Dim partDoc As PartDocument\n"
                    "Set partDoc = CATIA.ActiveDocument\n"
                    "partDoc.ExportData \"C:\\\\output\\\\part.stp\", \"stp\""
                ),
                "批量处理文件": (
                    "Dim fso As Object\n"
                    "Set fso = CreateObject(\"Scripting.FileSystemObject\")\n"
                    "Dim folder As Object\n"
                    "Set folder = fso.GetFolder(\"C:\\\\parts\")\n"
                    "For Each file In folder.Files\n"
                    "    If Right(file.Name, 8) = \".CATPart\" Then\n"
                    "        CATIA.Documents.Open file.Path\n"
                    "        ' 处理...\n"
                    "        CATIA.ActiveDocument.Close\n"
                    "    End If\n"
                    "Next"
                ),
            },
        },
        "pycatia_guide": {
            "title": "pycatia 使用指南",
            "content": (
                "pycatia 是最推荐的 Python CATIA 自动化库。\n\n"
                "【安装】\n"
                "pip install pycatia\n\n"
                "【基本用法】\n"
                "from pycatia import catia\n"
                "caa = catia()  # 连接到运行中的 CATIA\n\n"
                "# 访问当前文档\n"
                "doc = caa.active_document\n"
                "part = doc.part\n\n"
                "# 访问实体\n"
                "bodies = part.bodies\n"
                "body = bodies.item(1)  # 注意：pycatia 索引从1开始\n\n"
                "# 获取参考平面\n"
                "planes = part.origin_elements\n"
                "xy = planes.plane_xy\n\n"
                "# 创建草图\n"
                "ref = part.create_reference_from_object(xy)\n"
                "sketches = body.sketches\n"
                "sketch = sketches.add(ref)\n"
                "factory = sketch.open_edition()\n"
                "factory.create_closed_circle(0, 0, 25)\n"
                "sketch.close_edition()\n\n"
                "# 拉伸\n"
                "sf = part.shape_factory\n"
                "pad = sf.add_new_pad(sketch, 50)\n"
                "part.update()\n\n"
                "【主要模块】\n"
                "• pycatia.mec_mod_interfaces — 零件/实体/草图\n"
                "• pycatia.part_interfaces — Part Design 特征\n"
                "• pycatia.sketcher_interfaces — 2D 草图\n"
                "• pycatia.product_interfaces — 装配\n"
                "• pycatia.drafting_interfaces — 工程图\n"
                "• pycatia.hybrid_shape_interfaces — 曲面设计\n"
                "• pycatia.knowledge_interfaces — 参数/公式"
            ),
        },
        "error_handling": {
            "title": "自动化错误处理",
            "content": (
                "CATIA COM 自动化中的常见错误和处理方法：\n\n"
                "1. 'Application not found' — CATIA 未运行\n"
                "   → 先启动 CATIA 或用 CreateObject 创建新实例\n\n"
                "2. 'Method failed' — 操作参数无效\n"
                "   → 检查参数类型和范围，确保引用有效\n\n"
                "3. 'Permission denied' — 文件被锁定\n"
                "   → 关闭其他打开该文件的程序\n\n"
                "4. 'Type mismatch' — 对象类型不匹配\n"
                "   → 检查 COM 对象的接口类型\n\n"
                "5. 'Update error' — 模型更新失败\n"
                "   → 草图可能有错误，检查约束和轮廓\n\n"
                "最佳实践：\n"
                "• 每次操作后检查返回值\n"
                "• 在关键操作前后调用 Part.Update()\n"
                "• 使用 try/except (Python) 或 On Error (VBA) 捕获错误\n"
                "• 操作失败时 Undo 再重试"
            ),
        },
    },
}
