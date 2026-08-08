#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每日国际要闻：抓取前一天 RSS 头条并发送至 QQ 邮箱。

依赖：feedparser（pip install feedparser）
环境变量（从 GitHub Secrets 注入）：
  SMTP_USER  发件 QQ 邮箱，如 123456@qq.com
  SMTP_PASS  QQ 邮箱「授权码」（非登录密码）
  TO_EMAIL   接收邮箱（可与发件箱相同）
"""
import os
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import feedparser

# 国际新闻 RSS 源（中文为主）。单个源失败不影响整体，会自动跳过。
FEEDS = [
    ("BBC中文", "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml"),
    ("纽约时报中文", "https://cn.nytimes.com/rss/"),
    ("联合国新闻(中文)", "https://news.un.org/feed/subscribe/zh/news/"),
    ("新华网国际", "http://www.xinhuanet.com/news/world/world.xml"),
    ("央视新闻国际", "https://news.cctv.com/rss/world.xml"),
    ("RFI中文", "https://www.rfi.fr/zh/zhongwen/rss.xml"),
    ("德国之声中文", "https://www.dw.com/zh/%E4%B8%AD%E5%9B%BD/rss-90199999.xml"),
]

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Shanghai")
except Exception:
    TZ = timezone(timedelta(hours=8))


def yesterday_beijing():
    """返回北京时间「前一天」的日期。"""
    return (datetime.now(TZ) - timedelta(days=1)).date()


def fetch(ydate):
    """抓取国际新闻条目。

    优先取「昨天 + 今天」发布的条目；若不足 5 条（源更新滞后），
    则回退到最近 48 小时内的最新条目，保证日报不为空。所有条目
    按发布时间倒序、去重后最多返回 30 条。
    """
    now = datetime.now(TZ)
    tdate = now.date()
    window_start = now - timedelta(hours=48)
    all_items, seen = [], set()
    for name, url in FEEDS:
        try:
            d = feedparser.parse(url, agent="Mozilla/5.0")
        except Exception as ex:
            print(f"[warn] 源失败 {name}: {ex}")
            continue
        for e in d.entries:
            p = e.get("published_parsed") or e.get("updated_parsed")
            if not p:
                continue
            dt = datetime(*p[:6], tzinfo=timezone.utc).astimezone(TZ)
            key = e.get("link") or e.get("title")
            if key in seen:
                continue
            seen.add(key)
            all_items.append({
                "source": name,
                "title": e.get("title", "(无标题)"),
                "link": e.get("link", ""),
                "summary": e.get("summary", ""),
                "dt": dt,
            })
    all_items.sort(key=lambda x: x["dt"], reverse=True)

    primary = [it for it in all_items if it["dt"].date() in (ydate, tdate)]
    if len(primary) >= 5:
        items = primary[:30]
    else:
        # 源滞后时回退：最近 48 小时，仍不足则直接取最新若干条
        recent = [it for it in all_items if it["dt"] >= window_start]
        items = (recent if len(recent) >= 5 else all_items)[:30]
    return items


def _clean(text):
    """去除 HTML 标签与多余空白，便于正文预览。"""
    import re
    text = re.sub(r"<[^>]+>", "", text or "")
    return re.sub(r"\s+", " ", text).strip()


def build_html(items, ydate):
    if not items:
        rows = '<p style="color:#888">昨日暂无抓取到的新闻条目（可能源未更新或网络受限）。</p>'
    else:
        rows = ""
        for it in items:
            summary = _clean(it["summary"])
            if len(summary) > 120:
                summary = summary[:120] + "…"
            rows += f"""
            <div style="border-bottom:1px solid #eee;padding:10px 0">
              <a href="{it['link']}" style="font-size:16px;color:#1a73e8;text-decoration:none;font-weight:bold">{it['title']}</a>
              <div style="color:#666;font-size:12px;margin:4px 0">{it['source']} · {it['dt'].strftime('%Y-%m-%d %H:%M')}</div>
              <div style="color:#444;font-size:14px;line-height:1.5">{summary}</div>
            </div>"""
    return f"""
    <html><body style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:680px;margin:0 auto;padding:20px">
      <h2 style="color:#202124">🌍 国际要闻日报 · {ydate}</h2>
      <p style="color:#888;font-size:13px">由 GitHub Actions 自动抓取并发送 · 共 {len(items)} 条</p>
      {rows}
    </body></html>"""


def send_mail(html, ydate):
    user = os.environ["SMTP_USER"]
    pwd = os.environ["SMTP_PASS"]
    to = os.environ["TO_EMAIL"]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = Header(f"🌍 国际要闻日报 · {ydate}", "utf-8")
    msg["From"] = user
    msg["To"] = to
    msg.attach(MIMEText(html, "html", "utf-8"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.qq.com", 465, context=ctx) as s:
        s.login(user, pwd)
        s.send_message(msg)
    print(f"[ok] 已发送至 {to}")


def main():
    ydate = yesterday_beijing()
    print(f"[info] 抓取前一天新闻：{ydate}")
    items = fetch(ydate)
    print(f"[info] 命中 {len(items)} 条")
    html = build_html(items, ydate)
    send_mail(html, ydate)


if __name__ == "__main__":
    main()
