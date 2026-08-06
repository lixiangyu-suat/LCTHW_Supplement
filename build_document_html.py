#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the online-lecture HTML document group.

Each source note becomes a document folder
    build/document/html/<category>/<slug>/body.html
plus a meta.json, following the reference layout at
build/document/html/E1/3_3. The landing page is rendered to main.html and
index.html, and images are copied under imgs/.
"""

import html
import json
import os
import re
import shutil
import urllib.parse
from pathlib import Path

import mistune

import build_pages as bp


ROOT = Path(__file__).resolve().parent
SOURCE = bp.SOURCE
IMGS_SRC = SOURCE / "imgs"
OUT = ROOT / "build" / "document" / "html"
MAIN_REL = Path("main.md")

AUTHOR = "待补充"
TIME = "2026.8.6"

CATEGORY_DIRS = {"E1": "E1", "E4": "E4", "else": "Else"}


def category_dir(rel):
    kind = bp.classify_page(rel)
    return CATEGORY_DIRS.get(kind, kind)


def doc_slug(rel):
    stem = rel.stem
    kind = bp.classify_page(rel)
    if kind == "E1":
        match = re.match(r"^(\d+)-(\d+)", stem)
        if match:
            return "%s_%s" % (match.group(1), match.group(2))
    if kind == "E4":
        match = re.match(r"^练习(\d+)", stem)
        if match:
            return "练习" + match.group(1)
    return stem


def out_body(rel):
    if rel == MAIN_REL:
        return OUT / "main.html"
    return OUT / category_dir(rel) / doc_slug(rel) / "body.html"


def quoted(relpath):
    return urllib.parse.quote(relpath.replace("\\", "/"))


def page_href(from_rel, to_rel):
    from_body = out_body(from_rel)
    to_body = out_body(to_rel)
    return quoted(os.path.relpath(to_body, from_body.parent))


def find_image(name):
    candidates = []
    if IMGS_SRC.exists():
        candidates.extend(p for p in IMGS_SRC.rglob(name) if p.is_file())
    candidates.extend(p for p in SOURCE.rglob(name) if p.is_file())
    return candidates[0] if candidates else None


def image_href(target, current_rel):
    name = Path(target.replace("\\", "/")).name
    src = find_image(name)
    if not src:
        return None
    if src.is_relative_to(IMGS_SRC):
        img_rel = src.relative_to(IMGS_SRC)
    else:
        img_rel = Path(name)
    dest = OUT / "imgs" / img_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists() or dest.read_bytes() != src.read_bytes():
        shutil.copy2(src, dest)
    return quoted(os.path.relpath(dest, out_body(current_rel).parent))


def preprocess_wikis(text, current_rel, page_map):
    def replace_image(match):
        inner = match.group(1)
        target, _, opts = inner.partition("|")
        target = target.strip()
        opts = opts.strip()
        alt = Path(target.replace("\\", "/")).stem
        if opts and not opts.isdigit():
            alt = opts
        url = image_href(target, current_rel)
        if url:
            return "![%s](%s)" % (alt, url)
        return "![%s](#missing-image)" % alt

    text = bp.WIKI_IMAGE_RE.sub(replace_image, text)

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
            return "[%s](%s)" % (display, page_href(current_rel, rel))
        return display

    text = bp.WIKI_LINK_RE.sub(replace_link, text)
    return text


def nav_html(current_rel, prev, next_):
    links = []
    if prev:
        links.append(
            '<a class="nav-prev" href="%s" title="%s">&larr; 上一节</a>'
            % (page_href(current_rel, prev), html.escape(prev.stem, quote=True))
        )
    links.append(
        '<a class="nav-home" href="%s">返回</a>'
        % page_href(current_rel, MAIN_REL)
    )
    if next_:
        links.append(
            '<a class="nav-next" href="%s" title="%s">下一节 &rarr;</a>'
            % (page_href(current_rel, next_), html.escape(next_.stem, quote=True))
        )
    return '<nav class="page-nav">' + "".join(links) + "</nav>"


def write_page(rel, body_html):
    title = html.escape(bp.page_title(rel), quote=True)
    header = [
        '<header class="page-header">',
        '<h1 class="page-title">%s</h1>' % title,
    ]
    if rel != MAIN_REL:
        header.append(
            '<p class="page-home"><a href="%s">返回</a></p>'
            % page_href(rel, MAIN_REL)
        )
    header.append("</header>")
    body_html = "\n".join(header) + "\n\n" + body_html
    out = out_body(rel)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        bp.TEMPLATE.format(
            title=title, body=body_html, pygments_css=bp.PYGMENTS_CSS
        ),
        encoding="utf-8",
        newline="\n",
    )


def build_meta(rel):
    title = rel.stem
    if rel == MAIN_REL:
        tag = ["LCTHW"]
    elif rel.parent.parts:
        short = rel.parent.parts[0].split("-", 1)[0]
        tag = [short, "LCTHW"]
    else:
        tag = ["LCTHW"]
    return {
        "title": title,
        "author": AUTHOR,
        "time": TIME,
        "description": "LCTHW 补充讲义：" + title,
        "tag": tag,
    }


def write_meta(rel):
    doc_dir = out_body(rel).parent
    doc_dir.mkdir(parents=True, exist_ok=True)
    (doc_dir / "meta.json").write_text(
        json.dumps(build_meta(rel), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def remove_tree_safely(path):
    path = path.resolve()
    if not path.is_relative_to((ROOT / "build").resolve()):
        raise RuntimeError("refusing to remove outside build: %s" % path)
    if path.exists():
        shutil.rmtree(path)


def main():
    remove_tree_safely(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    if IMGS_SRC.exists():
        shutil.copytree(IMGS_SRC, OUT / "imgs")

    all_pages = bp.discover_pages()
    page_map = bp.make_page_map(all_pages)

    e1 = sorted(
        (p for p in all_pages if bp.classify_page(p) == "E1"), key=lambda p: p.name
    )
    e4 = sorted(
        (p for p in all_pages if bp.classify_page(p) == "E4"), key=lambda p: p.name
    )

    renderer = bp.LectureRenderer(escape=False)
    markdown = mistune.create_markdown(
        renderer=renderer,
        plugins=["table", "strikethrough", "task_lists", "url"],
    )

    built = []
    for rel in all_pages:
        category = bp.classify_page(rel)
        prev = next_ = None
        if category == "E1":
            index = e1.index(rel)
            prev = e1[index - 1] if index > 0 else None
            next_ = e1[index + 1] if index < len(e1) - 1 else None
        elif category == "E4":
            index = e4.index(rel)
            prev = e4[index - 1] if index > 0 else None
            next_ = e4[index + 1] if index < len(e4) - 1 else None

        text = bp.strip_appended_footer(bp.read_text(SOURCE / rel))
        text = preprocess_wikis(text, rel, page_map)
        body_html = bp.convert_callouts(markdown(text))
        nav = "" if rel == MAIN_REL else nav_html(rel, prev, next_)
        write_page(rel, body_html + nav)
        if rel != MAIN_REL:
            write_meta(rel)
        built.append(out_body(rel))

    shutil.copyfile(OUT / "main.html", OUT / "index.html")
    print("built %d documents under %s" % (len(built), OUT))


if __name__ == "__main__":
    main()
