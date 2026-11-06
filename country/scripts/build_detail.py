#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 /country/c/ 国家数据索引与 55 个单国详情页（静态直出，含 Dataset/FAQPage 结构化数据）。"""
import json, os, html, datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(BASE)
SITE = "https://3310zx.github.io/mbti-test"
data = json.load(open(os.path.join(BASE, "data", "country_data.json"), encoding="utf-8"))
ed = json.load(open(os.path.join(BASE, "data", "editorial.json"), encoding="utf-8"))
INDS = {i["key"]: i for i in data["indicators"]}
COUNTRY = {c["iso3"]: c for c in data["countries"]}
ED = ed["countries"]

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


def fact(key, m):
    if not m or not isinstance(m.get("value"), (int, float)):
        return None
    if key == "price_level":
        return f"{INDS[key]['zh']} {fmt(key, m['value'])}（美国=100，{m['year']} 年）"
    return f"{INDS[key]['zh']} {fmt(key, m['value'])}{UNIT_TAIL.get(key,'')}（{m['year']} 年）"


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
    return f'<nav class="crumbs" aria-label="面包屑">{sep.join(parts)}</nav>'


def bars(iso, lead=None):
    out = []
    for d in DIMS:
        s = dim_score(iso, d)
        v = "—" if s is None else str(int(round(s)))
        width = 0 if s is None else int(round(s))
        cls = " lead" if d["key"] == lead else ""
        out.append(
            f'<div class="bar-row"><span class="bar-label">{d["zh"]}</span>'
            f'<span class="bar-track"><span class="bar-fill{cls}" style="width:{width}%"></span></span>'
            f'<span class="bar-val">{v}</span></div>')
    return "".join(out)


def tier_label(i, x):
    t = x.get("tier")
    names = {1: "第一档 · 大城市", 2: "第二档 · 区域中心", 3: "第三档 · 小城与郊区"}
    return names.get(t, ["第一档", "第二档", "第三档"][i % 3])


def city_block(iso):
    e = ED.get(iso) or {}
    cities = e.get("cities") or []
    if not cities:
        return ""
    cards = "".join(
        f'<div class="city"><p class="tier">{tier_label(i, x)}</p><h4>{html.escape(x["name"])}</h4>'
        f'<p class="rent">${html.escape(str(x["rent"]))}<small> / 月租参考</small></p></div>'
        for i, x in enumerate(cities))
    return f'<div class="city-grid">{cards}</div>'


def tag_block(iso):
    e = ED.get(iso) or {}
    tags = e.get("tags") or []
    return "".join(f'<span class="tag">{html.escape(t)}</span>' for t in tags)


def metrics_rows(iso):
    c = COUNTRY[iso]
    rows = []
    for ind in data["indicators"]:
        m = c["metrics"].get(ind["key"])
        if not m or not isinstance(m.get("value"), (int, float)):
            rows.append(f'<tr><td>{ind["zh"]}</td><td class="num na">缺失</td><td class="num">—</td>'
                        f'<td class="num na">—</td></tr>')
            continue
        q = SCORES[ind["key"]].get(iso)
        qtxt = "—" if q is None else str(int(round(q)))
        rows.append(
            f'<tr><td>{ind["zh"]}<span class="dim"> · {ind["code"]}</span></td>'
            f'<td class="num">{fmt(ind["key"], m["value"])}{UNIT_TAIL.get(ind["key"], "")}</td>'
            f'<td class="num">{m["year"]}</td><td class="num">{qtxt}</td></tr>')
    return "".join(rows)


def kv_strip(iso):
    c = COUNTRY[iso]
    picks = ["price_level", "gdp_pc_ppp", "life_expectancy", "homicide"]
    cells = []
    for k in picks:
        m = c["metrics"].get(k)
        if not m or not isinstance(m.get("value"), (int, float)):
            continue
        cells.append(f'<div class="kv"><p class="kv-k">{INDS[k]["zh"]}</p>'
                     f'<p class="kv-v">{fmt(k, m["value"])}<small>{UNIT_TAIL.get(k,"")}</small></p>'
                     f'<p class="kv-y">{m["year"]} 年 · 世行</p></div>')
    return f'<div class="kv-strip">{"".join(cells)}</div>'


