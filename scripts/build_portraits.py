#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 16 型人格人物图鉴页 /portraits/index.html（多语言）。

用法：
    python3 scripts/build_portraits.py            # 只生成已启用的语言（当前仅中文）
    python3 scripts/build_portraits.py --lang all # 生成 LANGS 中全部语言（P2 阶段使用）

数据：scripts/data/portraits.json（中文）/ portraits.<lang>.json（其余语言，按需增补）
模板：scripts/templates/portraits.html（{{占位符}}）
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL_PATH = os.path.join(BASE, "scripts", "templates", "portraits.tpl")
DATA_DIR = os.path.join(BASE, "scripts", "data")
SITE = "https://3310zx.github.io/mbti-test"

# 语言清单：key / 输出目录（相对根）/ 页面 lang / hreflang / 下拉显示名 / 数据文件
LANGS = [
    dict(key="zh", out="portraits", lang="zh-CN", hreflang="zh-CN", label="简体中文", data="portraits.json"),
    dict(key="en", out="en/portraits", lang="en", hreflang="en", label="English", data="portraits.en.json"),
    dict(key="ja", out="ja/portraits", lang="ja", hreflang="ja", label="日本語", data="portraits.ja.json"),
    dict(key="ko", out="ko/portraits", lang="ko", hreflang="ko", label="한국어", data="portraits.ko.json"),
    dict(key="fr", out="fr/portraits", lang="fr", hreflang="fr", label="Français", data="portraits.fr.json"),
    dict(key="ru", out="ru/portraits", lang="ru", hreflang="ru", label="Русский", data="portraits.ru.json"),
    dict(key="bo", out="bo/portraits", lang="bo", hreflang="bo", label="བོད་སྐད།", data="portraits.bo.json"),
    dict(key="yue", out="yue/portraits", lang="yue", hreflang="yue", label="粵語", data="portraits.yue.json"),
    dict(key="es", out="es/portraits", lang="es", hreflang="es", label="Español", data="portraits.es.json"),
    dict(key="pt", out="pt/portraits", lang="pt", hreflang="pt", label="Português", data="portraits.pt.json"),
]
# 已上线语言（P1 只开中文；其余语言页与数据就位后把 key 加进这里即可）
BUILD_LANGS = ["zh"]

L = {x["key"]: x for x in LANGS}
ZH = L["zh"]

