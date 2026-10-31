#!/usr/bin/env python3
import json,re,html,shutil
from pathlib import Path
import markdown
from markdown.extensions.toc import slugify_unicode
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist';BASE='/knowledge/';URL='https://blog.sunlingzhang.com/knowledge/';DOWNLOAD='https://github.com/dollarser/helix-agent/releases'
def e(x):return html.escape(str(x),quote=True)
def article_order(article):
 # Use the livestream date and numeric daily session, independent of insertion order.
 session=re.search(r'第(\d+)场',article['title'])
 return (article['date'],int(session.group(1)) if session else 0,article['slug'])
def shell(title,description,body,path='',search=False):
 return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)} · 知识笔记</title><meta name="description" content="{e(description)}"><link rel="canonical" href="{URL}{path}"><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%23172c38'/%3E%3Ctext x='50' y='69' text-anchor='middle' font-size='65' fill='%23fffefa'%3E知%3C/text%3E%3C/svg%3E"><link rel="stylesheet" href="{BASE}assets/site.css"></head><body><header><nav class="wrap" aria-label="主导航"><a class="brand" href="{BASE}">知识笔记<small>NOTES INTO PRACTICE</small></a><div class="links"><a href="{BASE}index/">全部知识索引</a><a href="{BASE}reading/">专题阅读</a><a href="https://blog.sunlingzhang.com/">返回博客</a><a href="https://github.com/dollarser/knowledge">GitHub</a><a class="cta" href="{DOWNLOAD}" target="_blank" rel="noopener noreferrer">下载 Helix 安卓客户端 ↗</a></div></nav></header><main class="wrap">{body}</main><footer class="wrap">持续积累，保留依据。AI 辅助整理，发布前校订。 · <a href="{BASE}index/">全部知识索引</a> · <a href="https://github.com/dollarser/knowledge/issues">反馈与纠错</a></footer>{f'<script src="{BASE}assets/search.js" defer></script>' if search else ''}</body></html>'''
def platform():return f'''<aside class="platform" aria-label="Helix 安卓客户端下载"><div><span class="eyebrow">FROM NOTES TO PRACTICE</span><h2>把想法带到安卓上实践</h2><p>体验作者开发的 Helix 安卓客户端，在发布页选择版本下载。</p></div><a class="cta" href="{DOWNLOAD}" target="_blank" rel="noopener noreferrer">下载 Helix 安卓客户端 ↗</a></aside>'''
def write(path,text):
 p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def reading_page(articles):
 by_slug={a['slug']:a for a in articles}
 data=json.loads((ROOT/'reading-paths.json').read_text())
 sections=[];jumps=[];covered=set();ids=set()
 for topic in data['topics']:
  key=topic['id'];assert re.fullmatch('[a-z0-9-]+',key) and key not in ids;ids.add(key)
  jumps.append(f'<a href="#{e(key)}">{e(topic["title"])}</a>')
  entries=[];seen=set()
  for entry in sorted(topic['articles'],key=lambda item:article_order(by_slug[item['slug']]),reverse=True):
   slug=entry['slug'];assert slug in by_slug and slug not in seen;seen.add(slug);covered.add(slug)
   a=by_slug[slug];assert entry['note'].strip()
   entries.append(f'<li><a href="{BASE}notes/{slug}/">{e(a["title"])}</a><p>{e(entry["note"])}</p></li>')
  sections.append(f'<section class="reading-section" id="{e(key)}"><h2>{e(topic["title"])}</h2><p>{e(topic["description"])}</p><ul class="reading-list">{"".join(entries)}</ul></section>')
 assert covered==set(by_slug),'Every reviewed article needs a reading path'
 cases=[]
 case_file=ROOT/'case-followups.json'
 if case_file.exists():
  for case in json.loads(case_file.read_text())['cases']:
   stages=[]
   for stage in case['stages']:
    a=by_slug[stage['slug']]
    stages.append(f'<li><a href="{BASE}notes/{a["slug"]}/">{e(a["title"])}</a><p>{e(stage["summary"])}</p></li>')
   cases.append(f'<section class="case-entry"><h3>{e(case["title"])}</h3><p>{e(case["summary"])}</p><ol class="reading-list">{"".join(stages)}</ol></section>')
 followups=f'<section class="reading-section" id="case-followups"><h2>同一案例的前后讨论</h2>{"".join(cases)}</section>' if cases else ''
 body=f'<section class="index-page reading-page"><a class="back" href="{BASE}index/">← 全部知识索引</a><h1>专题阅读</h1><p class="lead">按手头的问题找经验，再进入完整文章阅读具体做法。</p><div class="reading-jumps" aria-label="专题目录">{"".join(jumps)}</div>{"".join(sections)}{followups}</section>{platform()}'
 write('reading/index.html',shell('专题阅读','按获客运营、收费交付、工具提效与创业复盘查找完整直播知识。',body,'reading/'))
