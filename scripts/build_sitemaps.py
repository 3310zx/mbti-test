#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把根级 sitemap.xml 按语言拆分为 sitemaps/sitemap-*.xml 分片，并生成根级索引 sitemap-index.xml。

- 分片内仅保留 <loc> + <lastmod> + hreflang 交替链接（去掉 changefreq / priority）
- 所有 loc / hreflang href 一律为绝对 https 链接
- 原 sitemap.xml 保留不动（兼容旧入口）
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://3310zx.github.io/mbti-test/"
SRC = os.path.join(BASE, "sitemap.xml")
OUT_DIR = os.path.join(BASE, "sitemaps")

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML = "http://www.w3.org/1999/xhtml"

MULTI_LANGS = ("ko/", "fr/", "ru/", "es/", "pt/", "yue/", "bo/")


def shard_of(rel):
    """按路径前缀判定所属分片。"""
    if rel.startswith("country/ja/") or rel.startswith("ja/"):
        return "ja"
    if rel.startswith("country/en/") or rel.startswith("en/"):
        return "en"
    if rel.startswith(MULTI_LANGS):
        return "multi"
    if rel.startswith("country/"):
        return "zh"
    return "core"


def parse_source():
    tree = ET.parse(SRC)
    root = tree.getroot()
    entries = []
    for url in root.findall(f"{{{NS}}}url"):
        loc = url.findtext(f"{{{NS}}}loc", default="").strip()
        lastmod = url.findtext(f"{{{NS}}}lastmod", default="").strip()
        alts = []
        for link in url.findall(f"{{{XHTML}}}link"):
            if link.get("rel") != "alternate":
                continue
            alts.append((link.get("hreflang"), (link.get("href") or "").strip()))
        entries.append({"loc": loc, "lastmod": lastmod, "alts": alts})
    return entries


def to_file(loc):
    rel = loc[len(SITE):] if loc.startswith(SITE) else loc
    if rel == "" or rel.endswith("/"):
        return os.path.join(BASE, rel, "index.html")
    return os.path.join(BASE, rel)


def canonical_of(loc):
    path = to_file(loc)
    try:
        head = open(path, encoding="utf-8", errors="ignore").read(4096)
    except OSError:
        return None
    m = re.search(r'<link rel="canonical" href="([^"]+)"', head)
    return m.group(1).strip() if m else None


def fix_legacy(remap):
    """仅修复旧 sitemap.xml 中的死链 hreflang（types/ 段缺失），URL 条目与其它标签保持不动。"""
    src = open(SRC, encoding="utf-8").read()
    changed = []

    def repl(m):
        href = m.group(1)
        new = remap.get(href, href)
        if new != href:
            changed.append((href, new))
        return f'href="{new}"'

    out = re.sub(r'href="(https://[^"]+)"', repl, src)
    if changed:
        with open(SRC, "w", encoding="utf-8") as f:
            f.write(out)
    print(f"旧 sitemap.xml hreflang 修复: {len(changed)} 条")
    return len(changed)