# 各语言的页面文案骨架（P2 增补语言时在这里补对应词条）
UI = {
    "zh": dict(
        title="16 型 MBTI 人格代表人物图鉴：16 张肖像 × 32 位男女名人对照",
        desc="INTJ 牛顿与简·奥斯汀、INFP 托尔金与奥黛丽·赫本……16 个类型各配一男一女两位代表：主位人物配肖像与三段详写，副位人物以文字卡呈现，附认知功能落点与一条可带走的提醒。",
        h1="16 型人格代表人物图鉴",
        crumb="16 型人物图鉴",
        family="16 张肖像 · 32 位代表人物 · 认知功能如何落地",
        intro="每种 MBTI 类型都有一批被反复引用的代表人物。这一页给 16 个类型各配一男一女两位：主位人物出肖像并三段详写——其所处的处境、用主导与辅助功能做出的具体决定，以及这段经历对同类型的人意味着什么；副位人物以文字卡简写，尽量选跨语言都叫得出名字的那一位。点击任意头像可跳到该条，点击“完整解析”可进入对应的类型百科页。",
        who="他是谁",
        who_m="他是谁",
        who_f="她是谁",
        second_label="另一位代表",
        second_note="副位人物以文字卡呈现，不配独立肖像；两性各半，类型归属同样来自公开的常见归类。",
        func="功能如何落地",
        take="给同类型的提醒",
        more="查看 {code} 完整解析 →",
        gallery_name="16 型人格代表人物图鉴",
        gallery_desc="16 位代表人物的肖像插画与认知功能类型对照。",
        credit_text="MBTI 认知功能测试 · 程序生成插画",
        license="https://3310zx.github.io/mbti-test/portraits/#credit",
        creator="MBTI 认知功能测试站",
    ),
}


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def load_data(lang_key: str) -> dict:
    path = os.path.join(DATA_DIR, L[lang_key]["data"])
    if not os.path.exists(path):
        raise SystemExit(f"缺少数据文件：{path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def rel_root(lang_key: str) -> str:
    """页面到站点根的相对前缀：根页 ../，语言子目录 ../../。"""
    depth = L[lang_key]["out"].count("/")
    return "../" * (depth + 1)


def replace_tpl(tpl: str, mapping: dict) -> str:
    for k, v in mapping.items():
        tpl = tpl.replace("{{%s}}" % k, v)
    left = re.findall(r"\{\{\w+\}\}", tpl)
    if left:
        raise SystemExit(f"模板占位符未替换：{sorted(set(left))}")
    return tpl


def build_items(items: list[dict], ui: dict, root: str) -> tuple[str, str]:
    """渲染 16 张主位卡片（肖像 + 三段详写）与副位文字卡（无肖像）。

    方案 B：主位出图 + who/func/take 三段详写；副位只在主位卡片底部以文字卡简写，
    不生成独立肖像，因此页面图片数仍为 16，与 ImageGallery 的 16 个 ImageObject 一致。
    """
    cards, chips = [], []
    for it in items:
        code = it["code"]
        low = code.lower()
        img = root + "images/portraits/%s.webp" % code
        page = "%stypes/%s.html" % (root, low)
        sec = it["second"]
        k_who = ui["who_f"] if it.get("gender") == "女" else ui["who_m"]
        sec_k_who = ui["who_f"] if sec.get("gender") == "女" else ui["who_m"]
        chips.append('<a class="pf-chip" href="#%s">%s</a>' % (low, esc(code)))
        cards.append("""      <article class="pf-item" id="{low}" style="--card-c1:{c1};--card-c2:{c2}">
        <div class="pf-media">
          <img src="{img}" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async">
          <span class="pf-badge">{code}</span>
        </div>
        <div class="pf-body">
          <h2 class="pf-name">{person}<span class="pf-life">{life}</span></h2>
          <div class="pf-tags"><span class="pf-tag">{alias}型 · {family}</span><span class="pf-tag">认知功能栈 {stack}</span></div>
          <p class="pf-p"><b class="pf-k">{k_who}</b>{who}</p>
          <p class="pf-p"><b class="pf-k">{k_func}</b>{func}</p>
          <p class="pf-quote"><b class="pf-k">{k_take}</b>{take}</p>
          <div class="pf-second">
            <div class="pf-second-head"><span class="pf-second-label">{sec_label} · {sec_gender}</span><span class="pf-second-name">{sec_name}</span><span class="pf-life">{sec_life}</span></div>
            <div class="pf-tags"><span class="pf-tag">{sec_role}</span></div>
            <p class="pf-p"><b class="pf-k">{sec_k_who}</b>{sec_who}</p>
            <p class="pf-p"><b class="pf-k">{k_func}</b>{sec_func}</p>
            <p class="pf-p"><b class="pf-k">{k_take}</b>{sec_take}</p>
          </div>
          <a class="pf-more" href="{page}">{more}</a>
        </div>
      </article>""".format(low=low, c1=it["c1"], c2=it["c2"], img=img, w=it["w"], h=it["h"], alt=esc(it["alt"]), code=esc(code), person=esc(it["person"]), life=esc(it["life"]), alias=esc(it["alias"]), family=esc(it["family"]), stack=esc(it["stack"]), k_who=esc(k_who), who=esc(it["who"]), k_func=esc(ui["func"]), func=esc(it["func"]), k_take=esc(ui["take"]), take=esc(it["take"]), sec_label=esc(ui["second_label"]), sec_gender=esc(sec["gender"]), sec_name=esc(sec["name"]), sec_life=esc(sec["life"]), sec_role=esc(sec["role"]), sec_k_who=esc(sec_k_who), sec_who=esc(sec["who"]), sec_func=esc(sec["func"]), sec_take=esc(sec["take"]), page=page, more=esc(ui["more"].format(code=code))))
    return "\n".join(cards), "\n".join(chips)


def build_jsonld(items: list[dict], ui: dict, lang_key: str) -> str:
    cfg, root = L[lang_key], rel_root(lang_key)
    page_url = f"{SITE}/{cfg['out']}/"
    images = []
    for it in items:
        images.append({
            "@type": "ImageObject",
            "@id": f"{page_url}#{it['code'].lower()}-image",
            "contentUrl": f"{SITE}/images/portraits/{it['code']}.webp",
            "name": it["alt"],
            "description": it["caption"],
            "caption": it["caption"],
            "width": {"@type": "QuantitativeValue", "value": it["w"], "unitCode": "E37"},
            "height": {"@type": "QuantitativeValue", "value": it["h"], "unitCode": "E37"},
            "creditText": ui["credit_text"],
            "creator": {"@type": "Organization", "name": ui["creator"], "url": SITE + "/"},
            "copyrightNotice": ui["creator"],
            "license": ui["license"],
            "representativeOfPage": False,
        })
    gallery = {
        "@context": "https://schema.org",
        "@type": "ImageGallery",
        "@id": page_url + "#gallery",
        "name": ui["gallery_name"],
        "description": ui["gallery_desc"],
        "url": page_url,
        "inLanguage": cfg["lang"],
        "isPartOf": {"@id": SITE + "/#website"},
        "associatedMedia": images,
    }
    collection = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": page_url,
        "url": page_url,
        "name": ui["h1"],
        "description": ui["desc"],
        "inLanguage": cfg["lang"],
        "isPartOf": {"@id": SITE + "/#website"},
        "mainEntity": {"@id": page_url + "#gallery"},
        "about": {"@type": "Thing", "name": "MBTI 16 种人格类型代表人物"},
        "mentions": [
            {
                "@type": "Person",
                "name": it["second"]["name"],
                "description": it["second"]["role"],
                "gender": "Female" if it["second"]["gender"] == "女" else "Male",
            }
            for it in items
        ],
    }
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": ui["gallery_name"],
        "numberOfItems": len(items),
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": f"{it['code']} {it['alias']} · {it['person']} / {it['second']['name']}",
                "url": f"{page_url}#{it['code'].lower()}",
                "item": {
                    "@type": "Person",
                    "name": it["person"],
                    "description": it["role"],
                    "url": f"{SITE}/{root}types/{it['code'].lower()}.html",
                },
            }
            for i, it in enumerate(items)
        ],
    }
    crumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "16 型百科", "item": SITE + "/types/"},
            {"@type": "ListItem", "position": 3, "name": ui["crumb"], "item": page_url},
        ],
    }
    return "\n".join(
        '<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False)
        for x in (collection, gallery, item_list, crumb)
    )


