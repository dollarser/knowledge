#!/usr/bin/env python3
"""Build static multi-channel knowledge website with independent channel addresses."""
import html
import json
import re
import shutil
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
BASE = '/knowledge/'
SITE_URL = 'https://blog.sunlingzhang.com/knowledge/'
DOWNLOAD = 'https://github.com/dollarser/helix-agent/releases'

CHANNELS = {
    'qizhi': {
        'id': 'qizhi',
        'category': '企智AI落地',
        'name': '企智AI落地派',
        'eyebrow': 'CHANNEL 01 / AI DELIVERY & BUSINESS',
        'icon': '🏢',
        'color': '#0e7490',
        'tagline': '实战交付与商业经营',
        'desc': '面向大模型选型微调、AI自动化工作流、企业真实接单交付、算力配置与获客经营的全息知识库。',
        'hero_title': '把AI落地讨论里的洞见，<br>留下来，接着用。',
        'hero_lead': '不讲空洞概念，只记录企业自动化、垂直Agent、私有化部署与获客交付的真实算账与踩坑经验。',
        'aside_title': '重在工程闭环与客户交付。',
        'aside_desc': '按每场连麦与技术讨论整理文档。留下真实案例、报价区间、提示词工作流与客户谈判底牌。'
    },
    'laozeng': {
        'id': 'laozeng',
        'category': '老曾职场博弈',
        'name': '产品老曾',
        'eyebrow': 'CHANNEL 02 / WORKPLACE POWER DYNAMICS',
        'icon': '♟️',
        'color': '#6d28d9',
        'tagline': '职场升迁与组织博弈全景',
        'desc': '从具体连麦案例理解大厂总监晋升、空降速胜、骨干跃迁、薪酬期权分水与组织政治博弈实战心法。',
        'hero_title': '职场组织博弈全景，<br>看懂身位、筹码与利益分水。',
        'hero_lead': '还原产品老曾数十场职场连麦：高管更迭站位、总监破局速胜、受气包身位转嫁与人机协同组织突围。',
        'aside_title': '以身位定动作，以筹码谋利益。',
        'aside_desc': '不谈空泛鸡汤，深度复盘大厂政治、汇报话术、向上管理与职场关键跃迁节点的决策底牌。'
    },
    'wangcen': {
        'id': 'wangcen',
        'category': '王岑消费投资',
        'name': '王岑消费投资',
        'eyebrow': 'CHANNEL 03 / CONSUMER INVESTMENT & CAPITAL',
        'icon': '🛍️',
        'color': '#c2410c',
        'tagline': '消费投行算账与连锁单店法则',
        'desc': '中国早期消费投资教父王岑抖音直播全息蒸馏：单店财务心算、加盟模式穿透、逆周期轻资产与资本股权真相。',
        'hero_title': '消费投行深度算账，<br>穿透单店模型与资本真相。',
        'hero_lead': '二十余年消费投资实战：穿透加盟流水泡沫、死守单店保本红线、防范早期股权掠夺、在存量周期中做透现金流。',
        'aside_title': '算透每一分账，守住现金流。',
        'aside_desc': '聚焦万店供应链虚胖脱水、文旅轻资产套利、下沉市场地推与拒绝盲目打低价价格战的投资哲学。'
    }
}

CAT_TO_CHANNEL = {c['category']: cid for cid, c in CHANNELS.items()}

def e(x):
    return html.escape(str(x), quote=True)

def article_order(article):
    session = re.search(r'第(\d+)场', article['title'])
    return (article['date'], int(session.group(1)) if session else 0, article['slug'])

def write(path, text):
    p = OUT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')

def platform():
    return f'''<aside class="platform" aria-label="相关开源工具"><div><span class="meta">相关工程实践</span><p>作者自研移动端实验工具：<a class="platform-helix" style="color:#ea580c;font-weight:700;text-decoration:underline;" href="{DOWNLOAD}" target="_blank" rel="noopener noreferrer">Helix 开源项目 ↗</a></p></div></aside>'''

