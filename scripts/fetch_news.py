#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日热点新闻采集脚本
- 调用 60s 开源接口获取当天热点新闻（无需密钥）
- 取前 10 条，生成 news/YYYY-MM-DD.md
- 由 GitHub Actions 定时调用
"""
import json
import os
import datetime
import urllib.request

API_URL = "https://60s-api.viki.moe/v2/60s"
NEWS_COUNT = 10
OUTPUT_DIR = "news"


def fetch_news():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    data = fetch_news()
    payload = data.get("data", {})
    news_list = [n for n in payload.get("news", []) if n]
    top = news_list[:NEWS_COUNT]

    news_date = payload.get("date") or datetime.date.today().strftime("%Y-%m-%d")
    today = datetime.date.today().strftime("%Y-%m-%d")

    lines = [
        f"# 📰 每日热点新闻摘要（{news_date}）\n",
        "> 本文件由 GitHub Actions 自动生成，数据来源：60s 开源接口（https://github.com/vikiboss/60s）\n",
        f"*生成时间：{today}*\n",
        "## 今日热点 Top 10\n",
    ]
    for i, item in enumerate(top, 1):
        lines.append(f"{i}. {item}")
    lines.append("")

    content = "\n".join(lines)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{today}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ 已生成：{out_path}")
    print(content)


if __name__ == "__main__":
    main()
