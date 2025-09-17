#!/usr/bin/env python3
"""
JSON结果处理器
用于处理民法典解析结果，将对象重新组织为数组格式
"""
import json
import os
from typing import List, Dict, Any

class JsonProcessor:
    """JSON结果处理器"""
    
    def __init__(self):
        """初始化处理器"""
        pass
    
    def process_civil_code_results(self, input_file: str = "民法典解析结果.json", output_file: str = None) -> str:
        """
        处理民法典解析结果，将对象重新组织为数组格式
        
        Args:
            input_file: 输入的JSON文件路径
            output_file: 输出的JSON文件路径，如果为None则自动生成
            
        Returns:
            输出文件路径
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")
        
        if not output_file:
            # 自动生成输出文件名
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_processed.json"
        
        print(f"开始处理JSON文件: {input_file}")
        
        try:
            # 读取原始JSON文件
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            print(f"原始数据长度: {len(data)}")
            
            # 处理数据
            processed_data = self._process_data(data)
            
            # 保存处理后的数据
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 处理完成！")
            print(f"📄 输出文件: {output_file}")
            print(f"📊 处理后的数据长度: {len(processed_data)}")
            
            return output_file
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON文件格式错误: {e}")
        except Exception as e:
            raise Exception(f"处理过程中出现错误: {e}")
    
    def _process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理数据，确保所有对象都在数组中
        
        Args:
            data: 原始数据
            
        Returns:
            处理后的数据数组
        """
        processed_data = []
        
        for i, item in enumerate(data):
            if isinstance(item, dict):
                # 如果是字典对象，直接添加到数组中
                processed_data.append(item)
                print(f"处理第 {i+1} 个对象: {item.get('article_number', f'第{i+1}条')}")
            elif isinstance(item, list):
                # 如果是数组，展开并添加到结果中
                for sub_item in item:
                    if isinstance(sub_item, dict):
                        processed_data.append(sub_item)
                        print(f"处理子对象: {sub_item.get('article_number', '未知条款')}")
            else:
                print(f"跳过非对象类型数据: {type(item)}")
        
        return processed_data
    
    def validate_json_structure(self, file_path: str) -> Dict[str, Any]:
        """
        验证JSON文件结构
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            验证结果字典
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            result = {
                "file_path": file_path,
                "is_valid": True,
                "data_type": type(data).__name__,
                "data_length": len(data) if isinstance(data, (list, dict)) else 0,
                "sample_keys": [],
                "errors": []
            }
            
            if isinstance(data, list):
                result["data_type"] = "array"
                if data and isinstance(data[0], dict):
                    result["sample_keys"] = list(data[0].keys())
            elif isinstance(data, dict):
                result["data_type"] = "object"
                result["sample_keys"] = list(data.keys())
            else:
                result["errors"].append(f"不支持的数据类型: {type(data)}")
                result["is_valid"] = False
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                "file_path": file_path,
                "is_valid": False,
                "error": f"JSON格式错误: {e}",
                "data_type": None,
                "data_length": 0,
                "sample_keys": [],
                "errors": [str(e)]
            }
        except Exception as e:
            return {
                "file_path": file_path,
                "is_valid": False,
                "error": f"读取文件错误: {e}",
                "data_type": None,
                "data_length": 0,
                "sample_keys": [],
                "errors": [str(e)]
            }
    
    def extract_articles_info(self, file_path: str) -> Dict[str, Any]:
        """
        提取条款信息统计
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            条款信息统计
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("数据不是数组格式")
            
            stats = {
                "total_articles": len(data),
                "valid_articles": 0,
                "articles_with_content": 0,
                "articles_with_summary": 0,
                "articles_with_keywords": 0,
                "sample_articles": [],
                "error_articles": []
            }
            
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    if "error" not in item:
                        stats["valid_articles"] += 1
                        
                        if item.get("content"):
                            stats["articles_with_content"] += 1
                        if item.get("summary"):
                            stats["articles_with_summary"] += 1
                        if item.get("keywords"):
                            stats["articles_with_keywords"] += 1
                        
                        # 收集前5个有效条款作为样本
                        if len(stats["sample_articles"]) < 5:
                            stats["sample_articles"].append({
                                "article_number": item.get("article_number", f"第{i+1}条"),
                                "content_length": len(item.get("content", "")),
                                "has_summary": bool(item.get("summary")),
                                "keywords_count": len(item.get("keywords", []))
                            })
                    else:
                        stats["error_articles"].append({
                            "index": i,
                            "error": item.get("error", "未知错误")
                        })
            
            return stats
            
        except Exception as e:
            return {
                "error": f"提取信息时出错: {e}",
                "total_articles": 0,
                "valid_articles": 0
            }


def main():
    """主函数示例"""
    processor = JsonProcessor()
    
    # 验证原始JSON文件结构
    print("🔍 验证原始JSON文件结构...")
    validation_result = processor.validate_json_structure("民法典解析结果.json")
    
    if validation_result["is_valid"]:
        print(f"✅ JSON文件有效")
        print(f"📊 数据类型: {validation_result['data_type']}")
        print(f"📊 数据长度: {validation_result['data_length']}")
        print(f"📊 示例字段: {validation_result['sample_keys'][:5]}")
    else:
        print(f"❌ JSON文件无效: {validation_result.get('error', '未知错误')}")
        return
    
    # 提取条款信息统计
    print("\n📈 提取条款信息统计...")
    stats = processor.extract_articles_info("民法典解析结果.json")
    
    if "error" not in stats:
        print(f"📊 总条款数: {stats['total_articles']}")
        print(f"📊 有效条款数: {stats['valid_articles']}")
        print(f"📊 有内容的条款: {stats['articles_with_content']}")
        print(f"📊 有摘要的条款: {stats['articles_with_summary']}")
        print(f"📊 有关键词的条款: {stats['articles_with_keywords']}")
        
        if stats['error_articles']:
            print(f"⚠️ 错误条款数: {len(stats['error_articles'])}")
    else:
        print(f"❌ 统计信息提取失败: {stats['error']}")
    
    # 处理JSON文件
    print("\n🔄 开始处理JSON文件...")
    try:
        output_file = processor.process_civil_code_results(
            input_file="民法典解析结果.json",
            output_file="民法典解析结果_processed.json"
        )
        print(f"✅ 处理完成，输出文件: {output_file}")
    except Exception as e:
        print(f"❌ 处理失败: {e}")


if __name__ == "__main__":
    main()
