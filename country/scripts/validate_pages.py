#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 country 子站：内部链接、占位符、JSON-LD、元信息唯一性。"""
import os, re, json, sys
from urllib.parse import urlparse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(BASE)
pages = []
for dirpath, dirnames, filenames in os.walk(BASE):
    if 'scripts' in dirpath or 'data' in dirpath or 'assets' in dirpath:
        continue
    for f in filenames:
        if f.endswith('.html'):
            pages.append(os.path.join(dirpath, f))
pages.sort()

problems = []
titles, descs, canons = {}, {}, {}
ld_count = 0
for p in pages:
    s = open(p, encoding='utf-8').read()
    rel = os.path.relpath(p, ROOT)
    if re.search(r'\{(upd|A|B)\}', s):
        problems.append(f'{rel}: 残留占位符')
    t = re.search(r'<title>(.*?)</title>', s)
    d = re.search(r'<meta name="description" content="(.*?)">', s)
    c = re.search(r'<link rel="canonical" href="(.*?)">', s)
    if not t or not t.group(1).strip():
        problems.append(f'{rel}: 缺 title')
    else:
        titles.setdefault(t.group(1), []).append(rel)
    if not d:
        problems.append(f'{rel}: 缺 description')
    else:
        descs.setdefault(d.group(1), []).append(rel)
        if len(d.group(1)) < 40:
            problems.append(f'{rel}: description 过短 {len(d.group(1))}')
    if not c:
        problems.append(f'{rel}: 缺 canonical')
    else:
        canons.setdefault(c.group(1), []).append(rel)
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        ld_count += 1
        try:
            json.loads(m.group(1))
        except Exception as e:
            problems.append(f'{rel}: JSON-LD 解析失败 {e}')
    # 内部链接
    for m in re.finditer(r'(?:href|src)="([^"#]+)"', s):
        u = m.group(1)
        if u.startswith(('http', 'mailto:', 'data:', 'javascript:')):
            continue
        target = u.split('?')[0].split('#')[0]
        if not target:
            continue
        tp = os.path.normpath(os.path.join(os.path.dirname(p), target))
        if target.endswith('/'):
            tp = os.path.join(tp, 'index.html')
        if not os.path.exists(tp):
            problems.append(f'{rel}: 断链 {u}')

for k, v in titles.items():
    if len(v) > 1:
        problems.append(f'title 重复: {k} -> {v}')
for k, v in descs.items():
    if len(v) > 1:
        problems.append(f'description 重复: {k[:40]} -> {v}')
for k, v in canons.items():
    if len(v) > 1:
        problems.append(f'canonical 重复: {k} -> {v}')

print(f'页面数: {len(pages)} | JSON-LD 块: {ld_count} | 问题数: {len(problems)}')
for x in problems[:40]:
    print(' -', x)
sys.exit(1 if problems else 0)
