#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KANIC 网站构建脚本
将仓库内所有 .md 文件转换为与 kanic.cn 风格一致的 HTML 页面
运行方式：python3 build.py
"""

import os
import re
import shutil

# ── 配置 ──────────────────────────────────────────────────────
SITE_URL   = "https://cases.kanic.cn"
LOGO_URL   = "https://form.kanic.cn/logo_reverse.png"
MAIN_URL   = "https://www.kanic.cn"
FORM_URL   = "https://form.kanic.cn"
PHONE      = "132-8923-0494"
PHONE_TEL  = "tel:13289230494"
OUT_DIR    = "dist"

SECTIONS = [
    ("experiment-diagram",    "01-实验框图",       "实验框图",      "EXP"),
    ("lab-tips",              "02-实验技巧",       "实验技巧",      "PART"),
    ("software-optimization", "03-软件优化",       "软件优化",      "SFTW"),
    ("engineering-application","04-工程与商业应用","工程与商业应用","APLY"),
]

# ── 简易 Markdown → HTML 转换 ─────────────────────────────────
def md_to_html(text, img_dir=""):
    """把 Markdown 转成 HTML 片段"""

    # 代码块
    def replace_code_block(m):
        lang = m.group(1) or ""
        code = m.group(2).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        return f'<pre><code class="lang-{lang}">{code}</code></pre>'
    text = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, text, flags=re.DOTALL)

    # 行内代码
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # 图片：统一修正为绝对路径 /slug/images-xxx/filename
    def fix_img(m):
        alt, src = m.group(1), m.group(2)
        if src.startswith("http"):
            return f'<img src="{src}" alt="{alt}" style="max-width:100%;border-radius:4px;margin:12px 0;">'
        # 取文件名部分
        filename = src.split("/")[-1].split("\\")[-1]
        if img_dir:
            new_src = f"{img_dir}/{filename}"
        else:
            new_src = filename
        return f'<img src="{new_src}" alt="{alt}" style="max-width:100%;border-radius:4px;margin:12px 0;">'
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', fix_img, text)

    # 链接
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)

    # 标题
    for i in range(6, 0, -1):
        hashes = "#" * i
        text = re.sub(rf'^{hashes}\s+(.+)$', rf'<h{i}>\1</h{i}>', text, flags=re.MULTILINE)

    # 粗体 / 斜体
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*',     r'<em>\1</em>',         text)

    # 水平线
    text = re.sub(r'^---+$', '<hr>', text, flags=re.MULTILINE)

    # 无序列表
    def replace_ul(m):
        items = re.findall(r'^[\*\-]\s+(.+)$', m.group(0), re.MULTILINE)
        lis = "".join(f"<li>{i}</li>" for i in items)
        return f"<ul>{lis}</ul>"
    text = re.sub(r'(^[\*\-]\s+.+$\n?)+', replace_ul, text, flags=re.MULTILINE)

    # 有序列表
    def replace_ol(m):
        items = re.findall(r'^\d+\.\s+(.+)$', m.group(0), re.MULTILINE)
        lis = "".join(f"<li>{i}</li>" for i in items)
        return f"<ol>{lis}</ol>"
    text = re.sub(r'(^\d+\.\s+.+$\n?)+', replace_ol, text, flags=re.MULTILINE)

    # blockquote
    text = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)

    # 段落
    block_tags = ('h1','h2','h3','h4','h5','h6','ul','ol','li',
                  'pre','blockquote','hr','img','table')
    lines, buf, out_lines = text.split('\n'), [], []
    for line in lines:
        stripped = line.strip()
        is_block = any(stripped.startswith(f'<{t}') or stripped.startswith(f'</{t}')
                       for t in block_tags)
        if stripped == '':
            if buf:
                out_lines.append(f'<p>{"".join(buf)}</p>')
                buf = []
            out_lines.append('')
        elif is_block:
            if buf:
                out_lines.append(f'<p>{"".join(buf)}</p>')
                buf = []
            out_lines.append(line)
        else:
            buf.append(stripped + ' ')
    if buf:
        out_lines.append(f'<p>{"".join(buf)}</p>')

    return '\n'.join(out_lines)


# ── HTML 模板 ─────────────────────────────────────────────────
def page_shell(title, breadcrumb_html, content_html, prev_link="", next_link=""):
    pager = ""
    if prev_link or next_link:
        pl = f'<a href="{prev_link[0]}">← {prev_link[1]}</a>' if prev_link else "<span></span>"
        nl = f'<a href="{next_link[0]}">{next_link[1]} →</a>' if next_link else "<span></span>"
        pager = f'<div class="nav-pager">{pl}{nl}</div>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | KANIC.CN</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif;background:#111;color:#111;min-height:100vh;display:flex;flex-direction:column}}
header{{background:#111;padding:0 1.5rem;height:56px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}}
.nav-link{{font-size:13px;color:#aaa;text-decoration:none;transition:color .15s}}
.nav-link:hover{{color:#fff}}
main{{flex:1;background:#e8e8e8;display:flex;justify-content:center;padding:2rem 1.5rem 3rem}}
.content{{width:100%;max-width:700px;background:#fff;border-top:3px solid #c0392b;padding:2rem 2rem 2.5rem}}
.breadcrumb{{font-size:12px;color:#999;margin-bottom:1.5rem;display:flex;align-items:center;gap:6px;flex-wrap:wrap}}
.breadcrumb a{{color:#999;text-decoration:none}}.breadcrumb a:hover{{color:#c0392b}}
.md h1{{font-size:22px;font-weight:500;color:#111;margin:0 0 1rem;padding-bottom:.75rem;border-bottom:1px solid #e5e5e5}}
.md h2{{font-size:17px;font-weight:500;color:#c0392b;margin:1.75rem 0 .75rem;letter-spacing:.04em}}
.md h3{{font-size:15px;font-weight:500;color:#333;margin:1.25rem 0 .5rem}}
.md h4,.md h5,.md h6{{font-size:14px;font-weight:500;color:#444;margin:1rem 0 .4rem}}
.md p{{font-size:14px;color:#444;line-height:1.85;margin-bottom:.85rem}}
.md ul,.md ol{{padding-left:1.4rem;margin-bottom:.85rem}}
.md li{{font-size:14px;color:#444;line-height:1.8;margin-bottom:.3rem}}
.md strong{{color:#111;font-weight:500}}
.md em{{font-style:italic;color:#555}}
.md blockquote{{border-left:3px solid #c0392b;padding:.5rem 1rem;background:#fafafa;margin:.85rem 0;font-size:14px;color:#555;line-height:1.7}}
.md code{{font-size:13px;background:#f5f5f5;border:1px solid #e5e5e5;padding:1px 6px;border-radius:3px;font-family:monospace}}
.md pre{{background:#f5f5f5;border:1px solid #e5e5e5;border-radius:4px;padding:1rem;overflow-x:auto;margin:.85rem 0}}
.md pre code{{background:none;border:none;padding:0;font-size:13px;line-height:1.7}}
.md hr{{border:none;border-top:1px solid #e5e5e5;margin:1.5rem 0}}
.md a{{color:#c0392b;text-decoration:none}}.md a:hover{{text-decoration:underline}}
.md img{{max-width:100%;border-radius:4px;margin:12px 0;display:block}}
.contact-bar{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;padding-top:1.5rem;border-top:1px solid #e5e5e5;margin-top:2rem}}
.contact-bar p{{font-size:13px;color:#666;margin-bottom:3px}}
.contact-bar a.phone{{font-size:15px;font-weight:500;color:#111;text-decoration:none}}
.contact-bar a.phone:hover{{color:#c0392b}}
.btn{{display:inline-block;padding:9px 20px;background:#c0392b;color:#fff;font-size:13px;font-weight:500;text-decoration:none;border-radius:2px;transition:background .15s;white-space:nowrap}}
.btn:hover{{background:#a93226}}
.nav-pager{{display:flex;justify-content:space-between;margin-top:1.5rem;padding-top:1.25rem;border-top:1px solid #e5e5e5;flex-wrap:wrap;gap:10px}}
.nav-pager a{{font-size:13px;color:#888;text-decoration:none;transition:color .15s}}
.nav-pager a:hover{{color:#c0392b}}
footer{{background:#111;color:#666;font-size:12px;text-align:center;padding:1rem 1.5rem;flex-shrink:0}}
footer a{{color:#888;text-decoration:none}}footer a:hover{{color:#fff}}
@media(max-width:480px){{main{{padding:1.5rem .75rem 2.5rem}}.content{{padding:1.5rem 1.25rem 2rem}}.md h1{{font-size:20px}}}}
</style>
</head>
<body>
<header>
  <a href="{MAIN_URL}"><img src="{LOGO_URL}" alt="KANIC.CN" style="height:28px;display:block;"></a>
  <a class="nav-link" href="{SITE_URL}">← 案例库首页</a>
</header>
<main><div class="content">
  <div class="breadcrumb">{breadcrumb_html}</div>
  <div class="md">{content_html}</div>
  {pager}
  <div class="contact-bar">
    <div>
      <p>有实验问题？随时联系我们</p>
      <a class="phone" href="{PHONE_TEL}">{PHONE}</a>
    </div>
    <a class="btn" href="{FORM_URL}">在线询价 →</a>
  </div>
</div></main>
<footer><a href="{MAIN_URL}">KANIC.CN</a> · 自动化控制实验解决方案</footer>
</body></html>"""