def shell(title, description, body, rel_path='', search=False, has_mermaid=False, channel=None):
    canonical = f"{SITE_URL}{rel_path}"
    
    # Navigation Links
    if channel:
        c = CHANNELS[channel]
        brand_html = f'''<a class="brand" href="{BASE}{c['id']}/">{c['name']}<small>{c['tagline'].upper()}</small></a>'''
        
        switch_items = []
        for cid, info in CHANNELS.items():
            act = ' active' if cid == channel else ''
            switch_items.append(f'''<a class="{act}" href="{BASE}{cid}/">{info['icon']} {info['name']}</a>''')
        
        links_html = f'''
        <div class="channel-switch" title="切换不同直播间专栏">{"".join(switch_items)}</div>
        <a href="{BASE}{c['id']}/index/">本专栏索引</a>
        <a href="{BASE}{c['id']}/reading/">专题阅读</a>
        <a href="{BASE}" style="color:var(--muted);font-weight:600;">知识库主站</a>
        <a href="https://blog.sunlingzhang.com/">返回博客</a>
        <a class="nav-helix" href="{DOWNLOAD}" target="_blank" rel="noopener noreferrer">Helix 移动端 ↗</a>
        '''
        footer_links = f'''<a href="{BASE}{c['id']}/index/">{c['name']}索引</a> · <a href="{BASE}">知识库主站</a> · <a href="https://blog.sunlingzhang.com/">博客主页</a> · <a href="https://github.com/dollarser/knowledge/issues">反馈与纠错</a>'''
    else:
        brand_html = f'''<a class="brand" href="{BASE}">知识笔记<small>NOTES INTO PRACTICE</small></a>'''
        links_html = f'''
        <a href="{BASE}qizhi/">🏢 企智AI</a>
        <a href="{BASE}laozeng/">♟️ 老曾职场</a>
        <a href="{BASE}wangcen/">🛍️ 王岑投资</a>
        <a href="{BASE}index/">全站索引</a>
        <a href="{BASE}reading/">全部专题</a>
        <a href="https://blog.sunlingzhang.com/">返回博客</a>
        <a class="nav-helix" href="{DOWNLOAD}" target="_blank" rel="noopener noreferrer">Helix 移动端 ↗</a>
        '''
        footer_links = f'''<a href="{BASE}index/">全站索引</a> · <a href="{BASE}reading/">全部专题</a> · <a href="https://blog.sunlingzhang.com/">博客主页</a> · <a href="https://github.com/dollarser/knowledge/issues">反馈与纠错</a>'''

    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)} · 知识笔记</title><meta name="description" content="{e(description)}"><link rel="canonical" href="{canonical}"><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%23172c38'/%3E%3Ctext x='50' y='69' text-anchor='middle' font-size='65' fill='%23fffefa'%3E知%3C/text%3E%3C/svg%3E"><link rel="stylesheet" href="{BASE}assets/site.css?v=20261107"></head><body><header><nav class="wrap" aria-label="主导航">{brand_html}<div class="links">{links_html}</div></nav></header><main class="wrap">{body}</main><footer class="wrap">持续积累，保留依据。AI 辅助整理，发布前校订。 · {footer_links}</footer>{f'<script src="{BASE}assets/search.js" defer></script>' if search else ''}{'<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";mermaid.initialize({startOnLoad:true,theme:"neutral",securityLevel:"loose",flowchart:{htmlLabels:true,curve:"basis"}});</script>' if has_mermaid else ''}</body></html>'''

def render_article_prose(source_path: Path):
    source_text = source_path.read_text(encoding='utf-8')
    assert not any(x in source_text for x in ['/Users/', '127.0.0.1', 'localhost:', 'speaker_id', 'transcription.raw', 'sk-proj-']), f'Private artifact in {source_path.name}'
    
    source_text = re.sub(r'\A---\n.*?\n---\s*', '', source_text, flags=re.S)
    source_text = re.sub(r'\A# [^\n]+\n', '', source_text, count=1)
    source_text = re.sub(r'([^\n\s])\n([-*] |\d+\. )', r'\1\n\n\2', source_text)
    
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'], extension_configs={'toc': {'slugify': slugify_unicode, 'toc_depth': '2'}})
    prose = md.convert(source_text)
    prose = re.sub(r'(<table>.*?</table>)', r'<div class="table-scroll">\1</div>', prose, flags=re.S)
    prose = re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>', lambda m: f'<pre class="mermaid">{html.unescape(m.group(1)).strip()}</pre>', prose, flags=re.S)
    has_mermaid = '<pre class="mermaid">' in prose
    return prose, has_mermaid

