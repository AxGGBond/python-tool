#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量提取.doc和.docx文件内容到.txt文件（Windows原生方法）
使用PowerShell和Word COM接口，但更稳定
"""

import os
import sys
from pathlib import Path
import argparse
from typing import List, Optional
import time
import subprocess
import tempfile

try:
    import docx2txt
    from docx import Document
except ImportError as e:
    print(f"缺少必要的库，请安装：poetry add docx2txt python-docx")
    print(f"错误详情：{e}")
    sys.exit(1)


class DocToTxtExtractorWindows:
    """Windows原生DOC到TXT提取器"""
    
    def __init__(self):
        self.methods = [
            self._extract_with_powershell,
            self._extract_with_docx2txt,
            self._extract_with_python_docx
        ]
        print("✓ 初始化完成，使用Windows原生方法")
    
    def extract_single_file(self, doc_path: str, output_path: Optional[str] = None) -> bool:
        """
        提取单个.doc或.docx文件内容到.txt文件
        
        Args:
            doc_path: .doc或.docx文件路径
            output_path: 输出.txt文件路径，如果为None则自动生成
            
        Returns:
            bool: 提取是否成功
        """
        try:
            doc_path = Path(doc_path).resolve()
            if not doc_path.exists():
                print(f"✗ 文件不存在：{doc_path}")
                return False
            
            if doc_path.suffix.lower() not in ['.doc', '.docx']:
                print(f"✗ 不是.doc或.docx文件：{doc_path}")
                return False
            
            # 生成输出路径
            if output_path is None:
                output_path = doc_path.with_suffix('.txt')
            else:
                output_path = Path(output_path)
            
            # 检查输出文件是否已存在
            if output_path.exists():
                print(f"⊘ 跳过（文件已存在）：{output_path.name}")
                return True
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"正在提取：{doc_path.name} -> {output_path.name}")
            
            # 检查文件是否被占用
            try:
                with open(doc_path, 'rb') as f:
                    pass
            except PermissionError:
                print(f"✗ 文件被占用或权限不足：{doc_path}")
                return False
            
            # 尝试多种方法提取内容
            content = None
            successful_method = None
            
            for i, method in enumerate(self.methods):
                try:
                    print(f"  尝试方法 {i+1}/{len(self.methods)}: {method.__name__}")
                    content = method(str(doc_path))
                    if content and content.strip():
                        successful_method = method.__name__
                        print(f"  ✓ 方法 {method.__name__} 成功")
                        break
                    else:
                        print(f"  - 方法 {method.__name__} 返回空内容")
                except Exception as e:
                    print(f"  - 方法 {method.__name__} 失败: {str(e)[:50]}...")
                    continue
            
            if content and content.strip():
                # 保存到txt文件
                with open(output_path, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(content.strip())
                print(f"✓ 提取成功：{output_path} (方法: {successful_method})")
                return True
            else:
                print(f"✗ 所有方法都无法提取内容：{doc_path}")
                return False
                
        except Exception as e:
            print(f"✗ 提取失败 {doc_path.name}：{e}")
            return False
    
    def _extract_with_powershell(self, doc_path: str) -> Optional[str]:
        """使用PowerShell和Word COM接口提取"""
        try:
            # 创建PowerShell脚本
            ps_script = f'''
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
    $doc = $word.Documents.Open("{doc_path}")
    $content = $doc.Content.Text
    $doc.Close()
    Write-Output $content
}} catch {{
    Write-Error $_.Exception.Message
}} finally {{
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}}
'''
            
            # 执行PowerShell脚本
            result = subprocess.run([
                'powershell', '-Command', ps_script
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                raise Exception(f"PowerShell失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("PowerShell超时")
        except Exception as e:
            raise Exception(f"PowerShell失败: {e}")
    
    def _extract_with_docx2txt(self, doc_path: str) -> Optional[str]:
        """使用docx2txt库提取"""
        try:
            content = docx2txt.process(doc_path)
            return content
        except Exception as e:
            raise Exception(f"docx2txt失败: {e}")
    
    def _extract_with_python_docx(self, doc_path: str) -> Optional[str]:
        """使用python-docx库提取"""
        try:
            doc = Document(doc_path)
            content = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    content.append(paragraph.text)
            return '\n'.join(content) if content else None
        except Exception as e:
            raise Exception(f"python-docx失败: {e}")
    
    def extract_batch(self, input_dir: str, output_dir: Optional[str] = None, 
                     recursive: bool = False, test_limit: Optional[int] = None) -> dict:
        """
        批量提取目录中的.doc和.docx文件内容
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录，如果为None则在原目录生成
            recursive: 是否递归搜索子目录
            test_limit: 测试模式，只处理前N个文件
            
        Returns:
            dict: 提取结果统计
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"✗ 输入目录不存在：{input_dir}")
            return {"success": 0, "failed": 0, "total": 0}
        
        # 设置输出目录
        if output_dir is None:
            output_path = input_path
        else:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        # 查找所有.doc和.docx文件
        if recursive:
            doc_files = list(input_path.rglob("*.doc")) + list(input_path.rglob("*.docx"))
        else:
            doc_files = list(input_path.glob("*.doc")) + list(input_path.glob("*.docx"))
        
        if not doc_files:
            print(f"✗ 在目录 {input_dir} 中未找到.doc或.docx文件")
            return {"success": 0, "failed": 0, "total": 0}
        
        print(f"找到 {len(doc_files)} 个文件（.doc和.docx）")
        print(f"输出目录：{output_path}")
        print("-" * 50)
        
        success_count = 0
        failed_count = 0
        
        # 测试模式：只处理前N个文件
        if test_limit:
            doc_files = doc_files[:test_limit]
            print(f"测试模式：只处理前 {len(doc_files)} 个文件")
        
        for i, doc_file in enumerate(doc_files):
            # 计算相对路径以保持目录结构
            if recursive and output_dir:
                rel_path = doc_file.relative_to(input_path)
                output_file = output_path / rel_path.with_suffix('.txt')
                output_file.parent.mkdir(parents=True, exist_ok=True)
            else:
                output_file = output_path / doc_file.with_suffix('.txt').name
            
            if self.extract_single_file(str(doc_file), str(output_file)):
                success_count += 1
            else:
                failed_count += 1
            
            # 每处理10个文件休息一下
            if i > 0 and i % 10 == 0:
                print(f"  已处理 {i} 个文件，休息2秒...")
                time.sleep(2)
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(doc_files)
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="批量将.doc和.docx文件内容提取到.txt文件（Windows原生方法）")
    parser.add_argument("input", help="输入文件或目录路径")
    parser.add_argument("-o", "--output", help="输出文件或目录路径")
    parser.add_argument("-r", "--recursive", action="store_true", 
                       help="递归搜索子目录（仅对目录有效）")
    parser.add_argument("--list", action="store_true", 
                       help="仅列出找到的.doc和.docx文件，不进行提取")
    parser.add_argument("--test", type=int, metavar="N", 
                       help="测试模式，只处理前N个文件")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"✗ 输入路径不存在：{args.input}")
        return
    
    extractor = DocToTxtExtractorWindows()
    
    try:
        if input_path.is_file():
            # 单个文件提取
            if args.list:
                print(f"找到文件：{input_path}")
            else:
                success = extractor.extract_single_file(
                    str(input_path), 
                    args.output
                )
                if success:
                    print("✓ 提取完成")
                else:
                    print("✗ 提取失败")
        
        elif input_path.is_dir():
            # 目录批量提取
            if args.list:
                # 查找所有.doc和.docx文件
                if args.recursive:
                    doc_files = list(input_path.rglob("*.doc")) + list(input_path.rglob("*.docx"))
                else:
                    doc_files = list(input_path.glob("*.doc")) + list(input_path.glob("*.docx"))
                
                if doc_files:
                    print(f"找到 {len(doc_files)} 个文件（.doc和.docx）：")
                    for doc_file in doc_files:
                        print(f"  - {doc_file}")
                else:
                    print("未找到.doc或.docx文件")
            else:
                # 执行批量提取
                result = extractor.extract_batch(
                    str(input_path),
                    args.output,
                    args.recursive,
                    args.test
                )
                
                print("-" * 50)
                print(f"提取完成！")
                print(f"总计：{result['total']} 个文件")
                print(f"成功：{result['success']} 个")
                print(f"失败：{result['failed']} 个")
        
        else:
            print(f"✗ 无效的输入路径：{args.input}")
    
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"✗ 发生错误：{e}")