# ── 分类首页（文章列表） ──────────────────────────────────────
def section_index(slug, name, articles):
    items_html = ""
    for art_slug, title in articles:
        items_html += f"""
    <a class="article-item" href="{art_slug}.html">
      <span class="article-title">{title}</span>
      <span class="arrow">→</span>
    </a>"""

    content = f"""
<style>
.article-item{{display:flex;justify-content:space-between;align-items:center;
  padding:.9rem 1rem;background:#fff;text-decoration:none;color:#111;
  border-left:3px solid transparent;transition:background .15s,border-color .15s;font-size:14px}}
.article-item:hover{{background:#fafafa;border-left-color:#c0392b}}
.article-title{{flex:1;line-height:1.5}}
.arrow{{color:#ccc;font-size:14px;margin-left:10px;transition:color .15s,transform .15s}}
.article-item:hover .arrow{{color:#c0392b;transform:translateX(3px)}}
.article-list{{display:flex;flex-direction:column;gap:1px;background:#e5e5e5;border:1px solid #e5e5e5;margin-top:1rem}}
.section-desc{{font-size:14px;color:#666;line-height:1.7;padding:.75rem 0 .25rem;border-bottom:1px solid #e5e5e5;margin-bottom:.25rem}}
</style>
<h1>{name}</h1>
<p class="section-desc">共 {len(articles)} 篇文章，点击标题阅读详情。</p>
<div class="article-list">{items_html}
</div>"""

    sec_idx = [s[0] for s in SECTIONS].index(slug)
    prev_link = (f"{SITE_URL}/{SECTIONS[sec_idx-1][0]}/", SECTIONS[sec_idx-1][2]) if sec_idx > 0 else None
    next_link = (f"{SITE_URL}/{SECTIONS[sec_idx+1][0]}/", SECTIONS[sec_idx+1][2]) if sec_idx < len(SECTIONS)-1 else None

    breadcrumb = f'<a href="{SITE_URL}">案例库</a> › <span>{name}</span>'
    return page_shell(name, breadcrumb, content, prev_link, next_link)


