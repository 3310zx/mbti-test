#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 /country/compare/ 两国对比页：静态直出默认对，JS 支持 ?a=&b= 切换。"""
import os, json
from build_detail import (BASE, SITE, data, ed, INDS, COUNTRY, ED, DIMS, RANK, TOTAL, TRANK,
                          SCORES, dim_score, total_score, fmt, UNIT_TAIL, head, crumbs, FOOT)

A, B = TOTAL[0], TOTAL[1]


def payload():
    out = {}
    for iso, c in COUNTRY.items():
        m = {}
        for ind in data["indicators"]:
            x = c["metrics"].get(ind["key"])
            if x and isinstance(x.get("value"), (int, float)):
                m[ind["key"]] = [x["value"], x["year"]]
        out[iso] = {"zh": c["zh"], "region": c["region"],
                    "total": round(total_score(iso), 1), "rank": TRANK[iso],
                    "dims": {d["key"]: (None if dim_score(iso, d) is None else round(dim_score(iso, d)))
                             for d in DIMS},
                    "metrics": m,
                    "cities": (ED.get(iso) or {}).get("cities") or [],
                    "tags": (ED.get(iso) or {}).get("tags") or []}
    return out


def static_block(a, b):
    ca, cb = COUNTRY[a], COUNTRY[b]
    head_rows = (f'<div class="vs-head">'
                 f'<div><p class="kicker">{ca["region"]}</p><h3><a href="../c/{a.lower()}/">{ca["zh"]}</a></h3>'
                 f'<p class="big">{total_score(a):.1f}<small> 综合分 · 第 {TRANK[a]} 位</small></p></div>'
                 f'<div><p class="kicker">{cb["region"]}</p><h3><a href="../c/{b.lower()}/">{cb["zh"]}</a></h3>'
                 f'<p class="big">{total_score(b):.1f}<small> 综合分 · 第 {TRANK[b]} 位</small></p></div></div>')
    dim_rows = ""
    for d in DIMS:
        x, y = dim_score(a, d), dim_score(b, d)
        dim_rows += (f'<tr><td class="dim">{d["zh"]}</td>'
                     f'<td class="num">{"" if x is None else int(round(x))}</td>'
                     f'<td class="num">{"" if y is None else int(round(y))}</td>'
                     f'<td class="dim">{"持平" if (x is not None and y is not None and int(round(x))==int(round(y))) else (ca["zh"] if (x or 0) > (y or 0) else cb["zh"])}</td></tr>')
    met_rows = ""
    for ind in data["indicators"]:
        ma, mb = ca["metrics"].get(ind["key"]), cb["metrics"].get(ind["key"])
        fa = fmt(ind["key"], ma["value"]) + UNIT_TAIL.get(ind["key"], "") if ma else "—"
        fb = fmt(ind["key"], mb["value"]) + UNIT_TAIL.get(ind["key"], "") if mb else "—"
        ya = ma["year"] if ma else "—"
        yb = mb["year"] if mb else "—"
        met_rows += (f'<tr><td class="dim">{ind["zh"]}</td><td class="num">{fa}<small> {ya}</small></td>'
                     f'<td class="num">{fb}<small> {yb}</small></td></tr>')
    return head_rows, dim_rows, met_rows


