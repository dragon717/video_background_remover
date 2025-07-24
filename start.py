#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频背景移除工具 - 快速启动脚本
自动检查环境、安装依赖并启动应用
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: Python {sys.version}")
        print("请升级Python后重试")
        return False
    
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    return True

def check_and_install_requirements():
    """检查并安装依赖包"""
    print("\n🔍 检查依赖包...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ 未找到requirements.txt文件")
        return False
    
    # 读取依赖列表
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    missing_packages = []
    
    # 检查每个包
    for requirement in requirements:
        package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0]
        
        # 特殊处理一些包名
        import_name = package_name
        if package_name == 'opencv-python':
            import_name = 'cv2'
        elif package_name == 'Pillow':
            import_name = 'PIL'
        elif package_name == 'colorlog':
            import_name = 'colorlog'
        
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name} 已安装")
        except ImportError:
            print(f"❌ {package_name} 未安装")
            missing_packages.append(requirement)
    
    # 安装缺失的包
    if missing_packages:
        print(f"\n📦 需要安装 {len(missing_packages)} 个依赖包...")
        
        try:
            # 升级pip
            print("🔄 升级pip...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
            
            # 安装依赖
            print("📦 安装依赖包...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            
            print("✅ 所有依赖包安装完成")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖包安装失败: {e}")
            print("\n💡 尝试手动安装:")
            print(f"pip install -r {requirements_file}")
            return False
    else:
        print("✅ 所有依赖包已安装")
    
    return True

def check_ffmpeg():
    """检查FFmpeg是否安装（用于WebM格式支持）"""
    print("\n🎬 检查FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg 已安装")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  FFmpeg 未安装")
    print("💡 FFmpeg用于创建WebM格式视频（可选）")
    print("安装方法:")
    print("  macOS: brew install ffmpeg")
    print("  Ubuntu: sudo apt install ffmpeg")
    print("  Windows: 下载FFmpeg并添加到PATH")
    
    return False

def show_startup_menu():
    """显示启动菜单"""
    print("\n" + "="*60)
    print("🎬 视频背景移除工具 - 启动菜单")
    print("="*60)
    print("1. 🖥️  启动图形界面 (推荐)")
    print("2. 💻 命令行帮助")
    print("3. 📚 运行使用示例")
    print("4. 🔧 环境检查")
    print("5. 📖 查看说明文档")
    print("0. ❌ 退出")
    print("="*60)
    
    while True:
        try:
            choice = input("\n请选择操作 (0-5): ").strip()
            
            if choice == '1':
                start_gui()
                break
            elif choice == '2':
                show_cli_help()
            elif choice == '3':
                run_examples()
            elif choice == '4':
                run_environment_check()
            elif choice == '5':
                show_documentation()
            elif choice == '0':
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入0-5")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except EOFError:
            break

def start_gui():
    """启动图形界面"""
    print("\n🚀 启动图形界面...")
    
    try:
        # 检查GUI依赖
        import tkinter
        print("✅ GUI依赖检查通过")
        
        # 启动GUI应用
        gui_script = Path(__file__).parent / "gui_app.py"
        if gui_script.exists():
            subprocess.run([sys.executable, str(gui_script)])
        else:
            print("❌ GUI应用文件不存在: gui_app.py")
            
    except ImportError:
        print("❌ tkinter未安装")
        print("安装方法:")
        print("  Ubuntu: sudo apt-get install python3-tk")
        print("  macOS/Windows: 通常自带tkinter")
    except Exception as e:
        print(f"❌ 启动GUI失败: {e}")

def show_cli_help():
    """显示命令行帮助"""
    print("\n📖 命令行使用方法:")
    print("-" * 40)
    
    help_text = """
基本用法:
  python video_background_remover.py -i input.mp4 -o output_folder

参数说明:
  -i, --input     输入视频文件路径
  -o, --output    输出目录路径
  -m, --model     AI模型 (u2net, u2netp, u2net_human_seg, isnet-general-use, silueta)
  -f, --max-frames 最大处理帧数
  --no-webm       不创建WebM格式
  -v, --verbose   详细输出

示例:
  # 基本使用
  python video_background_remover.py -i video.mp4 -o output
  
  # 使用人物专用模型，限制100帧
  python video_background_remover.py -i video.mp4 -o output -m u2net_human_seg -f 100
  
  # 批量处理
  python batch_processor.py -i input_folder -o output_folder
"""
    
    print(help_text)

def run_examples():
    """运行使用示例"""
    print("\n🎯 运行使用示例...")
    
    example_script = Path(__file__).parent / "example_usage.py"
    if example_script.exists():
        try:
            subprocess.run([sys.executable, str(example_script)])
        except Exception as e:
            print(f"❌ 运行示例失败: {e}")
    else:
        print("❌ 示例文件不存在: example_usage.py")

def run_environment_check():
    """运行环境检查"""
    print("\n🔧 环境检查")
    print("=" * 30)
    
    # Python版本
    check_python_version()
    
    # 依赖包
    check_and_install_requirements()
    
    # FFmpeg
    check_ffmpeg()
    
    # 磁盘空间
    print("\n💾 检查磁盘空间...")
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (1024**3)
        print(f"✅ 可用磁盘空间: {free_gb} GB")
        
        if free_gb < 2:
            print("⚠️  磁盘空间不足，建议至少保留2GB空间")
    except Exception as e:
        print(f"❌ 无法检查磁盘空间: {e}")
    
    # 内存
    print("\n🧠 检查内存...")
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_gb = memory.total // (1024**3)
        available_gb = memory.available // (1024**3)
        print(f"✅ 总内存: {memory_gb} GB")
        print(f"✅ 可用内存: {available_gb} GB")
        
        if available_gb < 2:
            print("⚠️  可用内存较少，建议关闭其他程序")
    except ImportError:
        print("💡 安装psutil可查看详细内存信息: pip install psutil")
    except Exception as e:
        print(f"❌ 无法检查内存: {e}")
    
    print("\n✅ 环境检查完成")

def show_documentation():
    """显示文档"""
    print("\n📚 查看文档")
    print("=" * 20)
    
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        print(f"📖 README文档: {readme_file}")
        
        # 尝试在默认程序中打开
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(readme_file)])
            elif sys.platform == "win32":  # Windows
                os.startfile(str(readme_file))
            else:  # Linux
                subprocess.run(["xdg-open", str(readme_file)])
            print("✅ 已在默认程序中打开README")
        except Exception:
            print("💡 请手动打开README.md文件查看详细文档")
    else:
        print("❌ README.md文件不存在")
    
    print("\n📁 项目文件:")
    files = [
        ("video_background_remover.py", "主处理脚本"),
        ("gui_app.py", "图形界面应用"),
        ("batch_processor.py", "批量处理工具"),
        ("example_usage.py", "使用示例"),
        ("requirements.txt", "依赖包列表")
    ]
    
    for filename, description in files:
        filepath = Path(__file__).parent / filename
        status = "✅" if filepath.exists() else "❌"
        print(f"  {status} {filename} - {description}")

def main():
    """主函数"""
    print("🎬 视频背景移除工具 - 快速启动")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 检查并安装依赖
    if not check_and_install_requirements():
        print("\n❌ 依赖检查失败，请手动安装依赖后重试")
        return 1
    
    # 检查FFmpeg（可选）
    check_ffmpeg()
    
    # 显示启动菜单
    show_startup_menu()
    
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n👋 用户中断，再见！")
        exit(0)
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        exit(1)