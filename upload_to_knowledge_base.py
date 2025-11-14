#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量上传文件到知识库
将指定目录下的所有文件上传到知识库
"""

import os
import requests
import time
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Set

# API 配置
API_URL = "http://121.40.171.214/v1/datasets/7de958a4-08de-4801-b6ca-c98215907885/document/create-by-file"
AUTHORIZATION_TOKEN = "dataset-pxnKXpar9XKLmOjDUmV55Iug"

# 已上传文件记录文件路径
UPLOADED_FILES_LOG = "uploaded_files_log.json"
# 失败文件记录文件路径
FAILED_FILES_LOG = "failed_files_log.json"

# 上传配置数据
UPLOAD_DATA = {
    "indexing_technique": "high_quality",
    "process_rule": {
        "rules": {
            "pre_processing_rules": [
                {"id": "remove_extra_spaces", "enabled": True},
                {"id": "remove_urls_emails", "enabled": True}
            ],
            "segmentation": {
                "separator": "\n\n",
                "max_tokens": 1024,
                "chunk_overlap": 200
            }
        },
        "mode": "custom"
    }
}

def get_file_signature(file_path: str) -> str:
    """
    获取文件签名（用于唯一标识文件）
    使用文件路径、大小和修改时间生成签名
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件签名字符串
    """
    try:
        stat = os.stat(file_path)
        # 使用文件路径、大小和修改时间生成唯一签名
        signature_str = f"{file_path}|{stat.st_size}|{stat.st_mtime}"
        return hashlib.md5(signature_str.encode('utf-8')).hexdigest()
    except Exception:
        # 如果获取失败，使用文件路径的MD5作为备用
        return hashlib.md5(file_path.encode('utf-8')).hexdigest()

def load_uploaded_files(log_file: str) -> Dict[str, Dict]:
    """
    加载已上传文件记录
    
    Args:
        log_file: 记录文件路径
    
    Returns:
        已上传文件字典，key为文件签名，value为文件信息
    """
    if not os.path.exists(log_file):
        return {}
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"警告: 加载已上传文件记录失败: {e}")
        return {}

def save_uploaded_file(log_file: str, uploaded_files: Dict[str, Dict], file_path: str, result: Dict):
    """
    保存已上传文件记录
    
    Args:
        log_file: 记录文件路径
        uploaded_files: 已上传文件字典
        file_path: 文件路径
        result: 上传结果
    """
    try:
        file_signature = get_file_signature(file_path)
        uploaded_files[file_signature] = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "upload_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status_code": result.get("status_code"),
            "success": result.get("success", False)
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(uploaded_files, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"警告: 保存已上传文件记录失败: {e}")

def is_file_uploaded(file_path: str, uploaded_files: Dict[str, Dict]) -> bool:
    """
    检查文件是否已上传
    
    Args:
        file_path: 文件路径
        uploaded_files: 已上传文件字典
    
    Returns:
        True表示已上传，False表示未上传
    """
    if not os.path.exists(file_path):
        return False
    
    # 标准化文件路径（统一使用绝对路径，处理路径分隔符）
    normalized_path = os.path.abspath(file_path).replace('\\', '/')
    
    # 方法1: 通过文件路径匹配（日志中有 file_path 字段）
    for file_info in uploaded_files.values():
        if isinstance(file_info, dict):
            logged_path = file_info.get('file_path', '')
            if logged_path:
                normalized_logged_path = os.path.abspath(logged_path).replace('\\', '/')
                if normalized_path == normalized_logged_path:
                    return True
    
    # 方法2: 通过文件名匹配（兼容旧格式，key 是文件名）
    file_name = os.path.basename(file_path)
    if file_name in uploaded_files:
        logged_info = uploaded_files[file_name]
        if isinstance(logged_info, dict):
            logged_path = logged_info.get('file_path', '')
            if logged_path:
                normalized_logged_path = os.path.abspath(logged_path).replace('\\', '/')
                if normalized_path == normalized_logged_path:
                    return True
    
    # 方法3: 通过文件签名匹配（如果日志格式使用签名作为 key）
    file_signature = get_file_signature(file_path)
    if file_signature in uploaded_files:
        return True
    
    return False

def load_failed_files(log_file: str) -> Dict[str, Dict]:
    """
    加载失败文件记录
    
    Args:
        log_file: 记录文件路径
    
    Returns:
        失败文件字典，key为文件签名，value为文件信息
    """
    if not os.path.exists(log_file):
        return {}
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"警告: 加载失败文件记录失败: {e}")
        return {}

def save_failed_file(log_file: str, failed_files: Dict[str, Dict], file_path: str, error_msg: str, status_code: Optional[int] = None):
    """
    保存失败文件记录
    
    Args:
        log_file: 记录文件路径
        failed_files: 失败文件字典
        file_path: 文件路径
        error_msg: 错误信息
        status_code: HTTP状态码（可选）
    """
    try:
        file_signature = get_file_signature(file_path)
        failed_files[file_signature] = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "error": error_msg,
            "status_code": status_code,
            "fail_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "retry_count": failed_files.get(file_signature, {}).get("retry_count", 0) + 1
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(failed_files, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"警告: 保存失败文件记录失败: {e}")

def remove_failed_file(log_file: str, failed_files: Dict[str, Dict], file_path: str):
    """
    从失败文件记录中移除文件（当文件重新上传成功时调用）
    
    Args:
        log_file: 记录文件路径
        failed_files: 失败文件字典
        file_path: 文件路径
    """
    try:
        file_signature = get_file_signature(file_path)
        if file_signature in failed_files:
            del failed_files[file_signature]
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(failed_files, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"警告: 移除失败文件记录失败: {e}")

def upload_file(file_path: str, data_config: Dict) -> Dict:
    """
    上传单个文件到知识库
    
    Args:
        file_path: 文件路径
        data_config: 上传配置数据
    
    Returns:
        上传结果字典，包含成功/失败信息
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {
                "success": False,
                "file_path": file_path,
                "error": "文件不存在"
            }
        
        # 准备 multipart/form-data
        files = {
            'file': (os.path.basename(file_path), open(file_path, 'rb'))
        }
        
        # 准备 data 参数（JSON 字符串）
        data = {
            'data': json.dumps(data_config, ensure_ascii=False)
        }
        
        # 设置请求头
        headers = {
            'Authorization': f'Bearer {AUTHORIZATION_TOKEN}'
        }
        
        # 发送 POST 请求
        response = requests.post(
            API_URL,
            headers=headers,
            data=data,
            files=files,
            timeout=300  # 5分钟超时，因为文件可能较大
        )
        
        # 关闭文件
        files['file'][1].close()
        
        # 检查响应状态
        if response.status_code == 200 or response.status_code == 201:
            return {
                "success": True,
                "file_path": file_path,
                "status_code": response.status_code,
                "response": response.json() if response.content else None
            }
        else:
            return {
                "success": False,
                "file_path": file_path,
                "status_code": response.status_code,
                "error": response.text
            }
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "file_path": file_path,
            "error": "请求超时"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "file_path": file_path,
            "error": f"请求异常: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "file_path": file_path,
            "error": f"未知错误: {str(e)}"
        }

