#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 country 子站的国家数据页：c/index.html + 55 个单国详情页（静态直出，含 Dataset/FAQPage 结构化数据）。

多语言（参照 scripts/build_portraits.py 的 BUILD_LANGS 做法）：
    python3 build_detail.py                 # 构建 BUILD_LANGS 中的全部语言
    python3 build_detail.py --lang ja       # 只构建日文，输出 country/ja/...
    python3 build_detail.py --lang zh       # 只重建中文，输出 country/c/...

    zh -> country/c/index.html + country/c/<iso>/index.html
    ja -> country/ja/index.html + country/ja/c/<iso>/index.html

术语与文案统一来自 data/i18n_<lang>.json；数值一律取 data/country_data.json 原值，脚本不做任何换算或补值。
"""
import json, os, sys, html

from site_meta import (analytics, adsense_head, ad_unit, share_image_meta, CSSV,
                       pairs_for, pair_slug)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(BASE)
SITE = "https://3310zx.github.io/mbti-test"

# 当前支持的语言；与 country 页树一一对应
BUILD_LANGS = ["zh", "ja"]

data = json.load(open(os.path.join(BASE, "data", "country_data.json"), encoding="utf-8"))
ed = json.load(open(os.path.join(BASE, "data", "editorial.json"), encoding="utf-8"))
INDS = {i["key"]: i for i in data["indicators"]}
COUNTRY = {c["iso3"]: c for c in data["countries"]}
ED = ed["countries"]
UPDATED = ed.get("updated") or "2026-11"

# ---------- 语言上下文（由 set_lang 注入，供各模板函数读取） ----------
LANG = "zh"
I18N = None          # data/i18n_<lang>.json 的内容；zh 为 None（直接用内嵌中文原文）


def set_lang(lang):
    global LANG, I18N
    LANG = lang
    if lang == "zh":
        I18N = None
    else:
        p = os.path.join(BASE, "data", "i18n_%s.json" % lang)
        I18N = json.load(open(p, encoding="utf-8"))


def T(key, zh, **kw):
    """取当前语言词条：zh 返回内置中文原文，其他语言用 i18n 模板格式化。"""
    if LANG == "zh" or I18N is None:
        return zh
    s = I18N["ui"][key]
    return s.format(**kw) if kw else s


def NM(iso):
    """国家显示名。"""
    if LANG == "zh":
        return COUNTRY[iso]["zh"]
    return I18N["countries"][iso]["name"]


def EDF(iso, key, default=""):
    """editorial 字段（tags / visa_note / hook / tip / cities）按语言取值。"""
    if LANG == "zh":
        return (ED.get(iso) or {}).get(key) or default
    return I18N["countries"][iso].get(key) or default


def INAME(key):
    return INDS[key]["zh"] if LANG == "zh" else I18N["indicators"][key]


def UNAME(key):
    return UNIT_TAIL.get(key, "") if LANG == "zh" else I18N["units"].get(key, "")


def RNAME(region):
    return region if LANG == "zh" else I18N["regions"][region]


def DNAME(d):
    return d["zh"] if LANG == "zh" else I18N["dims"][d["key"]]["name"]


def DNOTE(d):
    return d["note"] if LANG == "zh" else I18N["dims"][d["key"]]["note"]


DIMS = [
    {"key": "cost", "zh": "生活成本", "note": "物价水平与日常开销压力，越低越轻松", "inds": [("price_level", 1.0)]},
    {"key": "income", "zh": "收入机会", "note": "人均产出水平与就业市场松紧", "inds": [("gdp_pc_ppp", 0.5), ("unemployment", 0.5)]},
    {"key": "safety", "zh": "安全治安", "note": "以每十万人凶杀率衡量的公共安全", "inds": [("homicide", 1.0)]},
    {"key": "health", "zh": "医疗健康", "note": "预期寿命与医疗体系投入强度", "inds": [("life_expectancy", 0.55), ("health_spend", 0.45)]},
    {"key": "nature", "zh": "自然环境", "note": "空气质量、森林覆盖与人口密度", "inds": [("pm25", 0.45), ("forest", 0.35), ("density", 0.2)]},
    {"key": "society", "zh": "社会与数字化", "note": "互联网普及、城市化与女性就业参与", "inds": [("internet", 0.4), ("urbanization", 0.3), ("female_labor", 0.3)]},
]
DIM_BY_KEY = {d["key"]: d for d in DIMS}
UNIT_TAIL = {"gdp_pc_ppp": " 国际元", "life_expectancy": " 岁", "homicide": " 起", "pm25": " µg/m³",
             "forest": "%", "density": " 人/km²", "female_labor": "%", "health_spend": "%",
             "internet": "%", "unemployment": "%", "urbanization": "%"}


# ---------- 评分（与前端 index.html 的 buildScores/dimScore/totalScore 完全一致） ----------
def build_scores():
    out = {}
    for ind in data["indicators"]:
        pairs = [(c["iso3"], c["metrics"][ind["key"]]["value"]) for c in data["countries"]
                 if ind["key"] in c.get("metrics", {}) and isinstance(c["metrics"][ind["key"]].get("value"), (int, float))]
        pairs.sort(key=lambda x: x[1])
        n = len(pairs)
        m = {}
        if n == 1:
            m[pairs[0][0]] = 50.0
        i = 0
        while i < n:
            j = i
            while j + 1 < n and pairs[j + 1][1] == pairs[i][1]:
                j += 1
            pct = ((i + j) / 2) / (n - 1) * 100 if n > 1 else 50.0
            for t in range(i, j + 1):
                if ind["direction"] == -1:
                    s = 100 - pct
                elif ind["direction"] == 0:
                    s = max(0.0, 100 - 2 * abs(pct - 50))
                else:
                    s = pct
                m[pairs[t][0]] = s
            i = j + 1
        out[ind["key"]] = m
    return out


SCORES = build_scores()


def dim_score(iso, dim):
    num = den = 0.0
    for k, w in dim["inds"]:
        s = SCORES[k].get(iso)
        if isinstance(s, (int, float)):
            num += s * w
            den += w
    return num / den if den else None


def total_score(iso, weights=None):
    num = den = 0.0
    for d in DIMS:
        s = dim_score(iso, d)
        if s is not None:
            w = 1.0 if weights is None else weights[d["key"]]
            num += s * w
            den += w
    return num / den if den else 0.0


def fmt(key, v):
    if not isinstance(v, (int, float)):
        return "—"
    if key == "gdp_pc_ppp":
        return format(int(round(v)), ",")
    if key == "homicide":
        return f"{v:.2f}"
    return f"{v:.1f}"


def unit_text(key):
    """Dataset 里的单位文本：物价指数统一用「美国=100」口径。"""
    if key == "price_level":
        return "US=100" if LANG == "zh" else "米国=100"
    return UNAME(key)


def fact(key, m):
    if not m or not isinstance(m.get("value"), (int, float)):
        return None
    name = INAME(key)
    if key == "price_level":
        if LANG == "zh":
            return f"{name} {fmt(key, m['value'])}（美国=100，{m['year']} 年）"
        return T("fact_price", "", name=name, val=fmt(key, m['value']), year=m["year"])
    if LANG == "zh":
        return f"{name} {fmt(key, m['value'])}{UNIT_TAIL.get(key,'')}（{m['year']} 年）"
    return T("fact_general", "", name=name, val=fmt(key, m['value']), unit=UNAME(key), year=m["year"])


RANK = {}
for d in DIMS:
    rows = [(iso, dim_score(iso, d)) for iso in COUNTRY]
    rows = [r for r in rows if r[1] is not None]
    rows.sort(key=lambda x: (-x[1], x[0]))
    RANK[d["key"]] = {iso: i + 1 for i, (iso, s) in enumerate(rows)}
    RANK[d["key"]]["_n"] = len(rows)

TOTAL = sorted(COUNTRY, key=lambda iso: (-total_score(iso), iso))
TRANK = {iso: i + 1 for i, iso in enumerate(TOTAL)}

REGION = {}
for c in data["countries"]:
    REGION.setdefault(c["region"], []).append(c["iso3"])


# ---------- HTML 片段 ----------
def crumbs(items, up="../"):
    parts = []
    for name, href in items[:-1]:
        parts.append(f'<a href="{href}">{name}</a>')
    parts.append(f'<span aria-current="page">{items[-1][0]}</span>')
    sep = '<span class="sep">/</span>'
    aria = "面包屑" if LANG == "zh" else T("crumbs_aria", "")
    return f'<nav class="crumbs" aria-label="{aria}">{sep.join(parts)}</nav>'


def bars(iso, lead=None):
    out = []
    for d in DIMS:
        s = dim_score(iso, d)
        v = "—" if s is None else str(int(round(s)))
        width = 0 if s is None else int(round(s))
        cls = " lead" if d["key"] == lead else ""
        out.append(
            f'<div class="bar-row"><span class="bar-label">{DNAME(d)}</span>'
            f'<span class="bar-track"><span class="bar-fill{cls}" style="width:{width}%"></span></span>'
            f'<span class="bar-val">{v}</span></div>')
    return "".join(out)


def tier_label(i, x):
    t = x.get("tier")
    if LANG == "zh":
        names = {1: "第一档 · 大城市", 2: "第二档 · 区域中心", 3: "第三档 · 小城与郊区"}
        return names.get(t, ["第一档", "第二档", "第三档"][i % 3])
    names = {1: T("tier1", ""), 2: T("tier2", ""), 3: T("tier3", "")}
    return names.get(t, [T("tier1", ""), T("tier2", ""), T("tier3", "")][i % 3])


def city_block(iso):
    """城市租金卡片：城市名与档位标签按语言取，租金一律沿用中文 editorial 数值。"""
    src = ED.get(iso) or {}
    zh_cities = src.get("cities") or []
    if not zh_cities:
        return ""
    if LANG == "zh":
        names = [x["name"] for x in zh_cities]
    else:
        names = [x["name"] for x in (EDF(iso, "cities") or [])]
        if len(names) != len(zh_cities):
            names = [x["name"] for x in zh_cities]
    suffix = " / 月租参考" if LANG == "zh" else T("rent_suffix", "")
    cards = "".join(
        f'<div class="city"><p class="tier">{tier_label(i, x)}</p><h4>{html.escape(names[i])}</h4>'
        f'<p class="rent">${html.escape(str(x["rent"]))}<small>{suffix}</small></p></div>'
        for i, x in enumerate(zh_cities))
    return f'<div class="city-grid">{cards}</div>'


def tag_block(iso):
    tags = EDF(iso, "tags") or []
    return "".join(f'<span class="tag">{html.escape(t)}</span>' for t in tags)


def metrics_rows(iso):
    c = COUNTRY[iso]
    lab_ind = T("th_ind", "指标")
    lab_val = T("th_val", "数值")
    lab_year = T("th_year", "年份")
    lab_pct = T("th_pct", "分位分")
    miss = T("miss", "缺失")
    rows = []
    for ind in data["indicators"]:
        m = c["metrics"].get(ind["key"])
        if not m or not isinstance(m.get("value"), (int, float)):
            rows.append(f'<tr><td data-label="{lab_ind}">{INAME(ind["key"])}</td><td class="num na" data-label="{lab_val}">{miss}</td>'
                        f'<td class="num" data-label="{lab_year}">—</td><td class="num na" data-label="{lab_pct}">—</td></tr>')
            continue
        q = SCORES[ind["key"]].get(iso)
        qtxt = "—" if q is None else str(int(round(q)))
        rows.append(
            f'<tr><td data-label="{lab_ind}">{INAME(ind["key"])}<span class="dim"> · {ind["code"]}</span></td>'
            f'<td class="num" data-label="{lab_val}">{fmt(ind["key"], m["value"])}{UNAME(ind["key"])}</td>'
            f'<td class="num" data-label="{lab_year}">{m["year"]}</td><td class="num" data-label="{lab_pct}">{qtxt}</td></tr>')
    return "".join(rows)


def kv_strip(iso):
    c = COUNTRY[iso]
    picks = ["price_level", "gdp_pc_ppp", "life_expectancy", "homicide"]
    cells = []
    for k in picks:
        m = c["metrics"].get(k)
        if not m or not isinstance(m.get("value"), (int, float)):
            continue
        ytxt = f'{m["year"]} 年 · 世行' if LANG == "zh" else T("kv_year", "", year=m["year"])
        cells.append(f'<div class="kv"><p class="kv-k">{INAME(k)}</p>'
                     f'<p class="kv-v">{fmt(k, m["value"])}<small>{UNAME(k)}</small></p>'
                     f'<p class="kv-y">{ytxt}</p></div>')
    return f'<div class="kv-strip">{"".join(cells)}</div>'


def head(title, desc, canon, alt_zh, alt_ja, ctx, extra=""):
    """ctx: sr(站点根相对) / cp(country 目录相对) / nav / lang_href / lang_hl / lang_label / site_name"""
    sr, cp = ctx["sr"], ctx["cp"]
    e = html.escape(desc, quote=True)
    t = html.escape(title, quote=True)
    navs = "".join(f'      <a href="{h}">{lab}</a>\n' for h, lab in ctx["nav"])
    langline = f'      <a href="{ctx["lang_href"]}" hreflang="{ctx["lang_hl"]}" lang="{ctx["lang_hl"]}">{ctx["lang_label"]}</a>\n'
    html_lang = "zh-CN" if LANG == "zh" else I18N["html_lang"]
    og_locale = "zh_CN" if LANG == "zh" else I18N["og_locale"]
    site_name = "最适合生活的国家" if LANG == "zh" else I18N["ui"].get("og_site_name", "住みやすい国データ")
    brand = f'MBTI<em>·</em>人生地理' if LANG == "zh" else f'MBTI<em>・</em>人生地理'
    toggle = "打开导航" if LANG == "zh" else T("nav_toggle", "")
    return f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{e}">
<meta name="color-scheme" content="light">
<meta name="robots" content="max-image-preview:large">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="zh-CN" href="{alt_zh}">
<link rel="alternate" hreflang="ja" href="{alt_ja}">
<link rel="alternate" hreflang="x-default" href="{alt_zh}">
<meta property="og:type" content="article">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{e}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="{og_locale}">
<meta property="og:site_name" content="{site_name}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{e}">
{share_image_meta(LANG)}{adsense_head()}{analytics()}<link rel="stylesheet" href="{cp}assets/country.css?v={CSSV}">
<script defer src="{cp}assets/nav.js?v={CSSV}"></script>
{extra}</head>
<body>
<header class="site-head">
  <div class="wrap head-inner">
    <a class="brand" href="{sr}">{brand}</a>
    <button class="nav-toggle" type="button" aria-controls="site-nav" aria-expanded="false" aria-label="{toggle}"><i></i><i></i><i></i></button>
    <nav class="head-nav" id="site-nav">
{navs}{langline}    </nav>
  </div>
</header>
<main id="main">
"""