def build_lang_switch(current: str) -> str:
    opts = []
    for key in BUILD_LANGS:
        cfg = L[key]
        sel = " selected" if key == current else ""
        # 各语言页相互跳转到同语言的图鉴页
        href = "index.html" if key == current else os.path.relpath(
            os.path.join(BASE, L[key]["out"], "index.html"), os.path.join(BASE, L[current]["out"])
        ).replace(os.sep, "/")
        opts.append(f'  <option value="{href}"{sel}>{esc(cfg["label"])}</option>')
    return "\n".join(opts)


def build_hreflang() -> str:
    rows = []
    for key in BUILD_LANGS:
        cfg = L[key]
        rows.append(f'<link rel="alternate" hreflang="{cfg["hreflang"]}" href="{SITE}/{cfg["out"]}/">')
    rows.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}/{ZH["out"]}/">')
    return "\n".join(rows)


def render(lang_key: str) -> str:
    cfg = L[lang_key]
    if lang_key not in UI:
        raise SystemExit(f"缺少 {lang_key} 的页面文案 UI")
    ui = UI[lang_key]
    data = load_data(lang_key)
    items = data["items"]
    if len(items) != 16:
        raise SystemExit(f"{lang_key} 条目数应为 16，实际 {len(items)}")
    tpl = open(TPL_PATH, encoding="utf-8").read()
    root = rel_root(lang_key)
    cards, chips = build_items(items, ui, root)
    page_url = f"{SITE}/{cfg['out']}/"
    out = replace_tpl(tpl, {
        "TITLE": esc(ui["title"]),
        "DESC": esc(ui["desc"]),
        "CANONICAL": page_url,
        "HREFLANG": build_hreflang(),
        "OG_LOCALE": cfg["lang"].replace("-", "_"),
        "OG_IMAGE": f"{SITE}/images/portraits/INTJ.webp",
        "JSONLD": build_jsonld(items, ui, lang_key),
        "LANG_OPTIONS": build_lang_switch(lang_key),
        "CRUMB": esc(ui["crumb"]),
        "H1": esc(ui["h1"]),
        "FAMILY": esc(ui["family"]),
        "INTRO": esc(ui["intro"]),
        "SECOND_NOTE": esc(ui["second_note"]),
        "CHIPS": chips,
        "ITEMS": cards,
    })
    out = out.replace('<html lang="zh-CN">', f'<html lang="{cfg["lang"]}">', 1)
    dst = os.path.join(BASE, cfg["out"], "index.html")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"[build] {dst}  ({len(out)} bytes, {len(items)} 条)")
    return dst


