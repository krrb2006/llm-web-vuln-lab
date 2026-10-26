from __future__ import annotations

"""Build the illustrated final Word report from the audited repository findings."""

from pathlib import Path
from datetime import date
import shutil

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "最终实验报告_2026-10-26.docx"
TMP = ROOT / "artifacts" / "final_report_2026-10-26"

NAVY = "12355B"
BLUE = "1F5A99"
CYAN = "2D8CBE"
TEAL = "159A9C"
GREEN = "39A96B"
GOLD = "F2B134"
LIGHT = "EAF2F8"
GRAY = "5B6573"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_border(cell, color: str = "D9E2F3") -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right"):
        tag = qn(f"w:{edge}")
        node = borders.find(tag)
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "4")
        node.set(qn("w:color"), color)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_hyperlink(paragraph, text: str, url: str) -> None:
    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), BLUE)
    r_pr.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    r_pr.append(underline)
    new_run.append(r_pr)
    text_node = OxmlElement("w:t")
    text_node.text = text
    new_run.append(text_node)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def font(size=10.5, bold=False, color="1F2937", name="Microsoft YaHei"):
    r = {"size": Pt(size), "bold": bold, "font": name}
    # caller assigns via helper; returned values are intentionally simple
    return r


def make_charts() -> dict[str, Path]:
    TMP.mkdir(parents=True, exist_ok=True)
    try:
        f_title = ImageFont.truetype("C:\\Windows\\Fonts\\msyhbd.ttc", 34)
        f_text = ImageFont.truetype("C:\\Windows\\Fonts\\msyh.ttc", 24)
        f_small = ImageFont.truetype("C:\\Windows\\Fonts\\msyh.ttc", 20)
    except OSError:
        f_title = f_text = f_small = ImageFont.load_default()

    metrics = TMP / "formal_metrics.png"
    img = Image.new("RGB", (1600, 780), "white")
    draw = ImageDraw.Draw(img)
    draw.text((75, 45), "正式实验三版 Prompt 的分类与定位结果（每版 N=12）", fill="#12355B", font=f_title)
    left, top, bottom = 180, 160, 650
    draw.line((left, top, left, bottom), fill="#6B7280", width=3)
    draw.line((left, bottom, 1490, bottom), fill="#6B7280", width=3)
    for pct in range(0, 101, 20):
        y = bottom - int((bottom - top) * pct / 110)
        draw.line((left, y, 1490, y), fill="#D9E2F3", width=2)
        draw.text((85, y - 12), str(pct), fill="#4B5563", font=f_small)
    centers = [450, 820, 1190]
    for cx, label in zip(centers, ("V0", "V1", "V2")):
        h = int((bottom - top) * 100 / 110)
        draw.rectangle((cx - 110, bottom - h, cx - 22, bottom), fill="#1F5A99")
        draw.rectangle((cx + 22, bottom - h, cx + 110, bottom), fill="#39A96B")
        draw.text((cx - 92, bottom - h - 42), "100%", fill="#12355B", font=f_small)
        draw.text((cx + 38, bottom - h - 42), "100%", fill="#1C6B45", font=f_small)
        draw.text((cx - 24, bottom + 25), label, fill="#1F2937", font=f_text)
    draw.rectangle((1040, 705, 1068, 733), fill="#1F5A99")
    draw.text((1080, 705), "分类准确率", fill="#374151", font=f_small)
    draw.rectangle((1270, 705, 1298, 733), fill="#39A96B")
    draw.text((1310, 705), "定位正确率", fill="#374151", font=f_small)
    img.save(metrics)

    bonus = TMP / "bonus_completion.png"
    img = Image.new("RGB", (1600, 700), "white")
    draw = ImageDraw.Draw(img)
    draw.text((75, 40), "加分实验完成度：26 / 26", fill="#12355B", font=f_title)
    kinds = ["Prompt Injection", "Burp 联动", "上下文消融", "高级案例"]
    totals = [16, 2, 4, 4]
    colors = ["#1F5A99", "#2D8CBE", "#159A9C", "#F2B134"]
    for i, (kind, n, color) in enumerate(zip(kinds, totals, colors)):
        y = 160 + i * 120
        draw.text((80, y + 18), kind, fill="#374151", font=f_text)
        draw.rounded_rectangle((440, y, 1380, y + 70), radius=14, fill="#EDF2F7")
        draw.rounded_rectangle((440, y, 440 + int(900 * n / 16), y + 70), radius=14, fill=color)
        draw.text((1410, y + 15), f"{n}/{n}", fill="#12355B", font=f_text)
    draw.text((440, 640), "所有加分记录独立于 36 条主实验统计", fill="#6B7280", font=f_small)
    img.save(bonus)

    pipeline = TMP / "audit_pipeline.png"
    img = Image.new("RGB", (1800, 520), "#F7FAFC")
    draw = ImageDraw.Draw(img)
    boxes = [
        (55, 150, 355, 370, "样本与真值", "源码 · 行号 · 哈希"),
        (450, 150, 750, 370, "冻结输入包", "固定 code_input"),
        (845, 150, 1145, 370, "LLM 结构化输出", "raw · JSON · 截图"),
        (1240, 150, 1540, 370, "人工与本地复核", "POC · DOM · HTTP"),
    ]
    colors2 = ["#12355B", "#1F5A99", "#2D8CBE", "#159A9C"]
    for (x1, y1, x2, y2, title, sub), color in zip(boxes, colors2):
        draw.rounded_rectangle((x1, y1, x2, y2), radius=28, fill=color)
        draw.text((x1 + 28, y1 + 52), title, fill="white", font=f_title)
        draw.text((x1 + 28, y1 + 120), sub, fill="#DDEEFF", font=f_text)
    for x1 in (370, 765, 1160):
        draw.polygon([(x1, 248), (x1 + 58, 248), (x1 + 58, 230), (x1 + 92, 260), (x1 + 58, 290), (x1 + 58, 272), (x1, 272)], fill="#6B8FB7")
    draw.text((55, 55), "可审计的 LLM 辅助漏洞挖掘流程", fill="#12355B", font=f_title)
    draw.text((55, 425), "原则：模型建议不等于漏洞触发；每一层均保存可回溯证据。", fill="#4B5563", font=f_text)
    img.save(pipeline)
    return {"metrics": metrics, "bonus": bonus, "pipeline": pipeline}


