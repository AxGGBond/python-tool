#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL SQL 文件导入工具
支持大文件导入，可以显示进度
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse

def import_sql_file(host="localhost", port=3306, user="root", password="", 
                    database="", sql_file="", charset="utf8mb4"):
    """
    导入 SQL 文件到 MySQL
    
    Args:
        host: MySQL 主机地址
        port: MySQL 端口
        user: 用户名
        password: 密码
        database: 数据库名
        sql_file: SQL 文件路径
        charset: 字符集
    """
    
    if not os.path.exists(sql_file):
        print(f"✗ SQL 文件不存在：{sql_file}")
        return False
    
    file_size = os.path.getsize(sql_file)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"=== MySQL SQL 文件导入工具 ===")
    print(f"文件: {sql_file}")
    print(f"大小: {file_size_mb:.2f} MB")
    print(f"数据库: {database}")
    print(f"主机: {host}:{port}")
    print("-" * 50)
    
    # 构建 mysql 命令
    mysql_cmd = [
        "mysql",
        f"-h{host}",
        f"-P{port}",
        f"-u{user}",
        f"-p{password}" if password else "",
        f"--default-character-set={charset}",
        database
    ]
    
    # 移除空参数
    mysql_cmd = [c for c in mysql_cmd if c]
    
    print("正在导入，请稍候...")
    print("（大文件可能需要较长时间）\n")
    
    try:
        # 读取 SQL 文件并导入
        with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
            process = subprocess.Popen(
                mysql_cmd,
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                print("✓ 导入成功！")
                if stdout:
                    print(stdout)
                return True
            else:
                print("✗ 导入失败")
                if stderr:
                    print("错误信息：")
                    print(stderr)
                return False
                
    except FileNotFoundError:
        print("✗ 未找到 mysql 命令")
        print("请确保 MySQL 客户端已安装并在 PATH 中")
        print("\n或者使用以下方法：")
        print("1. 安装 MySQL 客户端")
        print("2. 使用 Docker 执行：")
        print(f"   docker exec -i law-manage-mysql mysql -u{user} -p{password} {database} < {sql_file}")
        return False
    except Exception as e:
        print(f"✗ 导入出错：{e}")
        return False


def import_with_docker(container_name="law-manage-mysql", user="root", 
                       password="", database="", sql_file=""):
    """使用 Docker 容器导入 SQL 文件"""
    
    if not os.path.exists(sql_file):
        print(f"✗ SQL 文件不存在：{sql_file}")
        return False
    
    file_size = os.path.getsize(sql_file)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"=== 使用 Docker 导入 SQL 文件 ===")
    print(f"容器: {container_name}")
    print(f"文件: {sql_file}")
    print(f"大小: {file_size_mb:.2f} MB")
    print(f"数据库: {database}")
    print("-" * 50)
    
    # 获取 SQL 文件的绝对路径
    sql_file_abs = os.path.abspath(sql_file)
    
    # 构建 docker exec 命令
    # 方法1：通过 stdin 导入
    print("正在导入，请稍候...\n")
    
    try:
        with open(sql_file_abs, 'r', encoding='utf-8', errors='ignore') as f:
            docker_cmd = [
                "docker", "exec", "-i", container_name,
                "mysql",
                f"-u{user}",
                f"-p{password}" if password else "",
                database
            ]
            
            # 移除空参数
            docker_cmd = [c for c in docker_cmd if c]
            
            process = subprocess.Popen(
                docker_cmd,
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                print("✓ 导入成功！")
                return True
            else:
                print("✗ 导入失败")
                if stderr:
                    print("错误信息：")
                    print(stderr)
                return False
                
    except Exception as e:
        print(f"✗ 导入出错：{e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="MySQL SQL 文件导入工具")
    parser.add_argument("sql_file", help="SQL 文件路径")
    parser.add_argument("-H", "--host", default="localhost", help="MySQL 主机地址")
    parser.add_argument("-P", "--port", type=int, default=3306, help="MySQL 端口")
    parser.add_argument("-u", "--user", default="root", help="MySQL 用户名")
    parser.add_argument("-p", "--password", default="", help="MySQL 密码")
    parser.add_argument("-d", "--database", required=True, help="数据库名")
    parser.add_argument("--docker", help="使用 Docker 容器导入（容器名称）")
    parser.add_argument("--charset", default="utf8mb4", help="字符集")
    
    args = parser.parse_args()
    
    if args.docker:
        success = import_with_docker(
            container_name=args.docker,
            user=args.user,
            password=args.password,
            database=args.database,
            sql_file=args.sql_file
        )
    else:
        success = import_sql_file(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            database=args.database,
            sql_file=args.sql_file,
            charset=args.charset
        )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 交互式模式
        print("=== MySQL SQL 文件导入工具 ===\n")
        
        sql_file = input("请输入 SQL 文件路径: ").strip()
        if not sql_file or not os.path.exists(sql_file):
            print("文件不存在")
            sys.exit(1)
        
        use_docker = input("是否使用 Docker 容器？(y/N): ").strip().lower() == 'y'
        
        if use_docker:
            container_name = input("容器名称 (默认: law-manage-mysql): ").strip() or "law-manage-mysql"
            user = input("MySQL 用户名 (默认: root): ").strip() or "root"
            password = input("MySQL 密码: ").strip()
            database = input("数据库名: ").strip()
            
            import_with_docker(container_name, user, password, database, sql_file)
        else:
            host = input("MySQL 主机 (默认: localhost): ").strip() or "localhost"
            port = input("MySQL 端口 (默认: 3306): ").strip() or "3306"
            user = input("MySQL 用户名 (默认: root): ").strip() or "root"
            password = input("MySQL 密码: ").strip()
            database = input("数据库名: ").strip()
            
            import_sql_file(host, int(port), user, password, database, sql_file)
    else:
        main()

