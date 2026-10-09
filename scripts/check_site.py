#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mbti-site 静态体检：死链 / hreflang 11 条 / lang-switch selected / 标签配对。

用法: python3 scripts/check_site.py
任一检查失败输出详情并以 exit 1 退出（供 GitHub Actions 使用）。
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "//", "#")

errors = []
warnings = []


def check_links():
    """死链检查：相对 href/src 解析到磁盘必须存在。"""
    for page in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(page, ROOT)
        text = open(page, encoding="utf-8").read()
        base = os.path.dirname(page)
        for attr in ("href", "src"):
            for m in re.finditer(r'\b%s="([^"]*)"' % attr, text):
                target = m.group(1).strip()
                if not target or target.startswith(SKIP_PREFIX) or target.startswith("#"):
                    continue
                # 跳过 JS 字符串拼接（src="'+o+=... 这类非真实 HTML 属性值）
                if "'" in target or '"' in target or "+" in target or "(" in target or "," in target:
                    continue
                # 去掉锚点 / 查询参数
                clean = target.split("#", 1)[0].split("?", 1)[0]
                if not clean:
                    continue
                resolved = os.path.normpath(os.path.join(base, clean))
                if not os.path.exists(resolved):
                    errors.append("[死链] %s -> %s (%s=%s)" % (rel, resolved, attr, target))


def check_hreflang():
    """每页 hreflang 必须 11 条（10 语言 + x-default）。"""
    for page in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(page, ROOT)
        text = open(page, encoding="utf-8").read()
        n = len(re.findall(r"hreflang=", text))
        if n != 11:
            errors.append("[hreflang] %s 期望 11 条，实际 %d 条" % (rel, n))


def check_lang_switch():
    """每个 select.lang-switch 内 selected option 必须恰好 1 个。"""
    for page in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(page, ROOT)
        text = open(page, encoding="utf-8").read()
        for sel in re.finditer(r"<select[^>]*class=\"[^\"]*lang-switch[^\"]*\"[^>]*>.*?</select>", text, re.S):
            body = sel.group(0)
            opts = re.findall(r"<option\b[^>]*>", body)
            sel_opts = [o for o in opts if re.search(r"\bselected\b", o)]
            if len(sel_opts) != 1:
                errors.append(
                    "[lang-switch] %s 中 selected option 数量为 %d（期望 1）"
                    % (rel, len(sel_opts))
                )


def check_tag_pairs():
    """style / script 标签开闭配对。"""
    for page in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(page, ROOT)
        text = open(page, encoding="utf-8").read()
        for tag in ("style", "script"):
            opens = len(re.findall(r"<%s[\s>]" % tag, text))
            closes = len(re.findall(r"</%s>" % tag, text))
            if opens != closes:
                errors.append("[tag-pair] %s <%s> 开 %d / 闭 %d 不配对" % (rel, tag, opens, closes))


def main():
    check_links()
    check_hreflang()
    check_lang_switch()
    check_tag_pairs()
    if errors:
        print("CHECK FAILED: %d 个问题" % len(errors))
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("CHECK PASSED: 死链 / hreflang / lang-switch / 标签配对 全部通过 (%d 个 HTML)" %
          len(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)))


if __name__ == "__main__":
    main()
