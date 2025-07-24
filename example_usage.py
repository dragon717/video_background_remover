#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频背景移除工具 - 使用示例
演示如何使用各种功能
"""

import os
import sys
from pathlib import Path
from video_background_remover import VideoBackgroundRemover
from batch_processor import BatchVideoProcessor

def example_basic_usage():
    """
    示例1: 基本使用方法
    """
    print("=== 示例1: 基本视频背景移除 ===")
    
    # 创建处理器
    remover = VideoBackgroundRemover(model_name='u2net')
    
    # 设置输入输出路径（请根据实际情况修改）
    input_video = "sample_video.mp4"  # 替换为你的视频文件
    output_dir = "output_basic"
    
    # 检查输入文件是否存在
    if not os.path.exists(input_video):
        print(f"⚠️  输入视频文件不存在: {input_video}")
        print("请将你的视频文件重命名为 'sample_video.mp4' 或修改代码中的路径")
        return
    
    try:
        # 处理视频
        result = remover.process_video(
            input_video=input_video,
            output_dir=output_dir,
            max_frames=50,  # 限制处理50帧用于演示
            create_webm=True
        )
        
        print("✅ 处理完成！")
        print(f"📊 处理了 {result['frame_count']} 帧")
        print(f"🎥 输出MP4: {result['output_mp4']}")
        if result['output_webm']:
            print(f"🎬 输出WebM: {result['output_webm']}")
        print(f"📁 帧目录: {result['frames_dir']}")
        print(f"🖼️  处理后帧目录: {result['processed_frames_dir']}")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")

def example_different_models():
    """
    示例2: 使用不同的AI模型
    """
    print("\n=== 示例2: 比较不同AI模型效果 ===")
    
    input_video = "sample_video.mp4"
    
    if not os.path.exists(input_video):
        print(f"⚠️  输入视频文件不存在: {input_video}")
        return
    
    # 测试不同模型
    models = [
        ('u2net', '通用模型'),
        ('u2netp', '轻量版模型'),
        ('u2net_human_seg', '人物专用模型')
    ]
    
    for model_name, description in models:
        print(f"\n🤖 测试模型: {model_name} ({description})")
        
        try:
            remover = VideoBackgroundRemover(model_name=model_name)
            output_dir = f"output_{model_name}"
            
            result = remover.process_video(
                input_video=input_video,
                output_dir=output_dir,
                max_frames=20,  # 少量帧用于快速比较
                create_webm=False
            )
            
            print(f"✅ {description} 处理完成")
            print(f"📁 输出目录: {output_dir}")
            
        except Exception as e:
            print(f"❌ {description} 处理失败: {e}")

def example_single_frame_processing():
    """
    示例3: 单帧图像处理
    """
    print("\n=== 示例3: 单帧图像背景移除 ===")
    
    # 创建处理器
    remover = VideoBackgroundRemover(model_name='u2net')
    
    # 示例图像路径（请替换为实际图像）
    input_image = "sample_image.jpg"  # 替换为你的图像文件
    output_image = "output_transparent.png"
    
    if not os.path.exists(input_image):
        print(f"⚠️  输入图像文件不存在: {input_image}")
        print("请准备一张图像文件并重命名为 'sample_image.jpg'")
        return
    
    try:
        # 处理单帧
        remover.remove_background_from_frame(input_image, output_image)
        print(f"✅ 单帧处理完成: {output_image}")
        
    except Exception as e:
        print(f"❌ 单帧处理失败: {e}")

def example_batch_processing():
    """
    示例4: 批量处理多个视频
    """
    print("\n=== 示例4: 批量处理视频 ===")
    
    # 创建测试目录结构
    input_dir = "batch_input"
    output_dir = "batch_output"
    
    # 检查是否有视频文件用于批量处理
    if not os.path.exists(input_dir):
        print(f"⚠️  批量输入目录不存在: {input_dir}")
        print("请创建 'batch_input' 目录并放入一些视频文件")
        return
    
    # 查找视频文件
    video_files = []
    for ext in ['.mp4', '.avi', '.mov']:
        video_files.extend(Path(input_dir).glob(f"*{ext}"))
    
    if not video_files:
        print(f"⚠️  在 {input_dir} 中未找到视频文件")
        return
    
    print(f"📁 找到 {len(video_files)} 个视频文件")
    
    try:
        # 创建批处理器
        processor = BatchVideoProcessor(
            model_name='u2netp',  # 使用轻量模型加快处理
            max_frames=30  # 限制帧数
        )
        
        # 执行批处理
        stats = processor.process_batch(
            input_dir=input_dir,
            output_dir=output_dir,
            create_webm=False
        )
        
        print("\n📊 批处理统计:")
        print(f"总文件数: {stats['total']}")
        print(f"成功处理: {stats['success']}")
        print(f"处理失败: {stats['failed']}")
        print(f"总耗时: {stats['total_time']:.2f} 秒")
        
    except Exception as e:
        print(f"❌ 批处理失败: {e}")

def example_custom_workflow():
    """
    示例5: 自定义工作流程
    """
    print("\n=== 示例5: 自定义处理工作流程 ===")
    
    input_video = "sample_video.mp4"
    
    if not os.path.exists(input_video):
        print(f"⚠️  输入视频文件不存在: {input_video}")
        return
    
    try:
        # 创建处理器
        remover = VideoBackgroundRemover(model_name='u2net')
        
        # 步骤1: 提取帧
        print("🎬 步骤1: 提取视频帧...")
        output_dir = "custom_workflow"
        frame_count, fps, width, height, frames_list = remover.extract_frames(
            video_path=input_video,
            output_dir=output_dir,
            max_frames=20
        )
        print(f"✅ 提取了 {frame_count} 帧")
        
        # 步骤2: 处理帧（移除背景）
        print("🤖 步骤2: AI背景移除...")
        processed_frames = remover.process_frames(frames_list, output_dir)
        print(f"✅ 处理了 {len(processed_frames)} 帧")
        
        # 步骤3: 创建输出视频
        print("🎥 步骤3: 生成透明背景视频...")
        output_video = os.path.join(output_dir, "custom_output.mp4")
        remover.create_transparent_video(
            processed_frames=processed_frames,
            output_path=output_video,
            fps=fps,
            width=width,
            height=height
        )
        print(f"✅ 生成视频: {output_video}")
        
        print("\n🎉 自定义工作流程完成！")
        
    except Exception as e:
        print(f"❌ 自定义工作流程失败: {e}")

def create_sample_structure():
    """
    创建示例目录结构
    """
    print("\n=== 创建示例目录结构 ===")
    
    # 创建目录
    directories = [
        "batch_input",
        "output_basic",
        "output_u2net",
        "output_u2netp",
        "output_u2net_human_seg",
        "batch_output",
        "custom_workflow"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 创建目录: {directory}")
    
    # 创建说明文件
    readme_content = """