def get_all_files(directory: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    获取目录下的所有文件
    
    Args:
        directory: 目录路径
        extensions: 可选的文件扩展名列表，如 ['.pdf', '.docx']，None 表示所有文件
    
    Returns:
        文件路径列表
    """
    file_list = []
    
    if not os.path.exists(directory):
        print(f"错误: 目录不存在: {directory}")
        return file_list
    
    # 遍历目录及其子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            
            # 如果指定了扩展名过滤，则只处理匹配的文件
            if extensions:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in extensions:
                    file_list.append(file_path)
            else:
                file_list.append(file_path)
    
    return file_list

def main():
    """
    主函数
    """
    # 配置参数
    # upload_dir = r"D:\项淼链目管理\律师项目\项目数据\数据公司数据-法律法规\法规文件"
    upload_dir = r"D:\项淼链目管理\律师项目\项目数据\数据公司数据-法律法规\行政规章"
    
    # 可选：指定要上传的文件类型，None 表示上传所有文件
    # 例如：['.pdf', '.docx', '.doc', '.txt']
    file_extensions = None
    
    print("=" * 60)
    print("开始批量上传文件到知识库")
    print("=" * 60)
    print(f"上传目录: {upload_dir}")
    print(f"API地址: {API_URL}")
    print(f"已上传记录: {UPLOADED_FILES_LOG}")
    print(f"失败文件记录: {FAILED_FILES_LOG}")
    print()
    
    # 加载已上传文件记录
    print("正在加载已上传文件记录...")
    uploaded_files = load_uploaded_files(UPLOADED_FILES_LOG)
    print(f"已记录 {len(uploaded_files)} 个已上传文件")
    
    # 加载失败文件记录
    failed_files = load_failed_files(FAILED_FILES_LOG)
    print(f"已记录 {len(failed_files)} 个失败文件")
    print()
    
    # 获取所有文件
    print("正在扫描文件...")
    file_list = get_all_files(upload_dir, file_extensions)
    
    if not file_list:
        print("错误: 未找到任何文件")
        return
    
    print(f"共找到 {len(file_list)} 个文件")
    print()
    
    # 过滤掉已上传的文件
    files_to_upload = []
    skipped_uploaded = 0
    
    for file_path in file_list:
        if is_file_uploaded(file_path, uploaded_files):
            skipped_uploaded += 1
        else:
            files_to_upload.append(file_path)
    
    print(f"需要上传: {len(files_to_upload)} 个文件")
    print(f"跳过已上传: {skipped_uploaded} 个文件")
    print()
    
    if not files_to_upload:
        print("所有文件都已上传完成！")
        return
    
    # 统计信息
    success_count = 0
    failed_count = 0
    failed_list = []
    
    # 上传文件
    for i, file_path in enumerate(files_to_upload, 1):
        file_name = os.path.basename(file_path)
        print(f"[{i}/{len(files_to_upload)}] 正在上传: {file_name}")
        
        result = upload_file(file_path, UPLOAD_DATA)
        
        if result["success"]:
            print(f"  ✓ 上传成功")
            success_count += 1
            # 保存已上传记录
            save_uploaded_file(UPLOADED_FILES_LOG, uploaded_files, file_path, result)
            # 如果之前失败过，从失败列表中移除
            remove_failed_file(FAILED_FILES_LOG, failed_files, file_path)
        else:
            error_msg = result.get("error", "未知错误")
            status_code = result.get("status_code")
            print(f"  ✗ 上传失败: {error_msg}")
            failed_count += 1
            failed_list.append({
                "file_path": file_path,
                "error": error_msg
            })
            # 保存失败文件记录
            save_failed_file(FAILED_FILES_LOG, failed_files, file_path, error_msg, status_code)
        
        # 添加延迟避免请求过于频繁（5秒间隔，避免大量文件上传时对系统造成压力）
        if i < len(files_to_upload):  # 最后一个文件不需要延迟
            time.sleep(5)
    
    # 打印统计信息
    print()
    print("=" * 60)
    print("上传完成!")
    print("=" * 60)
    print(f"总文件数: {len(file_list)}")
    print(f"跳过已上传: {skipped_uploaded} 个文件")
    print(f"本次需上传: {len(files_to_upload)} 个文件")
    print(f"成功上传: {success_count} 个文件")
    print(f"上传失败: {failed_count} 个文件")
    if len(files_to_upload) > 0:
        print(f"本次成功率: {success_count/len(files_to_upload)*100:.2f}%")
    
    # 如果有失败的文件，打印失败列表
    if failed_list:
        print()
        print("=" * 60)
        print("本次上传失败文件列表:")
        print("=" * 60)
        for failed_item in failed_list:
            print(f"  - {failed_item['file_path']}")
            print(f"    错误: {failed_item['error']}")
        print()
        print(f"提示: 所有失败文件已保存到 {FAILED_FILES_LOG}")
        print(f"      下次运行时，这些文件将会重新尝试上传")
    
    # 显示历史失败文件统计
    if len(failed_files) > 0:
        print()
        print("=" * 60)
        print("历史失败文件统计:")
        print("=" * 60)
        print(f"累计失败文件数: {len(failed_files)}")
        
        # 按重试次数排序
        sorted_failed = sorted(failed_files.items(), key=lambda x: x[1].get("retry_count", 0), reverse=True)
        high_retry = [item for item in sorted_failed if item[1].get("retry_count", 0) > 1]
        
        if high_retry:
            print(f"多次失败文件数: {len(high_retry)}")
            print()
            print("多次失败的文件（重试次数 > 1）:")
            for signature, info in high_retry[:10]:  # 只显示前10个
                print(f"  - {info['file_name']} (重试 {info.get('retry_count', 0)} 次)")
                print(f"    路径: {info['file_path']}")
                print(f"    最后错误: {info.get('error', '未知')}")
            if len(high_retry) > 10:
                print(f"  ... 还有 {len(high_retry) - 10} 个文件")
        
        print()
        print(f"完整失败文件列表请查看: {FAILED_FILES_LOG}")

if __name__ == "__main__":
    main()

