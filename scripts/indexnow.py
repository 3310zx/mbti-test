#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 sitemap.xml 中的 URL 批量推送给 IndexNow（Bing / DuckDuckGo / Yandex / Seznam）。
用法：python3 scripts/indexnow.py [--dry]
密钥文件：仓库根目录 <key>.txt，key 从环境变量 INDEXNOW_KEY 读取，缺省读取仓库内唯一 32 位 hex 文件名。
"""
import json, os, re, sys, urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "3310zx.github.io"
SITEMAP = os.path.join(BASE, "sitemap.xml")
ENDPOINT = "https://api.indexnow.org/indexnow"


def find_key():
    env = os.environ.get("INDEXNOW_KEY", "").strip()
    if env:
        return env
    for name in os.listdir(BASE):
        if re.fullmatch(r"[0-9a-f]{32}\.txt", name):
            return name[:-4]
    raise SystemExit("未找到 IndexNow 密钥文件（仓库根目录需存在 <32位hex>.txt）")


def urls():
    xml = open(SITEMAP, encoding="utf-8").read()
    out = []
    for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml):
        if loc.startswith(f"https://{HOST}/") and loc not in out:
            out.append(loc)
    return out


def main():
    key = find_key()
    url_list = urls()
    payload = {"host": HOST, "key": key, "keyLocation": f"https://{HOST}/mbti-test/{key}.txt", "urlList": url_list}
    if "--dry" in sys.argv:
        print(json.dumps(payload, ensure_ascii=False)[:600], "\n共", len(url_list), "条")
        return
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("HTTP", r.status, "提交", len(url_list), "条 URL")
            body = r.read().decode("utf-8", "ignore").strip()
            if body:
                print(body[:300])
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode("utf-8", "ignore")[:300])
        sys.exit(1)


if __name__ == "__main__":
    main()