def head(title, desc, canon, extra="", sr="../../", cp="../"):
    """sr = 站点根相对前缀；cp = country/ 目录相对前缀。"""
    e = html.escape(desc, quote=True)
    t = html.escape(title, quote=True)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{e}">
<meta name="color-scheme" content="light">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="zh-CN" href="{canon}">
<link rel="alternate" hreflang="x-default" href="{canon}">
<meta property="og:type" content="article">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{e}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="zh_CN">
<meta property="og:site_name" content="最适合生活的国家">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{e}">
<link rel="stylesheet" href="{cp}assets/country.css">
{extra}</head>
<body>
<header class="site-head">
  <div class="wrap head-inner">
    <a class="brand" href="{sr}">MBTI<em>·</em>人生地理</a>
    <nav class="head-nav">
      <a href="{cp}c/">国家数据</a>
      <a href="{cp}rank/">维度榜单</a>
      <a href="{cp}compare/">对比</a>
    </nav>
  </div>
</header>
<main id="main">
"""


UPDATED = ed.get("updated") or "2026-11"

FOOT = f"""</main>
<footer class="site-foot">
  <div class="wrap">
    <p class="disc">免责声明：本页基于公开统计数据整理，非移民、法律或税务建议。任何迁居、签证、税务安排请咨询持牌专业人士。</p>
    <p class="src">数据来源：世界银行公开数据（<a href="https://data.worldbank.org/" target="_blank" rel="noopener">World Bank Open Data</a>，CC BY 4.0），各指标年份单独标注；城市租金与签证标签为编辑整理，非官方数据。更新：{UPDATED}</p>
    <p class="copy">MBTI · 人生地理 / Where To Live</p>
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
    # 最强维度里最突出的单项
    ind_best = max(best_d["inds"], key=lambda kv: SCORES[kv[0]].get(iso, 0))
    m = c["metrics"].get(ind_best[0])
    best_fact = fact(ind_best[0], m) or ""
    ind_worst = min(worst_d["inds"], key=lambda kv: SCORES[kv[0]].get(iso, 100))
    mw = c["metrics"].get(ind_worst[0])
    worst_fact = fact(ind_worst[0], mw) or ""
    return best_d, best_s, best_fact, worst_d, worst_s, worst_fact


def tier_word(s):
    return "强项" if s >= 70 else ("中位水平" if s >= 50 else "明显偏弱")