def main():
 articles=sorted(json.loads((ROOT/'articles.json').read_text()),key=article_order,reverse=True);slugs=set()
 for a in articles:
  assert re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',a['slug']) and a['slug'] not in slugs
  assert a['reviewed'] is True,'Only explicitly reviewed articles can be published'
  assert a['source'].strip(),'Source disclosure required';slugs.add(a['slug'])
  source=ROOT/'content'/f"{a['slug']}.md";assert source.is_file()
  text=source.read_text()
  assert not any(x in text for x in ['/Users/','127.0.0.1','localhost:','speaker_id','transcription.raw','sk-proj-']),f'Private artifact in {source.name}'
 if OUT.exists():shutil.rmtree(OUT)
 OUT.mkdir();shutil.copytree(ROOT/'assets',OUT/'assets');write('.nojekyll','')
 cards=[];index_entries=[];categories=sorted({a['category'] for a in articles})
 for a in articles:
  path=f"notes/{a['slug']}/";tags=''.join(f'<span class="pill">{e(t)}</span>' for t in a['tags']);search=' '.join([a['title'],a['description'],a['category'],*a['tags']]).lower()
  cards.append(f'''<article class="card" data-card data-category="{e(a['category'])}" data-search="{e(search)}"><div class="meta">{e(a['category'])} · {e(a['date'])}</div><h2><a href="{BASE}{path}">{e(a['title'])}</a></h2><p>{e(a['description'])}</p><div>{tags}</div><a class="read" href="{BASE}{path}">阅读笔记 →</a></article>''')
  source_text=(ROOT/'content'/f"{a['slug']}.md").read_text()
  # The page shell owns the title; render the body once, with stable chapter anchors.
  source_text=re.sub(r'\A# [^\n]+\n', '', source_text, count=1)
  md=markdown.Markdown(extensions=['tables','fenced_code','toc'],extension_configs={'toc':{'slugify':slugify_unicode,'toc_depth':'2'}})
  prose=md.convert(source_text)
  prose=re.sub(r'(<table>.*?</table>)',r'<div class="table-scroll">\1</div>',prose,flags=re.S)
  index_entries.append((a,f'''<article class="index-entry" data-card><h2><a href="{BASE}{path}">{e(a['title'])}</a></h2><p>{e(a['description'])}</p></article>'''))
  body=f'''<article class="article"><a class="back" href="{BASE}">← 全部知识笔记</a><p class="eyebrow">{e(a['category'])} / {e(a['date'])}</p><h1>{e(a['title'])}</h1><p class="lead">{e(a['description'])}</p><div>{tags}</div><div class="prose">{prose}</div>{platform()}</article>'''
  write(path+'index.html',shell(a['title'],a['description'],body,path))
 buttons=''.join(f'<button type="button" data-filter="{e(c)}" aria-pressed="{str(c=="全部").lower()}">{e(c)}</button>' for c in ['全部',*categories])
 body=f'''<section class="hero"><div><span class="eyebrow">A GROWING KNOWLEDGE GARDEN</span><h1>把讨论里的洞见，<br>留下来，接着用。</h1><p class="intro">从 AI 应用、工程实践到商业讨论。围绕具体问题整理知识，让每个结论都带着条件、分歧与来源。</p></div><div class="aside"><strong>按主题积累，回到原文核对。</strong>按直播或连贯讨论整理知识文档。按主题分章，留下完整案例、操作过程、工具用法与经营经验。</div></section><section aria-label="知识笔记"><div class="toolbar"><div class="filters" aria-label="分类筛选">{buttons}</div><label><span class="meta">搜索笔记 </span><input id="search" type="search" placeholder="搜索标题、主题或标签" aria-label="搜索知识笔记"></label></div><div class="section-label"><span>知识笔记 / KNOWLEDGE NOTES</span><span id="count" aria-live="polite">{len(articles)} 篇笔记</span></div><div class="grid">{''.join(cards)}</div><p class="empty" id="empty" hidden>没有找到匹配的笔记，试试其他关键词。</p></section>{platform()}'''
 write('index.html',shell('把讨论里的洞见留下来','持续积累 AI 应用、工程实践与商业讨论中的知识，保留条件、分歧与来源。',body,search=True))
 index_body=f'''<section class="index-page"><h1>全部知识索引</h1><div class="index-list">{''.join(item for _,item in index_entries)}</div></section>{platform()}'''
 write('index/index.html',shell('全部知识索引','所有已发布知识文档的链接与简短摘要。',index_body,'index/'))
 reading_page(articles)
 redirects=json.loads((ROOT/'redirects.json').read_text()) if (ROOT/'redirects.json').exists() else {}
 for old,new in redirects.items():
  assert re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',old) and old not in slugs
  assert new in slugs,'Redirect target must be a reviewed article'
  route=f'notes/{new}/'
  target=f'{BASE}{route}';canonical=f'{URL}{route}'
  label='完整知识文档'
  write(f'notes/{old}/index.html',f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0;url={e(target)}"><link rel="canonical" href="{e(canonical)}"><title>{label}</title></head><body><p>请前往<a href="{e(target)}">{label}</a>。</p></body></html>')
 write('404.html',shell('页面未找到','请回到知识库查找笔记。',f'<section class="article"><h1>这篇笔记还没有找到</h1><p><a class="cta" href="{BASE}">回到知识库</a></p></section>'))
 write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{URL}{p}</loc></url>' for p in ['','index/','reading/',*[f"notes/{a['slug']}/" for a in articles]])+'</urlset>')
 print(f'Built {len(articles)} reviewed articles at {OUT}')
if __name__=='__main__':main()