def page():
    sr, cp = "../../", "../"
    canon = f"{SITE}/country/compare/"
    title = f"{COUNTRY[A]['zh']} vs {COUNTRY[B]['zh']}：生活成本、收入、治安等 12 项指标对比"
    desc = (f"{COUNTRY[A]['zh']}与{COUNTRY[B]['zh']}逐项对比：六维度分位分、12 项世界银行指标原始值与年份、"
            f"城市一居室租金与签证标签。支持切换任意两国。")
    hr, dr, mr = static_block(A, B)
    opts = "".join(f'<option value="{c["iso3"]}">{c["zh"]}</option>' for c in data["countries"])
    body = f"""{crumbs([("首页", sr), ("国家对比", "")])}
<section class="page-hero">
  <div class="wrap">
    <p class="kicker">Compare · Head to Head</p>
    <h1>两国横向对比</h1>
    <p class="lede">默认展示等权综合分最高的两个国家：{COUNTRY[A]["zh"]} 与 {COUNTRY[B]["zh"]}。
    换国家只需改下拉框，地址栏会同步更新，可直接把对比链接发给别人。</p>
    <div class="cmp-pick">
      <label>国家 A <select id="selA">{opts}</select></label>
      <span class="vs">VS</span>
      <label>国家 B <select id="selB">{opts}</select></label>
    </div>
  </div>
</section>

<section class="wrap section">
  <div id="vsHead">{hr}</div>
  <div class="split">
    <div class="panel">
      <h2>维度对比</h2>
      <div class="tbl-wrap"><table class="metrics"><thead><tr><th>维度</th>
      <th style="text-align:right" id="thA">{COUNTRY[A]["zh"]}</th>
      <th style="text-align:right" id="thB">{COUNTRY[B]["zh"]}</th><th>占优</th></tr></thead>
      <tbody id="dimBody">{dr}</tbody></table></div>
      <p class="weight-note">数字为该维度的 55 国分位分，越高表示在该维度越占优；成本维度分数高＝更便宜。</p>
    </div>
    <div class="panel">
      <h2>12 项原始指标</h2>
      <div class="tbl-wrap"><table class="metrics"><thead><tr><th>指标</th>
      <th style="text-align:right">数值 · 年份</th><th style="text-align:right">数值 · 年份</th></tr></thead>
      <tbody id="metBody">{mr}</tbody></table></div>
      <p class="tbl-src">数值取自世界银行公开数据（CC BY 4.0），年份逐项标注；"—" 表示该国该项缺失。单位：人均 GDP 为国际元，凶杀率为每十万人，PM2.5 为 µg/m³。</p>
    </div>
  </div>
</section>

<section class="wrap section">
  <h2>怎么读这张对比表</h2>
  <p class="weight-note">分位分只说明「在 55 个候选国家里的相对位置」，不能跨维度比较绝对优劣。
  如果你更在意收入，就把收入机会看得更重；如果预算紧张，成本维度的差距往往比其它五项加起来更能决定体验。
  想按自己的权重算，<a href="{cp}#intro">做 18 道题</a>后在结果页拖动滑块重算。</p>
</section>

<script>
window.CMP = {json.dumps(payload(), ensure_ascii=False)};
(function(){{
  var DIMS = {json.dumps([{"key":d["key"],"zh":d["zh"]} for d in DIMS], ensure_ascii=False)};
  var INDS = {json.dumps([{"key":i["key"],"zh":i["zh"],"unit":UNIT_TAIL.get(i["key"],"")} for i in data["indicators"]], ensure_ascii=False)};
  var selA=document.getElementById("selA"),selB=document.getElementById("selB");
  var q=new URLSearchParams(location.search);
  var initA=(q.get("a")||"{A}").toUpperCase(), initB=(q.get("b")||"{B}").toUpperCase();
  if(window.CMP[initA]) selA.value=initA; if(window.CMP[initB]) selB.value=initB;
  function num(v){{return v===null||v===undefined?"—":v;}}
  function render(){{
    var a=window.CMP[selA.value],b=window.CMP[selB.value];
    if(!a||!b)return;
    var h='<div class="vs-head"><div><p class="kicker">'+a.region+'</p><h3><a href="../c/'+selA.value.toLowerCase()+'/">'+a.zh+'</a></h3><p class="big">'+a.total+'<small> 综合分 · 第 '+a.rank+' 位</small></p></div>'
      +'<div><p class="kicker">'+b.region+'</p><h3><a href="../c/'+selB.value.toLowerCase()+'/">'+b.zh+'</a></h3><p class="big">'+b.total+'<small> 综合分 · 第 '+b.rank+' 位</small></p></div></div>';
    document.getElementById("vsHead").innerHTML=h;
    document.getElementById("thA").textContent=a.zh;
    document.getElementById("thB").textContent=b.zh;
    var dr="";
    DIMS.forEach(function(d){{
      var x=a.dims[d.key],y=b.dims[d.key];
      var win=(x===null||y===null)?"—":(x===y?"持平":(x>y?a.zh:b.zh));
      dr+='<tr><td class="dim">'+d.zh+'</td><td class="num">'+num(x)+'</td><td class="num">'+num(y)+'</td><td class="dim">'+win+'</td></tr>';
    }});
    document.getElementById("dimBody").innerHTML=dr;
    var mr="";
    INDS.forEach(function(i){{
      var ma=a.metrics[i.key]||[],mb=b.metrics[i.key]||[];
      var fa=ma.length?ma[0]+i.unit+" <small>"+ma[1]+"</small>":"—";
      var fb=mb.length?mb[0]+i.unit+" <small>"+mb[1]+"</small>":"—";
      mr+='<tr><td class="dim">'+i.zh+'</td><td class="num">'+fa+'</td><td class="num">'+fb+'</td></tr>';
    }});
    document.getElementById("metBody").innerHTML=mr;
    var u=new URL(location.href);u.searchParams.set("a",selA.value);u.searchParams.set("b",selB.value);history.replaceState(null,"",u);
  }}
  selA.addEventListener("change",render);selB.addEventListener("change",render);render();
}})();
</script>
"""
    return head(title, desc, canon, sr=sr, cp=cp) + body + FOOT


os.makedirs(os.path.join(BASE, "compare"), exist_ok=True)
open(os.path.join(BASE, "compare", "index.html"), "w", encoding="utf-8").write(page())
print("generated compare/index.html", A, "vs", B)
