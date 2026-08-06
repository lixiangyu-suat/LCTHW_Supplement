#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Incremental export of Obsidian notes to the SUAT_YSYX_Document format."""

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
BUILD = ROOT / "build"
BUILD_DOC = BUILD / "document"
TARGET_DOC = ROOT / "Target" / "SUAT_YSYX_Document-main" / "document"
STATE_FILE = BUILD / "target_state.json"

CONVERT_VERSION = "1"
AUTHOR = "待补充"
TIME = "2026.8.6"

WIKI_IMAGE_RE = re.compile(r"!\[\[([^\]\n]+?)\]\]")
WIKI_LINK_RE = re.compile(r"\[\[([^\]\n]+?)\]\]")
MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
MARK_RE = re.compile(r"==([^=\n]+?)==")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(path.read_bytes())


def sanitize_slug(stem):
    slug = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", stem).strip().strip(".")
    return slug or "untitled"


def read_text(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def strip_appended_footer(text):
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = [line.rstrip("\r") for line in text.rstrip("\r\n").split("\n")]
    if lines and "[[main|返回]]" in lines[-1] and lines[-1].strip().startswith("[["):
        lines.pop()
        while lines and lines[-1].strip() == "":
            lines.pop()
        return newline.join(lines)
    return text


def find_image(name):
    candidates = []
    imgs_dir = SOURCE / "imgs"
    if imgs_dir.exists():
        candidates.extend(imgs_dir.rglob(name))
    candidates.extend(SOURCE.rglob(name))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def ensure_asset(src_file, resource_dir, assets):
    resource_dir.mkdir(parents=True, exist_ok=True)
    name = src_file.name
    dest = resource_dir / name
    digest = sha256_file(src_file)
    if not dest.exists() or sha256_file(dest) != digest:
        shutil.copy2(src_file, dest)
    assets[name] = digest
    return name


def discover_docs():
    docs = []
    for path in sorted(SOURCE.rglob("*.md")):
        rel = path.relative_to(SOURCE)
        docs.append(rel)
    return docs


def build_meta(rel, slug, title):
    parent = rel.parent
    if rel == Path("main.md"):
        tag = ["LCTHW"]
    elif parent.parts:
        short = parent.parts[0].split("-", 1)[0]
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


def convert_md(text, rel, slug, doc_map, resource_dir, assets):
    def replace_image(match):
        inner = match.group(1)
        target, _, opts = inner.partition("|")
        target = target.strip()
        opts = opts.strip()
        name = Path(target.replace("\\", "/")).name
        src = find_image(name)
        if not src:
            return match.group(0)
        ensure_asset(src, resource_dir, assets)
        alt = Path(name).stem
        if opts and not opts.isdigit():
            alt = opts
        return "![%s](resource/%s)" % (alt, name)

    text = WIKI_IMAGE_RE.sub(replace_image, text)

    def replace_std_image(match):
        alt, href = match.group(1), match.group(2)
        if href.startswith("imgs/") or "/imgs/" in href:
            name = Path(href).name
            src = find_image(name)
            if src:
                ensure_asset(src, resource_dir, assets)
                return "![%s](resource/%s)" % (alt, name)
        return match.group(0)

    text = MD_IMAGE_RE.sub(replace_std_image, text)

    def replace_link(match):
        inner = match.group(1)
        target, _, display = inner.partition("|")
        target = target.strip().replace("\\", "/")
        target_no_frag = target.split("#", 1)[0].strip()
        if target_no_frag.lower().endswith(".md"):
            target_no_frag = target_no_frag[:-3]
        target_doc = doc_map.get(Path(target_no_frag).name)
        display = display.strip() or Path(target_no_frag).name
        if target_doc:
            target_slug = target_doc[0]
            return "[%s](../%s/index.md)" % (display, target_slug)
        return display

    text = WIKI_LINK_RE.sub(replace_link, text)
    text = MARK_RE.sub(r"<mark>\1</mark>", text)
    return text


def fingerprint_for(text, meta, assets):
    payload = "\n".join(
        [
            CONVERT_VERSION,
            text,
            json.dumps(meta, ensure_ascii=False, sort_keys=True),
            "\n".join("%s:%s" % item for item in sorted(assets.items())),
        ]
    )
    return sha256_bytes(payload.encode("utf-8"))


def files_ok(doc_dir, assets):
    if not (doc_dir / "index.md").exists():
        return False
    for name in assets:
        if not (doc_dir / "resource" / name).exists():
            return False
    return True


def remove_tree_safely(path):
    path = path.resolve()
    parent = path.parent.resolve()
    if not path.is_relative_to(parent):
        raise RuntimeError("refusing to remove outside expected directory")
    if path.exists():
        shutil.rmtree(path)


def main():
    force = "--force" in sys.argv
    BUILD_DOC.mkdir(parents=True, exist_ok=True)
    state = {}
    if STATE_FILE.exists():
        state = json.loads(read_text(STATE_FILE))

    docs = discover_docs()
    doc_map = {}
    for rel in docs:
        slug = sanitize_slug(rel.stem)
        if slug in doc_map:
            raise RuntimeError("duplicate slug: %s" % slug)
        doc_map[slug] = (slug, rel)
    stem_map = {Path(rel.stem).name: (slug, rel) for slug, rel in doc_map.values()}

    rebuilt = []
    unchanged = []
    added = []

    for rel in docs:
        slug, _ = doc_map[sanitize_slug(rel.stem)]
        title = rel.stem
        meta = build_meta(rel, slug, title)
        doc_dir = BUILD_DOC / slug
        resource_dir = doc_dir / "resource"
        assets = {}
        text = strip_appended_footer(read_text(SOURCE / rel))
        converted = convert_md(text, rel, slug, stem_map, resource_dir, assets)
        fingerprint = fingerprint_for(converted, meta, assets)

        previous = state.get(slug)
        is_new = previous is None
        changed = force or is_new or previous.get("fingerprint") != fingerprint
        if changed or not files_ok(doc_dir, assets):
            doc_dir.mkdir(parents=True, exist_ok=True)
            write_text(doc_dir / "index.md", converted)
            write_text(doc_dir / "meta.json", json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
            if resource_dir.exists():
                referenced = set(assets)
                for stale in resource_dir.iterdir():
                    if stale.is_file() and stale.name not in referenced:
                        stale.unlink()
            state[slug] = {
                "fingerprint": fingerprint,
                "src": rel.as_posix(),
            }
            if is_new:
                added.append(slug)
            else:
                rebuilt.append(slug)
        else:
            unchanged.append(slug)

    current_slugs = set(doc_map)
    for child in list(BUILD_DOC.iterdir()):
        if child.is_dir() and child.name not in current_slugs:
            remove_tree_safely(child)
    for slug in list(state):
        if slug not in current_slugs:
            state.pop(slug, None)
            remove_tree_safely(TARGET_DOC / slug)

    write_text(STATE_FILE, json.dumps(state, ensure_ascii=False, indent=2) + "\n")

    target_doc_root = TARGET_DOC
    target_doc_root.mkdir(parents=True, exist_ok=True)
    copied = []
    for slug in current_slugs:
        source_dir = BUILD_DOC / slug
        target_dir = target_doc_root / slug
        if not target_dir.exists() or slug in rebuilt or slug in added:
            shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
            src_resource = source_dir / "resource"
            tgt_resource = target_dir / "resource"
            if src_resource.exists():
                src_names = {p.name for p in src_resource.iterdir() if p.is_file()}
                if tgt_resource.exists():
                    for stale in tgt_resource.iterdir():
                        if stale.is_file() and stale.name not in src_names:
                            stale.unlink()
            elif tgt_resource.exists():
                remove_tree_safely(tgt_resource)
            copied.append(slug)

    print("added:", ", ".join(added) if added else "-")
    print("rebuilt:", ", ".join(rebuilt) if rebuilt else "-")
    print("unchanged:", ", ".join(unchanged) if unchanged else "-")
    print("copied to target:", ", ".join(copied) if copied else "-")


if __name__ == "__main__":
    main()
