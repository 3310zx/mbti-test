#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国际动态候选抓取脚本（方案 B 半自动）

职责：从 Google News RSS 抓取「签证 / 居留 / 生活成本」相关的候选新闻，
去重后写入 country/updates/candidates.json。
本脚本只产出「候选」，不会改动 data.js —— 是否收录由人工核对决定。

用法（本地或 GitHub Actions 均可）：
    python3 country/scripts/fetch_updates.py

依赖：仅标准库。
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from difflib import SequenceMatcher

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.dirname(os.path.dirname(HERE))          # 仓库根
UPDATES_DIR = os.path.join(SITE_ROOT, "country", "updates")
DATA_JS = os.path.join(UPDATES_DIR, "data.js")
CANDIDATES = os.path.join(UPDATES_DIR, "candidates.json")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# 检索式：只收政策变动类，不收泛新闻
QUERIES = [
    '"digital nomad visa" OR "residence permit" when:14d',
    '"golden visa" OR "citizenship by investment" when:14d',
    '"visa policy" OR "immigration policy" changes when:14d',
    '"cost of living" expat policy OR rule when:14d',
    'Thailand OR Malaysia OR Portugal OR "United Arab Emirates" visa rule when:14d',
    'Japan OR Korea OR Taiwan OR Singapore visa OR residence when:14d',
    'Mexico OR Panama OR Georgia OR Serbia residence permit when:14d',
    'Italy OR Spain OR Greece OR Hungary "digital nomad" OR visa when:14d',
]

MAX_PER_QUERY = 10
SIM_THRESHOLD = 0.72   # 标题相似度超过该值视为重复

# 噪音词：命中即丢弃，避免「Visa 公司财报」「加密货币」等误命中占用人工核对时间
NOISE = [
    "stablecoin", "crypto", "bitcoin", "blockchain", "earnings", "quarterly results",
    "stock", "shares", "ceo", "appoints", "partnership", "sponsor", "ipo",
    "airline", "flight", "hotel", "tourism boom", "world cup", "olympic",
]


def is_noise(title):
    t = (title or "").lower()
    return any(w in t for w in NOISE)


def norm_title(t):
    t = (t or "").lower()
    t = re.sub(r"[-|–:].*$", " ", t)          # 去掉 Google News 标题尾巴的媒体名
    t = re.sub(r"[^0-9a-z\u4e00-\u9fff ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def fetch_rss(query):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def parse_rss(xml_bytes, query):
    out = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        print("  [warn] RSS 解析失败: %s" % exc, file=sys.stderr)
        return out
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        src_node = item.find("source")
        source = src_node.text.strip() if src_node is not None and src_node.text else ""
        if not title or not link:
            continue
        try:
            dt = datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
            date = dt.strftime("%Y-%m-%d")
        except Exception:
            date = ""
        out.append({
            "title": title,
            "source": source,
            "date": date,
            "url": link,
            "query": query,
        })
    return out


def load_existing_titles():
    """读取 data.js 中已收录条目的标题，用于去重。"""
    titles = []
    if not os.path.exists(DATA_JS):
        return titles
    raw = open(DATA_JS, encoding="utf-8").read()
    m = re.search(r"window\.UPDATES_DATA\s*=\s*(\{.*\})\s*;", raw, re.S)
    if not m:
        return titles
    try:
        data = json.loads(m.group(1))
    except Exception:
        return titles
    for it in data.get("items", []):
        titles.append(norm_title(it.get("headline", "")))
    return titles


def is_duplicate(title, known):
    nt = norm_title(title)
    for k in known:
        if not k:
            continue
        if nt == k:
            return True
        if SequenceMatcher(None, nt, k).ratio() >= SIM_THRESHOLD:
            return True
    return False


def main():
    os.makedirs(UPDATES_DIR, exist_ok=True)
    known = load_existing_titles()

    # 保留上一轮候选中「尚未处理」的条目，避免每次覆盖丢失人工未核对的记录
    kept = []
    if os.path.exists(CANDIDATES):
        try:
            prev = json.load(open(CANDIDATES, encoding="utf-8"))
            kept = [c for c in prev.get("candidates", []) if not c.get("approved")]
        except Exception:
            kept = []

    fresh, seen, errors = [], [], 0
    for q in QUERIES:
        print("查询: %s" % q)
        try:
            items = parse_rss(fetch_rss(q), q)
        except Exception as exc:
            print("  [error] %s" % exc, file=sys.stderr)
            errors += 1
            time.sleep(2)
            continue
        for it in items[:MAX_PER_QUERY]:
            if is_noise(it["title"]):
                continue
            if is_duplicate(it["title"], known) or is_duplicate(it["title"], seen):
                continue
            seen.append(norm_title(it["title"]))
            fresh.append(it)
        time.sleep(1.2)

    if not fresh and errors == len(QUERIES):
        print("全部查询失败，保留原 candidates.json 不覆盖", file=sys.stderr)
        return 1

    # 合并：去重后旧候选 + 新候选，按日期倒序
    merged, soc = [], []
    for c in kept + fresh:
        nt = norm_title(c.get("title", ""))
        if nt in soc:
            continue
        soc.append(nt)
        c.setdefault("approved", False)
        merged.append(c)
    merged.sort(key=lambda x: x.get("date") or "", reverse=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "本文件为自动抓取的候选池，未收录。人工核对后把要收录条目的 approved 改为 true，运行 merge_candidates.py 并入 data.js。",
        "candidates": merged,
    }
    with open(CANDIDATES, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print("\n新增候选 %d 条，候选池合计 %d 条 -> %s" % (len(fresh), len(merged), CANDIDATES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
