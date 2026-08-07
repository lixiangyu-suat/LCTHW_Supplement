import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path

# 定义源文件夹和目标文件夹
SOURCE_DIR = Path("source")
BUILD_DIR = Path("build/document")

AUTHOR = "SnowWolf"

def build_docs():
    # 1. 初始化：清空并重建 build/document 目录，确保每次打包都是干净的
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # 2. 遍历 source 目录下的所有 md 文件
    for md_path in SOURCE_DIR.rglob("*.md"):
        
        # 排除掉不需要单独成页的文件和管理文件夹
        if md_path.name in ["main.md", "目录_else.md", "example.md"] or "admin" in md_path.parts:
            continue

        # 获取时间
        now = datetime.now()
        formatted_time = f"{now.year}.{now.month}.{now.day}"

        # 提取分类（例如 "E1-Linux C编程一站式学习"）和文件名（例如 "3-3_函数——参数的传递"）
        category_name = md_path.parent.name
        file_stem = md_path.stem

        # 3. 创建独立的目标文件夹及其 resource 子文件夹
        target_folder = BUILD_DIR / file_stem
        resource_folder = target_folder / "resource"
        resource_folder.mkdir(parents=True, exist_ok=True)

        # 读取原始 markdown 内容
        content = md_path.read_text(encoding="utf-8")

        # 4. 处理图片：复制图片并替换 Markdown 中的路径
        # 匹配 Obsidian 语法的双链图片: ![[Pasted image...png]]
        def replace_obsidian_img(match):
            img_name = match.group(1)
            copy_image(img_name, resource_folder)
            # 转换为通用 Markdown 图片格式，并指向 resource 文件夹
            return f'![{img_name}](resource/{img_name})'

        # 匹配 HTML 语法的图片: <img src="imgs/xxx.png">
        def replace_html_img(match):
            img_name = match.group(1)
            copy_image(img_name, resource_folder)
            # 替换路径指向 resource
            return f'src="resource/{img_name}"'

        content = re.sub(r'!\[\[([^\]]+)\]\]', replace_obsidian_img, content)
        content = re.sub(r'src="[^"]*?([^"/]+\.(png|webp|gif|jpg))"', replace_html_img, content)

        # 5. 写入统一的 index.md
        (target_folder / "index.md").write_text(content, encoding="utf-8")

        # 6. 自动生成前端框架需要的 meta.json
        meta_data = {
            "title": file_stem,
            "author": AUTHOR,
            "time": formatted_time,
            "description": "",
            "tag": []
            }
        with open(target_folder / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=2)

    print("✅ 全自动打包完成！请前往 build/document/ 查看生成的格式。")

def copy_image(img_name, target_resource_folder):
    """辅助函数：从 source 寻找图片并复制到指定 resource 文件夹"""
    src_img = SOURCE_DIR / "imgs" / img_name
    if src_img.exists():
        shutil.copy(src_img, target_resource_folder / img_name)

if __name__ == "__main__":
    build_docs()