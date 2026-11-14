#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 /country/compare/<a>-vs-<b>/ 长尾对比页：静态直出一对国家的六维/12 指标对照与差值解读。

页面结构：结论卡 → 六维对照表 → 逐维度解读 → 12 项原始指标 → 三种取舍场景 → 常见问题 → 相关对比。
每页自带 FAQPage + BreadcrumbList 结构化数据，可直接被搜索结果以问答形态展示。
"""
import os
import json

from build_detail import (BASE, SITE, data, INDS, COUNTRY, ED, DIMS, RANK,
                          dim_score, total_score, fmt, UNIT_TAIL, TRANK,
                          head, crumbs, FOOT)
from site_meta import PAIRS, pair_slug, ad_unit


# ---------- 取数 ----------
def num(iso, key):
    m = (COUNTRY[iso]["metrics"] or {}).get(key)
    if not m:
        return None
    v = m.get("value")
    return v if isinstance(v, (int, float)) else None


def year(iso, key):
    m = (COUNTRY[iso]["metrics"] or {}).get(key)
    return m.get("year") if m else None


def show(iso, key):
    """带单位的展示值，缺失返回 em dash。"""
    v = num(iso, key)
    if v is None:
        return "—"
    return f"{fmt(key, v)}{UNIT_TAIL.get(key, '')}"


def rel_pct(x, y):
    """x 相对 y 高（正）或低（负）百分之多少。"""
    if not x or not y:
        return None
    return (x / y - 1) * 100


def t1_rent(iso):
    """一线城市一居室租金中位参考（编辑口径，美元）。"""
    cities = (ED.get(iso) or {}).get("cities") or []
    for c in cities:
        if c.get("tier") == 1:
            return c.get("name"), c.get("rent")
    return None, None


# ---------- 文案片段 ----------
def dim_compare(a, b):
    """返回六个维度的对照数据。"""
    out = []
    for d in DIMS:
        xa, xb = dim_score(a, d), dim_score(b, d)
        if xa is None or xb is None:
            out.append({"dim": d, "xa": xa, "xb": xb, "gap": None, "win": None})
            continue
        gap = xa - xb
        win = a if gap > 0 else (b if gap < 0 else None)
        out.append({"dim": d, "xa": xa, "xb": xb, "gap": gap, "win": win})
    return out


def dim_sentence(a, b, row):
    d = row["dim"]
    zh_a, zh_b = COUNTRY[a]["zh"], COUNTRY[b]["zh"]
    if row["xa"] is None or row["xb"] is None:
        miss = zh_a if row["xa"] is None else zh_b
        return (f"{d['zh']}（{d['note']}）：{miss}该项缺少世界银行数据，无法直接比较，"
                f"这一项在双方综合分里都不计入分母。")
    xa, xb = row["xa"], row["xb"]
    ra, rb = RANK[d["key"]][a], RANK[d["key"]][b]
    if row["win"] is None:
        return (f"{d['zh']}（{d['note']}）：两国同为 {xa:.0f} 分（第 {ra}、{rb} 位），"
                f"在这个维度上几乎没有差别，不构成选择依据。")
    win_zh = zh_a if row["win"] == a else zh_b
    lose_zh = zh_b if row["win"] == a else zh_a
    gap = abs(row["gap"])
    if gap >= 20:
        tail = "差距接近两个档位，属于结构性差别，而不是统计噪声。"
    elif gap >= 8:
        tail = "差距明显，但两国仍在同一档位内。"
    else:
        tail = "差距有限，实际体感可能被城市与街区差异覆盖。"
    return (f"{d['zh']}（{d['note']}）：{zh_a} {xa:.0f} 分（第 {ra} 位）对 {zh_b} {xb:.0f} 分（第 {rb} 位），"
            f"{win_zh}领先 {gap:.0f} 分，{lose_zh}落后。{tail}")


def metrics_rows_pair(a, b):
    rows = ""
    for ind in data["indicators"]:
        va, vb = num(a, ind["key"]), num(b, ind["key"])
        fa = show(a, ind["key"]) if va is not None else "—"
        fb = show(b, ind["key"]) if vb is not None else "—"
        ya, yb = year(a, ind["key"]), year(b, ind["key"])
        ya = f'<small> {ya}</small>' if ya else ""
        yb = f'<small> {yb}</small>' if yb else ""
        if va is not None and vb is not None:
            diff = va - vb
            unit = UNIT_TAIL.get(ind["key"], "")
            dtxt = f"{diff:+.1f}{unit}" if abs(diff) < 100 else f"{diff:+.0f}{unit}"
        else:
            dtxt = "—"
        rows += (f'<tr><td>{ind["zh"]}'
                 f'<span class="dim"> · {ind["code"]}</span></td>'
                 f'<td class="num">{fa}{ya}</td><td class="num">{fb}{yb}</td>'
                 f'<td class="num">{dtxt}</td></tr>')
    return rows


def verdict_cards(a, b):
    zh_a, zh_b = COUNTRY[a]["zh"], COUNTRY[b]["zh"]
    ta, tb = total_score(a), total_score(b)
    ra, rb = TRANK[a], TRANK[b]
    lead = zh_a if ta > tb else zh_b
    lead_gap = abs(ta - tb)

    pa, pb = num(a, "price_level"), num(b, "price_level")
    if pa and pb:
        cheap = a if pa < pb else b
        cheap_zh = COUNTRY[cheap]["zh"]
        pct = abs(rel_pct(pa, pb)) if cheap == b else abs(rel_pct(pb, pa))
        cost_txt = (f"{zh_a} {pa:.0f} 对 {zh_b} {pb:.0f}（美国=100）；"
                    f"{cheap_zh}的宏观价格水平低 {pct:.0f}%。")
    else:
        cost_txt = "物价指数有一方缺失，无法比较。"

    ga, gb = num(a, "gdp_pc_ppp"), num(b, "gdp_pc_ppp")
    if ga and gb:
        rich = a if ga > gb else b
        rich_zh = COUNTRY[rich]["zh"]
        pct = abs(rel_pct(ga, gb)) if rich == b else abs(rel_pct(gb, ga))
        inc_txt = (f"{zh_a} {ga:,.0f} 对 {zh_b} {gb:,.0f} 国际元；{rich_zh}高 {pct:.0f}%。")
    else:
        inc_txt = "人均 GDP 有一方缺失，无法比较。"

    ha, hb = num(a, "homicide"), num(b, "homicide")
    la, lb = num(a, "life_expectancy"), num(b, "life_expectancy")
    safe = None
    if ha is not None and hb is not None:
        safe = a if ha < hb else b
    safe_txt = ""
    if ha is not None and hb is not None:
        safe_txt = f"凶杀率 {zh_a} {ha:.1f}／十万人 对 {zh_b} {hb:.1f}／十万人；"
    if la is not None and lb is not None:
        safe_txt += f"预期寿命 {zh_a} {la:.1f} 岁 对 {zh_b} {lb:.1f} 岁。"
    elif not safe_txt:
        safe_txt = "治安与医疗指标有一方缺失，无法比较。"

    na, ra1 = t1_rent(a)
    nb, rb1 = t1_rent(b)
    rent_txt = ""
    if ra1 and rb1:
        rent_txt = (f'<p class="weight-note">{zh_a} {na} 一居室参考租金约 {ra1} 美元／月，'
                    f'{zh_b} {nb} 约 {rb1} 美元／月（市中心挂牌区间中位，编辑口径，非官方统计）。</p>')

    cards = f"""<div class="split">
  <div class="panel">
    <p class="block-label">综合分（六维等权）</p>
    <p class="big">{ta:.1f} <small>对 {tb:.1f}</small></p>
    <p>{zh_a} 排第 {ra} 位，{zh_b} 排第 {rb} 位。{lead}整体领先 {lead_gap:.1f} 分，
    但这只是等权平均的结果——换一套权重，排序可能反过来。</p>
  </div>
  <div class="panel">
    <p class="block-label">生活成本</p>
    <p>{cost_txt}物价指数是 PPP 转换因子与市场汇率之比，衡量宏观价格水平，
    不含个人消费结构，也不等于「生活贵不贵」的全部。</p>
    {rent_txt}
  </div>