def build():
    entries = parse_source()

    # 去重：同一物理文件被多个 URL 收录时（如 /ai/ 与 /ai/index.html），
    # 按页面 canonical 保留规范变体，其余剔除；被剔除 URL 的 hreflang 引用重写到保留变体。
    by_file = {}
    for e in entries:
        by_file.setdefault(os.path.realpath(to_file(e["loc"])), []).append(e)
    drops, remap = [], {}
    keep_locs = []
    for f, group in by_file.items():
        if len(group) == 1:
            keep_locs.append(group[0]["loc"])
            continue
        canon = canonical_of(group[0]["loc"])
        keeper = next((g for g in group if g["loc"] == canon), None)
        if keeper is None:
            keeper = next((g for g in group if g["loc"].endswith("/")), group[0])
        keep_locs.append(keeper["loc"])
        for g in group:
            if g["loc"] != keeper["loc"]:
                drops.append((g["loc"], keeper["loc"], canon))
                remap[g["loc"]] = keeper["loc"]
    entries = [e for e in entries if e["loc"] in set(keep_locs)]
    known = {e["loc"] for e in entries}

    # 校验并修复 hreflang：href 必须为本站绝对 https 且落在已收录 URL 集合内。
    # 已知缺陷：types/*.html 的交替链接漏写 types/ 段（指向 /intj.html 等 404 路径），
    # 若能按 types/<basename> 归一后命中已收录 URL，则修正，否则视为死链剔除。
    repaired, dangling = [], []
    for e in entries:
        kept = []
        for lang, href in e["alts"]:
            href = remap.get(href, href)
            if href.startswith(SITE) and href in known:
                kept.append((lang, href))
                continue
            fixed = None
            if href.startswith(SITE):
                rel = href[len(SITE):].strip("/")
                parts = rel.split("/") if rel else []
                cands = []
                if len(parts) == 1:
                    cands.append(f"types/{parts[0]}")
                elif len(parts) == 2:
                    cands.append(f"{parts[0]}/types/{parts[1]}")
                for c in cands:
                    if SITE + c in known:
                        fixed = SITE + c
                        break
            if fixed:
                repaired.append((e["loc"], lang, href, fixed))
                kept.append((lang, fixed))
            else:
                dangling.append((e["loc"], lang, href))
        e["alts"] = kept

    groups = {}
    for e in entries:
        rel = e["loc"][len(SITE):] if e["loc"].startswith(SITE) else e["loc"]
        groups.setdefault(shard_of(rel), []).append(e)

    order = ["core", "zh", "ja", "en", "multi"]
    os.makedirs(OUT_DIR, exist_ok=True)

    written = []
    for name in order:
        items = groups.get(name, [])
        if not items:
            continue
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<urlset xmlns="{NS}"',
            f'        xmlns:xhtml="{XHTML}">',
        ]
        for e in items:
            lines.append("  <url>")
            lines.append(f'    <loc>{e["loc"]}</loc>')
            if e["lastmod"]:
                lines.append(f'    <lastmod>{e["lastmod"]}</lastmod>')
            seen = set()
            for lang, href in e["alts"]:
                if (lang, href) in seen:
                    continue
                seen.add((lang, href))
                lines.append(
                    f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{href}"/>'
                )
            lines.append("  </url>")
        lines.append("</urlset>")

        path = os.path.join(OUT_DIR, f"sitemap-{name}.xml")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        lastmods = sorted({e["lastmod"] for e in items if e["lastmod"]})
        written.append((f"sitemap-{name}.xml", len(items), lastmods[-1] if lastmods else ""))

    # 根级索引
    idx = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<sitemapindex xmlns="{NS}">',
    ]
    for fname, _n, lm in written:
        idx.append("  <sitemap>")
        idx.append(f"    <loc>{SITE}sitemaps/{fname}</loc>")
        if lm:
            idx.append(f"    <lastmod>{lm}</lastmod>")
        idx.append("  </sitemap>")
    idx.append("</sitemapindex>")
    with open(os.path.join(BASE, "sitemap-index.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(idx) + "\n")

    fix_legacy({r[2]: r[3] for r in repaired})

    print(f"源 URL 数: {len(entries)} | 分片数: {len(written)}")
    for fname, n, lm in written:
        print(f"  {fname:24s} {n:4d}  lastmod {lm}")
    print(f"分片 URL 合计: {sum(n for _, n, _ in written)}")
    if drops:
        print(f"重复 URL 去重: {len(drops)} 条（同一页面被两个地址收录，保留 canonical 变体）")
        for d, k, c in drops:
            print(f"    剔除 {d}  ->  保留 {k}  (canonical={c})")
    if repaired:
        uniq = sorted({(r[2], r[3]) for r in repaired})
        print(f"hreflang 修正: {len(repaired)} 条（{len(uniq)} 个唯一目标）")
        for a, b in uniq[:5]:
            print(f"    {a}  ->  {b}")
    if dangling:
        print(f"[WARN] 剔除的死链 hreflang {len(dangling)} 条：")
        for d in dangling[:20]:
            print("   ", d)
    else:
        print("hreflang 校验: 全部交替链接均指向本站已收录 URL，无死链")
    return 0 if sum(n for _, n, _ in written) == len(entries) else 1


if __name__ == "__main__":
    sys.exit(build())
