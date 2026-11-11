# 本地产物和验收

推荐兼容现有流水线的结构；换实现仍保留这些逻辑关系。

- manifest.json：真实场次、边界依据、源文件清单与解码时长；内部id和当天ordinal分开。
- source-quality.json：每个问题的file_id/kind/evidence/handling。
- chunks.json：当前唯一计划；chunk_id/file_id/core_start/core_end/audio_start/audio_end/audio路径及累计偏移。更改前备份。
- raw/：原始响应含请求偏移与耗时；candidates/：明确unreviewed_candidates。
- transcript.segments.json：稳定segment_id、chunk_id、file_id、file_start/end、原文、局部speaker、原响应。
- review.json：reviewed_chunks映射；每块decision/notes/approved_corrections。批准改词具1基segment/before/after/reason；原文不覆盖。
- transcript.corrected.segments.json、corrections.json：仅应用批准修改，保留原文和核验方式。
- discussion-index.json：时间单元+多主题链接，可保留所有段；问答/论证组可关联多个段，不以一个ASR段天然等于一个完整论证。
- topics.json、claims.json、evidence.json：不连续主题、具体采用主张、条件与反对、原文位置和原句。章级证据索引便于查找，但不声称每段都逐句绑定；精细主张需更细证据。
- knowledge-summary.md：单场完整知识文档；quality-report.md与boundary-review.json说明覆盖/异常/边界；delivery-validation.json记录结构检查，非准确率认证。
- published.json：仅在实际发布验收后记录commit/部署run/公开链接/核验正文和CTA。

## 最终版本一致性

遗漏审计至少记录 `schema_version`、`article_sha256`、`review_method`、`audio_audition`、`candidate_status`、有用条目去向/待确认及未解决问题。新场优先使用统一字段；旧场允许通过显式映射读取knowledge-v3子目录、tool-ledger等旧名称，不为统一文件名重跑ASR。

`article_sha256`计算公开content正文的精确UTF-8字节；审计后又修改正文，即使只改标题/删附录，也应记录改动及核查范围并重新绑定版本。不能仅把旧哈希换成新值就宣称全审；语义改动须回原文，纯排版改动需检查差异。published中的正文哈希与当前审计版本相同，部署后另保存实际GET页面哈希；两者用途不同。

旧审计中的待补项已完成时，记录解决位置与核查证据；未明确解决的仍保留。章级来源组不等于逐句主张认证，工具存在/原文明确命名/官方仓库与许可已核验也分别记状态。

跨已发布文章做结构与记录检查，可运行 `python3 .agents/skills/qizhi-ai-distill/scripts/audit_published.py /absolute/project`。只读脚本检查文章、审核集合、旧版台账位置与哈希绑定；警告不是语义遗漏判定，执行通过也不证明音频识别准确或知识零遗漏。

检查：当前chunks与review集合完全对应；所有成功raw存在、非空、未截断；每个有音频文件核心从0连续到解码总时长；源质量问题逐项披露；批准改词精确匹配；每处采用证据源存在且已审、时间正确；候选未直接混入；恢复边界人工文本核对。无声/不可解码源留记录而不造chunk。

公开版只含审过的一篇正文及显式白名单条目，内部路径/凭证/手机号/原始音视频/逐字稿不公开。检查构建结果、内部链接、来源说明、日期和CTA；推送后等待Pages等部署成功，再实际GET文章和首页检查新正文，不只HEAD或远程commit。单个客户端的拒绝响应不等于页面宕机；核实际响应与正文内容。

## 已审来源映射的自动校验

本项目可用 `scripts/finalize_reviewed_session.py --output 显式场次目录 --article 本地定稿` 从已审核的chapter-sources生成主张/主题/讨论索引；该工具不执行审核、不调用模型、不发布。要求计划与全读review精确一致、每条1基raw位置真实存在，区分被合并过滤的请求上下文来源与保留的合并段；纯弹幕章节可用已全文审核的 `event_ids` 独立作为证据，`source_ids` 留空，不可借不相关口述凑引用。混合章节分别保留音频和弹幕证据；弹幕ID、原句与全文阅读覆盖必须核验。两种证据都没有的章节拒绝生成。章级引用仍不代表逐句核验。生成后继续validate_delivery及独立遗漏/语义复核。
