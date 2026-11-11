# 知识笔记

公开知识库：<https://hilex.me/>。

从 AI 应用、工程实践与讨论中积累可复用的知识。下载作者开发的 [Helix 安卓客户端](https://github.com/dollarser/helix-agent/releases)。

## 发布文章

1. 在 `content/` 编写 Markdown，说明结论、条件、证据、不同意见和未解决问题。
2. 完成内容校订与公开范围检查后，在 `articles.json` 显式加入元数据，设置 `reviewed: true` 并填写 `source`。
3. 本地运行 `pip install -r requirements.txt` 和 `python scripts/build.py`，预览 `dist/`。
4. 推送 `main` 后由 GitHub Actions 部署 Pages。项目沿用用户博客域名，不设置独立 CNAME。

只发布清单中明确选中的文章；原视频、录音、原始逐字稿、用户数据与内部审核材料保留在本地工作区，不放入这个公开仓库。AI 候选稿不能直接发布，不能将案例、推测或营销表达改写成已验证事实。公开正文保留日期、事实条件和证据边界；原文定位、来源映射与审核记录保留在本地，不附公开来源定位。

已复核直播知识通过 articles.json 发布。编辑合篇可包含话题连贯的停播前后录制，但不据此认证连续开播；旧地址通过 redirects.json 兼容。未完成复核的内容不加入发布清单。

## 知识蒸馏 Skill

`skills/` 是蒸馏规则的唯一维护源，包含企智 AI 与产品老曾两套 Skill、共用审核规则、实体事实与经验卡数据及生成脚本。实体事实维护 JSON，Markdown 检索视图由对应脚本生成，不维护重复快照。

在 Codex、Antigravity 等工具中直接加载对应的 `skills/<名称>/SKILL.md`。本地 Distillation 项目的 `.agents/skills` 通过符号链接指向本目录；录制、原始转写、审核证据、任务队列和运行配置仍由本地项目管理，不随 Skill 上传。Skill 提到的 `WORK_STATE.md`、队列和 `docs/distillation-runtime.md` 均指执行项目中的文件。

检查生成视图：

```sh
python3 skills/qizhi-ai-distill/scripts/render_reference_views.py --check
python3 skills/laozeng-workplace-distill/scripts/render_workplace_cards.py --check
```

第二条同时核对本仓库的职场经验手册正文；未加 `--check` 时会重新生成，修改前应先确认相关原文与本地审核记录。