</div>
<div class="split">
  <div class="panel">
    <p class="block-label">收入水平</p>
    <p>{inc_txt}人均 GDP 按购买力平价折算，反映产出水平而不是到手工资；实际可支配收入还要看税制、社保与工时。</p>
  </div>
  <div class="panel">
    <p class="block-label">安全与健康</p>
    <p>{safe_txt}{("凶杀率更低的是" + COUNTRY[safe]["zh"] + "，但这一项不覆盖盗窃、诈骗与家暴等更常见的治安问题。") if safe else ""}</p>
  </div>
</div>"""
    return cards, lead, lead_gap


def scenario_blocks(a, b, rows):
    zh_a, zh_b = COUNTRY[a]["zh"], COUNTRY[b]["zh"]
    by_key = {r["dim"]["key"]: r for r in rows}

    def winner_of(key):
        r = by_key[key]
        if r["win"] is None:
            return None, 0
        return COUNTRY[r["win"]]["zh"], abs(r["gap"])

    blocks = []
    w, g = winner_of("cost")
    if w:
        blocks.append(("预算优先", f"成本维度 {w} 占优 {g:.0f} 分。"
                                 f"如果你的可支配预算偏紧，房租与日常开销会吃掉收入差距带来的大部分好处，"
                                 f"这时候成本分高的一方往往是更现实的选择。"))
    w, g = winner_of("income")
    if w:
        blocks.append(("收入优先", f"收入维度 {w} 占优 {g:.0f} 分。"
                                 f"如果目标是先提高现金流、再谈生活质量，就业市场与薪资水平比物价更重要，"
                                 f"但要同时核实目标行业的签证门槛与语言要求。"))
    w, g = winner_of("safety")
    if w:
        blocks.append(("安全与医疗优先", f"安全与医疗维度 {w} 领先 {g:.0f} 分。"
                                       f"家庭、老人或未成年人随行时，这两项的权重通常要显著高于收入与成本。"))
    w, g = winner_of("nature")
    if w:
        blocks.append(("环境优先", f"自然与环境维度 {w} 领先 {g:.0f} 分。"
                                 f"空气质量与人口密度对长期生活体验的影响是持续的，换个城市也很难抵消国家级差异。"))
    w, g = winner_of("society")
    if w:
        blocks.append(("社会与数字化优先", f"社会与数字化维度 {w} 领先 {g:.0f} 分。"
                                        f"互联网普及、城市化与女性劳动参与率反映的是结构性环境，"
                                        f"对远程工作、创业与家庭分工的影响比单项补贴更直接。"))
    if not blocks:
        blocks.append(("数据不足", "两国在这六个维度上的数据都有缺失，建议先看各自单国页里可用的原始指标。"))

    cards = "".join(
        f'<div class="panel"><p class="block-label">{name}</p><p>{text}</p></div>' for name, text in blocks)
    return f'<div class="split">{cards}</div>'


def faq_items(a, b, rows):
    zh_a, zh_b = COUNTRY[a]["zh"], COUNTRY[b]["zh"]
    ta, tb = total_score(a), total_score(b)
    ra, rb = TRANK[a], TRANK[b]
    win_a = [r["dim"]["zh"] for r in rows if r["win"] == a]
    win_b = [r["dim"]["zh"] for r in rows if r["win"] == b]
    tie = [r["dim"]["zh"] for r in rows if r["win"] is None and r["xa"] is not None]

    q1 = f"{zh_a}和{zh_b}哪个更适合生活？"
    a1 = (f"没有脱离个人偏好的答案。按六维等权计算，{zh_a}综合分 {ta:.1f}，在 {len(COUNTRY)} 个国家中排第 {ra} 位；"
          f"{zh_b}综合分 {tb:.1f}，排第 {rb} 位。"
          + (f"{zh_a}占优的是{'、'.join(win_a)}；" if win_a else "")
          + (f"{zh_b}占优的是{'、'.join(win_b)}；" if win_b else "")
          + (f"{'、'.join(tie)}两国基本持平。" if tie else "")
          + "把自己的权重代进去之后，答案可能完全不同。")

    pa, pb = num(a, "price_level"), num(b, "price_level")
    q2 = f"{zh_a}和{zh_b}的生活成本差多少？"
    if pa and pb:
        cheap = zh_a if pa < pb else zh_b
        pct = abs(rel_pct(max(pa, pb), min(pa, pb)))
        a2 = (f"按世界银行物价水平指数（美国=100），{zh_a} 为 {pa:.0f}，{zh_b} 为 {pb:.0f}，"
              f"{cheap}的宏观价格水平低约 {pct:.0f}%。这个指数只反映一篮子商品的相对价格，"
              f"不含住房制度、税负与个人消费结构，实际落差要看具体城市。")
    else:
        a2 = "两国的物价水平指数至少有一方缺少年度数据，暂时无法给出差距。"

    ga, gb = num(a, "gdp_pc_ppp"), num(b, "gdp_pc_ppp")
    q3 = f"{zh_a}和{zh_b}哪个收入更高？"
    if ga and gb:
        rich = zh_a if ga > gb else zh_b
        pct = abs(rel_pct(max(ga, gb), min(ga, gb)))
        a3 = (f"人均 GDP（购买力平价）{zh_a} 为 {ga:,.0f} 国际元，{zh_b} 为 {gb:,.0f} 国际元，{rich}高约 {pct:.0f}%。"
              f"这是产出水平口径，不等于平均到手工资；还要结合失业率 "
              f"{show(a, 'unemployment')}（{zh_a}）与 {show(b, 'unemployment')}（{zh_b}）一起看。")
    else:
        a3 = "两国人均 GDP 至少有一方缺失，无法比较收入水平。"

    q4 = "只看这些数据能决定搬去哪吗？"
    a4 = ("不能。这里的数字都是国家级统计平均，覆盖不到城市与街区差异、签证与税制、语言与公共服务可及性，"
          "也无法反映个人行业与家庭情况。它适合用来做初步筛选与横向比较；"
          "真正的迁居、签证与税务安排请咨询持牌专业人士。")
    return [(q1, a1), (q2, a2), (q3, a3), (q4, a4)]


def page(a, b):
    zh_a, zh_b = COUNTRY[a]["zh"], COUNTRY[b]["zh"]
    slug = pair_slug(a, b)
    canon = f"{SITE}/country/compare/{slug}/"
    rows = dim_compare(a, b)
    ta, tb = total_score(a), total_score(b)
    cards, lead, lead_gap = verdict_cards(a, b)
    faqs = faq_items(a, b, rows)

    biggest = max([r for r in rows if r["gap"] is not None], key=lambda r: abs(r["gap"]), default=None)
    title = f"{zh_a} vs {zh_b}：生活费、收入、治安六维度数据对比"
    desc = (f"{zh_a}与{zh_b}逐项对比：综合分 {ta:.1f}（第 {TRANK[a]} 位）对 {tb:.1f}（第 {TRANK[b]} 位）"
            + (f"，{biggest['dim']['zh']}差距最大" if biggest else "")
            + "；含六个维度分位分、12 项世界银行原始指标与年份、城市租金与签证标签。")

    dim_rows = ""
    for r in rows:
        d = r["dim"]
        xa = "—" if r["xa"] is None else f"{r['xa']:.0f}"
        xb = "—" if r["xb"] is None else f"{r['xb']:.0f}"
        gap = "—" if r["gap"] is None else f"{r['gap']:+.0f}"
        win = "—" if r["win"] is None else COUNTRY[r["win"]]["zh"]
        dim_rows += (f'<tr><td class="dim"><a href="../../rank/{d["key"]}/">{d["zh"]}</a></td>'
                     f'<td class="num">{xa}</td><td class="num">{xb}</td>'
                     f'<td class="num">{gap}</td><td>{win}</td></tr>')

    dim_text = "".join(f"<p>{dim_sentence(a, b, r)}</p>" for r in rows)

    faq_html = "".join(
        f'<details class="faq-item"><summary>{q}</summary><div class="faq-body"><p>{ans}</p></div></details>'
        for q, ans in faqs)

    others = [(x, y) for x, y in PAIRS if (a in (x, y) or b in (x, y)) and {x, y} != {a, b}][:6]
    rel = "".join(
        f'<a class="peer" href="../{pair_slug(x, y)}/">{COUNTRY[x]["zh"]} vs {COUNTRY[y]["zh"]}'
        f'<span>综合分 {total_score(x):.1f} 对 {total_score(y):.1f}</span></a>' for x, y in others)
    rel_html = (f'<section class="wrap section">\n  <h2>相关的其它对比</h2>\n'
                f'  <div class="peer-grid">{rel}</div>\n</section>\n\n') if others else ""

    faqjson = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faqs],
    }
    crumbjson = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "MBTI 人生地理", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "国家数据", "item": f"{SITE}/country/c/"},
            {"@type": "ListItem", "position": 3, "name": "国家对比", "item": f"{SITE}/country/compare/"},
            {"@type": "ListItem", "position": 4, "name": f"{zh_a} vs {zh_b}", "item": canon},
        ],
    }
    ld = ('<script type="application/ld+json">' + json.dumps(faqjson, ensure_ascii=False) + '</script>\n'
          '<script type="application/ld+json">' + json.dumps(crumbjson, ensure_ascii=False) + '</script>\n')

    body = f"""{crumbs([("首页", "../../../"), ("国家数据", "../../c/"), ("国家对比", "../"), (f"{zh_a} vs {zh_b}", "")])}