def build_channel_reading(channel_id: str, channel_articles, all_articles_map, reading_data):
    c = CHANNELS[channel_id]
    by_slug = {a['slug']: a for a in channel_articles}
    
    # filter topics for this channel
    if channel_id == 'qizhi':
        topics = [t for t in reading_data['topics'] if not t['id'].startswith('laozeng-') and not t['id'].startswith('wangcen-')]
    elif channel_id == 'laozeng':
        topics = [t for t in reading_data['topics'] if t['id'].startswith('laozeng-')]
    else:
        topics = [t for t in reading_data['topics'] if t['id'].startswith('wangcen-')]

    sections = []
    jumps = []
    covered = set()
    
    for topic in topics:
        key = topic['id']
        jumps.append(f'<a href="#{e(key)}">{e(topic["title"])}</a>')
        entries = []
        for entry in sorted(topic['articles'], key=lambda item: article_order(all_articles_map[item['slug']]), reverse=True):
            slug = entry['slug']
            if slug not in by_slug:
                continue
            covered.add(slug)
            a = by_slug[slug]
            entries.append(f'<li><a href="{BASE}{channel_id}/notes/{slug}/">{e(a["title"])}</a><p>{e(entry["note"])}</p></li>')
        sections.append(f'<section class="reading-section" id="{e(key)}"><h2>{e(topic["title"])}</h2><p>{e(topic["description"])}</p><ul class="reading-list">{"".join(entries)}</ul></section>')

    # cases for qizhi only
    followups = ''
    if channel_id == 'qizhi':
        case_file = ROOT / 'case-followups.json'
        if case_file.exists():
            cases = []
            for case in json.loads(case_file.read_text(encoding='utf-8'))['cases']:
                stages = []
                for stage in case['stages']:
                    if stage['slug'] in by_slug:
                        a = by_slug[stage['slug']]
                        stages.append(f'<li><a href="{BASE}{channel_id}/notes/{a["slug"]}/">{e(a["title"])}</a><p>{e(stage["summary"])}</p></li>')
                if stages:
                    cases.append(f'<section class="case-entry"><h3>{e(case["title"])}</h3><p>{e(case["summary"])}</p><ol class="reading-list">{"".join(stages)}</ol></section>')
            if cases:
                followups = f'<section class="reading-section" id="case-followups"><h2>同一案例的前后讨论跟踪</h2>{"".join(cases)}</section>'

    jumps_html = f'<div class="reading-jumps" style="margin:20px 0 30px;">{"".join(jumps)}</div>'
    body = f'''<section class="index-page reading-page"><a class="back" href="{BASE}{channel_id}/">← 返回{c["name"]}专栏首页</a><p class="eyebrow">{c["eyebrow"]}</p><h1>{c["name"]} · 专题阅读</h1><p class="lead">{c["desc"]}</p>{jumps_html}{"".join(sections)}{followups}</section>{platform()}'''
    write(f'{channel_id}/reading/index.html', shell(f'{c["name"]}专题阅读', c["desc"], body, f'{channel_id}/reading/', channel=channel_id))

