#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 sitemap.xml 中的 URL 批量推送给 IndexNow（Bing / DuckDuckGo / Yandex / Seznam）。
用法：python3 scripts/indexnow.py [--dry]
密钥文件：仓库根目录 <key>.txt，key 从环境变量 INDEXNOW_KEY 读取，缺省读取仓库内唯一 32 位 hex 文件名。
"""
import json, os, re, sys, time, urllib.error, urllib.request

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
    """汇总 sitemap.xml 页面 URL + sitemap-images.xml 中的图片 URL"""
    out = []
    for path in (SITEMAP, os.path.join(BASE, "sitemap-images.xml")):
        if not os.path.exists(path):
            continue
        xml = open(path, encoding="utf-8").read()
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)
        locs += re.findall(r"<image:loc>\s*([^<\s]+)\s*</image:loc>", xml)
        for loc in locs:
            if loc.startswith(f"https://{HOST}/") and loc not in out:
                out.append(loc)
    return out


def wait_key(key, timeout=300):
    """等 Pages 部署完成、keyLocation 可访问（否则 IndexNow 会拒绝）"""
    kl = f"https://{HOST}/mbti-test/{key}.txt"
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(kl, timeout=15) as r:
                if r.status == 200 and key in r.read().decode("utf-8", "ignore"):
                    print("keyLocation 已可访问：", kl)
                    return True
        except Exception:
            pass
        print("等待 keyLocation 上线… %ds" % int(time.time() - t0))
        time.sleep(15)
    return False


def post(payload, attempts=3):
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    for i in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                print("HTTP", r.status, "提交", len(payload["urlList"]), "条 URL")
                body = r.read().decode("utf-8", "ignore").strip()
                if body:
                    print(body[:300])
                return True
        except urllib.error.HTTPError as e:
            print("第 %d 次尝试 HTTP %s: %s" % (i, e.code, e.read().decode("utf-8", "ignore")[:200]))
        except Exception as e:
            print("第 %d 次尝试失败: %s" % (i, e))
        if i < attempts:
            time.sleep(20)
    return False


def main():
    key = find_key()
    url_list = urls()
    payload = {"host": HOST, "key": key, "keyLocation": f"https://{HOST}/mbti-test/{key}.txt", "urlList": url_list}
    if "--dry" in sys.argv:
        print(json.dumps(payload, ensure_ascii=False)[:600], "\n共", len(url_list), "条")
        return
    if "--no-wait" not in sys.argv and not wait_key(key):
        print("keyLocation 300s 内仍未上线，跳过本次提交")
        sys.exit(1)
    if not post(payload):
        sys.exit(1)


if __name__ == "__main__":
    main()
