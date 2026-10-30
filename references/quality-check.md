# 检查与交付边界

## 编译

使用 `build_report.py main.tex --render`。每次构建生成新目录，两个 XeLaTeX 回合，保存 build-summary.json、console-pass*.txt 和原始 log；阻止失败时交付旧 PDF。依赖仅本地 TeX Live：Beamer、ctex/fontspec、Latin Modern/Fandol、graphicx、amsmath/amssymb、booktabs/tabularx、TikZ。

脚本会筛查：编译失败、缺字、Overfull h/vbox、undefined references、rerun 请求、主题缺图标记；用可用的 pdfplumber 检查文字是否出界/进入页脚区和低有效分辨率图像。pypdf 提供页数/尺寸。可选 Python 依赖缺失不阻止编译，但相应检查标为 unavailable。Underfull 可能只是留白，记录并结合实际页面判断。

`build-summary.json` 记录 `visual_review_required=true`，不会自动声称“视觉通过”。`--render` 需要 Poppler 的 pdftoppm，生成所有页和有 Pillow 时的 contact-sheet。没有这些工具时可用本地已有替代，明确哪些检查未完成，不自动联网安装。

## 视觉检查

逐页检查：标题/横线、边距/对齐、中文缺字、数学上下标、表头与行间距、长公式、图内最小文字、图像是否拉伸、页码是否被裁剪、结论/来源是否互相遮挡。密集页看单页原尺寸；缩略图用于一致性检查。截图和渲染 PDF 必须对应最新源码。自动坐标筛查不能发现所有重叠或图内文本问题。

修复顺序：删重复内容 → 提炼观点 → 拆页 → 调栏宽/图裁剪 → 调局部间距。保持正文 10 pt 左右、表格 9 pt、说明 8 pt；不使用 shrink 掩盖问题。

## 内容检查

核对页间主线、无重复堆砌、图表来源、数据与原表一致、AP 定义与对照条件、论文作者陈述与我们的推断、已完成/进行中/计划状态、结果下降、未控制变量的因果措辞。

`data/report.json` 保持稳定 slide_id 和 evidence_kind/source_ids。已知缺口列在 missing_information，并在对应页可见；不把机器检查字段替代人的学术判断。完成报告仍有关键资料缺口时交付“待补充草稿”。

视觉复核记录 `qa/visual-review.md`：最新 PDF SHA256、总页数、查看页码、内容核对来源、修改及限制。这里的记录由实际检查者填写，编译脚本不代填。
