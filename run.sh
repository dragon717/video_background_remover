#!/bin/bash

# 视频背景移除工具 - 一键运行脚本
# 自动激活虚拟环境并启动工具

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🎬 视频背景移除工具 - 一键启动"
echo "=========================================="

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 创建虚拟环境失败"
        exit 1
    fi
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
echo "🔍 检查依赖包..."
python -c "import cv2, numpy, PIL, rembg, torch, torchvision, onnxruntime, tqdm, click, colorlog" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装依赖包..."
    pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖包安装失败"
        exit 1
    fi
    echo "✅ 依赖包安装成功"
else
    echo "✅ 所有依赖包已安装"
fi

# 启动工具
echo "🚀 启动视频背景移除工具..."
echo ""
python start.py

# 保持终端打开（可选）
echo ""
echo "按任意键退出..."
read -n 1