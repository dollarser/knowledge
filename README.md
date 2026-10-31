# 知识笔记

公开知识库：<https://blog.sunlingzhang.com/knowledge/>。

从 AI 应用、工程实践与讨论中积累可复用的知识。下载作者开发的 [Helix 安卓客户端](https://github.com/dollarser/helix-agent/releases)。

## 发布文章

1. 在 `content/` 编写 Markdown，说明结论、条件、证据、不同意见和未解决问题。
2. 完成内容校订与公开范围检查后，在 `articles.json` 显式加入元数据，设置 `reviewed: true` 并填写 `source`。
3. 本地运行 `pip install -r requirements.txt` 和 `python scripts/build.py`，预览 `dist/`。
4. 推送 `main` 后由 GitHub Actions 部署 Pages。项目沿用用户博客域名，不设置独立 CNAME。

只发布清单中明确选中的文章；原视频、录音、原始逐字稿、用户数据与内部审核材料保留在本地工作区，不放入这个公开仓库。AI 候选稿不能直接发布，不能将案例、推测或营销表达改写成已验证事实。公开正文保留日期、事实条件和证据边界；原文定位、来源映射与审核记录保留在本地，不附公开来源定位。

已复核直播知识通过 articles.json 发布。编辑合篇可包含话题连贯的停播前后录制，但不据此认证连续开播；旧地址通过 redirects.json 兼容。未完成复核的内容不加入发布清单。