def main():
    articles = sorted(json.loads((ROOT / 'articles.json').read_text(encoding='utf-8')), key=article_order, reverse=True)
    all_articles_map = {a['slug']: a for a in articles}
    reading_data = json.loads((ROOT / 'reading-paths.json').read_text(encoding='utf-8'))
    
    # Verification
    slugs = set()
    for a in articles:
        assert re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', a['slug']) and a['slug'] not in slugs
        assert a['reviewed'] is True, 'Only explicitly reviewed articles can be published'
        assert a['source'].strip(), 'Source disclosure required'
        slugs.add(a['slug'])
        source = ROOT / 'content' / f"{a['slug']}.md"
        assert source.is_file(), f"Missing content file: {source}"

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / 'assets', OUT / 'assets')
    write('.nojekyll', '')

    # Group articles by channel
    channel_articles_map = {cid: [] for cid in CHANNELS}
    for a in articles:
        cid = CAT_TO_CHANNEL.get(a['category'])
        assert cid, f"Unknown category: {a['category']} for {a['slug']}"
        channel_articles_map[cid].append(a)

    # 1. Build articles and channel sub-sites
    for cid, cinfo in CHANNELS.items():
        c_arts = channel_articles_map[cid]
        c_cards = []
        c_index_entries = []
        
        for a in c_arts:
            art_path = f"{cid}/notes/{a['slug']}/"
            tags_html = ''.join(f'<span class="pill">{e(t)}</span>' for t in a['tags'])
            search_str = ' '.join([a['title'], a['description'], a['category'], *a['tags']]).lower()
            
            c_cards.append(f'''<article class="card" data-card data-category="{e(a['category'])}" data-search="{e(search_str)}"><div class="meta">{e(a['category'])} · {e(a['date'])}</div><h2><a href="{BASE}{art_path}">{e(a['title'])}</a></h2><p>{e(a['description'])}</p><div>{tags_html}</div><a class="read" href="{BASE}{art_path}">阅读完整笔记 →</a></article>''')
            c_index_entries.append(f'''<article class="index-entry" data-card><h2><a href="{BASE}{art_path}">{e(a['title'])}</a></h2><p>{e(a['description'])}</p><div style="margin-top:6px;"><span class="meta">{e(a['date'])}</span></div></article>''')
            
            # Render individual article page in channel
            prose, has_mermaid = render_article_prose(ROOT / 'content' / f"{a['slug']}.md")
            art_body = f'''<article class="article"><a class="back" href="{BASE}{cid}/">← 返回{cinfo['name']}专栏</a><p class="eyebrow">{cinfo['eyebrow']} · {e(a['date'])}</p><h1>{e(a['title'])}</h1><p class="lead">{e(a['description'])}</p><div>{tags_html}</div><div class="prose">{prose}</div>{platform()}</article>'''
            write(f"{art_path}index.html", shell(a['title'], a['description'], art_body, art_path, has_mermaid=has_mermaid, channel=cid))
            
            # Old URL backward compatibility: /knowledge/notes/{slug}/ -> /knowledge/{cid}/notes/{slug}/
            redirect_target = f"{BASE}{art_path}"
            old_redirect_html = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0;url={e(redirect_target)}"><link rel="canonical" href="{SITE_URL}{art_path}"><title>正在重定向至专属直播间专栏...</title></head><body><p>正在前往专属专栏地址：<a href="{e(redirect_target)}">{e(a['title'])}</a></p></body></html>'''
            write(f"notes/{a['slug']}/index.html", old_redirect_html)

        # Channel Home Page
        c_hero = f'''<section class="hero"><div><span class="eyebrow">{cinfo['eyebrow']}</span><h1>{cinfo['hero_title']}</h1><p class="intro">{cinfo['hero_lead']}</p></div><div class="aside"><strong>{cinfo['aside_title']}</strong>{cinfo['aside_desc']}</div></section>'''
        c_toolbar = f'''<section aria-label="{cinfo['name']}笔记"><div class="toolbar"><div class="filters"><span style="font-weight:700;font-size:14px;color:var(--ink);">{cinfo['icon']} {cinfo['name']} ({len(c_arts)} 篇)</span></div><label><span class="meta">搜索专栏笔记 </span><input id="search" type="search" placeholder="搜索本专栏标题、标签或内容" aria-label="搜索专栏笔记"></label></div><div class="section-label"><span>{cinfo['eyebrow']}</span><span id="count" aria-live="polite">{len(c_arts)} 篇笔记</span></div><div class="grid">{''.join(c_cards)}</div><p class="empty" id="empty" hidden>本专栏未找到匹配的笔记，试试其他关键词。</p></section>{platform()}'''
        write(f"{cid}/index.html", shell(f"{cinfo['name']} · 专栏首页", cinfo['desc'], f"{c_hero}{c_toolbar}", f"{cid}/", search=True, channel=cid))

        # Channel Index Page
        c_index_body = f'''<section class="index-page"><a class="back" href="{BASE}{cid}/">← 返回{cinfo['name']}专栏首页</a><p class="eyebrow">{cinfo['eyebrow']}</p><h1>{cinfo['name']} · 完整知识索引</h1><p class="lead" style="color:var(--muted);margin-bottom:26px;">共收录 {len(c_arts)} 篇完整直播全息研报，按时间倒序归档排列。</p><div class="index-list">{''.join(c_index_entries)}</div></section>{platform()}'''
        write(f"{cid}/index/index.html", shell(f"{cinfo['name']}索引", cinfo['desc'], c_index_body, f"{cid}/index/", channel=cid))

        # Channel Reading Paths Page
        build_channel_reading(cid, c_arts, all_articles_map, reading_data)

    # 2. Build Multi-Channel Portal Hub at root: /knowledge/
    portal_cards = []
    recent_sections = []
    for cid, cinfo in CHANNELS.items():
        c_arts = channel_articles_map[cid]
        recents = c_arts[:3]
        recent_li = ''.join(f'<li><a href="{BASE}{cid}/notes/{a["slug"]}/" style="color:var(--ink);font-weight:600;">{e(a["title"])}</a> <span class="meta" style="font-size:12px;color:var(--muted);">({e(a["date"])})</span></li>' for a in recents)
        
        portal_cards.append(f'''
        <div class="portal-card {cid}">
          <div>
            <div class="channel-badge">{cinfo['icon']} {cinfo['eyebrow'].split(' / ')[0]}</div>
            <h2>{cinfo['name']}</h2>
            <div style="font-size:12px;font-weight:700;color:var(--muted);letter-spacing:1px;margin-bottom:12px;">{cinfo['tagline']}</div>
            <p class="desc">{cinfo['desc']}</p>
          </div>
          <div>
            <div class="stats"><span>收录规模</span><span>{len(c_arts)} 篇长文研报</span></div>
            <a class="enter-btn" href="{BASE}{cid}/">进入专栏主页 →</a>
          </div>
        </div>
        ''')
        
        recent_sections.append(f'''
        <div style="background:var(--card);border:1px solid var(--line);border-radius:8px;padding:24px;margin-bottom:20px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <h3 style="margin:0;font-size:19px;color:var(--ink);">{cinfo['icon']} {cinfo['name']} · 最新笔记</h3>
            <a href="{BASE}{cid}/" style="font-size:13px;color:var(--accent);font-weight:600;">查看全部 {len(c_arts)} 篇 →</a>
          </div>
          <ul style="padding-left:20px;margin:0;line-height:2;">{recent_li}</ul>
        </div>
        ''')

    hub_hero = f'''<section class="hero"><div><span class="eyebrow">KNOWLEDGE REPOSITORY · MULTI-CHANNEL</span><h1>把讨论里的洞见，<br>留下来，接着用。</h1><p class="intro">按照不同的主播与实战领域，严格设立三个完全独立的知识专栏。独立地址归档，专注各自的商业与技术底层。</p></div><div class="aside"><strong>专栏独立归集，杜绝混合混乱。</strong>每个直播间专栏拥有专属网址、专属索引与专题体系，满足垂直深度的学习检索需求。</div></section>'''
    hub_body = f'''
    {hub_hero}
    <section aria-label="直播间知识专栏">
      <div class="section-label"><span>独立直播间专栏 / INDEPENDENT CHANNELS</span><span>3 大垂直专栏 · 共 {len(articles)} 篇笔记</span></div>
      <div class="portal-grid">{''.join(portal_cards)}</div>
      <div class="section-label" style="margin-top:40px;"><span>各专栏最新动态 / LATEST UPDATES</span><span>实时同步</span></div>
      {''.join(recent_sections)}
    </section>
    {platform()}
    '''
    write("index.html", shell("知识笔记 · 专栏总入口", "按照企智AI落地、产品老曾职场博弈、王岑消费投资三大独立专栏，分别归集高价值直播全息蒸馏研报。", hub_body))

    # 3. Global Index Page (/knowledge/index/)
    channel_index_blocks = []
    for cid, cinfo in CHANNELS.items():
        c_arts = channel_articles_map[cid]
        c_links = ''.join(f'''<article class="index-entry"><h2><a href="{BASE}{cid}/notes/{a['slug']}/">{e(a['title'])}</a></h2><p>{e(a['description'])}</p><div style="margin-top:4px;"><span class="meta">{e(a['date'])}</span></div></article>''' for a in c_arts)
        channel_index_blocks.append(f'''
        <details class="index-channel-fold" open style="margin-top:20px;border:1px solid var(--line);border-radius:8px;background:var(--card);overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.03);">
          <summary style="cursor:pointer;padding:20px 24px;list-style:none;display:flex;justify-content:space-between;align-items:center;">
            <div>
              <span class="eyebrow">{cinfo['eyebrow']}</span>
              <h2 style="font-size:22px;margin:4px 0 4px;">{cinfo['icon']} {cinfo['name']}（{len(c_arts)} 篇）</h2>
              <p class="lead" style="margin:0;color:var(--muted);font-size:13px;">{cinfo['desc']}</p>
            </div>
            <span class="fold-pill" style="font-size:13px;padding:6px 14px;border:1px solid var(--line);border-radius:20px;background:var(--paper);font-weight:650;color:var(--ink);flex-shrink:0;margin-left:16px;"></span>
          </summary>
          <div class="index-list" style="padding:0 24px 20px;border-top:1px solid var(--line);">{c_links}</div>
        </details>
        ''')

    global_index_body = f'''<section class="index-page"><div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:12px;"><h1>全部知识索引</h1><div class="index-toggle-all" style="display:flex;gap:10px;"><button type="button" onclick="document.querySelectorAll('.index-channel-fold').forEach(d=>d.open=true)" style="padding:5px 14px;font-size:13px;border-radius:20px;border:1px solid var(--line);background:var(--card);cursor:pointer;color:var(--ink);">全部展开</button><button type="button" onclick="document.querySelectorAll('.index-channel-fold').forEach(d=>d.open=false)" style="padding:5px 14px;font-size:13px;border-radius:20px;border:1px solid var(--line);background:var(--card);cursor:pointer;color:var(--ink);">全部折叠</button></div></div><p class="lead" style="color:var(--muted);margin-bottom:26px;">全站共收录 3 大独立专栏、{len(articles)} 篇完整研报。点击各专栏可折叠查看，点击标题直接直达对应专栏地址。</p>{''.join(channel_index_blocks)}</section>{platform()}'''
    write("index/index.html", shell("全部知识索引", "所有已发布知识文档的链接与简短摘要。", global_index_body, "index/"))

    # 4. Global Reading Page (/knowledge/reading/)
    global_reading_sections = []
    global_jumps = []
    for topic in reading_data['topics']:
        key = topic['id']
        global_jumps.append(f'<a href="#{e(key)}">{e(topic["title"])}</a>')
        entries = []
        for entry in topic['articles']:
            slug = entry['slug']
            if slug in all_articles_map:
                a = all_articles_map[slug]
                cid = CAT_TO_CHANNEL[a['category']]
                entries.append(f'<li><a href="{BASE}{cid}/notes/{slug}/">{e(a["title"])}</a><p>{e(entry["note"])}</p></li>')
        global_reading_sections.append(f'<section class="reading-section" id="{e(key)}"><h2>{e(topic["title"])}</h2><p>{e(topic["description"])}</p><ul class="reading-list">{"".join(entries)}</ul></section>')

    global_reading_body = f'''<section class="index-page reading-page"><a class="back" href="{BASE}">← 返回知识库主页</a><h1>专题阅读总览</h1><p class="lead">按问题找经验，直达对应专栏深度研报。</p><div class="reading-jumps" style="margin:20px 0 30px;">{"".join(global_jumps)}</div>{"".join(global_reading_sections)}</section>{platform()}'''
    write("reading/index.html", shell("专题阅读总览", "按获客运营、收费交付、工具提效、职场博弈与单店算账查找完整直播知识。", global_reading_body, "reading/"))

    # 5. 404 & Sitemap
    write('404.html', shell('页面未找到', '请回到知识库查找笔记。', f'<section class="article"><h1>这篇笔记还没有找到</h1><p><a class="cta" href="{BASE}">回到知识库首页</a></p></section>'))
    
    sitemap_urls = ['', 'index/', 'reading/']
    for cid in CHANNELS:
        sitemap_urls.extend([f"{cid}/", f"{cid}/index/", f"{cid}/reading/"])
        for a in channel_articles_map[cid]:
            sitemap_urls.append(f"{cid}/notes/{a['slug']}/")

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{SITE_URL}{p}</loc></url>' for p in sitemap_urls) + '</urlset>'
    write('sitemap.xml', sitemap_xml)

    print(f"Built multi-channel site successfully with {len(articles)} reviewed articles across {len(CHANNELS)} channels at {OUT}")

if __name__ == '__main__':
    main()