SHARE_JS = """
(function(){
  var u = location.href;
  var OK = "__OK__", NG = "__NG__";
  function done(b, m){ b.textContent = m; setTimeout(function(){ b.textContent = b.dataset.t; }, 2000); }
  function cp(b){
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(u).then(function(){ done(b, OK); }, function(){ done(b, NG); });
      return;
    }
    var t = document.createElement("textarea"); t.value = u; document.body.appendChild(t); t.select();
    try { done(b, document.execCommand("copy") ? OK : NG); } catch (e) { done(b, NG); }
    t.parentNode && t.parentNode.removeChild(t);
  }
  var s = document.getElementById("sharePage"), c = document.getElementById("copyPage");
  if (s) s.addEventListener("click", function(){
    if (navigator.share) { navigator.share({ title: document.title, url: u }).catch(function(){}); } else { cp(s); }
  });
  if (c) c.addEventListener("click", function(){ cp(c); });
})();
"""


def foot():
    ok = "链接已复制" if LANG == "zh" else T("share_copied", "")
    ng = "复制失败" if LANG == "zh" else T("share_failed", "")
    share_js = SHARE_JS.replace("__OK__", ok).replace("__NG__", ng)
    if LANG == "zh":
        h2 = "把这一页分享出去"
        btn = "分享本页"
        copy_btn = "复制链接"
        note = "分享后对方打开的是同一份公开数据页，不含任何个人信息。"
        disc = ("免责声明：本页基于公开统计数据整理，非移民、法律或税务建议。"
                "任何迁居、签证、税务安排请咨询持牌专业人士。")
        src = ('数据来源：世界银行公开数据（<a href="https://data.worldbank.org/" target="_blank" rel="noopener">'
               'World Bank Open Data</a>，CC BY 4.0），各指标年份单独标注；城市租金与签证标签为编辑整理，非官方数据。更新：' + UPDATED)
        copy = "MBTI · 人生地理 / Where To Live"
        data_t_share, data_t_copy = "分享本页", "复制链接"
    else:
        h2 = T("foot_share_h2", "")
        btn = T("foot_share_btn", "")
        copy_btn = T("foot_copy_btn", "")
        note = T("foot_share_note", "")
        disc = T("foot_disc", "")
        src = T("foot_src", "", updated=UPDATED)
        copy = T("foot_copy", "")
        data_t_share, data_t_copy = btn, copy_btn
    return f"""<section class="wrap section">
  <h2>{h2}</h2>
  <div class="hero-actions" style="margin:0">
    <button class="btn primary" id="sharePage" type="button" data-t="{data_t_share}">{btn}</button>
    <button class="btn" id="copyPage" type="button" data-t="{data_t_copy}">{copy_btn}</button>
  </div>
  <p class="weight-note">{note}</p>
  <script>{share_js}</script>
</section>
</main>
<footer class="site-foot">
  <div class="wrap">
    <p class="disc">{disc}</p>
    <p class="src">{src}</p>
    <p class="copy">{copy}</p>
  </div>
</footer>
</body>
</html>
"""


