#!/usr/bin/env python3
"""把 report.md / index.md 渲染成纯静态页面（无需 Jekyll），并注入 SEO 元信息。
用法: python3 build_site.py
"""
import datetime
import json
import pathlib
import re

import markdown

SITE = "https://salt66688.github.io/yuanxiang-wansheng-dd"
ORG = "杭州元像万生科技有限公司"
BRAND = "盐脉基座大模型"

SEO = {
    "index.html": {
        "url": f"{SITE}/",
        "title": f"{ORG} 投资尽调报告｜{BRAND}（salt-u.com）业务核验",
        "desc": (
            f"投资人视角尽职调查：{ORG}（原杭州乐书数字科技）累计放款约 10 亿元中约六成为虚拟冲量订单，"
            f"息费收入约 660 万元对应收益率不足 1%；旗下「{BRAND}」（salt-u.com）无产品、无客户、无收入。"
            "含股权穿透、风险清单与投资建议。"
        ),
        "keywords": (
            f"{ORG},盐脉基座大模型,salt-u,salt-u.com,盐脉,杭州乐书数字科技,杭州昱财科技,"
            "供应链金融,尽职调查,投资尽调,标记类订单,助贷,关平,影子鑰,ShadowKey,91330109MABU52HJ0G"
        ),
        "type": "article",
    },
    "report.html": {
        "url": f"{SITE}/report.html",
        "title": f"全文｜{ORG} 投资尽调报告（{BRAND} / salt-u.com 核验）",
        "desc": (
            f"{ORG} 投资尽调报告全文，九章 12 张数据表：主体沿革与股权穿透、{BRAND}（salt-u.com）"
            "业务可信度评估、标记类订单识别与量化、风险清单 R1-R4 / O1-O6 / Y1-Y5、七项交割前置条件。"
        ),
        "keywords": (
            f"{ORG} 尽调报告,盐脉基座大模型,salt-u.com,salt-u,数据要素,大模型基座,"
            "杭州乐书数字科技,标记类订单,虚拟订单,冲量,股权投资,尽职调查全文"
        ),
        "type": "article",
    },
}

CSS = """
:root{--fg:#1a1a1a;--muted:#6b7280;--line:#e5e7eb;--accent:#b91c1c;--bg:#fff;--soft:#f8f9fb}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
 font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
 font-size:16px;line-height:1.85;-webkit-font-smoothing:antialiased}
.wrap{max-width:860px;margin:0 auto;padding:48px 24px 96px}
header.site{border-bottom:1px solid var(--line);margin-bottom:36px;padding-bottom:18px}
header.site a{color:var(--muted);text-decoration:none;font-size:13px;letter-spacing:.04em}
h1{font-size:30px;line-height:1.45;margin:8px 0 20px;font-weight:700;letter-spacing:-.01em}
h2{font-size:21px;margin:48px 0 16px;padding-left:12px;border-left:4px solid var(--accent);font-weight:700}
h3{font-size:17px;margin:32px 0 12px;font-weight:600;color:#111}
h4{font-size:16px;margin:24px 0 10px;font-weight:600;color:#374151}
p{margin:12px 0}
a{color:#1d4ed8;text-decoration:none;border-bottom:1px solid rgba(29,78,216,.25)}
a:hover{border-bottom-color:#1d4ed8}
strong{font-weight:600}
hr{border:0;border-top:1px solid var(--line);margin:40px 0}
blockquote{margin:18px 0;padding:12px 18px;background:var(--soft);border-left:3px solid #cbd5e1;color:#374151}
blockquote p{margin:0}
ul,ol{padding-left:24px;margin:12px 0}
li{margin:7px 0}
li>ul,li>ol{margin:6px 0}
table{border-collapse:collapse;width:100%;margin:22px 0;font-size:14.5px;display:block;overflow-x:auto;white-space:nowrap}
th,td{border:1px solid var(--line);padding:9px 12px;text-align:left;vertical-align:top;white-space:normal}
th{background:#f1f5f9;font-weight:600}
tbody tr:nth-child(even){background:#fafbfc}
code{background:#f2f4f7;padding:.15em .4em;border-radius:4px;font-size:.9em}
.callout{background:linear-gradient(180deg,#fff7f7,#fff);border:1px solid #fecaca;border-radius:10px;padding:18px 20px;margin:24px 0}
.callout p{margin:6px 0}
.meta{color:var(--muted);font-size:13.5px;line-height:1.7;margin:0}
footer{border-top:1px solid var(--line);margin-top:56px;padding-top:20px;color:var(--muted);font-size:13px}
.toc{background:var(--soft);border:1px solid var(--line);border-radius:10px;padding:16px 22px;margin:24px 0}
.toc h4{margin:0 0 8px;font-size:13px;letter-spacing:.08em;color:var(--muted);text-transform:uppercase}
.toc ul{list-style:none;padding:0;margin:0;columns:2;column-gap:28px}
.toc li{margin:4px 0;font-size:14.5px}
@media(max-width:640px){.toc ul{columns:1}.wrap{padding:28px 16px 64px}h1{font-size:24px}}
@media print{header.site,footer{display:none}.wrap{max-width:none;padding:0}}
"""


