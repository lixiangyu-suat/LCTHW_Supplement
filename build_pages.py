#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build standalone HTML pages from the Obsidian lecture notes."""

import html
import os
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

import mistune
from mistune.plugins.table import render_table

try:
    from pygments import highlight as pygments_highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name

    PYGMENTS_CSS = HtmlFormatter(style="friendly").get_style_defs(".highlight")
except Exception:
    pygments_highlight = None
    PYGMENTS_CSS = ""


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
BUILD = ROOT / "build" / "html"
IMGS_SRC = SOURCE / "imgs"
MAIN_REL = Path("main.md")
HOME_TITLE = "讲义首页"

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root {{
  --text: #1f2937;
  --border: #d8e0e8;
  --accent: #0f766e;
  --accent-weak: #e5f4f2;
  --code-bg: #f7f8fa;
  --code-text: #24292f;
}}
* {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; }}
body {{
  margin: 0;
  background: #f2f4f7;
  color: var(--text);
  font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
  line-height: 1.75;
}}
.page {{
  max-width: 920px;
  margin: 0 auto;
  background: #fff;
  min-height: 100vh;
  padding: 2rem 1.25rem 4rem;
  box-shadow: 0 0 0 1px rgba(17, 24, 39, 0.06);
}}
@media (min-width: 768px) {{
  .page {{ padding: 3rem 3.25rem 5rem; }}
}}
h1, h2, h3, h4, h5, h6 {{ color: #14202b; line-height: 1.35; }}
h1 {{ font-size: 1.75rem; margin: 1.2rem 0 0.8rem; }}
.page-title {{ font-size: 1.9rem; margin: 0 0 0.4rem; }}
.page-home {{ margin: 0 0 1.5rem; }}
.page-home a {{ font-size: 0.95rem; }}
h2 {{
  font-size: 1.35rem;
  margin: 1.6rem 0 0.7rem;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid var(--border);
}}
h3 {{ font-size: 1.15rem; }}
h4 {{ font-size: 1rem; }}
p {{ margin: 0.85rem 0; }}
a {{
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid rgba(15, 118, 110, 0.35);
}}
a:hover {{ color: #0b5d56; border-bottom-color: currentColor; }}
strong {{ color: #17212b; }}
ul, ol {{ padding-left: 1.5rem; margin: 0.8rem 0; }}
ul {{ list-style: disc; }}
ul ul {{ list-style: circle; }}
ul ul ul {{ list-style: square; }}
li::marker {{ color: #0f766e; }}
li {{ margin: 0.3rem 0; }}
li > ul, li > ol {{ margin: 0.2rem 0; }}
code {{ font-family: Consolas, "Courier New", monospace; font-size: 0.9em; }}
:not(pre) > code {{
  background: #eef2f5;
  border: 1px solid #dce3ea;
  border-radius: 4px;
  padding: 0.1em 0.35em;
  color: #274c62;
}}
pre {{
  background: var(--code-bg);
  color: var(--code-text);
  border: 1px solid #dce3ea;
  border-radius: 8px;
  padding: 1rem 1.1rem;
  overflow-x: auto;
  line-height: 1.55;
  font-size: 0.92em;
}}
pre code {{ background: none; border: 0; padding: 0; color: inherit; font-size: inherit; }}
img {{ max-width: 100%; height: auto; }}
.table-wrap {{ overflow-x: auto; margin: 1.1rem 0; }}
.table-wrap table {{ min-width: 520px; }}
table {{ border-collapse: collapse; width: 100%; margin: 0; font-size: 0.95em; }}
th, td {{ border: 1px solid #cfd9e2; padding: 0.5rem 0.65rem; text-align: left; vertical-align: top; }}
th {{ background: #eef3f7; font-weight: 600; }}
tbody tr:nth-child(even) {{ background: #f8fafc; }}
blockquote {{
  margin: 1rem 0;
  padding: 0.35rem 1rem;
  border-left: 4px solid #63a69f;
  background: #f2f9f8;
  color: #33434e;
}}
.callout {{
  margin: 1.2rem 0;
  padding: 0.9rem 1rem;
  border: 1px solid #d3dce4;
  border-left: 4px solid #0f766e;
  border-radius: 6px;
  background: #f2faf9;
}}
.callout-title {{ font-weight: 700; color: #0f766e; margin-bottom: 0.35rem; }}
.callout-body > :first-child {{ margin-top: 0; }}
.callout-body > :last-child {{ margin-bottom: 0; }}
.callout-warning {{ border-left-color: #d97706; background: #fff8eb; }}
.callout-warning .callout-title {{ color: #b45309; }}
.callout-note, .callout-info {{ border-left-color: #3b82f6; background: #eff6ff; }}
.callout-note .callout-title, .callout-info .callout-title {{ color: #1d4ed8; }}
.callout-danger {{ border-left-color: #dc2626; background: #fef2f2; }}
.callout-danger .callout-title {{ color: #b91c1c; }}
hr {{ border: 0; border-top: 1px solid var(--border); margin: 2rem 0; }}
.img-wrap {{ margin: 1.4rem 0; text-align: center; }}
.img-wrap img {{
  max-width: min(100%, 720px);
  height: auto;
  border: 1px solid #d3dce4;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(17, 24, 39, 0.08);
}}
.page-nav {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  align-items: center;
  justify-content: space-between;
  margin-top: 3rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border);
}}
.page-nav a {{
  display: inline-block;
  padding: 0.55rem 0.95rem;
  border: 1px solid #c9d6e0;
  border-radius: 6px;
  background: #f6f9fb;
  color: #1d4e63;
  font-weight: 500;
}}
.page-nav a:hover {{
  background: var(--accent-weak);
  border-color: #7fb4ac;
  color: var(--accent);
}}
.page-nav .nav-home {{ margin: 0 auto; }}
@media (max-width: 560px) {{
  .page-nav {{ justify-content: center; }}
  .page-nav .nav-home {{ order: -1; width: 100%; text-align: center; }}
}}
{pygments_css}
.highlight {{ background: transparent; }}
</style>
</head>
<body>
<main class="page">
{body}
</main>
</body>
</html>
"""


WIKI_IMAGE_RE = re.compile(r"!\[\[([^\]\n]+?)\]\]")
WIKI_LINK_RE = re.compile(r"\[\[([^\]\n]+?)\]\]")


class LectureRenderer(mistune.HTMLRenderer):
    def image(self, text, url, title=None):
        img = super().image(text, url, title)
        return '<div class="img-wrap">' + img + "</div>"

    def block_code(self, code, info=None):
        if pygments_highlight:
            lang = (info or "").split()[0] if info else ""
            if lang:
                try:
                    lexer = get_lexer_by_name(lang, stripall=False)
                    highlighted = pygments_highlight(
                        code, lexer, HtmlFormatter(nowrap=True)
                    )
                    return (
                        '<pre><code class="language-%s">%s</code></pre>'
                        % (lang, highlighted)
                    )
                except Exception:
                    pass
        return super().block_code(code, info)

    def table(self, text):
        return '<div class="table-wrap">' + render_table(self, text) + "</div>"

    def link(self, text, url, title=None):
        safe_url = self.safe_url(url)
        result = '<a href="' + safe_url + '"'
        if title:
            result += ' title="' + mistune.safe_entity(title) + '"'
        if url.startswith(("http://", "https://")):
            result += ' target="_blank" rel="noopener"'
        return result + ">" + text + "</a>"


def discover_pages():
    pages = []
    for path in SOURCE.rglob("*.md"):
        rel = path.relative_to(SOURCE)
        pages.append(rel)
    return pages


def classify_page(rel):
    if rel == MAIN_REL:
        return "main"
    if rel.parts and rel.parts[0] == "E1-Linux C编程一站式学习":
        return "E1"
    if rel.parts and rel.parts[0] == "E4-笨方法学C":
        return "E4"
    if rel.parts and rel.parts[0] == "Else":
        return "else"
    return "standalone"


def make_page_map(pages):
    page_map = {}
    for rel in pages:
        page_map[rel.stem] = rel
        page_map[rel.with_suffix("").as_posix()] = rel
    return page_map


def page_title(rel):
    if rel == MAIN_REL:
        return HOME_TITLE
    return rel.stem


def read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def update_source_footer(rel, footer):
    if rel == MAIN_REL:
        return
    path = SOURCE / rel
    text = read_text(path)
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = [line.rstrip("\r") for line in text.rstrip("\r\n").split("\n")]
    if lines and "[[main|返回]]" in lines[-1] and lines[-1].strip().startswith("[["):
        lines.pop()
        while lines and lines[-1].strip() == "":
            lines.pop()
    body = newline.join(lines)
    if body:
        body += newline
    updated = body + newline + footer + newline
    if updated != text:
        path.write_bytes(updated.encode("utf-8"))


def strip_appended_footer(text):
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = [line.rstrip("\r") for line in text.rstrip("\r\n").split("\n")]
    if lines and "[[main|返回]]" in lines[-1] and lines[-1].strip().startswith("[["):
        lines.pop()
        while lines and lines[-1].strip() == "":
            lines.pop()
        return newline.join(lines)
    return text


def footer_for(prev, next_):
    parts = []
    if prev:
        parts.append("[[%s|上一节]]" % prev.stem)
    parts.append("[[main|返回]]")
    if next_:
        parts.append("[[%s|下一节]]" % next_.stem)
    return " · ".join(parts)


def relative_href(from_md_rel, to_md_rel):
    from_out = (BUILD / from_md_rel).with_suffix(".html")
    to_out = (BUILD / to_md_rel).with_suffix(".html")
    rel = os.path.relpath(to_out, from_out.parent)
    return urllib.parse.quote(rel.replace("\\", "/"))


def asset_href(from_md_rel, asset_rel):
    from_out = (BUILD / from_md_rel).with_suffix(".html")
    to_out = BUILD / asset_rel
    rel = os.path.relpath(to_out, from_out.parent)
    return urllib.parse.quote(rel.replace("\\", "/"))


def resolve_image(target, current_rel):
    name = Path(target.replace("\\", "/")).name
    candidates = []
    if IMGS_SRC.exists():
        candidates = [p for p in IMGS_SRC.rglob(name) if p.is_file()]
    if not candidates:
        clean = target.replace("\\", "/")
        if clean.startswith("imgs/"):
            direct = IMGS_SRC / clean[len("imgs/"):]
            if direct.is_file():
                candidates = [direct]
    if not candidates:
        return None
    chosen = candidates[0]
    img_rel = chosen.relative_to(IMGS_SRC)
    asset_rel = (Path("imgs") / img_rel).as_posix()
    return asset_href(current_rel, asset_rel)


def preprocess_wikis(text, current_rel, page_map):
    def replace_image(match):
        inner = match.group(1)
        target, _, opts = inner.partition("|")
        target = target.strip()
        opts = opts.strip()
        alt = Path(target.replace("\\", "/")).stem
        if opts and not opts.isdigit():
            alt = opts
        url = resolve_image(target, current_rel)
        if url:
            return "![%s](%s)" % (alt, url)
        return "![%s](#missing-image)" % alt

    text = WIKI_IMAGE_RE.sub(replace_image, text)

    def replace_link(match):
        inner = match.group(1)
        target, _, display = inner.partition("|")
        target = target.strip().replace("\\", "/")
        target_no_frag = target.split("#", 1)[0].strip()
        if target_no_frag.lower().endswith(".md"):
            target_no_frag = target_no_frag[:-3]
        target_norm = target_no_frag.strip("/")
        rel = page_map.get(target_norm) or page_map.get(Path(target_norm).name)
        display = display.strip() or Path(target_norm).name
        if rel:
            return "[%s](%s)" % (display, relative_href(current_rel, rel))
        return display

    text = WIKI_LINK_RE.sub(replace_link, text)
    return text


CALLOUT_RE = re.compile(
    r"<blockquote>\s*<p>\[!([A-Za-z]+)\](.*?)</blockquote>",
    re.DOTALL,
)


def convert_callouts(html):
    def replace(match):
        kind = match.group(1).lower()
        rest = match.group(2)
        closing_p = rest.find("</p>")
        if closing_p == -1:
            first_content = rest
            after = ""
        else:
            first_content = rest[:closing_p]
            after = rest[closing_p + 4 :]
        first_lines = first_content.splitlines()
        first_line_text = first_lines[0].strip() if first_lines else ""
        if first_line_text:
            title = first_line_text
            remaining_first = "\n".join(first_lines[1:]).strip()
        else:
            title = match.group(1).upper()
            remaining_first = "\n".join(first_lines[1:]).strip()
        body_parts = []
        if remaining_first:
            body_parts.append(remaining_first)
        if after.strip():
            body_parts.append(after.strip())
        body = "\n".join(body_parts)
        return (
            '<div class="callout callout-%s">\n'
            '<div class="callout-title">%s</div>\n'
            '<div class="callout-body">%s</div>\n'
            "</div>" % (kind, title, body)
        )

    return CALLOUT_RE.sub(replace, html)


def nav_html(current_rel, prev, next_):
    links = []
    if prev:
        title = html.escape(prev.stem, quote=True)
        href = relative_href(current_rel, prev)
        links.append(
            '<a class="nav-prev" href="%s" title="%s">&larr; 上一节</a>'
            % (href, title)
        )
    if next_:
        title = html.escape(next_.stem, quote=True)
        href = relative_href(current_rel, next_)
        links.append(
            '<a class="nav-next" href="%s" title="%s">下一节 &rarr;</a>'
            % (href, title)
        )
    home_href = relative_href(current_rel, MAIN_REL)
    links.insert(1, '<a class="nav-home" href="%s">返回</a>' % home_href)
    return '<nav class="page-nav">' + "".join(links) + "</nav>"


def write_page(rel, body_html):
    title = html.escape(page_title(rel), quote=True)
    header = [
        '<header class="page-header">',
        '<h1 class="page-title">%s</h1>' % title,
    ]
    if rel != MAIN_REL:
        home_href = relative_href(rel, MAIN_REL)
        header.append('<p class="page-home"><a href="%s">返回</a></p>' % home_href)
    header.append("</header>")
    body_html = "\n".join(header) + "\n\n" + body_html
    out = BUILD / rel.with_suffix(".html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        TEMPLATE.format(title=title, body=body_html, pygments_css=PYGMENTS_CSS),
        encoding="utf-8",
        newline="\n",
    )


def main(targets=None):
    if BUILD.exists():
        if not BUILD.resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError("build directory is outside the workspace")
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)

    if IMGS_SRC.exists():
        shutil.copytree(IMGS_SRC, BUILD / "imgs")

    all_pages = discover_pages()
    if targets:
        pages = []
        for raw in targets:
            rel = Path(raw)
            if rel not in all_pages:
                raise SystemExit("unknown page: %s" % raw)
            pages.append(rel)
        full_build = False
    else:
        pages = all_pages
        full_build = True
    page_map = make_page_map(all_pages)

    e1 = sorted(
        [p for p in all_pages if classify_page(p) == "E1"], key=lambda p: p.name
    )
    e4 = sorted(
        [p for p in all_pages if classify_page(p) == "E4"], key=lambda p: p.name
    )

    renderer = LectureRenderer(escape=False)
    markdown = mistune.create_markdown(
        renderer=renderer,
        plugins=["table", "strikethrough", "task_lists", "url"],
    )

    for rel in pages:
        category = classify_page(rel)
        prev = next_ = None
        nav = ""
        footer = None

        if category == "E1":
            index = e1.index(rel)
            prev = e1[index - 1] if index > 0 else None
            next_ = e1[index + 1] if index < len(e1) - 1 else None
        elif category == "E4":
            index = e4.index(rel)
            prev = e4[index - 1] if index > 0 else None
            next_ = e4[index + 1] if index < len(e4) - 1 else None
        elif category != "main":
            footer = "[[main|返回]]"

        if footer is None and category != "main":
            footer = footer_for(prev, next_)

        if full_build and rel != MAIN_REL:
            update_source_footer(rel, footer)

        text = read_text(SOURCE / rel)
        if full_build and rel != MAIN_REL:
            text = strip_appended_footer(text)
        text = preprocess_wikis(text, rel, page_map)
        body_html = convert_callouts(markdown(text))
        if full_build and rel != MAIN_REL:
            nav = nav_html(rel, prev, next_)
        write_page(rel, body_html + nav)

    if full_build or MAIN_REL in pages:
        shutil.copyfile(BUILD / "main.html", BUILD / "index.html")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
