# 安装、使用与维护

## 目录与依赖

Skill 的根目录是 `academic-group-meeting/`：入口 `SKILL.md`，界面信息 `agents/openai.yaml`，主题及起始内容 `assets/templates/`，脚本 `scripts/`，规范 `references/`，示例 `examples/`。

当前官方支持用户级 `$HOME/.agents/skills/` 和项目级 `.agents/skills/`：<https://learn.chatgpt.com/docs/build-skills>（2026-10-12 核对）。默认将这个目录安装为 `$HOME/.agents/skills/academic-group-meeting/`，方便跨项目使用。避免在用户级与项目级同时装同名副本。现有安装不覆盖；先选择版本/备份策略。若未出现在列表，重启 Codex；也可先在请求中给出本 Skill 的绝对路径。

本地需要 TeX Live 和 XeLaTeX。编译脚本仅依赖 Python 标准库；PDF 页/裁剪脚本需 pypdf；页面几何检查需 pdfplumber；缩略图需 Pillow；渲染需 Poppler。优先已有依赖。主题不需要网络、字体下载、shell escape 或 Python 绘图库。

## 调用与手工命令

自然语言可用“使用组会汇报 Skill 的论文模式……”，明确调用可用 `$academic-group-meeting`。提供资料路径、希望强调的点、报告日期和已有报告路径即可。未指定身份/日期时保留待补充，不能把系统当天日期猜成组会日期。

```powershell
# 所有路径均可带空格；替换 <skill> 和 <report> 为实际路径
python "<skill>/scripts/init_report.py" --mode paper --output "<new-report>"
python "<skill>/scripts/build_report.py" "<report>/main.tex" --render
python "<skill>/scripts/csv_to_tex.py" "results.csv" --columns method AP50 AP_small --output "<report>/data/table.tex"
python "<skill>/scripts/extract_pdf.py" "paper.pdf" --page 4 --crop 30 240 550 690 --output "<report>/figures/architecture.pdf"
```

最后一条坐标仅作语法示例，实际坐标必须从用户论文测量。PDF 裁剪保留原图清晰度；插图使用 `\ReportImage{figures/architecture.pdf}`。表格使用 `\input{data/table.tex}`。转换脚本不会生成学术结论；由 Codex 根据证据填充页面与伴随 JSON。

直接本地编译也可在报告目录执行 XeLaTeX 两次；建议将输出放入新 build 目录，避免替换旧 PDF。脚本构建输出 `build/<时间戳>/main.pdf`，支持 `--output-dir` 指定尚不存在的目录。返回码 0 为编译且日志未发现阻断项，1 为失败，2 为需要修复的日志问题；0 不代表视觉/学术审查通过。

## 样式与组件

修改单份报告的 `style.tex`，示例：

```tex
\definecolor{GMBlue}{HTML}{0173B2}
\setbeamerfont{frametitle}{size=\fontsize{12}{15}\selectfont}
\setbeamersize{text margin left=1cm,text margin right=1cm}
\setCJKsansfont{Microsoft YaHei} % 必须本机存在
```

共享模板改动作用于未来初始化的报告，已生成报告保留自己的主题副本。修改字体时同步 CJK main/sans 的需要；默认 Fandol 符合参考课件中的少量中文。正文层级采用 `normal text`；不要改进度条或加入花哨动画来填空。

替换参考风格：保存新参考路径/来源 → 抽样标题、密集公式、结果表、目录与结束页 → 测量并看渲染 → 更新 visual-style.md 与 theme/fonts/style → 使用两个示例回归编译和视觉核对。比例变更需要同时修改 main.tex 的 aspectratio 和重新评估各组件的高度。

新增组件：在 theme 中定义 `\Report...` 宏，沿用已有区块和辅助宏，更新 layouts.md 并加入短组件示例。不要复制整个主题到每个组件。

## 持续更新与来源记录

报告项目保留：main.tex、report.tex、fonts.tex、style.tex、theme、content/、figures/、data/、qa/。转移给其他电脑时这些文件必须一起复制，无对已安装 Skill 的绝对依赖。

更新时创建新的日期/版本目录，再更改本周新增页面、数据和来源。稳定 slide_id 用于追踪页面，不要求页码固定。建议 report.json 的每条 slides 记录 `slide_id`、`claim`、`layout`、`evidence_kind`、`source_ids`、`status`；sources.json 每条记录 `source_id`、`path`、`sha256`、`location`、`notes`。二者是证据/规划记录，与 TeX 独立，不是自动生成器输入。

示例虚构内容都标 demo，示例 CSV/图像的演示身份应随页保留。新报告初始化不会复制 examples 的虚构内容，只使用待补充骨架。