def structured_data(seo, page_name, today):
    about = [
        {
            "@type": "Organization",
            "name": ORG,
            "alternateName": ["杭州乐书数字科技有限公司", "杭州昱财科技有限公司"],
            "identifier": "91330109MABU52HJ0G",
            "url": f"{SITE}/",
        },
        {"@type": "Brand", "name": BRAND, "url": "https://salt-u.com"},
        {"@type": "Organization", "name": "杭州乐书数字科技有限公司"},
        {"@type": "Organization", "name": "杭州零图电子商务有限公司"},
    ]
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": seo["title"],
        "name": seo["title"],
        "description": seo["desc"],
        "inLanguage": "zh-CN",
        "datePublished": today,
        "dateModified": today,
        "url": seo["url"],
        "mainEntityOfPage": {"@type": "WebPage", "@id": seo["url"]},
        "isAccessibleForFree": True,
        "author": {"@type": "Organization", "name": "投资人尽调"},
        "publisher": {"@type": "Organization", "name": "投资人尽调"},
        "about": about,
        "mentions": [
            {"@type": "Thing", "name": "尽职调查"},
            {"@type": "Thing", "name": "供应链金融"},
            {"@type": "Thing", "name": "标记类订单"},
            {"@type": "Thing", "name": "数据要素"},
        ],
        "keywords": seo["keywords"],
    }
    ld = json.dumps(data, ensure_ascii=False, indent=2)
    return f'<script type="application/ld+json">\n{ld}\n</script>'


def page(page_name, body, today, home=False):
    seo = SEO[page_name]
    nav = (
        ""
        if home
        else f'<header class="site"><a href="index.html">{ORG} · 投资尽调报告</a></header>'
    )
    return f"""<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{seo["title"]}</title>
<meta name="description" content="{seo["desc"]}">
<meta name="keywords" content="{seo["keywords"]}">
<meta name="author" content="投资人尽调">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="googlebot" content="index,follow">
<link rel="canonical" href="{seo["url"]}">
<meta property="og:type" content="{seo["type"]}">
<meta property="og:site_name" content="{ORG} 投资尽调报告">
<meta property="og:title" content="{seo["title"]}">
<meta property="og:description" content="{seo["desc"]}">
<meta property="og:url" content="{seo["url"]}">
<meta property="og:locale" content="zh_CN">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{seo["title"]}">
<meta name="twitter:description" content="{seo["desc"]}">
{structured_data(seo, page_name, today)}
<style>{CSS}</style></head>
<body><div class="wrap">{nav}{body}
<footer><p>{ORG} 投资尽调报告｜{BRAND}（salt-u.com）业务核验｜本材料为投资研究用途，不构成审计报告、法律意见或投资建议。文中金额均为概数。</p></footer>
</div></body></html>"""


def md2html(text):
    return markdown.markdown(
        text, extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"]
    )


def build():
    root = pathlib.Path(__file__).parent
    today = datetime.date.today().isoformat()

    # ---- report.html ----
    rep = (root / "report.md").read_text(encoding="utf-8")
    html = md2html(rep)
    hs = re.findall(r"<h2>(.*?)</h2>", html)
    items = []
    for h in hs:
        slug = re.sub(r"[^\w\u4e00-\u9fa5]+", "-", h).strip("-").lower()
        html = html.replace(f"<h2>{h}</h2>", f'<h2 id="{slug}">{h}</h2>', 1)
        items.append(f'<li><a href="#{slug}">{h}</a></li>')
    toc = '<div class="toc"><h4>目录</h4><ul>' + "".join(items) + "</ul></div>"
    html = html.replace("</h1>", "</h1>" + toc, 1)
    (root / "report.html").write_text(page("report.html", html, today), encoding="utf-8")

    # ---- index.html ----
    idx = (root / "index.md").read_text(encoding="utf-8")
    idx = re.sub(r"^---.*?---\s*", "", idx, flags=re.S)
    (root / "index.html").write_text(page("index.html", md2html(idx), today, home=True), encoding="utf-8")

    # ---- robots.txt / sitemap.xml ----
    (root / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {SITE}/sitemap.xml\n",
        encoding="utf-8",
    )
    urls = "".join(
        f"  <url><loc>{v['url']}</loc><lastmod>{today}</lastmod>"
        f"<changefreq>weekly</changefreq><priority>{'1.0' if k == 'index.html' else '0.9'}</priority></url>\n"
        for k, v in SEO.items()
    )
    (root / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}</urlset>\n",
        encoding="utf-8",
    )
    print("built:", (root / "index.html").stat().st_size, (root / "report.html").stat().st_size)


if __name__ == "__main__":
    build()
