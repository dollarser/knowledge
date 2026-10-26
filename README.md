# 知识笔记

公开知识库：<https://blog.sunlingzhang.com/knowledge/>。

从 AI 应用、工程实践与讨论中积累可复用的知识。下载作者开发的 [Helix 安卓客户端](https://github.com/dollarser/helix-agent/releases)。

## 发布文章

1. 在 `content/` 编写 Markdown，说明结论、条件、证据、不同意见和未解决问题。
2. 完成内容校订与公开范围检查后，在 `articles.json` 显式加入元数据，设置 `reviewed: true` 并填写 `source`。
3. 本地运行 `pip install -r requirements.txt` 和 `python scripts/build.py`，预览 `dist/`。
4. 推送 `main` 后由 GitHub Actions 部署 Pages。项目沿用用户博客域名，不设置独立 CNAME。

只发布清单中明确选中的文章；原视频、录音、原始逐字稿、用户数据与内部审核材料保留在本地工作区，不放入这个公开仓库。AI 候选稿不能直接发布，不能将案例、推测或营销表达改写成已验证事实。引用原讨论时保留日期、来源、时间定位与证据边界。

目前上线知识整理方法和阅读指南；直播笔记将在复核后加入，不将未完成场次包装成完整总结。
