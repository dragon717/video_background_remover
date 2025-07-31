#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频背景移除工具
支持从MP4视频中提取主体，生成透明背景的输出
"""

import os
import cv2
import numpy as np
from PIL import Image
import rembg
from rembg import remove, new_session
from tqdm import tqdm
import argparse
import logging
import colorlog
from pathlib import Path
import shutil

# 配置日志
def setup_logger():
    """设置彩色日志"""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    ))
    
    logger = colorlog.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()

class VideoBackgroundRemover:
    """视频背景移除处理类"""
    
    def __init__(self, model_name='u2net'):
        """
        初始化背景移除器
        
        Args:
            model_name (str): 使用的模型名称，可选: u2net, u2netp, u2net_human_seg, isnet-general-use, silueta
        """
        self.model_name = model_name
        logger.info(f"初始化背景移除模型: {model_name}")
        
        # 创建rembg会话
        try:
            self.session = new_session(model_name)
            logger.info("模型加载成功")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def extract_frames(self, video_path, output_dir, max_frames=None):
        """
        从视频中提取帧
        
        Args:
            video_path (str): 输入视频路径
            output_dir (str): 输出目录
            max_frames (int): 最大帧数限制
            
        Returns:
            tuple: (帧数, fps, 视频宽度, 视频高度)
        """
        logger.info(f"开始提取视频帧: {video_path}")
        
        # 创建输出目录
        frames_dir = os.path.join(output_dir, 'frames')
        os.makedirs(frames_dir, exist_ok=True)
        
        # 打开视频
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        # 获取视频信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        logger.info(f"视频信息: {total_frames}帧, {fps}fps, {width}x{height}")
        
        # 限制帧数
        if max_frames and max_frames < total_frames:
            total_frames = max_frames
            logger.info(f"限制处理帧数为: {max_frames}")
        
        frame_count = 0
        extracted_frames = []
        
        with tqdm(total=total_frames, desc="提取帧") as pbar:
            while True:
                ret, frame = cap.read()
                if not ret or (max_frames and frame_count >= max_frames):
                    break
                
                # 保存帧
                frame_filename = f"frame_{frame_count:06d}.png"
                frame_path = os.path.join(frames_dir, frame_filename)
                cv2.imwrite(frame_path, frame)
                extracted_frames.append(frame_path)
                
                frame_count += 1
                pbar.update(1)
        
        cap.release()
        logger.info(f"成功提取 {frame_count} 帧")
        
        return frame_count, fps, width, height, extracted_frames
    
    def remove_background_from_frame(self, frame_path, output_path):
        """
        从单帧图像中移除背景
        
        Args:
            frame_path (str): 输入帧路径
            output_path (str): 输出路径
        """
        try:
            # 读取图像
            with open(frame_path, 'rb') as f:
                input_data = f.read()
            
            # 移除背景
            output_data = remove(input_data, session=self.session)
            
            # 保存结果
            with open(output_path, 'wb') as f:
                f.write(output_data)
                
        except Exception as e:
            logger.error(f"处理帧失败 {frame_path}: {e}")
            raise
    
    def process_frames(self, frames_list, output_dir):
        """
        批量处理帧，移除背景
        
        Args:
            frames_list (list): 帧文件路径列表
            output_dir (str): 输出目录
            
        Returns:
            list: 处理后的帧路径列表
        """
        logger.info("开始批量移除背景")
        
        # 创建输出目录
        processed_dir = os.path.join(output_dir, 'processed_frames')
        os.makedirs(processed_dir, exist_ok=True)
        
        processed_frames = []
        
        with tqdm(total=len(frames_list), desc="移除背景") as pbar:
            for i, frame_path in enumerate(frames_list):
                # 生成输出路径
                frame_filename = f"processed_frame_{i:06d}.png"
                output_path = os.path.join(processed_dir, frame_filename)
                
                # 处理帧
                self.remove_background_from_frame(frame_path, output_path)
                processed_frames.append(output_path)
                
                pbar.update(1)
        
        logger.info(f"成功处理 {len(processed_frames)} 帧")

        return processed_frames
    
    def create_transparent_video(self, processed_frames, output_path, fps, width, height):
        """
        从处理后的帧创建透明背景视频
        
        Args:
            processed_frames (list): 处理后的帧路径列表
            output_path (str): 输出视频路径
            fps (float): 帧率
            width (int): 视频宽度
            height (int): 视频高度
        """
        logger.info(f"开始创建透明背景视频: {output_path}")
        
        # 使用支持透明度的编码器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), True)
        
        if not out.isOpened():
            logger.error("无法创建视频写入器")
            raise ValueError("无法创建视频文件")
        
        with tqdm(total=len(processed_frames), desc="生成视频") as pbar:
            for frame_path in processed_frames:
                # 读取带透明度的图像
                img = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)
                
                if img is None:
                    logger.warning(f"无法读取帧: {frame_path}")
                    continue
                
                # 如果图像有4个通道(RGBA)，需要处理透明度
                if img.shape[2] == 4:
                    # 将RGBA转换为RGB，使用白色背景
                    alpha = img[:, :, 3] / 255.0
                    for c in range(3):
                        img[:, :, c] = img[:, :, c] * alpha + 255 * (1 - alpha)
                    img = img[:, :, :3]
                
                # 确保图像尺寸正确
                if img.shape[:2] != (height, width):
                    img = cv2.resize(img, (width, height))
                
                out.write(img.astype(np.uint8))
                pbar.update(1)
        
        out.release()
        logger.info("视频创建完成")
    
    def create_webm_with_transparency(self, processed_frames, output_path, fps):
        """
        创建支持透明度的WebM视频
        
        Args:
            processed_frames (list): 处理后的帧路径列表
            output_path (str): 输出视频路径
            fps (float): 帧率
        """
        logger.info(f"开始创建透明WebM视频: {output_path}")
        
        # 使用ffmpeg命令创建透明WebM
        frames_pattern = os.path.join(os.path.dirname(processed_frames[0]), 'processed_frame_%06d.png')
        
        cmd = f"ffmpeg -y -framerate {fps} -i '{frames_pattern}' -c:v libvpx-vp9 -pix_fmt yuva420p '{output_path}'"
        
        logger.info(f"执行命令: {cmd}")
        os.system(cmd)
    
    def process_video(self, input_video, output_dir, max_frames=None, create_webm=True):
        """
        完整的视频处理流程
        
        Args:
            input_video (str): 输入视频路径
            output_dir (str): 输出目录
            max_frames (int): 最大处理帧数
            create_webm (bool): 是否创建WebM格式
            
        Returns:
            dict: 处理结果信息
        """
        logger.info(f"开始处理视频: {input_video}")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # 1. 提取帧
            frame_count, fps, width, height, frames_list = self.extract_frames(
                input_video, output_dir, max_frames
            )
            
            # 2. 处理帧（移除背景）
            processed_frames = self.process_frames(frames_list, output_dir)
            
            # 3. 创建输出视频
            output_mp4 = os.path.join(output_dir, 'output_transparent.mp4')
            self.create_transparent_video(processed_frames, output_mp4, fps, width, height)
            
            # 4. 可选：创建WebM格式（更好的透明度支持）
            output_webm = None
            if create_webm:
                output_webm = os.path.join(output_dir, 'output_transparent.webm')
                try:
                    self.create_webm_with_transparency(processed_frames, output_webm, fps)
                except Exception as e:
                    logger.warning(f"WebM创建失败: {e}")
                    output_webm = None
            
            # 返回结果信息
            result = {
                'input_video': input_video,
                'output_dir': output_dir,
                'frame_count': frame_count,
                'fps': fps,
                'resolution': (width, height),
                'output_mp4': output_mp4,
                'output_webm': output_webm,
                'frames_dir': os.path.join(output_dir, 'frames'),
                'processed_frames_dir': os.path.join(output_dir, 'processed_frames')
            }
            
            logger.info("视频处理完成！")
            logger.info(f"输出MP4: {output_mp4}")
            if output_webm:
                logger.info(f"输出WebM: {output_webm}")
            logger.info(f"原始帧目录: {result['frames_dir']}")
            logger.info(f"处理后帧目录: {result['processed_frames_dir']}")
            
            return result
            
        except Exception as e:
            logger.error(f"视频处理失败: {e}")
            raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='视频背景移除工具')
    parser.add_argument('-i', '--input', required=True, help='输入视频路径')
    parser.add_argument('-o', '--output', required=True, help='输出目录')
    parser.add_argument('-m', '--model', default='u2net', 
                       choices=['u2net', 'u2netp', 'u2net_human_seg', 'isnet-general-use', 'silueta'],
                       help='背景移除模型')
    parser.add_argument('-f', '--max-frames', type=int, help='最大处理帧数')
    parser.add_argument('--no-webm', action='store_true', help='不创建WebM格式')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 检查输入文件
    if not os.path.exists(args.input):
        logger.error(f"输入文件不存在: {args.input}")
        return 1
    
    try:
        # 创建处理器
        remover = VideoBackgroundRemover(model_name=args.model)
        
        # 处理视频
        result = remover.process_video(
            input_video=args.input,
            output_dir=args.output,
            max_frames=args.max_frames,
            create_webm=not args.no_webm
        )
        
        logger.info("\n=== 处理完成 ===")
        logger.info(f"处理帧数: {result['frame_count']}")
        logger.info(f"视频分辨率: {result['resolution'][0]}x{result['resolution'][1]}")
        logger.info(f"帧率: {result['fps']:.2f} fps")
        logger.info(f"输出文件: {result['output_mp4']}")
        if result['output_webm']:
            logger.info(f"WebM文件: {result['output_webm']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"处理失败: {e}")
        return 1

if __name__ == '__main__':
    exit(main())