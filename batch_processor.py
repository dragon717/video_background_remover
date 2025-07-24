#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量视频背景移除工具
支持批量处理多个视频文件
"""

import os
import argparse
import glob
from pathlib import Path
from video_background_remover import VideoBackgroundRemover, setup_logger
import time
import json

logger = setup_logger()

class BatchVideoProcessor:
    """批量视频处理器"""
    
    def __init__(self, model_name='u2net', max_frames=None):
        """
        初始化批量处理器
        
        Args:
            model_name (str): AI模型名称
            max_frames (int): 每个视频的最大处理帧数
        """
        self.model_name = model_name
        self.max_frames = max_frames
        self.remover = VideoBackgroundRemover(model_name=model_name)
        self.results = []
    
    def find_video_files(self, input_dir, extensions=None):
        """
        查找目录中的视频文件
        
        Args:
            input_dir (str): 输入目录
            extensions (list): 支持的文件扩展名
            
        Returns:
            list: 视频文件路径列表
        """
        if extensions is None:
            extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        
        video_files = []
        input_path = Path(input_dir)
        
        if not input_path.exists():
            logger.error(f"输入目录不存在: {input_dir}")
            return video_files
        
        for ext in extensions:
            pattern = f"**/*{ext}"
            files = list(input_path.glob(pattern))
            video_files.extend([str(f) for f in files])
        
        # 去重并排序
        video_files = sorted(list(set(video_files)))
        logger.info(f"找到 {len(video_files)} 个视频文件")
        
        return video_files
    
    def process_single_video(self, video_path, output_base_dir, create_webm=True):
        """
        处理单个视频文件
        
        Args:
            video_path (str): 视频文件路径
            output_base_dir (str): 输出基础目录
            create_webm (bool): 是否创建WebM格式
            
        Returns:
            dict: 处理结果
        """
        video_name = Path(video_path).stem
        output_dir = os.path.join(output_base_dir, video_name)
        
        logger.info(f"开始处理: {video_path}")
        start_time = time.time()
        
        try:
            result = self.remover.process_video(
                input_video=video_path,
                output_dir=output_dir,
                max_frames=self.max_frames,
                create_webm=create_webm
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            result.update({
                'status': 'success',
                'processing_time': processing_time,
                'video_name': video_name
            })
            
            logger.info(f"完成处理: {video_name} (耗时: {processing_time:.2f}秒)")
            
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            
            result = {
                'status': 'failed',
                'error': str(e),
                'processing_time': processing_time,
                'video_name': video_name,
                'input_video': video_path,
                'output_dir': output_dir
            }
            
            logger.error(f"处理失败: {video_name} - {e}")
        
        return result
    
    def process_batch(self, input_dir, output_dir, create_webm=True, extensions=None):
        """
        批量处理视频文件
        
        Args:
            input_dir (str): 输入目录
            output_dir (str): 输出目录
            create_webm (bool): 是否创建WebM格式
            extensions (list): 支持的文件扩展名
            
        Returns:
            dict: 批处理结果统计
        """
        logger.info(f"开始批量处理: {input_dir} -> {output_dir}")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 查找视频文件
        video_files = self.find_video_files(input_dir, extensions)
        
        if not video_files:
            logger.warning("未找到任何视频文件")
            return {'total': 0, 'success': 0, 'failed': 0, 'results': []}
        
        # 处理每个视频
        total_start_time = time.time()
        
        for i, video_path in enumerate(video_files, 1):
            logger.info(f"\n=== 处理进度: {i}/{len(video_files)} ===")
            
            result = self.process_single_video(video_path, output_dir, create_webm)
            self.results.append(result)
        
        total_end_time = time.time()
        total_time = total_end_time - total_start_time
        
        # 统计结果
        success_count = sum(1 for r in self.results if r['status'] == 'success')
        failed_count = len(self.results) - success_count
        
        stats = {
            'total': len(video_files),
            'success': success_count,
            'failed': failed_count,
            'total_time': total_time,
            'results': self.results
        }
        
        # 保存处理报告
        self.save_report(output_dir, stats)
        
        logger.info(f"\n=== 批处理完成 ===")
        logger.info(f"总计: {stats['total']} 个文件")
        logger.info(f"成功: {stats['success']} 个")
        logger.info(f"失败: {stats['failed']} 个")
        logger.info(f"总耗时: {total_time:.2f} 秒")
        
        return stats
    
    def save_report(self, output_dir, stats):
        """
        保存处理报告
        
        Args:
            output_dir (str): 输出目录
            stats (dict): 统计信息
        """
        report_path = os.path.join(output_dir, 'batch_processing_report.json')
        
        # 准备报告数据
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'model_name': self.model_name,
            'max_frames': self.max_frames,
            'statistics': {
                'total_files': stats['total'],
                'successful': stats['success'],
                'failed': stats['failed'],
                'total_processing_time': stats['total_time']
            },
            'results': []
        }
        
        # 添加每个文件的处理结果
        for result in stats['results']:
            result_info = {
                'video_name': result['video_name'],
                'status': result['status'],
                'processing_time': result['processing_time']
            }
            
            if result['status'] == 'success':
                result_info.update({
                    'frame_count': result.get('frame_count', 0),
                    'fps': result.get('fps', 0),
                    'resolution': result.get('resolution', [0, 0]),
                    'output_mp4': result.get('output_mp4', ''),
                    'output_webm': result.get('output_webm', '')
                })
            else:
                result_info['error'] = result.get('error', '')
            
            report_data['results'].append(result_info)
        
        # 保存报告
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            logger.info(f"处理报告已保存: {report_path}")
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
    
    def generate_html_report(self, output_dir, stats):
        """
        生成HTML格式的处理报告
        
        Args:
            output_dir (str): 输出目录
            stats (dict): 统计信息
        """
        html_path = os.path.join(output_dir, 'batch_processing_report.html')
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>批量视频处理报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; }}
        .summary {{ background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-item {{ text-align: center; padding: 10px; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #2196F3; }}
        .stat-label {{ color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; font-weight: bold; }}
        .success {{ color: #4CAF50; font-weight: bold; }}
        .failed {{ color: #f44336; font-weight: bold; }}
        .progress-bar {{ width: 100%; height: 20px; background-color: #f0f0f0; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background-color: #4CAF50; transition: width 0.3s ease; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>批量视频背景移除处理报告</h1>
        
        <div class="summary">
            <h3>处理概要</h3>
            <p><strong>处理时间:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>使用模型:</strong> {self.model_name}</p>
            <p><strong>最大帧数限制:</strong> {self.max_frames or '无限制'}</p>
            <p><strong>总处理时间:</strong> {stats['total_time']:.2f} 秒</p>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{stats['total']}</div>
                <div class="stat-label">总文件数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number success">{stats['success']}</div>
                <div class="stat-label">成功处理</div>
            </div>
            <div class="stat-item">
                <div class="stat-number failed">{stats['failed']}</div>
                <div class="stat-label">处理失败</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {(stats['success']/stats['total']*100) if stats['total'] > 0 else 0:.1f}%"></div>
        </div>
        <p style="text-align: center; margin-top: 10px;">成功率: {(stats['success']/stats['total']*100) if stats['total'] > 0 else 0:.1f}%</p>
        
        <h3>详细结果</h3>
        <table>
            <thead>
                <tr>
                    <th>视频名称</th>
                    <th>状态</th>
                    <th>处理时间</th>
                    <th>帧数</th>
                    <th>分辨率</th>
                    <th>帧率</th>
                    <th>备注</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in stats['results']:
            status_class = 'success' if result['status'] == 'success' else 'failed'
            status_text = '成功' if result['status'] == 'success' else '失败'
            
            if result['status'] == 'success':
                frame_count = result.get('frame_count', 'N/A')
                resolution = f"{result.get('resolution', [0, 0])[0]}x{result.get('resolution', [0, 0])[1]}"
                fps = f"{result.get('fps', 0):.2f}"
                note = '处理完成'
            else:
                frame_count = 'N/A'
                resolution = 'N/A'
                fps = 'N/A'
                note = result.get('error', '未知错误')[:50] + ('...' if len(result.get('error', '')) > 50 else '')
            
            html_content += f"""
                <tr>
                    <td>{result['video_name']}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{result['processing_time']:.2f}s</td>
                    <td>{frame_count}</td>
                    <td>{resolution}</td>
                    <td>{fps}</td>
                    <td>{note}</td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"HTML报告已保存: {html_path}")
        except Exception as e:
            logger.error(f"保存HTML报告失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量视频背景移除工具')
    parser.add_argument('-i', '--input-dir', required=True, help='输入目录路径')
    parser.add_argument('-o', '--output-dir', required=True, help='输出目录路径')
    parser.add_argument('-m', '--model', default='u2net',
                       choices=['u2net', 'u2netp', 'u2net_human_seg', 'isnet-general-use', 'silueta'],
                       help='背景移除模型')
    parser.add_argument('-f', '--max-frames', type=int, help='每个视频的最大处理帧数')
    parser.add_argument('--no-webm', action='store_true', help='不创建WebM格式')
    parser.add_argument('--extensions', nargs='+', 
                       default=['.mp4', '.avi', '.mov', '.mkv', '.wmv'],
                       help='支持的视频文件扩展名')
    parser.add_argument('--html-report', action='store_true', help='生成HTML格式报告')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 检查输入目录
    if not os.path.exists(args.input_dir):
        logger.error(f"输入目录不存在: {args.input_dir}")
        return 1
    
    try:
        # 创建批处理器
        processor = BatchVideoProcessor(
            model_name=args.model,
            max_frames=args.max_frames
        )
        
        # 执行批处理
        stats = processor.process_batch(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            create_webm=not args.no_webm,
            extensions=args.extensions
        )
        
        # 生成HTML报告
        if args.html_report:
            processor.generate_html_report(args.output_dir, stats)
        
        # 显示最终统计
        if stats['failed'] > 0:
            logger.warning(f"有 {stats['failed']} 个文件处理失败，请查看报告了解详情")
        
        return 0 if stats['failed'] == 0 else 1
        
    except Exception as e:
        logger.error(f"批处理失败: {e}")
        return 1

if __name__ == '__main__':
    exit(main())