<section class="page-hero">
  <div class="wrap">
    <p class="kicker">{COUNTRY[a]["region"]} × {COUNTRY[b]["region"]} · Head to Head</p>
    <h1>{zh_a} 还是 {zh_b}：六维度数据对比</h1>
    <p class="lede">同样一套世界银行数据、同样六个维度，把{zh_a}和{zh_b}放在一起看：综合分 <strong>{ta:.1f}</strong>（第 {TRANK[a]} 位）
    对 <strong>{tb:.1f}</strong>（第 {TRANK[b]} 位），{lead}整体领先 {lead_gap:.1f} 分；
    真正决定体感的差距往往集中在两三个维度上，下面逐项拆开。</p>
    <div class="hero-actions">
      <a class="btn primary" href="../../#intro">测一测我更适合哪个</a>
      <a class="btn ghost" href="../">换一组国家对比</a>
    </div>
  </div>
</section>

<section class="wrap section">
  <h2>先看结论</h2>
  {cards}
</section>

{ad_unit("广告 · 下方是逐维度数据")}

<section class="wrap section">
  <h2>六个维度对照</h2>
  <div class="tbl-wrap"><table class="metrics">
  <thead><tr><th>维度</th><th style="text-align:right">{zh_a}</th><th style="text-align:right">{zh_b}</th>
  <th style="text-align:right">差值</th><th>占优</th></tr></thead>
  <tbody>{dim_rows}</tbody></table></div>
  <p class="tbl-src">分数为该维度在 {len(COUNTRY)} 个候选国家内部排序折算的分位分（0–100），成本维度分数高＝更便宜；
  差值＝{zh_a} − {zh_b}。分位分只表示相对位置，不能跨维度比较绝对优劣。</p>
