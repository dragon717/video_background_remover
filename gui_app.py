#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频背景移除工具 - GUI界面
提供简单易用的图形界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import sys
from video_background_remover import VideoBackgroundRemover, setup_logger
import logging

class VideoBackgroundRemoverGUI:
    """视频背景移除GUI应用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("视频背景移除工具 v1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 变量
        self.input_video_path = tk.StringVar()
        self.output_dir_path = tk.StringVar()
        self.model_name = tk.StringVar(value='u2net')
        self.max_frames = tk.StringVar()
        self.create_webm = tk.BooleanVar(value=True)
        
        # 处理器
        self.remover = None
        self.processing = False
        
        # 设置日志
        self.setup_logging()
        
        # 创建界面
        self.create_widgets()
        
        # 设置默认输出目录
        self.output_dir_path.set(os.path.join(os.path.expanduser("~"), "Desktop", "video_output"))
    
    def setup_logging(self):
        """设置日志系统"""
        self.logger = setup_logger()
        
        # 创建自定义日志处理器，将日志输出到GUI
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                # 在主线程中更新GUI
                self.text_widget.after(0, lambda: self.append_log(msg))
            
            def append_log(self, msg):
                self.text_widget.insert(tk.END, msg + "\n")
                self.text_widget.see(tk.END)
        
        # 稍后会设置这个处理器
        self.gui_handler = None
    
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="视频背景移除工具", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 输入视频选择
        ttk.Label(main_frame, text="输入视频:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_video_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="浏览", command=self.browse_input_video).grid(row=1, column=2, pady=5)
        
        # 输出目录选择
        ttk.Label(main_frame, text="输出目录:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_dir_path, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="浏览", command=self.browse_output_dir).grid(row=2, column=2, pady=5)
        
        # 模型选择
        ttk.Label(main_frame, text="AI模型:").grid(row=3, column=0, sticky=tk.W, pady=5)
        model_combo = ttk.Combobox(main_frame, textvariable=self.model_name, values=[
            'u2net', 'u2netp', 'u2net_human_seg', 'isnet-general-use', 'silueta'
        ], state='readonly', width=20)
        model_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(5, 5))
        
        # 模型说明
        model_info = ttk.Label(main_frame, text="u2net: 通用模型 | u2net_human_seg: 人物专用 | isnet-general-use: 高精度通用", 
                              font=('Arial', 8), foreground='gray')
        model_info.grid(row=4, column=1, sticky=tk.W, pady=(0, 10), padx=(5, 5))
        
        # 最大帧数限制
        ttk.Label(main_frame, text="最大帧数:").grid(row=5, column=0, sticky=tk.W, pady=5)
        frames_frame = ttk.Frame(main_frame)
        frames_frame.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(5, 5))
        ttk.Entry(frames_frame, textvariable=self.max_frames, width=10).pack(side=tk.LEFT)
        ttk.Label(frames_frame, text="(留空表示处理全部帧)", font=('Arial', 8), foreground='gray').pack(side=tk.LEFT, padx=(5, 0))
        
        # 输出格式选项
        ttk.Label(main_frame, text="输出格式:").grid(row=6, column=0, sticky=tk.W, pady=5)
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=6, column=1, sticky=tk.W, pady=5, padx=(5, 5))
        ttk.Checkbutton(format_frame, text="创建WebM格式 (更好的透明度支持)", variable=self.create_webm).pack(side=tk.LEFT)
        
        # 处理按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        self.process_button = ttk.Button(button_frame, text="开始处理", command=self.start_processing, style='Accent.TButton')
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="停止处理", command=self.stop_processing, state='disabled')
        self.stop_button.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.StringVar(value="准备就绪")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=8, column=0, columnspan=3, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 日志输出区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="5")
        log_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置日志处理器
        self.gui_handler = self.GUILogHandler(self.log_text)
        self.gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(self.gui_handler)
        
        # 配置主框架的行权重
        main_frame.rowconfigure(10, weight=1)
        
        # 添加菜单栏
        self.create_menu()
    
    class GUILogHandler(logging.Handler):
        def __init__(self, text_widget):
            super().__init__()
            self.text_widget = text_widget
        
        def emit(self, record):
            msg = self.format(record)
            # 在主线程中更新GUI
            self.text_widget.after(0, lambda: self.append_log(msg))
        
        def append_log(self, msg):
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.see(tk.END)
            # 限制日志行数
            lines = self.text_widget.get("1.0", tk.END).count("\n")
            if lines > 1000:
                self.text_widget.delete("1.0", "100.0")
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="清空日志", command=self.clear_log)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def browse_input_video(self):
        """浏览输入视频文件"""
        filename = filedialog.askopenfilename(
            title="选择输入视频",
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv"), ("所有文件", "*.*")]
        )
        if filename:
            self.input_video_path.set(filename)
    
    def browse_output_dir(self):
        """浏览输出目录"""
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_dir_path.set(dirname)
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def show_help(self):
        """显示使用说明"""
        help_text = """
视频背景移除工具使用说明：

1. 选择输入视频：点击"浏览"按钮选择要处理的MP4视频文件