if __name__ == "__main__":
    # 如果没有命令行参数，提供交互式使用
    if len(sys.argv) == 1:
        print("=== DOC/DOCX到TXT内容提取工具（Windows原生方法） ===")
        print()
        
        # 获取输入路径
        input_path = input("请输入.doc/.docx文件或包含这些文件的目录路径：").strip()
        if not input_path:
            print("未输入路径，退出")
            sys.exit(0)
        
        input_path = Path(input_path)
        if not input_path.exists():
            print(f"路径不存在：{input_path}")
            sys.exit(1)
        
        # 检查是否为目录
        if input_path.is_dir():
            recursive = input("是否递归搜索子目录？(y/N)：").strip().lower() == 'y'
            output_dir = input("输出目录（留空则在原目录生成）：").strip()
            if not output_dir:
                output_dir = None
            
            extractor = DocToTxtExtractorWindows()
            try:
                result = extractor.extract_batch(str(input_path), output_dir, recursive)
                print("-" * 50)
                print(f"提取完成！")
                print(f"总计：{result['total']} 个文件")
                print(f"成功：{result['success']} 个")
                print(f"失败：{result['failed']} 个")
            finally:
                pass
        
        else:
            # 单个文件
            output_file = input("输出文件路径（留空则自动生成）：").strip()
            if not output_file:
                output_file = None
            
            extractor = DocToTxtExtractorWindows()
            try:
                success = extractor.extract_single_file(str(input_path), output_file)
                if success:
                    print("✓ 提取完成")
                else:
                    print("✗ 提取失败")
            finally:
                pass
    else:
        main()
