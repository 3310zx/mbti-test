#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量注入 BreadcrumbList 结构化数据 + 可见面包屑导航（多语言可复用）。

覆盖页面（按语言目录扫描）：
  <lang>/types/*.html        层级：首页 > 16 型百科 > 「CODE 类型名」
  <lang>/types/index.html    层级：首页 > 16 型百科（当前页）
  <lang>/privacy.html        层级：首页 > 隐私政策
  <lang>/high-need-test/index.html  层级：首页 > 高需求朋友测试
跳过：首页（根节点无需面包屑）、404.html（noindex 页面）

用法：
  python3 scripts/inject_breadcrumb.py --lang zh --dry-run
  python3 scripts/inject_breadcrumb.py --lang zh
  python3 scripts/inject_breadcrumb.py --lang all

特性：幂等（已含 BreadcrumbList 的页面自动跳过）、不改动原有 <style>/<script>、
使用 CSS 变量配色（兼容深色主题）、相对链接经 check_site.py 死链校验。
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://3310zx.github.io/mbti-test/"
TYPES = sorted(
    "INTJ INTP ENTJ ENTP INFJ INFP ENFJ ENFP ISTJ ISFJ ESTJ ESFJ ISTP ISFP ESTP ESFP".split()
)

# 每种语言的目录前缀与文案（新增语言只需在此登记）
LANGS = {
    "zh": {"dir": "", "home": "首页", "types": "16 型百科", "privacy": "隐私政策", "hn": "高需求朋友测试"},
    "en": {"dir": "en", "home": "Home", "types": "All 16 Types", "privacy": "Privacy Policy", "hn": "High-Need Friend Test"},
    "ja": {"dir": "ja", "home": "ホーム", "types": "16タイプ一覧", "privacy": "プライバシーポリシー", "hn": "高需要な友人テスト"},
    "ko": {"dir": "ko", "home": "홈", "types": "16유형 백과", "privacy": "개인정보 처리방침", "hn": "높은 요구 친구 테스트"},
    "fr": {"dir": "fr", "home": "Accueil", "types": "Les 16 types", "privacy": "Confidentialité", "hn": "Test de l'ami exigeant"},
    "ru": {"dir": "ru", "home": "Главная", "types": "Все 16 типов", "privacy": "Конфиденциальность", "hn": "Тест требовательного друга"},
    "bo": {"dir": "bo", "home": "གཙོ་ངོས།", "types": "རིགས་ 16", "privacy": "གསང་བའི་སྲོལ་ཡིག", "hn": "དགོས་མཁོ་ཆེ་བའི་གྲོགས་པོའི་བརྟག་དཔྱད།"},
    "yue": {"dir": "yue", "home": "首頁", "types": "16 型百科", "privacy": "私隱政策", "hn": "高需求朋友測試"},
    "es": {"dir": "es", "home": "Inicio", "types": "Los 16 tipos", "privacy": "Privacidad", "hn": "Test del amigo exigente"},
    "pt": {"dir": "pt", "home": "Início", "types": "Os 16 tipos", "privacy": "Privacidade", "hn": "Teste do amigo exigente"},
}

CRUMB_STYLE = (
    "font-size:13px;line-height:1.5;display:flex;flex-wrap:wrap;align-items:center;"
    "gap:6px;color:var(--md-on-surface-variant,#6e6e73);"
)
LINK_STYLE = "color:var(--md-primary,#0071e3);text-decoration:none;font-weight:500;"
SEP = '<span aria-hidden="true" style="opacity:.55;">›</span>'


def rel_home(rel_path):
    """当前页面到语言目录首页的相对路径。"""
    depth = rel_path.count("/")
    return "../" * depth + "index.html" if depth else "index.html"


def rel_types_index(rel_path):
    depth = rel_path.count("/")
    if depth == 0:
        return "types/index.html"
    return "../" * (depth - 1) + "types/index.html" if depth > 1 else "index.html"


def page_cname(text, code):
    m = re.search(r'<div class="cname">(.*?)</div>', text, re.S)
    if not m:
        return code
    label = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return label or code


def build_items(text, rel_path, cfg):
    """返回 [(name, url_abs 或 None, href_rel 或 None)]，按层级顺序。"""
    lang_base = BASE + (cfg["dir"] + "/" if cfg["dir"] else "")
    home = (cfg["home"], lang_base, rel_home(rel_path))
    types_idx = (cfg["types"], lang_base + "types/", rel_types_index(rel_path))
    base = os.path.basename(rel_path)

    if rel_path.startswith("types/") and base != "index.html":
        code = base[:-5].upper()
        label = page_cname(text, code)
        return [home, types_idx, (label, lang_base + "types/" + base, None)]
    if rel_path == "types/index.html":
        return [home, (types_idx[0], types_idx[1], None)]
    if rel_path == "privacy.html":
        return [home, (cfg["privacy"], lang_base + "privacy.html", None)]
    if rel_path == "high-need-test/index.html":
        return [home, (cfg["hn"], lang_base + "high-need-test/", None)]
    return None


def build_nav(items, extra_style=""):
    parts = []
    for i, (name, _abs, href) in enumerate(items):
        if href:
            parts.append('<a href="%s" style="%s">%s</a>' % (href, LINK_STYLE, name))
        else:
            parts.append('<span aria-current="page" style="%s">%s</span>' % (LINK_STYLE.replace("color:var(--md-primary,#0071e3)", "color:var(--md-on-surface-variant,#6e6e73)"), name))
        if i < len(items) - 1:
            parts.append(SEP)
    return (
        '    <nav class="breadcrumb-nav" aria-label="面包屑导航" style="%s%s">\n      %s\n    </nav>\n'
        % (CRUMB_STYLE, extra_style, "\n      ".join(parts))
    )


def build_ld(items):
    list_items = []
    for i, (name, abs_url) in enumerate([(n, a) for n, a, _h in items], start=1):
        list_items.append({"@type": "ListItem", "position": i, "name": name, "item": abs_url})
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": list_items,
    }
    return (
        '<script type="application/ld+json">%s</script>\n'
        % json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    )


def process(path, cfg, dry_run):
    rel_path = os.path.relpath(path, ROOT).replace(os.sep, "/")
    text = open(path, encoding="utf-8").read()
    if '"BreadcrumbList"' in text:
        return "skip(已存在)"
    items = build_items(text, rel_path, cfg)
    if not items:
        return "skip(不在范围)"
    if "high-need-test" in rel_path:
        anchor = "</header>"
        nav = build_nav(items, "margin:0;padding:12px 22px 0;max-width:1100px;margin:0 auto;")
        if text.count(anchor) < 1:
            return "skip(无锚点)"
        new = text.replace(anchor, anchor + "\n" + nav.rstrip("\n"), 1)
    else:
        anchor = '<div class="wrap">'
        if text.count(anchor) != 1:
            return "skip(wrap 锚点 %d 个)" % text.count(anchor)
        nav = build_nav(items)
        new = text.replace(anchor, anchor + "\n" + nav, 1)

    if "</head>" not in new:
        return "skip(无 </head>)"
    new = new.replace("</head>", build_ld(items) + "</head>", 1)

    if not dry_run:
        open(path, "w", encoding="utf-8").write(new)
    return "ok(+%d bytes)" % (len(new) - len(text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="zh", help="语言代码：zh/en/ja/ko/fr/ru/bo/yue/es/pt/all")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    langs = list(LANGS) if args.lang == "all" else [args.lang]
    total = 0
    for lang in langs:
        if lang not in LANGS:
            print("未知语言：%s" % lang)
            sys.exit(2)
        cfg = LANGS[lang]
        d = os.path.join(ROOT, cfg["dir"]) if cfg["dir"] else ROOT
        targets = sorted(glob.glob(os.path.join(d, "types", "*.html")))
        for extra in ("privacy.html", os.path.join("high-need-test", "index.html")):
            p = os.path.join(d, extra)
            if os.path.exists(p):
                targets.append(p)
        print("== %s (%d 个页面) ==" % (lang, len(targets)))
        for p in targets:
            res = process(p, cfg, args.dry_run)
            print("  %-45s %s" % (os.path.relpath(p, ROOT), res))
            if res.startswith("ok"):
                total += 1
    print("\n完成：%s 注入 %d 个页面" % ("dry-run 预计" if args.dry_run else "实际", total))


if __name__ == "__main__":
    main()
