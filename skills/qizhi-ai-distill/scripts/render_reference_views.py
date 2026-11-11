#!/usr/bin/env python3
"""Generate the two JSON-backed reference views; no exported Skill copies.
Run from any cwd. --check is read-only and exits nonzero on drift.
"""
import argparse
import json
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
PROJECT = SKILL.parents[1]

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def cell(value):
    return str(value or '').replace('|', '\\|').replace('\n', '<br>')

def views():
    facts = load(SKILL / 'references/model-facts.json')
    lexicon = load(SKILL / 'references/terminology-lexicon.json')
    entities = facts['models'] + facts.get('other_entities', [])
    ids = [e['id'] for e in entities]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate fact entity IDs')
    text = ['# 模型与工具事实调研视图', '',
            '> 自动生成；仅编辑 model-facts.json，随后运行 scripts/render_reference_views.py。', '',
            '保留用户确认来自官方调研的既有内容；本次迁移不重新认证产品参数。缺失原调研链接标为待补，不虚构出处。使用时核录制日期、具体版本与适用范围，不将背景事实当成模糊口述的身份确认。', '']
    for e in entities:
        text += ['## ' + e['name'], '', '- ID：`' + e['id'] + '`',
                 '- 调研时间：' + str(e.get('last_research_at') or '待补'),
                 '- 来源记录：' + e.get('source_attachment_status', '见官方来源'), '']
        for k, v in e.get('research_assertions', {}).items():
            if v:
                text += ['- ' + k + '：' + str(v)]
        for source in e.get('official_sources', []):
            text += ['- 官方来源：' + json.dumps(source, ensure_ascii=False)]
        text += ['']
    for field in ['legacy_research_notes', 'prior_research_excerpt']:
        if facts.get(field):
            text += ['## 迁移调研记录：' + field, '',
                     facts[field] if isinstance(facts[field], str) else json.dumps(facts[field], ensure_ascii=False, indent=2), '']
    terms = ['# 转写近音词与名称候选', '',
             '> 自动生成；仅编辑 terminology-lexicon.json，随后运行 scripts/render_reference_views.py。', '',
             '本表只提示候选，不能自动替换。逐处读原文及上下文、核依据、显式批准review后重新渲染校订产物。产品事实与调研出处见 [model-facts.md](model-facts.md)，不在词典重复维护。', '',
             '| 候选名称 | 原词/音译 | 事实引用 |', '| --- | --- | --- |']
    for e in lexicon['entries']:
        if e.get('auto_apply') is not False or not e.get('context_required'):
            raise ValueError('Candidate must prohibit automatic application: ' + e['id'])
        ref = e['facts_ref']
        if ref['file'] != 'model-facts.json' or ref['entity_id'] not in ids:
            raise ValueError('Unknown fact reference: ' + e['id'])
        terms += ['| ' + cell(e['standard']) + ' | ' + cell(', '.join(e['misnomers'])) + ' | `' + ref['entity_id'] + '` |']
    terms += ['', '不得仅因不熟悉新型号就改成旧型号；也不得仅因已知产品存在就强配同音词。数字、版本和通用英文单词尤其需要当场证据。', '背景解释和延伸建议只进入正文及台账，不回写为参与者原话。', '']
    return {'references/model-facts.md': ('\n'.join(text) + '\n').encode(),
            'references/terminology-lexicon.md': '\n'.join(terms).encode()}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = views()
    outputs = {SKILL / rel: data for rel, data in generated.items()}
    drift = [str(path.relative_to(PROJECT)) for path, data in outputs.items()
             if not path.exists() or path.read_bytes() != data]
    if args.check:
        if drift:
            print(json.dumps({'status': 'drift', 'paths': drift}, ensure_ascii=False, indent=2))
            return 1
    else:
        for path, data in outputs.items():
            if not path.exists() or path.read_bytes() != data:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
    print(json.dumps({'status': 'passed', 'mode': 'check' if args.check else 'generate',
                      'generated_views': len(generated),
                      'changed_outputs': 0 if args.check else len(drift)}, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