# ── 主构建逻辑 ────────────────────────────────────────────────
def build():
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)

    for slug, folder, name, prefix in SECTIONS:
        sec_out = os.path.join(OUT_DIR, slug)
        os.makedirs(sec_out, exist_ok=True)

        # 复制图片文件夹，并记录图片目录名
        img_dirs = [d for d in os.listdir(folder)
                    if os.path.isdir(os.path.join(folder, d)) and d.startswith("images")]
        img_web_path = ""
        for img_dir in img_dirs:
            src = os.path.join(folder, img_dir)
            dst = os.path.join(sec_out, img_dir)
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            img_web_path = img_dir  # 相对于该分类页的图片路径

        # 收集文章
        md_files = sorted([
            f for f in os.listdir(folder)
            if f.endswith(".md") and not f.upper().startswith("README")
        ])

        articles = []
        for md_file in md_files:
            art_slug = md_file[:-3]
            title = art_slug
            m = re.match(r'^\d+[\.\-\s]*[。．]?\s*(.+)', art_slug)
            if m:
                title = m.group(1).strip()
            title = re.sub(r'\s*-(?:EXP|PART|SFTW|APLY)[\w\-]*$', '', title)
            articles.append((art_slug, title))

            md_path = os.path.join(folder, md_file)
            with open(md_path, encoding="utf-8") as f:
                raw = f.read()

            html_body = md_to_html(raw, img_web_path)
            breadcrumb = (
                f'<a href="{SITE_URL}">案例库</a> › '
                f'<a href="{SITE_URL}/{slug}/">{name}</a> › '
                f'<span>{title}</span>'
            )

            art_idx = len(articles) - 1
            prev_art = (f"{articles[art_idx-1][0]}.html", articles[art_idx-1][1]) if art_idx > 0 else None

            out_html = page_shell(title, breadcrumb, html_body, prev_art, None)
            with open(os.path.join(sec_out, f"{art_slug}.html"), "w", encoding="utf-8") as f:
                f.write(out_html)

        # 分类首页
        idx_html = section_index(slug, name, articles)
        with open(os.path.join(sec_out, "index.html"), "w", encoding="utf-8") as f:
            f.write(idx_html)

        print(f"✓ {slug} ({name})：{len(articles)} 篇文章")

    # 主页
    if os.path.exists("index.html"):
        shutil.copy("index.html", os.path.join(OUT_DIR, "index.html"))
        print("✓ 主页 index.html")

    print(f"\n构建完成 → ./{OUT_DIR}/")


if __name__ == "__main__":
    build()
