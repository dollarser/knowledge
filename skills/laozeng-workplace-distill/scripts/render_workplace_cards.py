#!/usr/bin/env python3
"""Render reviewed cards and the skill index from one source. No inference."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = Path(__file__).resolve().parents[1]


def render(data):
    assert data['schema_version'] == 2
    cards = data['cards']
    assert sorted(c['id'] for c in cards) == list(range(1, 58))
    by_id = {c['id']: c for c in cards}
    groups = data['topics']
    assert sorted(i for g in groups for i in g['card_ids']) == list(range(1, 58))
    out = [data['introduction'], '## 按问题找经验', '']
    for g in groups:
        out.append(f"- [{g['title']}](#meta-{g['id']})：" + '、'.join(str(i) for i in g['card_ids']))
    out += ['', '## 57张卡速查', '', '| 编号 | 经验卡 | 关联案例 |', '| --- | --- | --- |']
    for c in sorted(cards, key=lambda c: c['id']):
        out.append(f"| {c['id']} | [{c['title']}](#model-{c['id']}) | [完整讨论](/knowledge/notes/{c['source_article']}/) |")
    for g in groups:
        out += ['', f"## <a id=\"meta-{g['id']}\"></a>{g['title']}", '', g['description']]
        for i in g['card_ids']:
            c = by_id[i]
            assert c['bodyMarkdown'].strip() and c['source_article']
            out += ['', f"### <a id=\"model-{i}\"></a>{i}. {c['title']}", '', c['bodyMarkdown'].strip(), '',
                    f"[阅读关联案例](/knowledge/notes/{c['source_article']}/)"]
    out += ['', '## 怎样使用这些经验', '', '先看卡片解决什么问题，再进入关联文章了解当时的人物、权责和业务处境。相似案例可以一起比较；已有动作、讨论中的建议和后续结果要分开理解。', '']
    index = ['# 职场经验卡检索索引', '', '> 自动生成；仅维护 workplace-lexicon.json，再运行 scripts/render_workplace_cards.py。', '',
             '这里是已回源卡片的检索入口，不保存另一套脱离案例的模型结论。观点和建议回到卡片及关联案例阅读；不把旧模型名称当事实证据。', '',
             '| 编号 | 经验卡 | 原讨论 |', '| --- | --- | --- |']
    for c in sorted(cards, key=lambda c: c['id']):
        index.append(f"| {c['id']} | [{c['title']}](https://blog.sunlingzhang.com/knowledge/notes/laozeng-workplace-codex/#model-{c['id']}) | [{c['source_article']}](https://blog.sunlingzhang.com/knowledge/notes/{c['source_article']}/) |")
    return '\n'.join(out), '\n'.join(index) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = json.loads((SKILL / 'references/workplace-lexicon.json').read_text())
    article, index = render(data)
    for path, value in [(ROOT / 'content/laozeng-workplace-codex.md', article),
                        (SKILL / 'references/workplace-lexicon.md', index)]:
        if args.check:
            assert path.read_text() == value, f'Generated file drift: {path}'
        else:
            path.write_text(value)
    print('Reviewed 57-card article and skill index: ' + ('exact' if args.check else 'generated'))


if __name__ == '__main__':
    main()