</section>

<section class="wrap section">
  <h2>逐维度解读</h2>
  <div class="panel">
  {dim_text}
  </div>
  <p class="weight-note">每个维度的构成指标与权重见<a href="../../rank/">维度榜单</a>；单项原始值与年份见下方表格。</p>
</section>

<section class="wrap section">
  <h2>12 项原始指标与年份</h2>
  <div class="tbl-wrap"><table class="metrics">
  <thead><tr><th>指标</th><th style="text-align:right">{zh_a}</th><th style="text-align:right">{zh_b}</th>
  <th style="text-align:right">差值</th></tr></thead>
  <tbody>{metrics_rows_pair(a, b)}</tbody></table></div>
  <p class="tbl-src">数据来源：世界银行公开数据（CC BY 4.0），取各国最新可用年份的原始值，未做估算、插值或填充。
  差值为{zh_a}减{zh_b}的原始差值；成本、凶杀率、PM2.5 越低越好，收入、寿命、互联网与医疗支出越高越好，
  人口密度为中性指标。</p>
</section>

<section class="wrap section">
  <h2>三种常见的取舍</h2>
  {scenario_blocks(a, b, rows)}
</section>

{ad_unit("广告 · 下方为常见问题")}

<section class="wrap section">
  <h2>常见问题</h2>
  <div class="faq-grid">{faq_html}</div>
</section>

{rel_html}<section class="wrap section">
  <h2>单独看两个国家</h2>
  <div class="peer-grid">
    <a class="peer" href="../../c/{a.lower()}/">{zh_a}<span>12 项原始指标、城市租金与签证标签</span></a>
    <a class="peer" href="../../c/{b.lower()}/">{zh_b}<span>12 项原始指标、城市租金与签证标签</span></a>
    <a class="peer" href="../">更多国家对比<span>支持任意两国切换</span></a>
  </div>
</section>
"""
    return head(title, desc, canon, ld, sr="../../../", cp="../../") + body + FOOT


def main():
    outdir = os.path.join(BASE, "compare")
    n = 0
    for a, b in PAIRS:
        d = os.path.join(outdir, pair_slug(a, b))
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page(a, b))
        n += 1
    print(f"generated {n} pair pages under compare/")


if __name__ == "__main__":
    main()