def country_page(iso):
    sr, cp = "../../../", "../../"
    c = COUNTRY[iso]
    e = ED.get(iso) or {}
    zh = c["zh"]
    slug = iso.lower()
    canon = f"{SITE}/country/c/{slug}/"
    tot = total_score(iso)
    best_d, best_s, best_fact, worst_d, worst_s, worst_fact = strength_text(iso)
    title = f"{zh}生活数据：物价、收入、治安、医疗、自然与社会六维度评分与排名"
    desc = (f"{zh}在 55 个国家中综合匹配分 {tot:.1f}（六维等权），排第 {TRANK[iso]} 位；"
            f"最强的是{best_d['zh']}（{best_s:.0f} 分），最弱的是{worst_d['zh']}（{worst_s:.0f} 分）。"
            f"含 12 项世界银行指标原始值与年份、三大城市一居室租金参考与签证门槛标签。")

    faq = [
        (f"{zh}在 55 个国家里综合排第几？",
         f"按六个维度等权计算，{zh}的综合匹配分是 {tot:.1f}，在 {len(TOTAL)} 个国家中排第 {TRANK[iso]} 位。"
         f"其中{best_d['zh']} {best_s:.0f} 分（{tier_word(best_s)}，第 {RANK[best_d['key']][iso]} 位），"
         f"{worst_d['zh']} {worst_s:.0f} 分（{tier_word(worst_s)}，第 {RANK[worst_d['key']][iso]} 位）。"
         f"分数是按候选国家内部排序折算的分位分，不代表绝对好坏。"),
        (f"{zh}的物价和收入在世界范围内处于什么水平？",
         f"{(fact('price_level', c['metrics'].get('price_level')) or '物价水平指数缺失')}；"
         f"{(fact('gdp_pc_ppp', c['metrics'].get('gdp_pc_ppp')) or '人均 GDP 缺失')}。"
         f"两项都是宏观平均口径：物价指数是 PPP 转换因子与市场汇率之比，不含个人消费结构差异；"
         f"人均 GDP 按购买力平价折算，反映产出水平而非到手工资。"),
        (f"只看数据就能决定要不要搬去{zh}吗？",
         "不能。这里的指标都是国家层面的统计平均，覆盖不到城市与街区差异、签证与税制、语言与公共服务可及性，"
         "也无法反映你个人的行业与家庭情况。数据只适合用来做初步筛选与横向比较，"
         "真正的迁居、签证与税务安排请咨询持牌专业人士。"),
    ]

    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": f"{zh}生活条件数据集：12 项世界银行指标",
        "description": f"{zh}在物价水平、人均 GDP（PPP）、预期寿命、凶杀率、PM2.5、森林覆盖率、人口密度、"
                       f"女性劳动参与率、医疗支出占 GDP、互联网使用率、失业率、城市化率共 12 项指标上的最新可用数值与年份。",
        "url": canon,
        "isAccessibleForFree": True,
        "creator": {"@type": "Organization", "name": "MBTI · 人生地理"},
        "publisher": {"@type": "Organization", "name": "MBTI · 人生地理"},
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "isBasedOn": "https://data.worldbank.org/",
        "spatialCoverage": {"@type": "Country", "name": zh},
        "temporalCoverage": "2020/2025",
        "variableMeasured": [
            {"@type": "PropertyValue", "name": ind["zh"],
             "value": c["metrics"][ind["key"]]["value"] if ind["key"] in c["metrics"] else None,
             "unitText": UNIT_TAIL.get(ind["key"], "US=100" if ind["key"] == "price_level" else ""),
             "measurementTechnique": ind["code"],
             "description": f"{ind['zh']}，数据年份 "
                            f"{c['metrics'][ind['key']]['year'] if ind['key'] in c['metrics'] else '缺失'}"}
            for ind in data["indicators"]],
    }
    faqjson = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq],
    }
    ld = ('<script type="application/ld+json">' + json.dumps(dataset, ensure_ascii=False) + '</script>\n'
          '<script type="application/ld+json">' + json.dumps(faqjson, ensure_ascii=False) + '</script>\n')

    ds_sorted = sorted([(d, dim_score(iso, d)) for d in DIMS if dim_score(iso, d) is not None], key=lambda x: -x[1])
    dim_rows = "".join(
        f'<tr><td><a href="{cp}rank/{d["key"]}/">{d["zh"]}</a></td>'
        f'<td class="num">{s:.0f}</td><td class="num">第 {RANK[d["key"]][iso]} / {RANK[d["key"]]["_n"]}</td>'
        f'<td class="dim">{d["note"]}</td></tr>' for d, s in ds_sorted)

    peers = [x for x in REGION[c["region"]] if x != iso][:6]
    peer_links = "".join(f'<a class="peer" href="../{p.lower()}/">{COUNTRY[p]["zh"]}'
                         f'<span>{total_score(p):.0f} 分</span></a>' for p in peers)
    compare_url = cp + f"compare/?a={iso}"

    ind_high = max(SCORES[k].get(iso, -1) for k in SCORES)
    body = f"""{crumbs([("首页", sr), ("国家数据", cp + "c/"), (zh, "")])}
<section class="page-hero">
  <div class="wrap">
    <p class="kicker">{c["region"]} · World Bank Data</p>
    <h1>{zh}生活数据：六个维度到底强在哪、弱在哪</h1>
    <p class="lede">按六个维度等权计算，{zh}在 {len(TOTAL)} 个候选国家里综合匹配分 <strong>{tot:.1f}</strong>，排第 <strong>{TRANK[iso]}</strong> 位。
    最强的一项是{best_d["zh"]}（{best_s:.0f} 分，第 {RANK[best_d["key"]][iso]} 位），{worst_d["zh"]}是它的短板（{worst_s:.0f} 分，第 {RANK[worst_d["key"]][iso]} 位）。
    下面每一项都标注了世界银行的原始值、年份与在 55 国中的分位分。</p>
    <div class="hero-actions">
      <a class="btn primary" href="{sr}#intro">测一测我该去哪</a>
      <a class="btn ghost" href="{compare_url}">与其它国家对比</a>
    </div>
    {kv_strip(iso)}
  </div>
</section>

<section class="wrap section">
  <h2>六个维度的分位分</h2>
  <div class="split">
    <div class="panel">
      {bars(iso, best_d["key"])}
      <p class="weight-note">分数含义：在 {len(TOTAL)} 个候选国家内部排序折算成 0–100 分（分位排名制）。
      70 分以上可视为该维度的强项，50 分附近是中等，40 分以下说明它在同类国家里明显落后。</p>
    </div>
    <div class="panel">
      <p class="block-label">维度明细与排名</p>
      <div class="tbl-wrap"><table class="metrics"><thead><tr><th>维度</th><th style="text-align:right">分数</th>
      <th style="text-align:right">排名</th><th>衡量什么</th></tr></thead><tbody>{dim_rows}</tbody></table></div>
    </div>
  </div>
</section>

<section class="wrap section">
  <h2>强项与短板</h2>
  <div class="split">
    <div class="panel">
      <p class="block-label">最强：{best_d["zh"]} · {best_s:.0f} 分</p>
      <p>{best_fact}。这一项在 {RANK[best_d["key"]]["_n"]} 个有数据的国家里排第 {RANK[best_d["key"]][iso]} 位，
      是{zh}整体分数的主要来源。</p>
    </div>
    <div class="panel">
      <p class="block-label">最弱：{worst_d["zh"]} · {worst_s:.0f} 分</p>
      <p>{worst_fact}。这一项排在第 {RANK[worst_d["key"]][iso]} 位，是选择{zh}时需要主动权衡的部分。</p>
    </div>
  </div>
  <p class="weight-note">{e.get("hook", "")}</p>
</section>

<section class="wrap section">
  <h2>城市生活成本：一居室月租参考</h2>
  {city_block(iso)}
  <p class="weight-note">租金为市中心一居室挂牌价区间的中位水平，按编辑口径整理成三档，用于横向感受城市间落差，不是官方统计，也不含水电与押金。</p>
</section>

<section class="wrap section">
  <h2>签证与居留门槛</h2>
  <div class="tagrow">{tag_block(iso)}</div>
  <p class="weight-note">{e.get("visa_note", "")} 实用提示：{e.get("tip", "")}</p>
  <p class="weight-note">以上为编辑整理的常见路径概述，不构成法律意见；具体门槛、配额与审理时间以各国移民部门最新公告为准。</p>
</section>

<section class="wrap section">
  <h2>12 项原始数据与年份</h2>
  <div class="tbl-wrap"><table class="metrics">
  <thead><tr><th>指标</th><th style="text-align:right">数值</th><th style="text-align:right">年份</th>
  <th style="text-align:right">55 国分位分</th></tr></thead>
  <tbody>{metrics_rows(iso)}</tbody></table></div>
  <p class="tbl-src">数据来源：世界银行公开数据 API（CC BY 4.0），取各国最新可用年份的原始值，未做估算、插值或填充；缺失值原样保留。分位分为候选国家内部相对位置，不是国际通行评级。</p>
</section>

<section class="wrap section">
  <h2>同区域国家的横向比较</h2>
  <div class="peer-grid">{peer_links}</div>
  <p class="weight-note">分数为六维等权下的综合匹配分。想看单一维度的完整排序，可到<a href="{cp}rank/">维度榜单</a>；想按自己的权重算，<a href="{sr}#intro">做 18 道题</a>后可以拖动滑块重算。</p>
</section>

<section class="wrap section">
  <h2>常见问题</h2>
  <div class="faq-grid">
  {"".join(f'<details class="faq-item"><summary>{q}</summary><div class="faq-body"><p>{a}</p></div></details>' for q, a in faq)}
  </div>
</section>
"""
    return head(title, desc, canon, ld, sr="../../../", cp="../../") + body + FOOT


