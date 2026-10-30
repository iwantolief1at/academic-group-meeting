# 组件与选择规则

所有组件在 `assets/templates/common/beamerthemeGroupMeeting.sty`，参数均为 TeX 内容；也可直接写原生 `frame` 使用相同主题。每个宏生成一页，标题尽量一行，必要时不超过两行。

| 需求 | 组件及参数 |
|---|---|
| 标题页 | `\ReportTitlePage`，元信息来自 report.tex |
| 目录页 | `\ReportOutline{左栏内容}{右栏内容}` |
| 章节页 | `\ReportSection{标题}{引导问题}`，同时登记 section |
| 普通页 | `\ReportContent{标题}{灰色导语}{正文}` |
| 双栏对比 | `\ReportCompare{标题}{导语}{左栏}{右栏}{结论}` |
| 网络结构 | `\ReportNetwork{标题}{导语}{图或 TikZ}{数据流解释}{来源}` |
| 公式解释 | `\ReportEquation{标题}{导语}{数学模式内容}{符号及机制解释}{结论}` |
| 大图 | `\ReportFigure{标题}{导语}{图像路径}{图注}{来源}` |
| 结果表 | `\ReportResults{标题}{导语}{tabular/tabularx}{结论}{来源}` |
| 消融表 | `\ReportAblation{标题}{对照条件}{表格}{结论}{限制与来源}` |
| 检测对比 | `\ReportDetection{标题}{导语}{GT图}{Baseline图}{改进图}{结论}`，各图同尺寸 |
| 阶段结论 | `\ReportSummary{标题}{证据与局限正文}{核心结论}` |
| 下一步 | `\ReportPlan{标题}{计划表/列表}{导师讨论问题}` |
| 结束页 | `\ReportEnd{主题}{日期/身份}{后续安排}` |

辅助组件：`\ReportLead{导语}`；`\ReportSource{来源}`；`\ReportTakeaway{结论}`；`\ReportPending{缺口}`；`\ReportPath{文件路径}`（安全显示下划线等常见路径字符）；`\ReportImage[高度]{路径}`（宽度限当前栏宽）；`GMBlock` / `GMConclusion` / `GMCaution` 环境分别蓝绿橙，参数为标题。

图像页预算：完整主图约 4.1 cm 高，检测三栏图约 3.7 cm 高；保留解释和来源空间。复杂网络图先全图总览，再分模块裁剪，不能把完整论文页面缩成难读的小图。矩形裁剪参数使用 PDF 点单位、左下原点，与页面截图的左上像素坐标不同。

表格建议 4–6 列、3–7 个主要结果行；9 pt 是推荐表格底线，过长时按指标/数据集拆页。保留表头、单位、小数精度、缺失值与对照标记。多级表头可手写 TeX，避免自动转换曲解语义。

公式不要当图片插入；宽公式使用 aligned/split 等拆分、先给核心项再给附录推导。只对独立且已说明的图允许局部缩放。不要使用 frame shrink、tiny 正文、resizebox 整页表格。

新增组件时在 sty 文件沿用颜色/字号/边距和 `\ReportLead`、`\ReportSource`、`\ReportTakeaway`；先在独立测试报告加入组件，再编译和查看实际页。新增宏避免改变已有组件含义。
