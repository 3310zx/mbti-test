#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 /country/rank/ 榜单总览与 6 个维度榜单页。"""
import os
from build_detail import (BASE, SITE, data, ed, INDS, COUNTRY, ED, DIMS, RANK, TOTAL, TRANK,
                          SCORES, dim_score, total_score, fmt, fact, UNIT_TAIL, head, crumbs, FOOT)

DIM_PAGE_EXTRA = {
    "cost": "物价水平指数是 PPP 转换因子与市场汇率之比（美国=100），衡量的是宏观价格水平；它不含个人消费结构，也不等于「生活贵不贵」的全部。",
    "income": "人均 GDP 按购买力平价折算，反映产出水平而不是到手工资；失业率取 ILO 模型估计口径，与各国社保申领条件无关。",
    "safety": "唯一的指标是每十万人故意杀人案件数，它不覆盖盗窃、诈骗、家暴等更常见的治安问题，也不能反映街区之间的巨大差异。",
    "health": "预期寿命反映的是历史死亡率的综合结果，医疗支出占 GDP 反映投入强度，两者都不直接等于医疗质量或可及性。",
    "nature": "PM2.5 为国家年均人口加权浓度，森林覆盖率不区分原始林与人工林，人口密度是中性指标——按「接近 55 国中位数得分最高」计算。",
    "society": "互联网使用率、城市化率与女性劳动参与率都是结构性指标，它们与「社会包容度」相关但不能等同。",
}


def rank_table(dim, rows, cp="../../"):
    out = []
    for i, (iso, s) in enumerate(rows):
        c = COUNTRY[iso]
        v = ""
        for k, w in dim["inds"]:
            f = fact(k, c["metrics"].get(k))
            if f:
                v += f + "；"
        out.append(f'<tr><td class="num">{i+1}</td>'
                   f'<td class="nm"><a href="{cp}c/{iso.lower()}/">{c["zh"]}</a></td>'
                   f'<td class="num">{s:.0f}</td><td class="dim">{c["region"]}</td>'
                   f'<td class="dim">{v.rstrip("；")}</td></tr>')
    return "".join(out)


def dim_page(dim):
    sr, cp = "../../../", "../../"
    key = dim["key"]
    rows = [(iso, dim_score(iso, dim)) for iso in COUNTRY]
    rows = sorted([r for r in rows if r[1] is not None], key=lambda x: (-x[1], x[0]))
    top3 = rows[:3]
    canon = f"{SITE}/country/rank/{key}/"
    title = f"{dim['zh']}最好的国家排名：55 国分位分榜单（{INDS[dim['inds'][0][0]]['zh']}等指标）"
    desc = (f"按{dim['zh']}给 55 个国家排序：第 1 名 {COUNTRY[top3[0][0]]['zh']}（{top3[0][1]:.0f} 分），"
            f"第 2 名 {COUNTRY[top3[1][0]]['zh']}（{top3[1][1]:.0f} 分），第 3 名 {COUNTRY[top3[2][0]]['zh']}（{top3[2][1]:.0f} 分）。"
            f"含每国原始指标值与年份，说明{dim['zh']}由哪些世行指标构成。")

    cards = []
    for i, (iso, s) in enumerate(top3):
        c = COUNTRY[iso]
        facts = "；".join(filter(None, [fact(k, c["metrics"].get(k)) for k, w in dim["inds"]]))
        cards.append(f'<article class="panel"><p class="block-label">第 {i+1} 名</p>'
                     f'<h3><a href="{cp}c/{iso.lower()}/">{c["zh"]}</a></h3>'
                     f'<p><strong>{s:.0f}</strong> 分 · {c["region"]}</p><p class="weight-note">{facts}</p></article>')

    comp = " + ".join(f'{INDS[k]["zh"]} {int(w*100)}%' for k, w in dim["inds"])
    body = f"""{crumbs([("首页", sr), ("维度榜单", cp + "rank/"), (dim["zh"], "")])}
<section class="page-hero">
  <div class="wrap">
    <p class="kicker">Ranking · {dim["zh"]}</p>
    <h1>{dim["zh"]}最好的国家：55 国完整排序</h1>
    <p class="lede">{dim["note"]}。本榜按该维度的分位分排序，第一名 {COUNTRY[top3[0][0]]["zh"]} 拿到 {top3[0][1]:.0f} 分，
    最后一名 {COUNTRY[rows[-1][0]]["zh"]} 只有 {rows[-1][1]:.0f} 分。分数是候选国家内部的相对位置，不是国际评级。</p>
    <p class="weight-note">这一维度怎么算：{comp}。</p>
    <div class="hero-actions">
      <a class="btn primary" href="{sr}#intro">按自己的权重算一遍</a>
      <a class="btn ghost" href="{cp}c/">看全部国家数据</a>
    </div>
  </div>
</section>

<section class="wrap section">
  <h2>前三名</h2>
  <div class="split three">{"".join(cards)}</div>
</section>

<section class="wrap section">
  <h2>55 国完整榜单</h2>
  <div class="tbl-wrap"><table class="metrics">
  <thead><tr><th style="text-align:right">排名</th><th>国家</th><th style="text-align:right">分数</th>
  <th>区域</th><th>原始指标（含年份）</th></tr></thead>
  <tbody>{rank_table(dim, rows, cp)}</tbody></table></div>
  <p class="tbl-src">分数由世界银行公开数据（CC BY 4.0）计算，缺失指标不计入分母，未做插值填充。{DIM_PAGE_EXTRA[key]}</p>
</section>

<section class="wrap section">
  <h2>其它维度</h2>
  <div class="peer-grid">{"".join(f'<a class="peer" href="../{d["key"]}/">{d["zh"]}<span>榜单</span></a>' for d in DIMS if d["key"] != key)}</div>
</section>
"""
    return head(title, desc, canon, sr=sr, cp=cp) + body + FOOT


