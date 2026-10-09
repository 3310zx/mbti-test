#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mbti-site 静态体检：死链 / hreflang 11 条 / lang-switch selected / 标签配对 / JS 三元表达式完整性。

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


def check_ternary():
    """JS 三元表达式完整性检查（防缺 else 分支导致脚本语法错误）。

    对每个 HTML 的 <script> 块做词法级扫描：
      1. 字符串未闭合（单/双引号，跨行即视为未闭合）；
      2. 括号配对（跳过字符串/注释/正则字面量）；
      3. 三元缺 else：`? '...'` 后直接以 `;` 结束（无 ` : ` 分支），
         排除 `+` 前缀的字符串拼接场景。
    """
    for page in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(page, ROOT)
        text = open(page, encoding="utf-8").read()
        for m in re.finditer(r"<script\b[^>]*>(.*?)</script>", text, re.S):
            js = m.group(1)
            line0 = text[: m.start()].count("\n") + 1

            # 1) 字符串未闭合
            i, n, line = 0, len(js), 1
            while i < n:
                c = js[i]
                if c == "\n":
                    line += 1; i += 1; continue
                if c == "/" and i + 1 < n and js[i + 1] == "/":
                    while i < n and js[i] != "\n":
                        i += 1
                    continue
                if c == "/" and i + 1 < n and js[i + 1] == "*":
                    i += 2
                    while i + 1 < n and not (js[i] == "*" and js[i + 1] == "/"):
                        if js[i] == "\n":
                            line += 1
                        i += 1
                    i += 2
                    continue
                if c in ("'", '"', "`"):
                    q = c; i += 1; closed = False
                    while i < n:
                        cc = js[i]
                        if cc == "\\":
                            i += 2; continue
                        if cc == q:
                            closed = True; i += 1; break
                        if cc == "\n":
                            line += 1
                            if q != "`":
                                break
                            i += 1; continue
                        i += 1
                    if not closed:
                        errors.append(
                            "[ternary] %s 脚本(起点行 %d) 第 %d 行字符串未闭合 %s"
                            % (rel, line0, line, q)
                        )
                    continue
                # 正则字面量跳过
                if c == "/" and i + 1 < n and js[i + 1] not in ("/", "*"):
                    j = i - 1
                    while j >= 0 and js[j].isspace():
                        j -= 1
                    prev = js[j] if j >= 0 else ""
                    if prev in "=(:[!&|?{};,":
                        i += 1
                        while i < n:
                            cc = js[i]
                            if cc == "\\":
                                i += 2; continue
                            if cc == "\n":
                                line += 1; i += 1; continue
                            if cc == "/":
                                i += 1; break
                            i += 1
                        continue
                i += 1

            # 2) 括号配对（独立于字符串扫描，复用跳过逻辑走一遍）
            stack = []
            pairs = {"(": ")", "{": "}", "[": "]"}
            i, line = 0, 1
            while i < n:
                c = js[i]
                if c == "\n":
                    line += 1; i += 1; continue
                if c == "/" and i + 1 < n and js[i + 1] == "/":
                    while i < n and js[i] != "\n":
                        i += 1
                    continue
                if c == "/" and i + 1 < n and js[i + 1] == "*":
                    i += 2
                    while i + 1 < n and not (js[i] == "*" and js[i + 1] == "/"):
                        if js[i] == "\n":
                            line += 1
                        i += 1
                    i += 2
                    continue
                if c in ("'", '"', "`"):
                    q = c; i += 1
                    while i < n:
                        cc = js[i]
                        if cc == "\\":
                            i += 2; continue
                        if cc == q:
                            i += 1; break
                        if cc == "\n":
                            line += 1
                            if q != "`":
                                break
                            i += 1; continue
                        i += 1
                    continue
                if c == "/" and i + 1 < n and js[i + 1] not in ("/", "*"):
                    j = i - 1
                    while j >= 0 and js[j].isspace():
                        j -= 1
                    prev = js[j] if j >= 0 else ""
                    if prev in "=(:[!&|?{};,":
                        i += 1
                        while i < n:
                            cc = js[i]
                            if cc == "\\":
                                i += 2; continue
                            if cc == "\n":
                                line += 1; i += 1; continue
                            if cc == "/":
                                i += 1; break
                            i += 1
                        continue
                if c in pairs:
                    stack.append((c, line))
                elif c in pairs.values():
                    if not stack:
                        errors.append("[ternary] %s 脚本(起点行 %d) 第 %d 行多余括号 %s"
                                      % (rel, line0, line, c))
                    else:
                        o, ol = stack.pop()
                        if pairs[o] != c:
                            errors.append(
                                "[ternary] %s 脚本(起点行 %d) 括号不配对：%s(第%d行) 被 %s(第%d行) 闭合"
                                % (rel, line0, o, ol, c, line)
                            )
                i += 1
            for o, ol in stack:
                errors.append("[ternary] %s 脚本(起点行 %d) 第 %d 行括号 %s 未闭合"
                              % (rel, line0, ol, o))

            # 3) 三元缺 else：`? '...';` 直接以分号结束
            for tm in re.finditer(r"\?\s*'(?:[^'\\]|\\.)*'\s*;", js):
                start = tm.start()
                j = start - 1
                while j >= 0 and js[j].isspace():
                    j -= 1
                if j >= 0 and js[j] == "+":
                    continue
                tline = js[:start].count("\n") + 1
                errors.append(
                    "[ternary] %s 脚本(起点行 %d) 第 %d 行三元表达式缺少 else 分支: %s"
                    % (rel, line0, tline, js[start : start + 80])
                )


def main():
    check_links()
    check_hreflang()
    check_lang_switch()
    check_tag_pairs()
    check_ternary()
    if errors:
        print("CHECK FAILED: %d 个问题" % len(errors))
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(
        "CHECK PASSED: 死链 / hreflang / lang-switch / 标签配对 / JS 三元表达式 全部通过 (%d 个 HTML)"
        % len(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
    )


if __name__ == "__main__":
    main()
