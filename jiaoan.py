import os
from docxtpl import DocxTemplate


def generate_qss_lesson_plan():
    # 1. 设置路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, '教案模板.docx')
    output_path = os.path.join(base_dir, '1.4_QSS样式美化_生成教案.docx')

    if not os.path.exists(template_path):
        print(f"错误：找不到模板文件 {template_path}")
        return

    # 2. 初始化模板对象
    doc = DocxTemplate(template_path)

    # 3. 构造数据上下文（严格匹配模板变量名）
    context = {
        "unit_name": "单元一：QSS 样式美化实战教案",
        "lesson_title": "1.4 样式美化：QSS 实战",
        "hours": "2",
        "class_name": "人工智能 2403",
        "week_info": "第 3 周 星期四 第 3-4 节",
        "teacher_name": "洪德衍",
        "location": "S1540",

        # 教学目标
        "teaching_objectives": [
            "能正确理解 QSS（Qt Style Sheets）的基本语法",
            "能独立为部件设置样式（颜色、字体、边框等）",
            "能使用选择器定制不同状态样式（hover、pressed 等）",
            "能根据设计稿复刻界面风格"
        ],

        # 重点难点
        "key_points": [
            "QSS 基本语法（类似 CSS）",
            "常用样式属性（background-color、border 等）",
            "状态伪类（:hover、:pressed、:disabled）",
            "类选择器与对象名选择器"
        ],
        "difficult_points": [
            "布局与样式的配合",
            "复杂样式（渐变、圆角、阴影）的实现",
            "样式冲突与优先级"
        ],
        "solutions": "提供 QSS 速查手册；通过对比演示展示效果；分步构建复杂样式。",

        # 思考作业
        "homework": [
            "简述 QSS 与 CSS 的异同。",
            "为一个按钮设置样式：蓝色背景、白色文字、圆角、hover 时变深。",
            "自定义一个输入框样式：边框、内边距、焦点时高亮。",
            "尝试复刻课程智慧食堂界面的顶部状态栏样式。"
        ],

        "teaching_logic": "采用“语法讲解→效果演示→案例实操→设计复刻”的思路。先讲解 QSS 基础语法，演示常用效果，引导学生实操练习，最后复刻真实界面。",

        # 教学详细内容（对应 sections 循环）
        "sections": [
            {
                "title": "课程理论知识",
                "duration": "40",
                "methods": "概念讲解 + 效果演示",
                "knowledge": "QSS 语法、样式属性、选择器、状态伪类。",
                "content": "讲解 QSS 基础语法与设置方式；介绍盒模型、背景颜色及字体属性；演示状态伪类的用法（hover, pressed）。"
            },
            {
                "title": "实操练习",
                "duration": "40",
                "methods": "案例实操 + 设计复刻",
                "knowledge": "按钮样式库、输入框样式、智慧食堂状态栏复刻。",
                "content": "任务1：创建5种不同风格的按钮（15分钟）；任务2：自定义输入框不同状态样式（10分钟）；任务3：复刻智慧食堂顶部深灰状态栏（15分钟）。"
            }
        ],

        # 思政内容
        "ideological_duration": "5",
        "ideological_contents": [
            {"title": "审美培养", "content": "界面美观是用户体验的重要组成部分，培养对色彩和布局的敏感度。"},
            {"title": "工匠精神", "content": "强调样式细节决定品质，培养像素级还原设计稿的态度。"}
        ],

        # 教学反思
        "reflection": "属性较多易记混，需提供速查卡片；渐变等复杂效果需增加可视化演示；通过样式组件库帮助学生复用代码。"
    }

    # 4. 执行渲染
    try:
        doc.render(context)
        doc.save(output_path)
        print(f"教案已成功生成：{output_path}")
    except Exception as e:
        print(f"渲染过程中出错：{e}")


if __name__ == "__main__":
    generate_qss_lesson_plan()