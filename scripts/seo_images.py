#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图片搜索/多模态通道改造：
1) 类型页代表人物图：本地化 alt + width/height
2) 注入 ImageObject 结构化数据
3) 生成图片 sitemap (sitemap-images.xml)
4) robots meta 补 max-image-preview:large
用法: python3 scripts/seo_images.py [--dry]
"""
import os, re, sys, json, glob, struct

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://3310zx.github.io/mbti-test"
LANGS = ['', 'en', 'es', 'fr', 'ja', 'ko', 'pt', 'ru', 'yue', 'bo']
DRY = '--dry' in sys.argv

ALT_TPL = {
    '':   '{T} {nick} · 代表人物 {person} 肖像',
    'yue': '{T} {nick} · 代表人物 {person} 肖像',
    'en':  '{T} {nick} — portrait of {person}',
    'es':  '{T} {nick} — retrato de {person}',
    'fr':  '{T} {nick} — portrait de {person}',
    'pt':  '{T} {nick} — retrato de {person}',
    'ja':  '{T} {nick} · 代表的人物 {person} の肖像',
    'ko':  '{T} {nick} · 대표 인물 {person} 초상화',
    'ru':  '{T} {nick} — портрет {person}',
    'bo':  '{T} {nick} · མཚོན་བྱེད་མི་སྣ {person} སྐུ་པར།',
}
CAPTION_TPL = {
    '':   '{T}（{nick}）代表人物 {person} 肖像插画',
    'yue': '{T}（{nick}）代表人物 {person} 肖像插畫',
    'en':  'Portrait illustration of {person}, notable figure of the {T} ({nick}) personality type',
    'es':  'Ilustración del retrato de {person}, figura notable del tipo {T} ({nick})',
    'fr':  'Illustration du portrait de {person}, figure marquante du type {T} ({nick})',
    'pt':  'Ilustração do retrato de {person}, figura notável do tipo {T} ({nick})',
    'ja':  'MBTI {T}（{nick}）の代表的人物 {person} の肖像イラスト',
    'ko':  '{T}({nick}) 유형의 대표 인물 {person} 초상화 일러스트',
    'ru':  'Портрет-иллюстрация {person}, известной личности типа {T} ({nick})',
    'bo':  '{T}（{nick}）མཚོན་བྱེད་མི་སྣ {person} སྐུ་པར།',
}


def webp_size(p):
    b = open(p, 'rb').read(48)
    if b[12:16] == b'VP8X':
        return int.from_bytes(b[24:27], 'little') + 1, int.from_bytes(b[27:30], 'little') + 1
    if b[12:16] == b'VP8 ':
        i = b.find(b'\x9d\x01\x2a')
        return (struct.unpack('<H', b[i+3:i+5])[0] & 0x3fff,
                struct.unpack('<H', b[i+5:i+7])[0] & 0x3fff)
    if b[12:16] == b'VP8L':
        bits = int.from_bytes(b[21:25], 'little')
        return (bits & 0x3fff) + 1, ((bits >> 14) & 0x3fff) + 1
    return None


def page_url(lang, t):
    return f"{SITE}/{lang + '/' if lang else ''}types/{t.lower()}.html"


def main():
    sizes = {os.path.basename(f)[:-5]: webp_size(f)
             for f in glob.glob(os.path.join(REPO, 'images/portraits/*.webp'))}
    changed = 0
    sitemap = []   # (page_url, img_url, title, caption)
    for lang in LANGS:
        for t in sorted(sizes):
            p = os.path.join(REPO, lang, 'types', f'{t.lower()}.html')
            if not os.path.exists(p):
                print('MISSING', p)
                continue
            s = open(p, encoding='utf-8').read()
            orig = s
            # 取本地化字段
            blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
            nick = person = None
            if blocks:
                try:
                    d = json.loads(blocks[0])
                    for node in d.get('@graph', []):
                        if node.get('@type') == 'Person':
                            person = node.get('name')
                except Exception:
                    pass
            # 昵称优先取 h1 的 cname: "INTJ型人格 · 建筑师" / "INTJ · Architect"
            m = re.search(r'<span class="cname"[^>]*>(.*?)</span>', s, re.S)
            if m:
                txt = re.sub(r'<[^>]+>', '', m.group(1)).strip()
                parts = re.split(r'\s*[·・]\s*', txt)
                if len(parts) > 1:
                    nick = parts[-1].strip()
            if not person:
                person = ''
            if not nick or nick == t:
                nick = ''
            alt = ALT_TPL[lang].format(T=t, nick=nick, person=person).replace('  ', ' ').strip()
            caption = CAPTION_TPL[lang].format(T=t, nick=nick or t, person=person).replace('（）', '').replace('()', '').strip()
            w, h = sizes[t]
            img_rel = ('../' if not lang else '../../') + f'images/portraits/{t}.webp'
            img_url = f"{SITE}/images/portraits/{t}.webp"

            # 1) 重写 <img>
            def fix_img(m):
                tag = m.group(0)
                tag = re.sub(r'\salt="[^"]*"', '', tag)
                tag = re.sub(r'\s(width|height)="[^"]*"', '', tag)
                tag = tag.replace('<img ', f'<img width="{w}" height="{h}" alt="{alt}" ', 1)
                return tag
            s = re.sub(r'<img\b[^>]*portraits/[A-Z]{4}\.webp[^>]*>', fix_img, s)

            # 2) ImageObject JSON-LD（幂等：先移除旧的）
            s = re.sub(r'\n?<script type="application/ld\+json" data-seo="imageobject">.*?</script>', '', s, flags=re.S)
            io = {
                "@context": "https://schema.org",
                "@type": "ImageObject",
                "contentUrl": img_url,
                "url": img_url,
                "name": alt,
                "caption": caption,
                "description": caption,
                "width": {"@type": "QuantitativeValue", "value": w, "unitCode": "E37"},
                "height": {"@type": "QuantitativeValue", "value": h, "unitCode": "E37"},
                "encodingFormat": "image/webp",
                "representativeOfPage": True,
                "inLanguage": {'': 'zh-CN', 'yue': 'yue'}.get(lang, lang),
                "creditText": "MBTI Cognitive Functions Test",
                "url_page": page_url(lang, t),
                "mainEntityOfPage": {"@type": "WebPage", "@id": page_url(lang, t)},
            }
            io.pop('url_page')
            tag = '<script type="application/ld+json" data-seo="imageobject">\n' + \
                  json.dumps(io, ensure_ascii=False, indent=2) + '\n</script>'
            s = s.replace('</head>', tag + '\n</head>', 1)

            if s != orig:
                changed += 1
                if not DRY:
                    open(p, 'w', encoding='utf-8').write(s)
            sitemap.append((page_url(lang, t), img_url, alt, caption))

    # 3) robots meta 全站补 max-image-preview:large
    rc = 0
    for f in glob.glob(os.path.join(REPO, '**', '*.html'), recursive=True):
        if '/.git/' in f:
            continue
        s = open(f, encoding='utf-8').read()
        o = s
        def fix_robots(m):
            c = m.group(1)
            if 'max-image-preview' in c:
                return m.group(0)
            return f'<meta name="robots" content="{c},max-image-preview:large">'
        s = re.sub(r'<meta name="robots" content="([^"]*)">', fix_robots, s)
        s = s.replace('index,follow,max-image-preview:large,max-image-preview:large',
                      'index,follow,max-image-preview:large')
        # 缺失 robots meta 的页面补上（404 页 noindex）
        if 'name="robots"' not in s and '</head>' in s:
            base = 'noindex,follow' if os.path.basename(f) == '404.html' else 'index,follow'
            s = s.replace('</head>',
                          f'<meta name="robots" content="{base},max-image-preview:large">\n</head>', 1)
        if s != o:
            rc += 1
            if not DRY:
                open(f, 'w', encoding='utf-8').write(s)

    # 4) 图片 sitemap
    from xml.sax.saxutils import escape
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
             '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for purl, iurl, title, caption in sitemap:
        lines += ['  <url>',
                  f'    <loc>{purl}</loc>',
                  '    <image:image>',
                  f'      <image:loc>{iurl}</image:loc>',
                  f'      <image:title>{escape(title)}</image:title>',
                  f'      <image:caption>{escape(caption)}</image:caption>',
                  '    </image:image>',
                  '  </url>']
    lines.append('</urlset>')
    if not DRY:
        open(os.path.join(REPO, 'sitemap-images.xml'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
        # robots.txt 挂载
        rp = os.path.join(REPO, 'robots.txt')
        rt = open(rp, encoding='utf-8').read()
        if 'sitemap-images.xml' not in rt:
            rt = rt.replace(f'Sitemap: {SITE}/sitemap.xml',
                            f'Sitemap: {SITE}/sitemap.xml\nSitemap: {SITE}/sitemap-images.xml')
            open(rp, 'w', encoding='utf-8').write(rt)

    print(f'类型页改写: {changed} | robots meta 改写: {rc} | 图片 sitemap 条目: {len(sitemap)}')
    print('样例 alt:', sitemap[0][2], '|', sitemap[16][2], '|', sitemap[-1][2])
    print('样例 caption:', sitemap[0][3])


if __name__ == '__main__':
    main()
