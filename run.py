#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频背景移除工具 - 一键运行脚本
自动处理虚拟环境和依赖安装
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, 
                              capture_output=True, text=True, encoding='utf-8')
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🎬 视频背景移除工具 - 一键启动")
    print("==========================================")
    
    # 获取脚本目录
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        input("按回车键退出...")
        return
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查虚拟环境
    venv_path = script_dir / "venv"
    if not venv_path.exists():
        print("🔄 创建虚拟环境...")
        success, stdout, stderr = run_command(f"{sys.executable} -m venv venv")
        if not success:
            print(f"❌ 创建虚拟环境失败: {stderr}")
            input("按回车键退出...")
            return
        print("✅ 虚拟环境创建成功")
    
    # 确定虚拟环境中的Python路径
    if platform.system() == "Windows":
        venv_python = venv_path / "Scripts" / "python.exe"
        venv_pip = venv_path / "Scripts" / "pip.exe"
    else:
        venv_python = venv_path / "bin" / "python"
        venv_pip = venv_path / "bin" / "pip"
    
    # 检查依赖包
    print("🔍 检查依赖包...")
    check_cmd = f'"{venv_python}" -c "import cv2, numpy, PIL, rembg, torch, torchvision, onnxruntime, tqdm, click, colorlog"'
    success, _, _ = run_command(check_cmd)
    
    if not success:
        print("📦 安装依赖包...")
        
        # 升级pip
        print("  - 升级pip...")
        success, _, stderr = run_command(f'"{venv_python}" -m pip install --upgrade pip')
        if not success:
            print(f"⚠️  pip升级失败: {stderr}")
        
        # 安装依赖
        print("  - 安装依赖包...")
        success, stdout, stderr = run_command(f'"{venv_pip}" install -r requirements.txt')
        if not success:
            print(f"❌ 依赖包安装失败: {stderr}")
            print("\n💡 请尝试手动安装:")
            print(f"   {venv_pip} install -r requirements.txt")
            input("按回车键退出...")
            return
        print("✅ 依赖包安装成功")
    else:
        print("✅ 所有依赖包已安装")
    
    # 检查tkinter
    print("🔍 检查tkinter支持...")
    tkinter_cmd = f'"{venv_python}" -c "import tkinter; print(\'tkinter可用\')"'
    tkinter_success, _, tkinter_error = run_command(tkinter_cmd)
    
    if not tkinter_success:
        print("⚠️  tkinter未安装或不可用")
        print("\n💡 解决方案:")
        print("1. 安装tcl-tk: brew install tcl-tk")
        print("2. 重新安装Python (如果使用pyenv):")
        print("   env LDFLAGS=\"-L$(brew --prefix tcl-tk)/lib\" \\")
        print("       CPPFLAGS=\"-I$(brew --prefix tcl-tk)/include\" \\")
        print("       PKG_CONFIG_PATH=\"$(brew --prefix tcl-tk)/lib/pkgconfig\" \\")
        print("       pyenv install 3.13.5")
        print("3. 或使用命令行版本 (选择菜单选项2)")
        print("")
    else:
        print("✅ tkinter可用")
    
    # 启动工具
    print("\n🚀 启动视频背景移除工具...")
    print("")
    
    try:
        # 直接运行start.py
        subprocess.run([str(venv_python), "start.py"], cwd=script_dir)
    except KeyboardInterrupt:
        print("\n👋 用户中断")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
    
    print("\n程序结束")
    input("按回车键退出...")

if __name__ == "__main__":
    main()