def index_page():
    sr, cp = "../../", "../"
    canon = f"{SITE}/country/c/"
    title = "55 个国家的生活数据总表：六维度评分、排名与原始指标"
    desc = ("55 个候选国家的生活条件总表：综合匹配分、六维度分数、区域与 12 项世界银行指标年份，"
            "按综合分排序，可点表头切换排序，每行进入单国详情页。")
    rows = []
    for iso in TOTAL:
        c = COUNTRY[iso]
        cells = [f'<td class="dim">{c["region"]}</td>',
                 f'<td class="nm"><a href="{iso.lower()}/">{c["zh"]}</a></td>',
                 f'<td class="num">{total_score(iso):.1f}</td>']
        for d in DIMS:
            s = dim_score(iso, d)
            cells.append(f'<td class="num">{"—" if s is None else int(round(s))}</td>')
        rows.append('<tr data-row>' + "".join(cells) + "</tr>")
    thead = ('<tr><th data-sort="text">区域</th><th data-sort="text">国家</th>'
             '<th data-sort="num" style="text-align:right">综合分</th>'
             + "".join(f'<th data-sort="num" style="text-align:right">{d["zh"]}</th>' for d in DIMS)
             + "</tr>")
    body = f"""{crumbs([("首页", sr), ("国家数据", "")])}
<section class="page-hero">
  <div class="wrap">
    <p class="kicker">55 Countries · 6 Dimensions</p>
    <h1>55 个国家的生活数据总表</h1>
    <p class="lede">综合分是六个维度的等权平均，只代表「默认权重下」的相对位置。真实排序取决于你更在意什么——
    到<a href="{sr}#intro">测试页</a>答完 18 道题，就能用你自己的权重重算；也可以直接进单国页看原始指标与年份。</p>
  </div>
</section>
<section class="wrap section">
  <div class="tbl-wrap"><table class="metrics sortable"><thead>{thead}</thead><tbody>{"".join(rows)}</tbody></table></div>
  <p class="tbl-src">点击表头可切换排序。分数为该维度在 55 国中的分位分（0–100），"—" 表示世界银行未收录该国该项数据。</p>
</section>
<section class="wrap section">
  <h2>按维度看榜单</h2>
  <div class="peer-grid">{"".join(f'<a class="peer" href="{cp}rank/{d["key"]}/">{d["zh"]}<span>Top 20 榜单</span></a>' for d in DIMS)}</div>
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
          return x.localeCompare(y,"zh")*dir;
        }});
        rows.forEach(function(r){{tb.appendChild(r);}});
      }});
    }})(i,th[i]);
  }}
}})();
</script>
"""
    return head(title, desc, canon, sr="../../", cp="../") + body + FOOT


os.makedirs(os.path.join(BASE, "c"), exist_ok=True)
open(os.path.join(BASE, "c", "index.html"), "w", encoding="utf-8").write(index_page())
n = 0
for iso in COUNTRY:
    d = os.path.join(BASE, "c", iso.lower())
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(country_page(iso))
    n += 1
print("generated c/index.html +", n, "country pages")
