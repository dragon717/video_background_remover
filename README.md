# 视频背景移除工具 🎬✨

一个基于AI深度学习的高质量视频背景移除工具，支持从MP4视频中提取主体并生成透明背景的输出。

## ✨ 主要特性

- 🤖 **多种AI模型支持**: U2-Net、ISNet等先进的背景分割模型
- 🎥 **完整视频处理**: 自动提取视频帧、处理、重新合成
- 🖼️ **帧图片输出**: 同时输出每帧的处理结果
- 📱 **图形界面**: 简单易用的GUI界面
- ⚡ **批量处理**: 支持批量处理多个视频文件
- 🎨 **多格式输出**: 支持MP4和WebM透明视频格式
- 📊 **详细报告**: 生成处理报告和统计信息

## 🚀 快速开始

### 环境要求

- Python 3.8+
- macOS / Windows / Linux
- 至少4GB内存
- 网络连接（首次下载AI模型）

### 安装步骤

1. **克隆或下载项目**
   ```bash
   # 如果你有git
   git clone <repository-url>
   cd 视频扣图
   
   # 或者直接下载解压到本目录
   ```

2. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

3. **验证安装**
   ```bash
   python video_background_remover.py --help
   ```

## 📖 使用方法

### 方法一：图形界面（推荐新手）

启动GUI应用：
```bash
python gui_app.py
```

界面操作步骤：
1. 点击"浏览"选择输入视频文件
2. 设置输出目录
3. 选择AI模型（推荐u2net）
4. 可选：设置最大处理帧数
5. 点击"开始处理"
6. 等待处理完成

### 方法二：命令行界面

#### 基本用法
```bash
python video_background_remover.py -i input.mp4 -o output_folder
```

#### 高级用法
```bash
# 使用人物专用模型，限制处理300帧
python video_background_remover.py \
  -i input.mp4 \
  -o output_folder \
  -m u2net_human_seg \
  -f 300

# 不生成WebM格式
python video_background_remover.py \
  -i input.mp4 \
  -o output_folder \
  --no-webm
```

#### 参数说明
- `-i, --input`: 输入视频文件路径
- `-o, --output`: 输出目录路径
- `-m, --model`: AI模型选择（见下方模型说明）
- `-f, --max-frames`: 最大处理帧数（可选）
- `--no-webm`: 不生成WebM格式
- `-v, --verbose`: 详细输出

### 方法三：批量处理

处理整个文件夹的视频：
```bash
python batch_processor.py -i input_folder -o output_folder
```

生成HTML报告：
```bash
python batch_processor.py \
  -i input_folder \
  -o output_folder \
  --html-report
```

## 🤖 AI模型说明

| 模型名称 | 特点 | 适用场景 | 处理速度 | 质量 |
|---------|------|----------|----------|------|
| `u2net` | 通用模型 | 大多数场景 | 中等 | 高 |
| `u2netp` | 轻量版 | 快速处理 | 快 | 中等 |
| `u2net_human_seg` | 人物专用 | 人物视频 | 中等 | 很高 |
| `isnet-general-use` | 高精度通用 | 要求高质量 | 慢 | 很高 |
| `silueta` | 轮廓检测 | 简单背景 | 快 | 中等 |

**推荐选择**：
- 🎬 **一般视频**: `u2net`
- 👤 **人物视频**: `u2net_human_seg`
- ⚡ **快速处理**: `u2netp`
- 🎨 **高质量要求**: `isnet-general-use`

## 📁 输出文件结构

处理完成后，输出目录包含：

```
output_folder/
├── output_transparent.mp4          # 透明背景MP4视频
├── output_transparent.webm         # 透明背景WebM视频（可选）
├── frames/                         # 原始视频帧
│   ├── frame_000001.png
│   ├── frame_000002.png
│   └── ...
├── processed_frames/               # 处理后的帧（透明背景）
│   ├── processed_frame_000001.png
│   ├── processed_frame_000002.png
│   └── ...
└── batch_processing_report.json    # 处理报告（批量处理时）
```

## 🎯 使用技巧

### 提高处理质量
1. **选择合适的模型**: 人物视频用`u2net_human_seg`，一般场景用`u2net`
2. **视频预处理**: 确保视频清晰度足够，避免过度压缩
3. **背景简单化**: 简单背景的抠图效果更好
4. **光线均匀**: 避免强烈的阴影和反光

### 优化处理速度
1. **限制帧数**: 使用`-f`参数限制处理帧数
2. **选择轻量模型**: 使用`u2netp`模型
3. **降低分辨率**: 预先将视频分辨率调整到合适大小
4. **批量处理**: 一次性处理多个文件更高效

### 内存优化
1. **分批处理**: 大视频文件建议分段处理
2. **关闭其他程序**: 处理时关闭不必要的应用
3. **监控内存**: 使用系统监控工具观察内存使用

## 🔧 故障排除

### 常见问题

**Q: 首次运行很慢？**
A: 首次运行会自动下载AI模型（约100-500MB），请保持网络连接。

**Q: 内存不足错误？**
A: 尝试：
- 限制处理帧数：`-f 100`
- 使用轻量模型：`-m u2netp`
- 关闭其他程序释放内存

**Q: 处理结果不理想？**
A: 尝试：
- 更换AI模型
- 检查原视频质量
- 确保背景与主体对比明显

**Q: WebM文件创建失败？**
A: 需要安装FFmpeg：
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# 下载FFmpeg并添加到PATH
```

**Q: GUI界面无法启动？**
A: 确保安装了tkinter：
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS和Windows通常自带
```

### 错误日志

如果遇到问题，请查看详细日志：
```bash
python video_background_remover.py -i input.mp4 -o output -v
```

## 🎨 高级用法

### 自定义处理流程

```python
from video_background_remover import VideoBackgroundRemover

# 创建处理器
remover = VideoBackgroundRemover(model_name='u2net')

# 自定义处理
result = remover.process_video(
    input_video='input.mp4',
    output_dir='output',
    max_frames=200,
    create_webm=True
)

print(f"处理完成，共{result['frame_count']}帧")
```

### 集成到其他项目

```python
# 只处理单帧
remover = VideoBackgroundRemover()
remover.remove_background_from_frame('input.png', 'output.png')

# 批量处理帧
frames = ['frame1.png', 'frame2.png', 'frame3.png']
processed = remover.process_frames(frames, 'output_dir')
```

## 📊 性能参考

| 视频规格 | 模型 | 处理时间 | 内存使用 |
|---------|------|----------|----------|
| 1080p, 30fps, 10s | u2net | ~5分钟 | ~2GB |
| 720p, 30fps, 10s | u2net | ~3分钟 | ~1.5GB |
| 1080p, 30fps, 10s | u2netp | ~3分钟 | ~1GB |
| 4K, 30fps, 10s | u2net | ~15分钟 | ~4GB |

*测试环境：MacBook Pro M1, 16GB RAM*

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd 视频扣图

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8

# 运行测试
pytest tests/
```

## 📄 许可证

MIT License - 详见LICENSE文件

## 🙏 致谢

- [rembg](https://github.com/danielgatis/rembg) - 优秀的背景移除库
- [U2-Net](https://github.com/xuebinqin/U-2-Net) - 强大的图像分割模型
- OpenCV - 计算机视觉处理库

## 📞 支持

如果这个工具对你有帮助，请给个⭐️！

有问题或建议？欢迎提交Issue或联系开发者。

---

**享受你的视频创作之旅！** 🎬✨