2. 设置输出目录：选择处理结果的保存位置

3. 选择AI模型：
   - u2net: 通用模型，适合大多数场景
   - u2netp: 轻量版u2net，处理速度更快
   - u2net_human_seg: 专门针对人物优化
   - isnet-general-use: 高精度通用模型
   - silueta: 轮廓检测模型

4. 设置最大帧数：可以限制处理的帧数以节省时间

5. 输出格式：建议勾选WebM格式以获得更好的透明度支持

6. 点击"开始处理"开始视频抠图

处理完成后，输出目录将包含：
- output_transparent.mp4: 透明背景视频
- output_transparent.webm: WebM格式透明视频
- frames/: 原始视频帧
- processed_frames/: 处理后的帧

注意：首次使用时会自动下载AI模型，请保持网络连接。
        """
        
        messagebox.showinfo("使用说明", help_text)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
视频背景移除工具 v1.0

基于AI深度学习的视频背景移除工具
支持多种AI模型，提供高质量的抠图效果

技术栈：
- Python + OpenCV
- Rembg AI模型
- U2-Net深度学习网络

开发者：AI助手
        """
        
        messagebox.showinfo("关于", about_text)
    
    def validate_inputs(self):
        """验证输入参数"""
        if not self.input_video_path.get():
            messagebox.showerror("错误", "请选择输入视频文件")
            return False
        
        if not os.path.exists(self.input_video_path.get()):
            messagebox.showerror("错误", "输入视频文件不存在")
            return False
        
        if not self.output_dir_path.get():
            messagebox.showerror("错误", "请选择输出目录")
            return False
        
        # 验证最大帧数
        if self.max_frames.get():
            try:
                max_frames = int(self.max_frames.get())
                if max_frames <= 0:
                    messagebox.showerror("错误", "最大帧数必须大于0")
                    return False
            except ValueError:
                messagebox.showerror("错误", "最大帧数必须是有效的整数")
                return False
        
        return True
    
    def start_processing(self):
        """开始处理视频"""
        if not self.validate_inputs():
            return
        
        if self.processing:
            messagebox.showwarning("警告", "正在处理中，请等待完成")
            return
        
        # 启动处理线程
        self.processing = True
        self.process_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar.start()
        self.progress_var.set("正在处理...")
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 在新线程中处理
        self.process_thread = threading.Thread(target=self.process_video_thread)
        self.process_thread.daemon = True
        self.process_thread.start()
    
    def stop_processing(self):
        """停止处理"""
        self.processing = False
        self.progress_var.set("正在停止...")
        # 注意：实际的停止逻辑需要在处理线程中实现
    
    def process_video_thread(self):
        """视频处理线程"""
        try:
            # 获取参数
            input_video = self.input_video_path.get()
            output_dir = self.output_dir_path.get()
            model_name = self.model_name.get()
            max_frames = None
            if self.max_frames.get():
                max_frames = int(self.max_frames.get())
            create_webm = self.create_webm.get()
            
            # 创建处理器
            self.remover = VideoBackgroundRemover(model_name=model_name)
            
            # 处理视频
            result = self.remover.process_video(
                input_video=input_video,
                output_dir=output_dir,
                max_frames=max_frames,
                create_webm=create_webm
            )
            
            # 处理完成
            self.root.after(0, lambda: self.processing_completed(result))
            
        except Exception as e:
            self.root.after(0, lambda: self.processing_failed(str(e)))
    
    def processing_completed(self, result):
        """处理完成回调"""
        self.processing = False
        self.process_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
        self.progress_var.set("处理完成！")
        
        # 显示结果
        message = f"""视频处理完成！

处理信息：
- 处理帧数: {result['frame_count']}
- 视频分辨率: {result['resolution'][0]}x{result['resolution'][1]}
- 帧率: {result['fps']:.2f} fps

输出文件：
- MP4: {result['output_mp4']}
"""
        
        if result['output_webm']:
            message += f"- WebM: {result['output_webm']}\n"
        
        message += f"\n帧文件目录：\n- 原始帧: {result['frames_dir']}\n- 处理后帧: {result['processed_frames_dir']}"
        
        messagebox.showinfo("处理完成", message)
        
        # 询问是否打开输出目录
        if messagebox.askyesno("打开目录", "是否打开输出目录查看结果？"):
            if sys.platform == "win32":
                os.startfile(result['output_dir'])
            elif sys.platform == "darwin":
                os.system(f"open '{result['output_dir']}'")
            else:
                os.system(f"xdg-open '{result['output_dir']}'")
    
    def processing_failed(self, error_msg):
        """处理失败回调"""
        self.processing = False
        self.process_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
        self.progress_var.set("处理失败")
        
        messagebox.showerror("处理失败", f"视频处理失败：\n{error_msg}")

def main():
    """主函数"""
    root = tk.Tk()
    app = VideoBackgroundRemoverGUI(root)
    
    # 设置窗口图标（如果有的话）
    try:
        # root.iconbitmap('icon.ico')  # 可以添加图标文件
        pass
    except:
        pass
    
    # 启动GUI
    root.mainloop()

if __name__ == '__main__':
    main()