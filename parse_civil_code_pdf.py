#!/usr/bin/env python3
"""
简单的PDF民法典解析脚本
"""
import os
from pdf_civil_code_parser import PDFCivilCodeParser

def main():
    """主函数"""
    print("PDF民法典解析器")
    print("=" * 40)
    
    # 使用配置的API密钥
    api_key = "sk-a14dc6cb330d4061a8d4396461f166f1"  # 请替换为实际的API密钥
    model = "qwen-plus-latest"
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    print(f"✅ 使用配置的API密钥和模型: {model}")
    print(f"✅ 使用base_url: {base_url}")
    
    # 检查文件是否存在
    input_file = "民法典.pdf"  # 请替换为实际的PDF文件名
    if not os.path.exists(input_file):
        print(f"❌ 文件 {input_file} 不存在")
        print("请将PDF文件放在当前目录中，并确保文件名正确")
        return
    
    print(f"✅ 找到文件: {input_file}")
    
    # 创建解析器
    parser = PDFCivilCodeParser(api_key=api_key, model=model)
    
    # 预览文档
    print("\n📖 预览文档内容...")
    parser.preview_pdf_content(input_file, max_articles=3)
    
    # 开始解析
    print(f"\n🚀 开始解析 {input_file}...")
    try:
        results = parser.parse_pdf_civil_code(
            input_file=input_file,
            output_file="民法典PDF解析结果.json",
            delay=1.0,
            use_structured_extraction=True,
            pdf_method="pdfplumber"
        )
        
        print(f"\n✅ 解析完成！")
        print(f"📊 共处理 {len(results)} 条法规")
        print(f"💾 结果已保存到: 民法典PDF解析结果.json")
        
        # 显示前几条结果
        print(f"\n📋 前3条解析结果预览:")
        for i, result in enumerate(results[:3]):
            if "error" not in result:
                print(f"{i+1}. {result.get('article_number', '未知条款')}")
                content = result.get('content', '')
                print(f"   内容: {content[:50]}..." if len(content) > 50 else f"   内容: {content}")
            else:
                print(f"{i+1}. 解析错误: {result.get('error', '未知错误')}")
        
    except Exception as e:
        print(f"❌ 解析过程中出现错误: {e}")

if __name__ == "__main__":
    main()
