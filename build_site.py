#!/usr/bin/env python3
"""把 report.md / README.md 渲染成纯静态页面（无需 Jekyll）。"""
import markdown, re, pathlib

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
.badge{display:inline-block;background:var(--accent);color:#fff;font-size:12px;font-weight:600;
 padding:2px 9px;border-radius:20px;letter-spacing:.05em;vertical-align:2px;margin-right:8px}
footer{border-top:1px solid var(--line);margin-top:56px;padding-top:20px;color:var(--muted);font-size:13px}
.toc{background:var(--soft);border:1px solid var(--line);border-radius:10px;padding:16px 22px;margin:24px 0}
.toc h4{margin:0 0 8px;font-size:13px;letter-spacing:.08em;color:var(--muted);text-transform:uppercase}
.toc ul{list-style:none;padding:0;margin:0;columns:2;column-gap:28px}
.toc li{margin:4px 0;font-size:14.5px}
@media(max-width:640px){.toc ul{columns:1}.wrap{padding:28px 16px 64px}h1{font-size:24px}}
@media print{header.site,footer{display:none}.wrap{max-width:none;padding:0}}
"""

def page(title, body, home=True):
    nav = '<header class="site"><a href="index.html">杭州元像万生科技有限公司 · 投资尽调报告</a></header>' if not home else ''
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{CSS}</style></head>
<body><div class="wrap">{nav}{body}
<footer><p>本材料为投资研究用途，不构成审计报告、法律意见或投资建议。文中金额均为概数。</p></footer>
</div></body></html>"""

def md2html(text):
    return markdown.markdown(text, extensions=["tables","fenced_code","sane_lists","attr_list"])

root = pathlib.Path(__file__).parent
rep = (root/"report.md").read_text(encoding="utf-8")
html = md2html(rep)
# 目录（抽取 h2 生成锚点）
hs = re.findall(r"<h2>(.*?)</h2>", html)
items = []
for h in hs:
    slug = re.sub(r"[^\w\u4e00-\u9fa5]+","-",h).strip("-").lower()
    html = html.replace(f"<h2>{h}</h2>", f'<h2 id="{slug}">{h}</h2>', 1)
    items.append(f'<li><a href="#{slug}">{h}</a></li>')
toc = '<div class="toc"><h4>目录</h4><ul>' + "".join(items) + "</ul></div>"
html = html.replace("</h1>", "</h1>" + toc, 1)
(root/"report.html").write_text(page("杭州元像万生科技有限公司 投资尽调报告", html), encoding="utf-8")

idx = (root/"index.md").read_text(encoding="utf-8")
idx = re.sub(r"^---.*?---\s*","",idx,flags=re.S)
body = md2html(idx).replace("<h2>","<h2>") 
(root/"index.html").write_text(page("杭州元像万生科技有限公司 投资尽调报告", body, home=True), encoding="utf-8")
print("ok", (root/"report.html").stat().st_size, (root/"index.html").stat().st_size)