def check(path: str, lang_key: str) -> None:
    """自检：占位符、条目数、图片存在与尺寸、JSON-LD 可解析、锚点完整。"""
    cfg = L[lang_key]
    root = rel_root(lang_key)
    t = open(path, encoding="utf-8").read()
    errs = []
    if re.search(r"\{\{\w+\}\}", t):
        errs.append("残留占位符")
    if t.count('class="pf-item"') != 16:
        errs.append("条目数不是 16")
    for code in re.findall(r'src="(\.\./+images/portraits/\w+\.webp)"', t):
        p = os.path.normpath(os.path.join(BASE, cfg["out"], code))
        if not os.path.exists(p):
            errs.append(f"图片缺失 {code}")
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            json.loads(blk)
        except Exception as e:  # noqa: BLE001
            errs.append(f"JSON-LD 解析失败 {e}")
    for href in re.findall(r'href="(\.\./[^"#]+\.html)"', t):
        p = os.path.normpath(os.path.join(BASE, cfg["out"], href))
        if not os.path.exists(p):
            errs.append(f"死链 {href}")
    # 图片声明尺寸与真实尺寸一致性（读 WebP VP8X/VP8 头）
    for m in re.finditer(r'<img src="(\.\./+images/portraits/(\w+)\.webp)" width="(\d+)" height="(\d+)"', t):
        w, h = real_webp_size(os.path.join(BASE, "images", "portraits", m.group(2) + ".webp"))
        if (int(m.group(3)), int(m.group(4))) != (w, h):
            errs.append(f"尺寸不符 {m.group(2)}: 声明 {m.group(3)}x{m.group(4)} 实际 {w}x{h}")
    if errs:
        print("[check] 失败：" + "；".join(sorted(set(errs))))
        sys.exit(1)
    print("[check] 通过：占位符/条目数/图片/JSON-LD/内链/尺寸")


def real_webp_size(path: str) -> tuple[int, int]:
    with open(path, "rb") as f:
        data = f.read(40)
    if data[12:16] == b"VP8X":
        w = int.from_bytes(data[24:27], "little") + 1
        h = int.from_bytes(data[27:30], "little") + 1
        return w, h
    if data[12:16] == b"VP8 ":
        w = int.from_bytes(data[26:28], "little") & 0x3FFF
        h = int.from_bytes(data[28:30], "little") & 0x3FFF
        return w, h
    raise SystemExit(f"无法读取 WebP 尺寸：{path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="build", help="build | all | 指定语言 key")
    args = ap.parse_args()
    if args.lang == "all":
        targets = [x["key"] for x in LANGS]
    elif args.lang == "build":
        targets = BUILD_LANGS
    else:
        targets = [args.lang]
    for key in targets:
        dst = render(key)
        check(dst, key)


if __name__ == "__main__":
    main()