def strength_text(iso):
    ds = [(d, dim_score(iso, d)) for d in DIMS]
    ds = [(d, s) for d, s in ds if s is not None]
    ds.sort(key=lambda x: -x[1])
    best_d, best_s = ds[0]
    worst_d, worst_s = ds[-1]
    c = COUNTRY[iso]
    ind_best = max(best_d["inds"], key=lambda kv: SCORES[kv[0]].get(iso, 0))
    m = c["metrics"].get(ind_best[0])
    best_fact = fact(ind_best[0], m) or ""
    ind_worst = min(worst_d["inds"], key=lambda kv: SCORES[kv[0]].get(iso, 100))
    mw = c["metrics"].get(ind_worst[0])
    worst_fact = fact(ind_worst[0], mw) or ""
    return best_d, best_s, best_fact, worst_d, worst_s, worst_fact


def tier_word(s):
    if LANG == "zh":
        return "强项" if s >= 70 else ("中位水平" if s >= 50 else "明显偏弱")
    if s >= 70:
        return T("tier_word_strong", "")
    return T("tier_word_mid", "") if s >= 50 else T("tier_word_weak", "")


def country_page(iso):
    c = COUNTRY[iso]
    zh = NM(iso)
    slug = iso.lower()
    if LANG == "zh":
        sr, cp = "../../../", "../../"
        canon = f"{SITE}/country/c/{slug}/"
        alt_zh, alt_ja = canon, f"{SITE}/country/ja/c/{slug}/"
        ctx = {"sr": sr, "cp": cp,
               "nav": [(cp + "c/", "国家数据"), (cp + "rank/", "维度榜单"), (cp + "compare/", "对比")],
               "lang_href": f"{cp}ja/c/{slug}/", "lang_hl": "ja", "lang_label": "日本語"}
        home_main = sr
        crumb_c = cp + "c/"
    else:
        sr, cp = "../../../../", "../../../"
        canon = f"{SITE}/country/ja/c/{slug}/"
        alt_zh, alt_ja = f"{SITE}/country/c/{slug}/", canon
        ctx = {"sr": sr, "cp": cp,
               "nav": [(cp + "c/", T("nav_c", "")), (cp + "rank/", T("nav_rank", "")), (cp + "compare/", T("nav_compare", ""))],
               "lang_href": f"{cp}c/{slug}/", "lang_hl": "zh-CN", "lang_label": T("lang_link_label", "")}
        home_main = sr + "ja/"
        crumb_c = "../../"

    tot = total_score(iso)
    best_d, best_s, best_fact, worst_d, worst_s, worst_fact = strength_text(iso)
    n_iso = len(TOTAL)

    if LANG == "zh":
        title = f"{zh}生活数据：物价、收入、治安、医疗、自然与社会六维度评分与排名"
        desc = (f"{zh}在 55 个国家与地区中综合匹配分 {tot:.1f}（六维等权），排第 {TRANK[iso]} 位；"
                f"最强的是{best_d['zh']}（{best_s:.0f} 分），最弱的是{worst_d['zh']}（{worst_s:.0f} 分）。"
                f"含 12 项世界银行指标原始值与年份、三大城市一居室租金参考与签证门槛标签。")
        h1 = f"{zh}生活数据：六个维度到底强在哪、弱在哪"
        kicker = f'{c["region"]} · World Bank Data'
        lede = (f'按六个维度等权计算，{zh}在 {n_iso} 个候选国家里综合匹配分 <strong>{tot:.1f}</strong>，排第 <strong>{TRANK[iso]}</strong> 位。\n'
                f'    最强的一项是{DNAME(best_d)}（{best_s:.0f} 分，第 {RANK[best_d["key"]][iso]} 位），'
                f'{DNAME(worst_d)}是它的短板（{worst_s:.0f} 分，第 {RANK[worst_d["key"]][iso]} 位）。\n'
                f'    下面每一项都标注了世界银行的原始值、年份与在 55 国/地区中的分位分。')
    else:
        title = T("d_title", "", name=zh, tot=f"{tot:.1f}", trank=TRANK[iso],
                  best=DNAME(best_d), best_s=f"{best_s:.0f}", worst=DNAME(worst_d), worst_s=f"{worst_s:.0f}")
        desc = T("d_desc", "", name=zh, tot=f"{tot:.1f}", trank=TRANK[iso], n=n_iso,
                 best=DNAME(best_d), best_s=f"{best_s:.0f}", worst=DNAME(worst_d), worst_s=f"{worst_s:.0f}")
        h1 = T("d_h1", "", name=zh)
        kicker = T("d_kicker", "", region=RNAME(c["region"]))
        lede = T("d_lede", "", name=zh, tot=f"{tot:.1f}", trank=TRANK[iso], n=n_iso,
                 best=DNAME(best_d), best_s=f"{best_s:.0f}", best_rank=RANK[best_d["key"]][iso],
                 worst=DNAME(worst_d), worst_s=f"{worst_s:.0f}", worst_rank=RANK[worst_d["key"]][iso])

    # ---------- FAQ ----------
    if LANG == "zh":
        price_fact = fact('price_level', c['metrics'].get('price_level')) or '物价水平指数缺失'
        gdp_fact = fact('gdp_pc_ppp', c['metrics'].get('gdp_pc_ppp')) or '人均 GDP 缺失'
        faq = [
            (f"{zh}在 55 个国家与地区里综合排第几？",
             f"按六个维度等权计算，{zh}的综合匹配分是 {tot:.1f}，在 {len(TOTAL)} 个国家中排第 {TRANK[iso]} 位。"
             f"其中{DNAME(best_d)} {best_s:.0f} 分（{tier_word(best_s)}，第 {RANK[best_d['key']][iso]} 位），"
             f"{DNAME(worst_d)} {worst_s:.0f} 分（{tier_word(worst_s)}，第 {RANK[worst_d['key']][iso]} 位）。"
             f"分数是按候选国家内部排序折算的分位分，不代表绝对好坏。"),
            (f"{zh}的物价和收入在世界范围内处于什么水平？",
             f"{price_fact}；{gdp_fact}。"
             f"两项都是宏观平均口径：物价指数是 PPP 转换因子与市场汇率之比，不含个人消费结构差异；"
             f"人均 GDP 按购买力平价折算，反映产出水平而非到手工资。"),
            (f"只看数据就能决定要不要搬去{zh}吗？",
             "不能。这里的指标都是国家层面的统计平均，覆盖不到城市与街区差异、签证与税制、语言与公共服务可及性，"
             "也无法反映你个人的行业与家庭情况。数据只适合用来做初步筛选与横向比较，"
             "真正的迁居、签证与税务安排请咨询持牌专业人士。"),
        ]
    else:
        price_fact = fact('price_level', c['metrics'].get('price_level')) or T("faq_price_miss", "")
        gdp_fact = fact('gdp_pc_ppp', c['metrics'].get('gdp_pc_ppp')) or T("faq_gdp_miss", "")
        faq = [
            (T("faq_q1", "", name=zh),
             T("faq_a1", "", name=zh, tot=f"{tot:.1f}", n=n_iso, trank=TRANK[iso],
               best=DNAME(best_d), best_s=f"{best_s:.0f}", best_word=tier_word(best_s), best_rank=RANK[best_d["key"]][iso],
               worst=DNAME(worst_d), worst_s=f"{worst_s:.0f}", worst_word=tier_word(worst_s), worst_rank=RANK[worst_d["key"]][iso])),
            (T("faq_q2", "", name=zh), T("faq_a2", "", price=price_fact, gdp=gdp_fact)),
            (T("faq_q3", "", name=zh), T("faq_a3", "")),
        ]

    # ---------- 结构化数据 ----------
    ds_name = (f"{zh}生活条件数据集：12 项世界银行指标" if LANG == "zh"
               else T("ds_name", "", name=zh))
    if LANG == "zh":
        ds_desc = (f"{zh}在物价水平、人均 GDP（PPP）、预期寿命、凶杀率、PM2.5、森林覆盖率、人口密度、"
                   f"女性劳动参与率、医疗支出占 GDP、互联网使用率、失业率、城市化率共 12 项指标上的最新可用数值与年份。")
        var_measured = [
            {"@type": "PropertyValue", "name": ind["zh"],
             "value": c["metrics"][ind["key"]]["value"] if ind["key"] in c["metrics"] else None,
             "unitText": UNIT_TAIL.get(ind["key"], "US=100" if ind["key"] == "price_level" else ""),
             "measurementTechnique": ind["code"],
             "description": f"{ind['zh']}，数据年份 "
                            f"{c['metrics'][ind['key']]['year'] if ind['key'] in c['metrics'] else '缺失'}"}
            for ind in data["indicators"]]
    else:
        ds_desc = T("ds_desc", "", name=zh)
        var_measured = [
            {"@type": "PropertyValue", "name": INAME(ind["key"]),
             "value": c["metrics"][ind["key"]]["value"] if ind["key"] in c["metrics"] else None,
             "unitText": unit_text(ind["key"]),
             "measurementTechnique": ind["code"],
             "description": T("ds_var_desc", "", name=INAME(ind["key"]),
                              year=(c["metrics"][ind["key"]]["year"] if ind["key"] in c["metrics"] else T("miss", "")))}
            for ind in data["indicators"]]

    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": ds_name,
        "description": ds_desc,
        "url": canon,
        "isAccessibleForFree": True,
        "creator": {"@type": "Organization", "name": "MBTI · 人生地理" if LANG == "zh" else "MBTI・人生地理"},
        "publisher": {"@type": "Organization", "name": "MBTI · 人生地理" if LANG == "zh" else "MBTI・人生地理"},
        "inLanguage": "zh-CN" if LANG == "zh" else I18N["html_lang"],
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "isBasedOn": "https://data.worldbank.org/",
        "spatialCoverage": {"@type": "Country", "name": zh},
        "temporalCoverage": "2020/2025",
        "variableMeasured": var_measured,
    }
    faqjson = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": "zh-CN" if LANG == "zh" else I18N["html_lang"],
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq],
    }
    ld = ('<script type="application/ld+json">' + json.dumps(dataset, ensure_ascii=False) + '</script>\n'
          '<script type="application/ld+json">' + json.dumps(faqjson, ensure_ascii=False) + '</script>\n')

    ds_sorted = sorted([(d, dim_score(iso, d)) for d in DIMS if dim_score(iso, d) is not None], key=lambda x: -x[1])
    lab_dim = T("th_dim", "维度")
    lab_score = T("th_score", "分数")
    lab_rank = T("th_rank", "排名")
    lab_what = T("th_what", "衡量什么")
    lab_ind = T("th_ind", "指标")
    lab_val = T("th_val", "数值")
    lab_year = T("th_year", "年份")
    if LANG == "zh":
        rank_txt = lambda k: f'第 {RANK[k][iso]} / {RANK[k]["_n"]}'
    else:
        rank_txt = lambda k: T("rank_of", "", rank=RANK[k][iso], n=RANK[k]["_n"])
    dim_rows = "".join(
        f'<tr><td data-label="{lab_dim}"><a href="{cp}rank/{d["key"]}/">{DNAME(d)}</a></td>'
        f'<td class="num" data-label="{lab_score}">{s:.0f}</td>'
        f'<td class="num" data-label="{lab_rank}">{rank_txt(d["key"])}</td>'
        f'<td class="dim" data-label="{lab_what}">{DNOTE(d)}</td></tr>' for d, s in ds_sorted)

    peers = [x for x in REGION[c["region"]] if x != iso][:6]
    peer_links = "".join(f'<a class="peer" href="../{p.lower()}/">{NM(p)}'
                         f'<span>{T("peer_score", str(int(round(total_score(p)))) + " 分", s=int(round(total_score(p))))}</span></a>' for p in peers)
    compare_url = cp + f"compare/?a={iso}"

    pl = pairs_for(iso)
    pair_html = ""
    if pl:
        links = "".join(
            f'<a class="peer" href="{cp}compare/{pair_slug(x, y)}/">{NM(x)} vs {NM(y)}'
            f'<span>' + (f'综合分 {total_score(x):.1f} 对 {total_score(y):.1f}' if LANG == "zh"
                         else T("pair_score", "", a=f"{total_score(x):.1f}", b=f"{total_score(y):.1f}")) + '</span></a>'
            for x, y in pl)
        h2pairs = f"与{zh}直接对比的国家" if LANG == "zh" else T("sec_pairs", "", name=zh)
        notepairs = ("每一页都把两个国家的六个维度分数、12 项世界银行原始指标与年份放在同一张表里逐行对照，"
                     "并算出成本与收入的实际落差，用来判断「多花的钱换到了什么」。") if LANG == "zh" else T("note_pairs", "")
        pair_html = (f'<section class="wrap section">\n  <h2>{h2pairs}</h2>\n'
                     f'  <div class="peer-grid">{links}</div>\n'
                     f'  <p class="weight-note">{notepairs}</p>\n</section>\n\n')

    if LANG == "zh":
        note_dims = (f'分数含义：在 {n_iso} 个候选国家内部排序折算成 0–100 分（分位排名制）。\n'
                     f'      70 分以上可视为该维度的强项，50 分附近是中等，40 分以下说明它在同类国家里明显落后。')
        best_para = (f'{best_fact}。这一项在 {RANK[best_d["key"]]["_n"]} 个有数据的国家里排第 {RANK[best_d["key"]][iso]} 位，\n'
                     f'      是{zh}整体分数的主要来源。')
        worst_para = f'{worst_fact}。这一项排在第 {RANK[worst_d["key"]][iso]} 位，是选择{zh}时需要主动权衡的部分。'
        label_best = f'最强：{DNAME(best_d)} · {best_s:.0f} 分'
        label_worst = f'最弱：{DNAME(worst_d)} · {worst_s:.0f} 分'
        note_city = "租金为市中心一居室挂牌价区间的中位水平，按编辑口径整理成三档，用于横向感受城市间落差，不是官方统计，也不含水电与押金。"
        visa_tail = "以上为编辑整理的常见路径概述，不构成法律意见；具体门槛、配额与审理时间以各国移民部门最新公告为准。"
        visa_line = f'{EDF(iso, "visa_note")} 实用提示：{EDF(iso, "tip")}'
        tbl_src = "数据来源：世界银行公开数据 API（CC BY 4.0），取各国最新可用年份的原始值，未做估算、插值或填充；缺失值原样保留。分位分为候选国家内部相对位置，不是国际通行评级。"
        peer_note = (f'分数为六维等权下的综合匹配分。想看单一维度的完整排序，可到<a href="{cp}rank/">维度榜单</a>；'
                     f'想按自己的权重算，<a href="{sr}#intro">做 18 道题</a>后可以拖动滑块重算。')
        h2_dims, h2_sw, h2_city, h2_visa, h2_metrics, h2_peer, h2_faq = ("六个维度的分位分", "强项与短板", "城市生活成本：一居室月租参考",
                                                                       "签证与居留门槛", "12 项原始数据与年份", "同区域国家的横向比较", "常见问题")
        block_dim = "维度明细与排名"
    else:
        note_dims = T("note_dims", "", n=n_iso)
        best_para = T("text_best", "", fact=best_fact, n=RANK[best_d["key"]]["_n"],
                      rank=RANK[best_d["key"]][iso], name=zh)
        worst_para = T("text_worst", "", fact=worst_fact, rank=RANK[worst_d["key"]][iso], name=zh)
        label_best = T("block_best", "", best=DNAME(best_d), best_s=f"{best_s:.0f}")
        label_worst = T("block_worst", "", worst=DNAME(worst_d), worst_s=f"{worst_s:.0f}")
        note_city = T("note_city", "")
        visa_tail = T("note_visa", "")
        visa_line = f'{EDF(iso, "visa_note")} {T("tip_prefix", "")}{EDF(iso, "tip")}'
        tbl_src = T("tbl_src", "")
        peer_note = T("note_peer", "", rank_href=cp + "rank/", test_href=home_main + "#intro")
        h2_dims, h2_sw, h2_city, h2_visa, h2_metrics, h2_peer, h2_faq = (
            T("sec_dims", ""), T("sec_sw", ""), T("sec_city", ""), T("sec_visa", ""),
            T("sec_metrics", ""), T("sec_peer", ""), T("sec_faq", ""))
        block_dim = T("block_dimdetail", "")

    body = f"""{crumbs([(T("crumbs_home", "首页"), home_main), (T("crumbs_c", "国家数据"), crumb_c), (zh, "")])}
<section class="page-hero">
  <div class="wrap">
    <p class="kicker">{kicker}</p>
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
    <div class="hero-actions">
      <a class="btn primary" href="{home_main}#intro">{T("btn_test", "测一测我该去哪")}</a>
      <a class="btn ghost" href="{compare_url}">{T("btn_compare", "与其它国家对比")}</a>
    </div>
    {kv_strip(iso)}
  </div>
</section>

<section class="wrap section">
  <h2>{h2_dims}</h2>
  <div class="split">
    <div class="panel">
      {bars(iso, best_d["key"])}
      <p class="weight-note">{note_dims}</p>
    </div>
    <div class="panel">
      <p class="block-label">{block_dim}</p>
      <div class="tbl-wrap"><table class="metrics stack"><thead><tr><th>{lab_dim}</th><th style="text-align:right">{lab_score}</th>
      <th style="text-align:right">{lab_rank}</th><th>{lab_what}</th></tr></thead><tbody>{dim_rows}</tbody></table></div>
    </div>
  </div>
</section>

<section class="wrap section">
  <h2>{h2_sw}</h2>
  <div class="split">
    <div class="panel">
      <p class="block-label">{label_best}</p>
      <p>{best_para}</p>
    </div>
    <div class="panel">
      <p class="block-label">{label_worst}</p>
      <p>{worst_para}</p>
    </div>
  </div>
  <p class="weight-note">{EDF(iso, "hook")}</p>
</section>

{ad_unit(T("ad1", "广告 · 下方继续看城市租金与签证门槛"))}

<section class="wrap section">
  <h2>{h2_city}</h2>
  {city_block(iso)}
  <p class="weight-note">{note_city}</p>
</section>

<section class="wrap section">
  <h2>{h2_visa}</h2>
  <div class="tagrow">{tag_block(iso)}</div>
  <p class="weight-note">{visa_line}</p>
  <p class="weight-note">{visa_tail}</p>
</section>

<section class="wrap section">
  <h2>{h2_metrics}</h2>
  <div class="tbl-wrap"><table class="metrics stack plain">
  <thead><tr><th>{lab_ind}</th><th style="text-align:right">{lab_val}</th><th style="text-align:right">{lab_year}</th>
  <th style="text-align:right">{T("th_pct", "55 国/地区分位分")}</th></tr></thead>
  <tbody>{metrics_rows(iso)}</tbody></table></div>
  <p class="tbl-src">{tbl_src}</p>
</section>

<section class="wrap section">
  <h2>{h2_peer}</h2>
  <div class="peer-grid">{peer_links}</div>
  <p class="weight-note">{peer_note}</p>
</section>

{pair_html}{ad_unit(T("ad2", "广告 · 下方为常见问题"))}
<section class="wrap section">
  <h2>{h2_faq}</h2>
  <div class="faq-grid">
  {"".join(f'<details class="faq-item"><summary>{q}</summary><div class="faq-body"><p>{a}</p></div></details>' for q, a in faq)}
  </div>
</section>
"""
    return head(title, desc, canon, alt_zh, alt_ja, ctx, ld) + body + foot()


