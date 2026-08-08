#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地执行：抓取前一天国际新闻并生成总结（HTML + 文本），不发送邮件。"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_news as fn

HTML_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "news_latest.html")
TXT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "news_latest.txt")


def main():
    ydate = fn.yesterday_beijing()
    print(f"[info] 抓取前一天新闻：{ydate}")
    items = fn.fetch(ydate)
    print(f"[info] 命中 {len(items)} 条")
    html = fn.build_html(items, ydate)

    with open(os.path.abspath(HTML_OUT), "w", encoding="utf-8") as f:
        f.write(html)

    lines = [f"国际要闻日报 · {ydate}", "=" * 40]
    for i, it in enumerate(items, 1):
        lines.append(f"{i}. 【{it['source']}】{it['title']}")
        lines.append(f"   时间：{it['dt'].strftime('%Y-%m-%d %H:%M')}  链接：{it['link']}")
        s = fn._clean(it["summary"])
        if s:
            lines.append(f"   摘要：{s[:120]}")
        lines.append("")
    text = "\n".join(lines)
    with open(os.path.abspath(TXT_OUT), "w", encoding="utf-8") as f:
        f.write(text)

    print(text)
    print(f"\n[ok] HTML -> {os.path.abspath(HTML_OUT)}")
    print(f"[ok] TXT  -> {os.path.abspath(TXT_OUT)}")


if __name__ == "__main__":
    main()
