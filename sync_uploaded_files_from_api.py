#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从API同步已上传文件列表
从知识库API获取已上传的文件列表，并保存到 uploaded_files_log.json
"""

import os
import requests
import json
import time
from typing import Dict, List

# API 配置
API_BASE_URL = "http://121.40.171.214/v1/datasets/7de958a4-08de-4801-b6ca-c98215907885"
DOCUMENTS_API_URL = f"{API_BASE_URL}/documents"
AUTHORIZATION_TOKEN = "dataset-pxnKXpar9XKLmOjDUmV55Iug"

# 已上传文件记录文件路径
UPLOADED_FILES_LOG = "uploaded_files_log.json"

def get_documents_from_api(page: int = 1, limit: int = 20) -> Dict:
    """
    从API获取文档列表
    
    Args:
        page: 页码，从1开始
        limit: 每页数量
    
    Returns:
        API返回的JSON数据
    """
    try:
        headers = {
            'Authorization': f'Bearer {AUTHORIZATION_TOKEN}'
        }
        
        params = {
            'page': page,
            'limit': limit
        }
        
        response = requests.get(DOCUMENTS_API_URL, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"获取文档列表失败: {e}")
        return None

def fetch_all_documents() -> List[Dict]:
    """
    获取所有文档（处理分页）
    
    Returns:
        所有文档的列表
    """
    all_documents = []
    page = 1
    limit = 100  # 每页获取100条，减少请求次数
    
    print("开始从API获取文档列表...")
    
    while True:
        print(f"正在获取第 {page} 页...")
        result = get_documents_from_api(page, limit)
        
        if not result:
            break
        
        documents = result.get('data', [])
        if not documents:
            break
        
        all_documents.extend(documents)
        print(f"  已获取 {len(documents)} 个文档，累计 {len(all_documents)} 个")
        
        # 检查是否还有更多数据
        has_more = result.get('has_more', False)
        if not has_more:
            break
        
        page += 1
        # 添加延迟避免请求过于频繁
        time.sleep(0.5)
    
    return all_documents

def convert_api_document_to_log_format(doc: Dict, upload_dir: str = None) -> Dict:
    """
    将API返回的文档信息转换为日志格式
    
    Args:
        doc: API返回的文档信息
        upload_dir: 上传目录，用于尝试匹配本地文件路径
    
    Returns:
        转换后的文档信息
    """
    file_name = doc.get('name', '')
    created_at = doc.get('created_at', 0)
    
    # 将时间戳转换为可读时间
    if created_at:
        upload_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created_at))
    else:
        upload_time = "未知"
    
    doc_info = {
        "file_name": file_name,
        "api_id": doc.get('id', ''),
        "upload_time": upload_time,
        "created_at": created_at,
        "indexing_status": doc.get('indexing_status', ''),
        "tokens": doc.get('tokens', 0),
        "enabled": doc.get('enabled', True),
        "archived": doc.get('archived', False),
        "data_source_type": doc.get('data_source_type', ''),
        "source": "api"  # 标记来源为API
    }
    
    # 如果提供了上传目录，尝试查找匹配的本地文件
    if upload_dir and os.path.exists(upload_dir):
        # 遍历目录查找匹配的文件名
        for root, dirs, files in os.walk(upload_dir):
            if file_name in files:
                file_path = os.path.join(root, file_name)
                doc_info["file_path"] = file_path
                # 获取文件信息
                try:
                    stat = os.stat(file_path)
                    doc_info["file_size"] = stat.st_size
                    doc_info["file_mtime"] = stat.st_mtime
                except:
                    pass
                break
    
    return doc_info

def save_documents_to_log(documents: List[Dict], log_file: str, upload_dir: str = None):
    """
    将文档列表保存到日志文件
    
    Args:
        documents: 文档列表
        log_file: 日志文件路径
        upload_dir: 上传目录（可选，用于匹配本地文件）
    """
    try:
        # 加载现有记录（如果存在）
        existing_records = {}
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    existing_records = json.load(f)
            except:
                pass
        
        # 以文件名为key创建新的记录结构
        # 使用文件名作为key，因为API返回的是文件名
        new_records = {}
        
        # 将现有记录转换为以文件名为key的格式
        for key, value in existing_records.items():
            file_name = value.get('file_name', '')
            if file_name:
                # 保留原有的签名key，但添加文件名索引
                new_records[file_name] = value
                new_records[file_name]['_signature_key'] = key  # 保留原始签名key
        
        # 更新或添加API获取的文档
        for doc in documents:
            doc_info = convert_api_document_to_log_format(doc, upload_dir)
            file_name = doc_info['file_name']
            
            if file_name:
                # 如果已存在该文件名的记录，合并信息
                if file_name in new_records:
                    # 保留本地文件路径信息
                    if 'file_path' in new_records[file_name] and 'file_path' not in doc_info:
                        doc_info['file_path'] = new_records[file_name]['file_path']
                    if 'file_size' in new_records[file_name] and 'file_size' not in doc_info:
                        doc_info['file_size'] = new_records[file_name]['file_size']
                    if 'file_mtime' in new_records[file_name] and 'file_mtime' not in doc_info:
                        doc_info['file_mtime'] = new_records[file_name]['file_mtime']
                
                new_records[file_name] = doc_info
        
        # 保存到文件
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(new_records, f, ensure_ascii=False, indent=2)
        
        print(f"\n成功保存 {len(new_records)} 个文档记录到 {log_file}")
        
    except Exception as e:
        print(f"保存文档列表失败: {e}")

def main():
    """
    主函数
    """
    # 可选：指定上传目录，用于匹配本地文件路径
    upload_dir = r"D:\项淼链目管理\律师项目\项目数据\数据公司数据-法律法规\法规文件"
    
    print("=" * 60)
    print("从API同步已上传文件列表")
    print("=" * 60)
    print(f"API地址: {DOCUMENTS_API_URL}")
    print(f"记录文件: {UPLOADED_FILES_LOG}")
    if upload_dir:
        print(f"上传目录: {upload_dir}")
    print()
    
    # 获取所有文档
    documents = fetch_all_documents()
    
    if not documents:
        print("未获取到任何文档")
        return
    
    print(f"\n总共获取到 {len(documents)} 个文档")
    
    # 显示文档统计信息
    print("\n文档状态统计:")
    status_count = {}
    for doc in documents:
        status = doc.get('indexing_status', 'unknown')
        status_count[status] = status_count.get(status, 0) + 1
    
    for status, count in sorted(status_count.items()):
        print(f"  {status}: {count} 个")
    
    # 保存到日志文件
    print()
    save_documents_to_log(documents, UPLOADED_FILES_LOG, upload_dir)
    
    print()
    print("=" * 60)
    print("同步完成!")
    print("=" * 60)
    print(f"已保存 {len(documents)} 个文档记录")
    print(f"记录文件: {UPLOADED_FILES_LOG}")

if __name__ == "__main__":
    main()