def index_page():
    sr, cp = "../../", "../"
    canon = f"{SITE}/country/rank/"
    title = "六维度榜单：生活费、收入、治安、医疗、环境、社会最好的国家"
    desc = ("六个维度各自的国家榜单入口，附等权综合分前 15 名。每个榜单按世界银行数据的分位分排序，"
            "标注构成该维度的指标与权重，可进入单国页看原始值与年份。")
    cards = []
    for d in DIMS:
        rows = [(iso, dim_score(iso, d)) for iso in COUNTRY]
        rows = sorted([r for r in rows if r[1] is not None], key=lambda x: (-x[1], x[0]))
        top = rows[0]
        cards.append(f'<a class="peer tall" href="{d["key"]}/">{d["zh"]}'
                     f'<span>第 1：{COUNTRY[top[0]]["zh"]}（{top[1]:.0f} 分）</span></a>')
    top15 = ""
    for i, iso in enumerate(TOTAL[:15]):
        c = COUNTRY[iso]
        cells = "".join(f'<td class="num">{int(round(dim_score(iso, d)))}</td>' for d in DIMS)
        top15 += (f'<tr><td class="num">{i+1}</td><td class="nm"><a href="../c/{iso.lower()}/">{c["zh"]}</a></td>'
                  f'<td class="num">{total_score(iso):.1f}</td>{cells}</tr>')
    thead = ('<tr><th style="text-align:right">排名</th><th>国家</th>'
             '<th style="text-align:right">综合分</th>'
             + "".join(f'<th style="text-align:right">{d["zh"]}</th>' for d in DIMS) + "</tr>")
    body = f"""{crumbs([("首页", sr), ("维度榜单", "")])}
<section class="page-hero">
  <div class="wrap">
    <p class="kicker">6 Dimensions · 55 Countries</p>
    <h1>六维度榜单</h1>
    <p class="lede">把「最适合生活」拆成六个可以单独比较的问题：哪里最便宜、哪里收入机会更好、哪里更安全、
    哪里医疗更强、哪里自然环境更舒服、哪里社会与数字化程度更高。每个榜单都能看到完整 55 国排序与构成指标。</p>
    <p class="weight-note">没有唯一的冠军，因为任何综合排名都必须先假设一套权重。下面的综合分用了最简单的等权平均，只作参照。</p>
  </div>
</section>

<section class="wrap section">
  <h2>按维度进入榜单</h2>
  <div class="peer-grid">{"".join(cards)}</div>
</section>

<section class="wrap section">
  <h2>等权综合分前 15 名</h2>
  <div class="tbl-wrap"><table class="metrics"><thead>{thead}</thead><tbody>{top15}</tbody></table></div>
  <p class="tbl-src">综合分为六个维度的等权平均。想换成自己的权重，<a href="{sr}#intro">答完 18 道题</a>后在结果页拖动滑块即可重算。</p>
</section>
"""
    return head(title, desc, canon, sr=sr, cp=cp) + body + FOOT


os.makedirs(os.path.join(BASE, "rank"), exist_ok=True)
open(os.path.join(BASE, "rank", "index.html"), "w", encoding="utf-8").write(index_page())
for d in DIMS:
    p = os.path.join(BASE, "rank", d["key"])
    os.makedirs(p, exist_ok=True)
    open(os.path.join(p, "index.html"), "w", encoding="utf-8").write(dim_page(d))
print("generated rank/index.html + 6 dim pages")