# 示例文件说明

请将你的测试文件放置如下：

1. sample_video.mp4 - 用于基本示例的视频文件
2. sample_image.jpg - 用于单帧处理的图像文件
3. batch_input/ - 放置多个视频文件用于批量处理

然后运行: python example_usage.py
"""
    
    with open("EXAMPLE_README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("📄 创建说明文件: EXAMPLE_README.txt")
    print("\n✅ 示例目录结构创建完成！")
    print("请按照 EXAMPLE_README.txt 的说明准备测试文件")

def main():
    """
    主函数 - 运行所有示例
    """
    print("🎬 视频背景移除工具 - 使用示例")
    print("=" * 50)
    
    # 创建示例目录结构
    create_sample_structure()
    
    # 检查是否有示例文件
    if not os.path.exists("sample_video.mp4"):
        print("\n⚠️  未找到示例视频文件 'sample_video.mp4'")
        print("请准备一个视频文件并重命名为 'sample_video.mp4' 后重新运行")
        print("\n或者直接修改示例代码中的文件路径")
        return
    
    # 运行示例
    try:
        example_basic_usage()
        example_different_models()
        example_single_frame_processing()
        example_batch_processing()
        example_custom_workflow()
        
        print("\n🎉 所有示例运行完成！")
        print("\n📁 查看各个输出目录了解处理结果")
        
    except KeyboardInterrupt:
        print("\n⏹️  用户中断执行")
    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")

if __name__ == "__main__":
    main()