# tkinter 问题解决方案 🔧

## 问题描述
在macOS上使用Python 3.13时，可能会遇到 `ModuleNotFoundError: No module named '_tkinter'` 错误。

## 解决方案

### 方案1: 安装tcl-tk并重新安装Python (推荐)

1. **安装tcl-tk**:
   ```bash
   brew install tcl-tk
   ```

2. **如果使用pyenv管理Python版本**:
   ```bash
   # 卸载当前Python版本
   pyenv uninstall 3.13.5
   
   # 重新安装Python，包含tkinter支持
   env LDFLAGS="-L$(brew --prefix tcl-tk)/lib" \
       CPPFLAGS="-I$(brew --prefix tcl-tk)/include" \
       PKG_CONFIG_PATH="$(brew --prefix tcl-tk)/lib/pkgconfig" \
       pyenv install 3.13.5
   ```

3. **如果使用Homebrew Python**:
   ```bash
   # 重新安装Python
   brew reinstall python@3.13
   ```

### 方案2: 使用命令行版本 (临时解决)

如果暂时无法解决tkinter问题，可以使用命令行版本:

```bash
# 在虚拟环境中运行
source venv/bin/activate
python video_background_remover.py --help

# 处理单个视频
python video_background_remover.py input.mp4 output.mp4

# 批量处理
python batch_processor.py
```

### 方案3: 使用系统Python (不推荐)

如果系统Python有tkinter支持，可以在系统环境中安装依赖:

```bash
# 注意：这会污染系统Python环境
pip3 install --user -r requirements.txt
python3 start.py
```

## 验证安装

运行以下命令验证tkinter是否可用:

```bash
python3 -c "import tkinter; print('tkinter 可用')"
```

## 常见问题

**Q: 为什么会出现这个问题？**
A: Python 3.13在编译时如果缺少tcl-tk开发库，就不会包含tkinter模块。

**Q: 能否只安装tkinter包？**
A: 不能。tkinter是Python标准库的一部分，需要在Python编译时包含。

**Q: 虚拟环境中能解决吗？**
A: 虚拟环境继承基础Python的模块，如果基础Python没有tkinter，虚拟环境也不会有。

## 推荐做法

1. 优先使用**方案1**彻底解决问题
2. 临时使用**方案2**的命令行版本
3. 避免使用方案3，以免污染系统环境