def set_run_font(run, size=10.5, bold=False, color="1F2937", font_name="Microsoft YaHei"):
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)


def add_paragraph(doc, text="", *, size=10.5, bold=False, color="1F2937", align=None, space_after=6, first_indent=True, style=None):
    p = doc.add_paragraph(style=style)
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.line_spacing = 1.35
    if first_indent:
        pf.first_line_indent = Cm(0.74)
    run = p.add_run(text)
    set_run_font(run, size, bold, color)
    return p


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Cm(0.65 + level * 0.5)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.25
    r = p.add_run(text)
    set_run_font(r, 10.2)
    return p


def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.space_before = Pt(14 if level == 1 else 9)
    p.paragraph_format.space_after = Pt(6)
    for r in p.runs:
        set_run_font(r, 16 if level == 1 else 12.5, True, NAVY)
    return p


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(7)
    r = p.add_run(text)
    set_run_font(r, 9, False, GRAY)
    return p


def add_table(doc, headers, rows, widths=None, font_size=8.8):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    header = table.rows[0]
    set_repeat_table_header(header)
    for i, text in enumerate(headers):
        c = header.cells[i]
        c.text = ""
        set_cell_shading(c, NAVY)
        set_cell_border(c, "FFFFFF")
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(str(text))
        set_run_font(r, font_size, True, "FFFFFF")
        if widths:
            c.width = Cm(widths[i])
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            c = cells[i]
            c.text = ""
            set_cell_border(c)
            if ridx % 2 == 0:
                set_cell_shading(c, "F5F9FD")
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.12
            r = p.add_run(str(value))
            set_run_font(r, font_size)
            if widths:
                c.width = Cm(widths[i])
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return table


def add_image(doc, path: Path, width_cm: float):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run()
    run.add_picture(str(path), width=Cm(width_cm))
    for doc_pr in run._r.xpath(".//wp:docPr"):
        doc_pr.set("descr", path.stem.replace("_", " "))
    return p