def index_page():
    slug_dir = "" if LANG == "zh" else "c/"
    if LANG == "zh":
        sr, cp = "../../", "../"
        canon = f"{SITE}/country/c/"
        alt_zh, alt_ja = canon, f"{SITE}/country/ja/"
        ctx = {"sr": sr, "cp": cp,
               "nav": [(cp + "c/", "国家数据"), (cp + "rank/", "维度榜单"), (cp + "compare/", "对比")],
               "lang_href": f"{cp}ja/", "lang_hl": "ja", "lang_label": "日本語"}
        home_main = sr
        crumb_c = ""
        nav_c_self = cp + "c/"
    else:
        sr, cp = "../../", "../"
        canon = f"{SITE}/country/ja/"
        alt_zh, alt_ja = f"{SITE}/country/c/", canon
        ctx = {"sr": sr, "cp": cp,
               "nav": ("./", T("nav_c", "")), }
        ctx["nav"] = [("./", T("nav_c", "")), (cp + "rank/", T("nav_rank", "")), (cp + "compare/", T("nav_compare", ""))]
        ctx["lang_href"] = "../c/"
        ctx["lang_hl"] = "zh-CN"
        ctx["lang_label"] = T("lang_link_label", "")
        home_main = sr + "ja/"
        crumb_c = ""
        nav_c_self = "./"

    n_iso = len(TOTAL)
    if LANG == "zh":
        title = "55 个国家与地区的生活数据总表：六维度评分、排名与原始指标"
        desc = ("55 个候选国家与地区的生活条件总表：综合匹配分、六维度分数、区域与 12 项世界银行指标年份，"
                "按综合分排序，可点表头切换排序，每行进入单国详情页。")
        h1 = "55 个国家与地区的生活数据总表"
        kicker = "55 Countries &amp; Regions · 6 Dimensions"
        lede = (f'综合分是六个维度的等权平均，只代表「默认权重下」的相对位置。真实排序取决于你更在意什么——\n'
                f'    到<a href="{home_main}#intro">测试页</a>答完 18 道题，就能用你自己的权重重算；也可以直接进单国页看原始指标与年份。')
        tbl_note = '点击表头可切换排序。分数为该维度在 55 国/地区中的分位分（0–100），"—" 表示世界银行未收录该国该项数据。'
        h2_rank = "按维度看榜单"
        top20 = "Top 20 榜单"
        lab_region, lab_country, lab_total = "区域", "国家", "综合分"
    else:
        title = T("idx_title", "")
        desc = T("idx_desc", "")
        h1 = T("idx_h1", "")
        kicker = T("idx_kicker", "")
        lede = T("idx_lede", "", test_href=home_main + "#intro")
        tbl_note = T("idx_note", "")
        h2_rank = T("idx_sec_rank", "")
        top20 = T("idx_top20", "")
        lab_region, lab_country, lab_total = T("th_region", ""), T("th_country", ""), T("th_total", "")

    rows = []
    for iso in TOTAL:
        cells = [f'<td class="dim">{RNAME(COUNTRY[iso]["region"])}</td>',
                 f'<td class="nm"><a href="{slug_dir}{iso.lower()}/">{NM(iso)}</a></td>',
                 f'<td class="num">{total_score(iso):.1f}</td>']
        for d in DIMS:
            s = dim_score(iso, d)
            cells.append(f'<td class="num">{"—" if s is None else int(round(s))}</td>')
        rows.append('<tr data-row>' + "".join(cells) + "</tr>")
    thead = (f'<tr><th data-sort="text">{lab_region}</th><th data-sort="text">{lab_country}</th>'
             f'<th data-sort="num" style="text-align:right">{lab_total}</th>'
             + "".join(f'<th data-sort="num" style="text-align:right">{DNAME(d)}</th>' for d in DIMS)
             + "</tr>")
    sort_locale = "zh" if LANG == "zh" else "ja"
    body = f"""{crumbs([(T("crumbs_home", "首页"), home_main), (T("crumbs_c", "国家数据"), "")])}
<section class="page-hero">
  <div class="wrap">
    <p class="kicker">{kicker}</p>
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>
<section class="wrap section">
  <div class="tbl-wrap"><table class="metrics sortable"><thead>{thead}</thead><tbody>{"".join(rows)}</tbody></table></div>
  <p class="tbl-src">{tbl_note}</p>
</section>
<section class="wrap section">
  <h2>{h2_rank}</h2>
  <div class="peer-grid">{"".join(f'<a class="peer" href="{cp}rank/{d["key"]}/">{DNAME(d)}<span>{top20}</span></a>' for d in DIMS)}</div>
</section>
<script>
(function(){{
  var t=document.querySelector("table.sortable");if(!t)return;
  var tb=t.tBodies[0],th=t.tHead.rows[0].cells;
  for(var i=0;i<th.length;i++){{
    (function(idx,cell){{
      cell.style.cursor="pointer";
      cell.addEventListener("click",function(){{
        var num=cell.getAttribute("data-sort")==="num";
        var dir=cell.getAttribute("data-dir")==="asc"?-1:1;
        for(var j=0;j<th.length;j++)th[j].removeAttribute("data-dir");
        cell.setAttribute("data-dir",dir===1?"desc":"asc");
        var rows=Array.prototype.slice.call(tb.rows);
        rows.sort(function(a,b){{
          var x=a.cells[idx].textContent.trim(),y=b.cells[idx].textContent.trim();
          if(num){{var nx=parseFloat(x),ny=parseFloat(y);
            if(isNaN(nx))return 1;if(isNaN(ny))return -1;return (nx-ny)*dir;}}
          return x.localeCompare(y,"{sort_locale}")*dir;
        }});
        rows.forEach(function(r){{tb.appendChild(r);}});
      }});
    }})(i,th[i]);
  }}
}})();
</script>
"""
    return head(title, desc, canon, alt_zh, alt_ja, ctx) + body + foot()


def build(lang):
    set_lang(lang)
    if lang == "zh":
        out_c = os.path.join(BASE, "c")
        idx_path = os.path.join(BASE, "c", "index.html")
    else:
        out_c = os.path.join(BASE, lang, "c")
        idx_path = os.path.join(BASE, lang, "index.html")
    os.makedirs(out_c, exist_ok=True)
    os.makedirs(os.path.dirname(idx_path), exist_ok=True)
    open(idx_path, "w", encoding="utf-8").write(index_page())
    n = 0
    for iso in COUNTRY:
        d = os.path.join(out_c, iso.lower())
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(country_page(iso))
        n += 1
    print("[%s] generated %s + %d country pages" % (lang, os.path.relpath(idx_path, ROOT), n))


def main():
    langs = list(BUILD_LANGS)
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--lang" and i + 1 < len(args):
            langs = [args[i + 1]]
        elif a.startswith("--lang="):
            langs = [a.split("=", 1)[1]]
    for lang in langs:
        build(lang)


if __name__ == "__main__":
    main()
