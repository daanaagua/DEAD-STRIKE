# DEAD STRIKE SEO / GEO 改进清单

日期：2026-04-11
分支：`codex/dead-strike-round-two-expansion`

## 目标

本清单用于记录 DEAD STRIKE 当前 SEO 与 GEO 的改进优先级，并明确哪些事项已经实施，哪些事项应在下一轮继续推进。

## 当前结论

- 当前代码库不需要再次更新 `sitemap.xml`。
- 本分支的 `sitemap.xml` 已在 2026-04-11 随 round-two 扩库更新，包含新增详情页与主要 hub 页的 `lastmod`。
- 若线上站点尚未部署本分支，则仍需要在部署完成后重新向 Google Search Console 与 Bing Webmaster 提交 sitemap。
- 现阶段更值得优先处理的不是 sitemap 数量，而是详情页结构化数据、站点 GEO 可引用信息、以及后续信任页与内容页建设。

## P0：本轮已实施

### 1. 为全部可索引详情页补充结构化数据

- 为 57 个可索引详情页补入 `VideoGame` JSON-LD。
- 同时补入 `BreadcrumbList` JSON-LD。
- `BreadcrumbList` 的分类中间层固定按 `zombie-games`、`fps-games`、`shooter-games` 优先级选取，避免多分类页面出现不稳定路径。
- `legacy-alias` 且 `noindex` 的历史别名页不补详情页 schema。

### 2. 让 round-two 生成链默认输出详情页 schema

- 修改 `tools/render_round_two_pages.py`。
- 新生成的详情页在输出时默认写入 `VideoGame` 与 `BreadcrumbList`，避免下次再手工补齐。

### 3. 为存量详情页增加一次性回填脚本

- 新增 `tools/backfill_detail_schema.py`。
- 该脚本仅修改 `<head>` 内的 JSON-LD 区块，不重写正文布局，不改正文文案。
- 脚本使用标准库与字符串插入方式，不依赖 `bs4`。

### 4. 补强首页品牌信号

- 在首页新增 `Organization` JSON-LD。
- 明确品牌名称、站点地址、logo 与站点定位。
- 本轮没有添加 `SearchAction`，因为站内当前并不存在真实可用的搜索功能，不能伪造结构化数据。

### 5. 扩充 `llms.txt`

- 将 `llms.txt` 从简表扩为主题分组清单。
- 新增核心页、分类 hub、round-two 四个主题簇，以及关键事实摘要。
- 目标是提升 AI 检索与引用时对站内页面的识别效率。

### 6. 增加 GEO 校验脚本

- 新增 `tools/verify_geo_signals.py`。
- 校验首页是否具备 `WebSite`、`VideoGame`、`FAQPage`、`Organization`。
- 校验 `llms.txt` 关键章节是否存在。
- 校验每个可索引详情页的 `VideoGame`、`BreadcrumbList`、`url`、`publisher`、图片与描述是否齐全。

## P1：建议下一轮尽快做

### 1. 补齐信任页

建议新增以下页面：

- `about`
- `contact`
- `privacy-policy`
- `terms`
- `editorial-policy`

这些页面的目标是提升站点可信度、可解释性与品牌完整度，而不是直接冲排名。

### 2. 增加更细的主题 hub

建议下一轮新增以下聚类页：

- `sniper-games`
- `zombie-defense-games`
- `multiplayer-shooter-games`

这样可以减少过多详情页只依赖三大主 hub 承接的问题，并提升长尾词覆盖。

### 3. 增加答案型内容页

建议新增 3 到 5 个非 iframe 型内容页，优先主题如下：

- `best-browser-zombie-fps-games`
- `best-sniper-browser-games`
- `dead-strike-controls-guide`
- `dead-strike-tips`
- `dead-strike-vs-other-browser-zombie-games`

这类页面更适合被 AI 总结、摘录与引用，也更容易承接问答型搜索意图。

### 4. 补品牌外部信号

如果后续具备公开资料，可继续补：

- `Organization.sameAs`
- 联系邮箱
- 品牌简介
- 可公开的社媒或仓库链接

前提是信息真实存在，不应杜撰。

## P2：后续优化

### 1. 强化重点详情页文案差异

- 优先重写流量潜力最高的 10 到 15 个详情页。
- 重点提高玩法说明、适合人群、节奏、场景、差异点的独特性。
- 目标是降低模板感与近重复风险。

### 2. 做性能专项

- 评估首页与重点详情页的 Core Web Vitals。
- 当前 iframe 普遍为 `loading="eager"`，后续若 LCP 偏差，应优先测试“首屏封面图 + 点击后加载 iframe”策略。

### 3. 做上线后的搜索平台运营动作

- 部署完成后重新提交 `sitemap.xml`。
- 观察 Google Search Console 的抓取与索引情况。
- 观察新补 schema 是否在富结果检测中无报错。

## 本轮实施范围

本轮只处理结构化数据、`llms.txt` 与 GEO 验证能力，不额外改动：

- 首页主视觉与正文结构
- 分类页文案
- 详情页正文文案
- 新增信任页
- 新增答案型内容页

## 风险说明

### 1. 不要伪造搜索功能

若站内没有真实搜索，不应添加 `SearchAction`。

### 2. 不要给 `noindex` 历史别名页补详情 schema

这类页面应继续保留为别名跳转或历史承接用途，避免制造冲突信号。

### 3. 后续若重渲染详情页，必须保留 schema 输出

任何新的详情页生成脚本，都应继续复用当前的 schema 生成逻辑。
