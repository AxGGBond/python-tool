#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法律法规文件下载器
从CSV文件中解析数据，下载法律法规文件到指定目录
"""

import csv
import os
import requests
import time
from urllib.parse import urlparse
import re
from pathlib import Path

def parse_csv_data(csv_file_path):
    """
    解析CSV文件，提取下载链接和文件名
    """
    data_list = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            if not line:
                continue
                
            # 按xinshu分割数据
            parts = line.split('xinshu')
            
            # 查找https下载链接，只处理包含b23/laws的链接
            download_url = ""
            for part in parts:
                if 'b23/laws' in part:
                    # part 可能是列表字符串，需要提取第一个元素
                    # 提取 b23/laws/... 格式的路径
                    match = re.search(r"b23/laws/[^',\]]+", part)
                    if match:
                        download_url = "https://bainiudata2.oss-cn-beijing.aliyuncs.com/" + match.group()
                        break
            
            if not download_url:
                continue
            
            # 获取文件名（最后一个xinshu后的内容）
            filename = parts[3].strip()
            if not filename:
                print(f"第{line_num}行未找到文件名，跳过")
                continue
            
            # 确保文件名有正确的扩展名
            if not filename.endswith(('.docx', '.pdf', '.doc')):
                # 从URL中推断文件扩展名
                if download_url.endswith('.docx'):
                    filename += '.docx'
                elif download_url.endswith('.pdf'):
                    filename += '.pdf'
                elif download_url.endswith('.doc'):
                    filename += '.doc'
                else:
                    filename += '.docx'  # 默认扩展名
            
            data_list.append({
                'line_num': line_num,
                'download_url': download_url,
                'filename': filename
            })
    
    return data_list

def download_file(url, filepath, filename):
    """
    下载文件到指定路径，支持断点续传
    """
    try:
        # 检查文件是否已存在
        full_path = os.path.join(filepath, filename)
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            if file_size > 0:  # 文件存在且不为空
                return True
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(filepath, exist_ok=True)
        
        # 保存文件
        with open(full_path, 'wb') as f:
            f.write(response.content)
        
        return True
        
    except requests.exceptions.RequestException as e:
        return {'error': str(e), 'url': url, 'filename': filename}
    except Exception as e:
        return {'error': str(e), 'url': url, 'filename': filename}

def main():
    """
    主函数
    """
    # 配置参数
    csv_file = "nmb_flfg_20250929100558.csv"
    download_dir = r"D:\项淼链目管理\律师项目\项目数据\数据公司数据-法律法规\法规文件"
    
    print("开始解析CSV文件...")
    
    # 解析CSV数据
    data_list = parse_csv_data(csv_file)
    print(f"共找到 {len(data_list)} 个可下载的文件")
    
    if not data_list:
        print("没有找到可下载的文件")
        return
    
    # 创建下载目录
    os.makedirs(download_dir, exist_ok=True)
    
    # 统计信息
    success_count = 0
    failed_count = 0
    skipped_count = 0
    failed_list = []
    
    # 下载文件
    for i, data in enumerate(data_list, 1):
        # 检查文件是否已存在
        full_path = os.path.join(download_dir, data['filename'])
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            if file_size > 0:
                skipped_count += 1
                continue
        
        result = download_file(
            data['download_url'], 
            download_dir, 
            data['filename']
        )

        print(result)
        
        if result == True:
            print(f"下载成功: {data['filename']}")
            success_count += 1
        else:
            print(f"下载失败: {data['filename']}")
            failed_count += 1
            failed_list.append(result)
        
        # 添加延迟避免请求过于频繁
        time.sleep(1)
    
    
    print(f"\n下载完成!")
    print(f"成功下载: {success_count} 个文件")
    print(f"跳过已存在: {skipped_count} 个文件")
    print(f"下载失败: {failed_count} 个文件")
    print(f"总计处理: {success_count + skipped_count + failed_count} 个文件")
    print(f"文件保存位置: {download_dir}")

if __name__ == "__main__":
    main()