def add_callout(doc, title: str, body: str, fill="EAF2F8"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_repeat_table_header(table.rows[0])
    cell = table.cell(0, 0)
    set_cell_shading(cell, fill)
    set_cell_border(cell, "B7CDE5")
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(title + "  ")
    set_run_font(r, 10.3, True, NAVY)
    r = p.add_run(body)
    set_run_font(r, 10.3)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def build() -> None:
    charts = make_charts()
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(1.8)
    section.left_margin = Cm(2.15)
    section.right_margin = Cm(2.15)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Microsoft YaHei"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(10.5)
    for style_name in ("Title", "Subtitle", "Heading 1", "Heading 2", "Heading 3"):
        s = styles[style_name]
        s.font.name = "Microsoft YaHei"
        s._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")

    # Header and footer.
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = header.add_run("网络安全课程大实验  |  LLM 辅助 Web 漏洞挖掘")
    set_run_font(r, 8.5, False, GRAY)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = footer.add_run("llm-web-vuln-lab  ·  2026-10-26  ·  第 ")
    set_run_font(r, 8.3, False, GRAY)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    footer._p.append(fld)
    r = footer.add_run(" 页")
    set_run_font(r, 8.3, False, GRAY)

    # Cover.
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Cm(2.4)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("网络安全课程大实验")
    set_run_font(r, 16, True, BLUE)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run("基于大语言模型辅助的 Web 漏洞挖掘与验证")
    set_run_font(r, 21, True, NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(30)
    r = p.add_run("——可审计的 SQL 注入与 XSS 教学靶场实验报告——")
    set_run_font(r, 12, False, GRAY)
    add_image(doc, charts["pipeline"], 16.3)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    for label, value in [("项目", "llm-web-vuln-lab"), ("实验日期", "2026-10-26"), ("实验范围", "本地 Docker 教学靶场 127.0.0.1:4280")]:
        r = p.add_run(f"{label}：{value}\n")
        set_run_font(r, 10.5, False, "374151")
    doc.add_page_break()

    # Abstract / contents.
    add_heading(doc, "摘  要", 1)
    add_paragraph(doc, "本实验构建了一个面向 SQL 注入（SQLi）与跨站脚本（XSS）的可审计教学靶场，考察大语言模型在受控 PHP 代码样本上的静态漏洞判断、行号定位和本地验证建议生成能力。数据集由 24 个漏洞版/修复版配对样本组成，其中 12 个样本进入正式测试；在 V0、V1、V2 三版 Prompt 下各运行一次，形成 36 条正式记录。实验将“模型预测、代码定位、POC 文本、环境适配、真实触发”分层归档，避免把模型的文字分析误写为漏洞已被验证。")
    add_paragraph(doc, "在本组教学样本上，三版 Prompt 的分类与定位均为 12/12 正确，SQLi 与 XSS 各 6 个正式样本均无误报、无漏报。加分部分完成 16 条 Prompt Injection、2 条 Burp 联动、4 条上下文消融及 4 条高级案例（二阶 SQLi、IDOR）记录。所有动态请求只发往本机回环地址 `127.0.0.1:4280`。", first_indent=True)
    add_callout(doc, "核心结论", "本实验验证的是一套可追溯的 LLM 辅助审计流程。V1/V2 在该小规模、配对的教学数据集上没有带来可观测的分类提升，其主要价值体现在输出约束、验证边界与可审计性。", "E8F5EE")
    add_heading(doc, "关键词", 2)
    add_paragraph(doc, "大语言模型；Web 漏洞挖掘；SQL 注入；跨站脚本；Prompt 工程；可追溯验证", first_indent=False, space_after=10)
    add_heading(doc, "目录", 1)
    contents = [
        "1. 实验背景、目标与边界", "2. 实验方案与可审计流程", "3. 数据集、Prompt 与冻结机制", "4. 本地验证环境与证据分层", "5. 正式实验结果与分析", "6. 加分实验与高级案例", "7. 限制、反思与改进", "8. 结论", "附录 A. 复现命令", "附录 B. 证据索引",
    ]
    for i, t in enumerate(contents, start=1):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(t)
        set_run_font(r, 10.5, False, NAVY)
    add_heading(doc, "1. 实验背景、目标与边界", 1)
    add_heading(doc, "1.1 研究问题", 2)
    add_paragraph(doc, "传统 Web 审计需要从外部输入、数据传播、防护措施到危险操作建立完整证据链。LLM 可以快速生成候选路径与验证思路，但其回答不能取代源码事实或运行观察。本实验围绕以下问题开展：")
    for t in ["在配对的 SQLi/XSS 教学样本中，模型是否能正确区分漏洞版与修复版？", "Prompt 从 V0 到 V2 的约束增强，是否改变分类或定位结果？", "模型生成的本地 POC 建议，如何在不扩展攻击范围的前提下形成可审计的验证线索？"]:
        add_bullet(doc, t)
    add_heading(doc, "1.2 安全边界", 2)
    add_table(doc, ["维度", "约束与做法"], [
        ("目标系统", "仅限仓库内 PHP 教学样例；不扫描、测试或访问公网目标。"),
        ("网络范围", "Docker 服务只映射到 127.0.0.1:4280；POC 中禁止外发数据。"),
        ("结论规则", "模型预测、HTTP 200、POC 文本均不等价于漏洞触发；触发以日志、DOM marker 或受控业务差异为准。"),
        ("外推范围", "结果仅针对 12 个正式教学样本，不外推为真实世界漏洞发现率。"),
    ], widths=[3.0, 12.6], font_size=9.2)
    add_heading(doc, "1.3 传统审计与 LLM 辅助的分工", 2)
    add_table(doc, ["环节", "传统人工审计", "LLM 辅助", "最终判据"], [
        ("路径发现", "追踪 source / flow / guard / sink", "提出候选数据流和行号", "原始源码与 line_map"),
        ("防护判断", "检查参数化、编码、净化、授权", "解释防护是否覆盖路径", "漏洞/修复配对差异"),
        ("验证设计", "构造普通与受控请求", "给出本地 POC 候选", "审核后的本地运行证据"),
        ("结论表达", "源码与观察综合判断", "结构化 JSON 输出", "原文、哈希、真值、日志"),
    ], widths=[2.2, 4.4, 4.4, 4.6])

    add_heading(doc, "2. 实验方案与可审计流程", 1)
    add_paragraph(doc, "整个实验链路以输入冻结为起点，以人工复核和本地观察为终点。图 1 展示了由样本与真值、冻结输入、结构化模型输出、人工/动态验证组成的四层证据链。")
    add_image(doc, charts["pipeline"], 16.0)
    add_caption(doc, "图 1  可审计的 LLM 辅助 Web 漏洞挖掘流程")
    add_heading(doc, "2.1 运行流程", 2)
    for t in ["固定源码和正式输入包：统一 LF 换行、SHA-256、行号映射，隔离废弃输入包。", "模型运行与归档：保存 Prompt、完整 input、原始回答、规范化 JSON、会话/设置截图及哈希。", "独立复核：核对模型预测、源码定位、输入与原文的绑定关系，并对照预先登记的真值。", "本地验证：只在教学 Docker 环境中执行审核后的 loopback 请求，以业务差异或 DOM marker 判定结果。"]:
        add_bullet(doc, t)
    add_heading(doc, "2.2 模型和 Prompt 口径", 2)
    add_paragraph(doc, "正式网页端运行采用默认/快速模式，深度思考开启、智能搜索关闭。DeepSeek 官方于 2026-10-17 公告 V4.1 Flash 升级为 DeepSeek-V4.1-Flash-1017，网页端与 App 同步更新；正式运行日期为 2026-10-19。因此本报告按“DeepSeek 网页默认/快速模式（官方版本映射：DeepSeek-V4.1-Flash-1017）”记载该批次。单条会话未保存 API/HAR 级别的后端模型字段，这一限制在第 7 章明确保留。")
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    r = p.add_run("官方版本公告：")
    set_run_font(r, 10.2, True, NAVY)
    add_hyperlink(p, "DeepSeek Updates - V4.1-Flash-1017", "https://api-docs.deepseek.com/news/news261017/")
    add_heading(doc, "2.3 Prompt 迭代原则", 2)
    add_table(doc, ["版本", "主要约束", "跨版本不变项"], [
        ("V0", "统一中文、JSON、行号、source/flow/guard/sink 审计基线", "固定 code_input；输入包哈希不变"),
        ("V1", "强化数据流可达性、有效防护与缺失上下文说明", "同一正式样本仅修改 Prompt 文本"),
        ("V2", "强调普通/测试对照、验证前提、触发判据；拒绝代码注释中的嵌入指令", "不将静态结论写成已触发"),
    ], widths=[2.0, 8.4, 5.2])

    add_heading(doc, "3. 数据集、Prompt 与冻结机制", 1)
    add_heading(doc, "3.1 数据集构成", 2)
    add_paragraph(doc, "数据集共 24 例，均按漏洞版/修复版进行配对。奇数构造例登记为 true，配对修复例登记为 false。正式测试集共 12 个样本：S007、S008、S009、S010、S011、S012、S019、S020、S021、S022、S023、S024；每例在 V0/V1/V2 各运行一次，共计 36 条正式记录。")
    add_table(doc, ["类别", "总样本", "正式样本", "真值分布", "运行次数"], [
        ("SQLi", "12", "6", "漏洞 6 / 修复 6", "18"),
        ("XSS", "12", "6", "漏洞 6 / 修复 6", "18"),
        ("合计", "24", "12", "漏洞 12 / 修复 12", "36"),
    ], widths=[2.4, 3.2, 3.2, 4.1, 3.2])
    add_heading(doc, "3.2 可追溯输入包", 2)
    add_paragraph(doc, "每个正式样本由源码、code_input.txt、line_map.json、source.json 和 manifest 组成。源码与输入统一按 UTF-8/LF 计算 SHA-256；已作废的 S009-S012 v1 输入包迁入 archive，避免误进入冻结扫描。冻结脚本以只读预检方式派生 36 条计划，仅在 Prompt、真值、证据和唯一输入包全部满足条件后写入正式计划字段。")
    add_callout(doc, "证据完整性规则", "原始模型回答不可被规范化结果覆盖；如 JSON 本身存在格式缺陷，必须在 format_valid 或复核记录中保留，而不能修改原文后重新计分。", "FFF5DE")

    add_heading(doc, "4. 本地验证环境与证据分层", 1)
    add_heading(doc, "4.1 Docker 教学环境", 2)
    add_paragraph(doc, "验证环境由 Windows 宿主机、Docker Desktop、DVWA 与 MariaDB 构成。样例以本地挂载方式进入容器；服务端口绑定在 127.0.0.1:4280。验证前运行源码一致性、PHP 语法与健康检查，验证时比较普通请求和受控请求的实际业务差异。")
    add_heading(doc, "4.2 POC 分层原则", 2)
    add_table(doc, ["层级", "定义", "报告表述"], [
        ("原始模型 POC", "模型原文中生成的脚本或请求文本", "只说明模型给出的建议"),
        ("环境适配 POC", "为本地路径、Cookie、初始化数据或断言作适配", "与原始 POC 分开记录"),
        ("逻辑修改版", "修改了关键验证逻辑的脚本", "不得反写为原始模型 POC 成功"),
        ("动态触发证据", "服务端日志、DOM marker 或受控业务差异", "可支持本地教学环境中的触发结论"),
    ], widths=[3.2, 7.0, 5.6])
    add_heading(doc, "4.3 代表性 SQLi 证据", 2)
    add_paragraph(doc, "S009 的受控请求在 Burp Repeater 中仅面向 127.0.0.1:4280。响应区域展示了 3 条教学人员记录，与正常 ids=1 的单条结果形成对照；这一观察用于证明查询结果集合发生扩展，而不是仅凭 HTTP 状态码判断。")
    add_image(doc, ROOT / "evidence" / "BURP_SQLI_01" / "screenshots" / "burp_sqli_repeater_S009_20261013.jpg", 15.8)
    add_caption(doc, "图 2  S009 的本地 Burp Repeater 受控请求与三条记录响应（目标为 127.0.0.1:4280）")
    add_heading(doc, "4.4 代表性二阶 SQLi 模型记录", 2)
    add_paragraph(doc, "高级案例 ADV_SECOND_SQLI 采用“先写入受控昵称、再经独立读取路径拼接查询”的二阶数据流。模型会话截图只说明模型对代码的结构化审计与 POC 文本建议；动态对照由独立本地检查脚本完成，并且不把截图本身解释为漏洞已触发。")
    add_image(doc, ROOT / "runs" / "ADV_SECOND_SQLI_VULN_R1" / "session_screenshot.png", 15.6)
    add_caption(doc, "图 3  ADV_SECOND_SQLI 漏洞版的网页端模型原始回答截图（模型审计证据）")

    add_heading(doc, "5. 正式实验结果与分析", 1)
    add_heading(doc, "5.1 整体统计", 2)
    add_paragraph(doc, "正式统计来自 results/formal_eval_2026-10-19-v2/summary.md。36 条记录均为 reviewed；三版 Prompt 在 12 个正式样本上得到相同分类与定位结果。")
    add_table(doc, ["Prompt", "N", "TP", "FP", "TN", "FN", "不确定", "准确率", "定位正确率", "原始 POC 可执行率"], [
        ("V0", "12", "6", "0", "6", "0", "0", "100.0%", "100.0%", "0.0%"),
        ("V1", "12", "6", "0", "6", "0", "0", "100.0%", "100.0%", "0.0%"),
        ("V2", "12", "6", "0", "6", "0", "0", "100.0%", "100.0%", "16.7%"),
    ], widths=[1.55, 1.0, 0.85, 0.85, 0.85, 0.85, 1.2, 2.0, 2.4, 3.3], font_size=8.1)
    add_image(doc, charts["metrics"], 15.3)
    add_caption(doc, "图 4  V0、V1、V2 的正式分类准确率与定位正确率")
    add_heading(doc, "5.2 Prompt 迭代的解释", 2)
    add_paragraph(doc, "V0→V1、V1→V2、V0→V2 的 12 个配对比较中均无预测变化，准确率变化均为 0.0%。因此不能写成“Prompt 优化提高了检测准确率”。更合适的解释是：本组漏洞版/修复版差异较清晰；V1/V2 的主要增益是要求模型公开证据边界、验证前提和缺失上下文，使输出更便于复核。")
    add_heading(doc, "5.3 代表性案例对照", 2)
    add_table(doc, ["案例", "漏洞版观察", "修复版观察", "证据含义"], [
        ("S009 SQLi", "ids=1 为 1 行；受控条件为 3 行", "不产生相同结果扩展", "查询语义发生改变"),
        ("S021 / S022 XSS", "S021 DOM data-lab-xss=yes", "S022 无 marker", "区分响应出现脚本与浏览器执行"),
        ("S011 SQLi", "适配后有排序变化", "配对控制无同样行为", "原始 POC 与适配结果分层"),
        ("ADV_SECOND_SQLI", "二次读取路径出现漏洞版/修复版差异", "参数化读取不出现同样差异", "跨请求数据流"),
        ("ADV_IDOR", "用户 101 可读取 owner 202 对象", "修复版同请求为空", "对象级授权过滤有效"),
    ], widths=[3.1, 4.5, 4.5, 4.2], font_size=8.7)

    add_heading(doc, "6. 加分实验与高级案例", 1)
    add_paragraph(doc, "加分计划共 26 条，现已完成归档并通过项目内复核。它们与 36 条正式实验分开统计，避免将探索性或对照性记录混入主实验指标。")
    add_image(doc, charts["bonus"], 15.1)
    add_caption(doc, "图 5  加分实验分项完成度")
    add_table(doc, ["类别", "数量", "主要内容", "结论"], [
        ("Prompt Injection", "16", "S013 官方四类注释攻击矩阵及 S001 对照", "注释攻击不改变 S013 的预测；历史证据缺陷保留，不覆盖原文"),
        ("Burp 联动", "2", "S009 SQLi 与 S021 XSS 的本地请求/响应或 DOM 证据", "保留可读请求、截图或 marker"),
        ("上下文消融", "4", "S007、S020 的 entry/full context", "独立保存，不纳入 36 条正式统计"),
        ("高级案例", "4", "二阶 SQLi 与 IDOR 漏洞版/修复版", "模型会话、哈希和本地对照均归档"),
    ], widths=[3.0, 1.5, 5.6, 6.2], font_size=8.7)
    add_heading(doc, "6.1 高级案例的价值", 2)
    add_paragraph(doc, "高级案例覆盖了单文件直接 sink 之外的两种安全逻辑：二阶 SQLi 需要追踪跨请求、跨存储的污染值；IDOR 则要求区分 SQL 参数化与对象级授权。其目的不是扩大攻击面，而是检验模型是否能将“使用预处理 SQL”与“授权逻辑正确”分开判断。")
    add_heading(doc, "6.2 S001 默认/快速模式记录", 2)
    add_paragraph(doc, "S001 官方 8 条采用独立的网页默认/快速模式会话。每条保存模型原文、输入、DOM 回答、截图、元数据和 POC 执行结果；A 对输入/原文哈希、JSON、会话截图和 loopback 限制完成自主复核，并在本机对 8 条模型 POC 逐条复跑，均以 exit code 0 结束。该批记录与早期存在绑定缺陷的历史 S001 文件并存，不覆盖历史证据。")

    add_heading(doc, "7. 限制、反思与改进", 1)
    add_table(doc, ["限制", "可能影响", "后续改进"], [
        ("样本规模小且为配对教学样本", "100% 结果不能代表真实 Web 项目表现", "扩充跨文件、跨请求、边界模糊的盲测集"),
        ("模型版本未保留逐请求 API/HAR 字段", "版本依据是网页模式证据与官方更新公告", "优先使用可导出模型 ID 的 API；保存版本横幅"),
        ("训练语料重合风险", "常见漏洞模式可能被模型熟悉", "引入新编写和隐蔽变体样本"),
        ("POC 与环境耦合", "路径、Cookie、数据初始化会影响执行", "持续区分原始、适配、逻辑修改 POC"),
        ("部分收口为 A_self_review", "复核独立性较弱", "引入双盲复核或外部评审"),
    ], widths=[4.1, 5.8, 5.8], font_size=8.8)
    add_heading(doc, "7.1 对课堂实验的启示", 2)
    add_paragraph(doc, "LLM 适合作为审计助手而不是裁判：它能整理候选路径、暴露遗漏的授权或编码检查、生成受限环境中的验证草案；但真正的结论仍应由固定输入、源码复核、动态对照与清晰的证据边界共同给出。尤其在“预处理 SQL 是否等于安全”“HTTP 200 是否等于利用成功”“模型给出 POC 是否等于漏洞已触发”等问题上，分层记录能够有效减少过度解读。")

    add_heading(doc, "8. 结论", 1)
    add_paragraph(doc, "本项目完成了从样本构造、输入冻结、模型运行、结构化归档、真值复核到本地动态验证的教学闭环。正式实验 36/36、加分实验 26/26 均有可读证据；在本组样本中 SQLi/XSS 的分类与定位均为 100%。同时，三版 Prompt 的预测没有变化，因而本报告不把 V1/V2 描述为提高了准确率。")
    add_paragraph(doc, "项目的核心产出是一条“模型输出 - 源码 - 本地环境 - 人工复核”相互约束的证据链：模型负责候选路径发现和验证建议，源码和可复现的本地观察负责安全结论。这一分工使 LLM 的辅助价值可被利用，同时避免将语言模型的表达能力误写成自动化漏洞证明。")

    doc.add_page_break()
    add_heading(doc, "附录 A. 复现命令", 1)
    for block in [
        "# 冻结与主实验审计\npython tools/check_freeze.py\npython -m unittest discover -s tests -v\npython tools/evaluate.py --manifest dataset/manifest.json --runs runs/formal.json --root . --out results/formal_eval_recheck\npython tools/audit_submission.py --strict",
        "# 高级案例本地动态对照\npython environment/build_advanced_cases.py --a-ref HEAD --c-ref HEAD --d-ref HEAD\npython environment/init_lab_db.py --reset-advanced\ndocker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml up -d\npython environment/check_advanced.py --output results/ADV_runtime_recheck.json --compose docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml",
    ]:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.left_indent = Cm(0.4)
        p.paragraph_format.right_indent = Cm(0.4)
        run = p.add_run(block)
        set_run_font(run, 8.3, False, "23364D", "Consolas")
        set_cell_shading if False else None
    add_heading(doc, "附录 B. 核心证据索引", 1)
    add_table(doc, ["证据类型", "仓库位置", "用途"], [
        ("数据与真值", "dataset/manifest.json；dataset/packets/；docs/C_输入包总清单.md", "样本、源码、行号与真值基线"),
        ("正式结果", "runs/formal.json；runs/F_*；results/formal_eval_2026-10-19-v2/", "36 条主实验原文、规范化和统计"),
        ("模型口径", "results/A_model_provenance_update_2026-10-26.md", "网页默认/快速模式与版本映射说明"),
        ("环境与动态验证", "environment/；results/A_ADV_runtime_recheck_2026-10-26.md", "Docker、业务对照、第二台电脑复现"),
        ("加分实验", "experiments/bonus_runs.plan.json；evidence/；runs/ADV_*_R1/", "Prompt Injection、Burp、CTX、ADV 证据"),
        ("最终审计", "python tools/audit_submission.py --strict", "基础项与加分证据完整性检查"),
    ], widths=[3.2, 8.0, 4.5], font_size=8.4)

    # Document properties.
    props = doc.core_properties
    props.title = "基于大语言模型辅助的 Web 漏洞挖掘与验证"
    props.subject = "网络安全课程大实验报告"
    props.author = "llm-web-vuln-lab"
    props.keywords = "LLM, Web security, SQLi, XSS, audit"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
