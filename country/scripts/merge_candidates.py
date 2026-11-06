#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
候选合并脚本（方案 B 人工核对后的落地步骤）

流程：
1. 打开 country/updates/candidates.json，把要收录的条目 "approved" 改成 true，
   并补齐 country / region / type / status / headline / detail 字段（缺的会报错提示）。
2. 运行：python3 country/scripts/merge_candidates.py
3. 脚本把 approved 条目并入 country/updates/data.js 的 items，并把这些条目从候选池移除。
4. 检查无误后 commit —— data.js 一更新，栏目页即刻生效。

用法：
    python3 country/scripts/merge_candidates.py            # 正式合并
    python3 country/scripts/merge_candidates.py --dry-run  # 只看会合并什么
"""

import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.dirname(os.path.dirname(HERE))
UPDATES_DIR = os.path.join(SITE_ROOT, "country", "updates")
DATA_JS = os.path.join(UPDATES_DIR, "data.js")
INDEX_HTML = os.path.join(UPDATES_DIR, "index.html")
LD_OPEN = '<script type="application/ld+json">'
CANDIDATES = os.path.join(UPDATES_DIR, "candidates.json")

REQUIRED = ["country", "region", "type", "status", "headline", "detail"]
VALID_TYPES = None   # 运行时从 data.js 的 categories 读取
VALID_STATUS = None  # 运行时从 data.js 的 status_legend 读取


def load_data():
    raw = open(DATA_JS, encoding="utf-8").read()
    m = re.search(r"window\.UPDATES_DATA\s*=\s*(\{.*\})\s*;", raw, re.S)
    if not m:
        sys.exit("data.js 格式异常：未找到 window.UPDATES_DATA = {...};")
    return json.loads(m.group(1)), raw, m.span(1)


def dump_data(data, raw, span):
    body = json.dumps(data, ensure_ascii=False, indent=2)
    return raw[:span[0]] + body + raw[span[1]:]


def sync_jsonld(data):
    """把 data.js 的条目同步进 index.html 的 JSON-LD，避免结构化数据与页面漂移。"""
    if not os.path.exists(INDEX_HTML):
        return
    s = open(INDEX_HTML, encoding="utf-8").read()
    i = s.find(LD_OPEN)
    if i < 0:
        return
    a = i + len(LD_OPEN)
    b = s.find("</script>", a)
    try:
        ld = json.loads(s[a:b])
    except Exception as exc:
        print("  [warn] JSON-LD 解析失败，跳过同步: %s" % exc, file=sys.stderr)
        return
    items = data.get("items", [])
    for node in ld.get("@graph", []):
        t = node.get("@type")
        if t == "WebPage":
            node["dateModified"] = data.get("verified_date", "")
        elif t == "ItemList":
            node["numberOfItems"] = len(items)
            node["itemListElement"] = [
                {
                    "@type": "ListItem",
                    "position": k + 1,
                    "name": "%s %s：%s" % (it.get("date", ""), it.get("country", ""), it.get("headline", "")),
                    "url": "./#%s-%s" % (it.get("date", ""), it.get("country", "")),
                }
                for k, it in enumerate(items)
            ]
    open(INDEX_HTML, "w", encoding="utf-8").write(
        s[:a] + json.dumps(ld, ensure_ascii=False, indent=2) + s[b:]
    )


def main():
    dry = "--dry-run" in sys.argv
    if not os.path.exists(CANDIDATES):
        sys.exit("未找到 candidates.json，请先运行 fetch_updates.py")

    data, raw, span = load_data()
    valid_types = [c["key"] for c in data.get("categories", [])]
    valid_status = [s["key"] if isinstance(s, dict) else s
                    for s in data.get("status_legend", [])]

    pool = json.load(open(CANDIDATES, encoding="utf-8"))
    items = pool.get("candidates", [])
    approved = [c for c in items if c.get("approved")]

    if not approved:
        print("没有 approved=true 的候选，无需合并。")
        return 0

    today = date.today().isoformat()
    errors, added = [], []
    for c in approved:
        miss = [k for k in REQUIRED if not str(c.get(k, "")).strip()]
        if miss:
            errors.append("%s 缺少字段: %s" % (c.get("title", "")[:40], ", ".join(miss)))
            continue
        if valid_types and c["type"] not in valid_types:
            errors.append("%s type 非法: %s（可选 %s）" % (c.get("title", "")[:40], c["type"], valid_types))
            continue
        if valid_status and c["status"] not in valid_status:
            errors.append("%s status 非法: %s（可选 %s）" % (c.get("title", "")[:40], c["status"], valid_status))
            continue
        item = {
            "date": c.get("date") or today,
            "country": c["country"],
            "region": c["region"],
            "type": c["type"],
            "status": c["status"],
            "headline": c["headline"],
            "detail": c["detail"],
            "sources": c.get("sources") or ([{"name": c.get("source", ""), "date": c.get("date") or today,
                                              "url": c.get("url", "")}] if c.get("url") else []),
        }
        added.append(item)

    if errors:
        print("以下候选不合格，已跳过：")
        for e in errors:
            print(" -", e)
        if not added:
            return 1

    if dry:
        print("干跑：将合并 %d 条" % len(added))
        for a in added:
            print(" -", a["date"], a["country"], a["headline"])
        return 0

    data["items"] = added + data.get("items", [])
    data["items"].sort(key=lambda x: x.get("date", ""), reverse=True)
    data["verified_date"] = today

    open(DATA_JS, "w", encoding="utf-8").write(dump_data(data, raw, span))
    sync_jsonld(data)

    leftover = [c for c in items if not c.get("approved")]
    pool["candidates"] = leftover
    json.dump(pool, open(CANDIDATES, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("已并入 %d 条，data.js 现有 %d 条；候选池剩余 %d 条。"
          % (len(added), len(data["items"]), len(leftover)))
    if errors:
        print("另有 %d 条候选不合格被保留在池中。" % len(errors))
    return 0


if __name__ == "__main__":
    sys.exit(main())
