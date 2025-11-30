#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成 GitHub 文件索引
使用方法：
1. 把这个脚本放在你的 meta 文件夹根目录
2. 运行: python generate_index.py
3. 会自动生成 README.md 文件，包含所有文件的 raw 链接
"""

import os
from pathlib import Path
import urllib.parse

# 配置你的 GitHub 信息
GITHUB_USER = "wandering1900"
REPO_NAME = "meta"
BRANCH = "main"

# 要忽略的文件/文件夹
IGNORE_LIST = ['.git', '.gitignore', 'README.md', 'generate_index.py', '__pycache__', '.DS_Store']

# 文件分类（根据扩展名）
FILE_CATEGORIES = {
    '数据文件': ['.dat', '.csv', '.xlsx', '.xls', '.sav', '.dta'],
    '文档文件': ['.pdf', '.doc', '.docx', '.txt', '.md'],
    '代码文件': ['.py', '.r', '.R', '.sps', '.do'],
    '压缩文件': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    '其他文件': []  # 默认分类
}

def get_category(file_ext):
    """根据文件扩展名获取分类"""
    file_ext = file_ext.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if file_ext in extensions:
            return category
    return '其他文件'

def generate_raw_url(file_path):
    """生成 GitHub raw 链接"""
    # 将路径转换为相对路径
    rel_path = file_path.replace('\\', '/')
    # URL 编码
    encoded_path = urllib.parse.quote(rel_path)
    # 生成 raw 链接
    return f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{encoded_path}"

def scan_directory(base_path='.'):
    """扫描目录并生成文件结构"""
    file_structure = {}
    
    for root, dirs, files in os.walk(base_path):
        # 移除忽略的文件夹
        dirs[:] = [d for d in dirs if d not in IGNORE_LIST]
        
        # 获取相对路径
        rel_root = os.path.relpath(root, base_path)
        if rel_root == '.':
            rel_root = '根目录'
        
        # 收集文件
        file_list = []
        for file in sorted(files):
            if file not in IGNORE_LIST:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, base_path)
                
                # 获取文件信息
                file_ext = os.path.splitext(file)[1]
                file_size = os.path.getsize(file_path)
                
                file_list.append({
                    'name': file,
                    'path': rel_file_path,
                    'ext': file_ext,
                    'size': file_size,
                    'category': get_category(file_ext)
                })
        
        if file_list:
            file_structure[rel_root] = file_list
    
    return file_structure

def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def generate_markdown(file_structure):
    """生成 Markdown 格式的索引"""
    md_content = []
    
    # 标题
    md_content.append("# 📚 学习资料索引\n")
    md_content.append(f"> 自动生成于 GitHub 仓库: `{GITHUB_USER}/{REPO_NAME}`\n")
    md_content.append("---\n")
    
    # 统计信息
    total_files = sum(len(files) for files in file_structure.values())
    total_dirs = len(file_structure)
    md_content.append("## 📊 统计信息\n")
    md_content.append(f"- 总文件数: **{total_files}** 个\n")
    md_content.append(f"- 总文件夹数: **{total_dirs}** 个\n")
    md_content.append("\n---\n")
    
    # 目录
    md_content.append("## 📑 目录\n")
    for i, folder_name in enumerate(sorted(file_structure.keys()), 1):
        anchor = folder_name.replace(' ', '-').replace('/', '-')
        md_content.append(f"{i}. [{folder_name}](#{anchor})\n")
    md_content.append("\n---\n")
    
    # 按文件夹列出文件
    for folder_name in sorted(file_structure.keys()):
        files = file_structure[folder_name]
        
        md_content.append(f"\n## 📁 {folder_name}\n")
        md_content.append(f"*共 {len(files)} 个文件*\n\n")
        
        # 按类别分组
        categorized = {}
        for file_info in files:
            category = file_info['category']
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(file_info)
        
        # 输出每个类别
        for category in sorted(categorized.keys()):
            if categorized[category]:
                md_content.append(f"### {category}\n\n")
                md_content.append("| 文件名 | 大小 | 链接 |\n")
                md_content.append("|--------|------|------|\n")
                
                for file_info in sorted(categorized[category], key=lambda x: x['name']):
                    name = file_info['name']
                    size = format_size(file_info['size'])
                    raw_url = generate_raw_url(file_info['path'])
                    
                    md_content.append(f"| {name} | {size} | [查看/下载]({raw_url}) |\n")
                
                md_content.append("\n")
        
        md_content.append("---\n")
    
    # 使用说明
    md_content.append("\n## 💡 使用说明\n\n")
    md_content.append("### 如何使用这些链接\n\n")
    md_content.append("1. **直接查看**: 点击「查看/下载」链接可以直接查看文件内容\n")
    md_content.append("2. **提供给 AI**: 复制链接提供给 Claude 等 AI 助手，它们可以直接读取分析\n")
    md_content.append("3. **下载文件**: 在浏览器中打开链接后，右键保存即可下载\n\n")
    
    md_content.append("### 重新生成索引\n\n")
    md_content.append("如果你添加了新文件，只需要重新运行 `generate_index.py` 即可更新此索引。\n\n")
    
    return ''.join(md_content)

def main():
    print("🔍 开始扫描文件...")
    file_structure = scan_directory()
    
    print("📝 生成索引文件...")
    markdown_content = generate_markdown(file_structure)
    
    # 保存到 README.md
    output_file = 'README.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✅ 索引已生成: {output_file}")
    print(f"📊 总共处理了 {sum(len(files) for files in file_structure.values())} 个文件")
    print("\n下一步:")
    print("1. 查看生成的 README.md 文件")
    print("2. 提交到 GitHub:")
    print("   git add README.md")
    print("   git commit -m 'Update file index'")
    print("   git push")
    print("\n3. 然后把这个链接给 AI:")
    print(f"   https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/README.md")

if __name__ == "__main__":
    main()
