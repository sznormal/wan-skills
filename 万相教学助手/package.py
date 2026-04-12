"""
打包脚本 - 准备参赛作品提交
"""

import os
import zipfile
import shutil
from datetime import datetime

def create_package():
    """创建参赛作品压缩包"""
    
    package_name = f"万相教学助手_参赛作品_{datetime.now().strftime('%Y%m%d')}"
    
    # 创建临时目录
    temp_dir = f"./{package_name}"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # 需要打包的文件
    files_to_include = [
        "SKILL.md",
        "main.py",
        "wanx_client.py",
        "generate_prompt.py",
        "storyboard_generator.py",
        "config.json",
        "examples.py",
        "requirements.txt",
        "README.md",
        "参赛说明书.md",
        "作品总结.md"
    ]
    
    # 复制文件
    for file in files_to_include:
        if os.path.exists(file):
            shutil.copy2(file, temp_dir)
            print(f"✓ 已添加: {file}")
        else:
            print(f"✗ 找不到: {file}")
    
    # 创建zip包
    zip_path = f"./{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    # 清理临时目录
    shutil.rmtree(temp_dir)
    
    print(f"\n✓ 作品已打包: {zip_path}")
    return zip_path


def verify_package():
    """验证包内容"""
    print("\n验证文件完整性...")
    
    required_files = [
        "SKILL.md",
        "main.py",
        "wanx_client.py",
        "generate_prompt.py",
        "storyboard_generator.py",
        "config.json",
        "examples.py",
        "requirements.txt",
        "README.md",
        "参赛说明书.md"
    ]
    
    all_exist = True
    for file in required_files:
        exists = os.path.exists(file)
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        if not exists:
            all_exist = False
    
    return all_exist


if __name__ == "__main__":
    print("=" * 60)
    print("万相教学助手 - 参赛作品打包工具")
    print("=" * 60)
    
    if verify_package():
        print("\n所有文件完整，准备打包...")
        create_package()
        print("\n打包完成！请提交压缩包参加比赛。")
    else:
        print("\n文件不完整，请检查后再打包。")
