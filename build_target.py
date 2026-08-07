import re
import shutil
import json
from datetime import datetime
from pathlib import Path

# 定义源文件夹和目标文件夹
SOURCE_DIR = Path("source")
BUILD_DIR = Path("build/document")
AUTHOR = "SnowWolf"

def copy_image(img_name, target_resource_folder):
    """辅助函数：从 source 寻找图片并复制到指定 resource 文件夹"""
    src_img = SOURCE_DIR / "imgs" / img_name
    if src_img.exists():
        shutil.copy(src_img, target_resource_folder / img_name)

def build_docs():
    # 1. 初始化：清空并重建 build/document 目录
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # 2. 遍历 source 目录下的所有 md 文件
    for md_path in SOURCE_DIR.rglob("*.md"):
        
        # 排除掉不需要单独成页的文件和管理文件夹
        if md_path.name in ["main.md", "目录_else.md", "example.md"] or "admin" in md_path.parts:
            continue

        file_stem = md_path.stem

        # 3. 创建独立的目标文件夹及其 resource 子文件夹
        target_folder = BUILD_DIR / file_stem
        resource_folder = target_folder / "resource"
        resource_folder.mkdir(parents=True, exist_ok=True)

        # 读取原始 markdown 内容
        content = md_path.read_text(encoding="utf-8")

        # 4. 处理图片：复制图片并替换 Markdown 中的路径
        def replace_obsidian_img(match):
            img_name = match.group(1)
            copy_image(img_name, resource_folder)
            
            # 【修复】使用相对路径 `resource/{img_name}` 适配网页渲染
            return f"""<br>
<p align="center">
  <img src="resource/{img_name}" alt="{img_name}" width="100%" />
</p>
<br>"""

        # 替换文档内的图片链接
        content = re.sub(r'!\[\[([^\]]+)\]\]', replace_obsidian_img, content)

        # 5. 写入统一的 index.md
        (target_folder / "index.md").write_text(content, encoding="utf-8")

        # 6. 使用 pathlib 原生方法替换后缀，并检查文件是否存在
        src_json = md_path.with_suffix(".json")
        if src_json.exists():
            # 读取原有 JSON 数据
            with open(src_json, "r", encoding="utf-8") as f:
                meta_data = json.load(f)
            
            # 赋值需要的字段
            meta_data["title"] = file_stem
            meta_data["author"] = AUTHOR
            
            # 组装无前缀0的时间格式
            now = datetime.now()
            meta_data["time"] = f"{now.year}.{now.month}.{now.day}"
            
            # 写入到目标的 meta.json
            with open(target_folder / "meta.json", "w", encoding="utf-8") as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=2)

    print("✅ 全自动打包完成！请前往 build/document/ 查看生成的格式。")


if __name__ == "__main__":
    build_docs()