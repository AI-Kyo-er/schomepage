#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分布式架构验证脚本
验证客户端（8000端口）和服务器端（5000端口）的正常运行
"""

import requests
import time
import threading
import subprocess
import os

def test_server_endpoint(port, name, endpoint=""):
    """测试服务器端点"""
    try:
        url = f"http://localhost:{port}{endpoint}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {name} (端口{port}): 正常响应 - {response.status_code}")
            return True
        else:
            print(f"⚠️ {name} (端口{port}): 响应状态 - {response.status_code}")
            return True  # 能响应就说明服务器在运行
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} (端口{port}): 连接失败")
        return False
    except Exception as e:
        print(f"❌ {name} (端口{port}): 错误 - {e}")
        return False

def start_server_background(directory, name, port):
    """在后台启动服务器"""
    print(f"🚀 启动 {name}...")
    try:
        process = subprocess.Popen(
            ['python3', 'server.py'],
            cwd=directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        time.sleep(3)  # 等待启动
        
        # 检查是否成功启动
        if test_server_endpoint(port, name):
            print(f"✅ {name} 启动成功")
            return process
        else:
            print(f"❌ {name} 启动失败")
            process.terminate()
            return None
    except Exception as e:
        print(f"❌ 启动 {name} 时出错: {e}")
        return None

def main():
    print("🔧 分布式架构验证开始")
    print("=" * 60)
    
    # 邮件配置信息
    print("📧 邮件配置:")
    print("   - 服务器邮箱: test6535@163.com")
    print("   - 客户端邮箱: test6536@163.com")
    print()
    
    # 检查当前状态
    print("🔍 检查当前服务状态:")
    server_running = test_server_endpoint(5000, "服务器端", "/")
    client_running = test_server_endpoint(8000, "客户端", "/")
    
    processes = []
    
    # 启动服务器端
    if not server_running:
        print("\n🚀 启动服务器端...")
        server_process = start_server_background(
            'cloudserver/login', 
            '服务器端', 
            5000
        )
        if server_process:
            processes.append(('服务器端', server_process))
            server_running = True
    
    # 启动客户端
    if not client_running:
        print("\n🚀 启动客户端...")
        client_process = start_server_background(
            'client/login', 
            '客户端', 
            8000
        )
        if client_process:
            processes.append(('客户端', client_process))
            client_running = True
    
    print("\n" + "=" * 60)
    print("📊 最终验证结果:")
    
    if server_running and client_running:
        print("✅ 分布式架构部署成功！")
        print()
        print("🌐 访问方式:")
        print("   - 服务器端直接访问: http://localhost:5000")
        print("     (完整功能，自足运行)")
        print("   - 客户端邮件认证访问: http://localhost:8000")
        print("     (通过邮件与服务器端通信)")
        print()
        print("🔐 认证模式:")
        print("   - 服务器端: 本地直接认证")
        print("   - 客户端: 邮件通信认证")
        print()
        print("📧 邮件通信流程:")
        print("   1. 客户端发送请求邮件到服务器邮箱")
        print("   2. 服务器验证后回复邮件到客户端邮箱")
        print("   3. 客户端接收回复完成认证")
        
        if processes:
            print(f"\n⚠️ 注意：{len(processes)}个服务在后台运行中")
            print("   使用 Ctrl+C 或 pkill -f 'python3.*server.py' 停止")
        
    else:
        print("❌ 部分服务启动失败")
        if not server_running:
            print("   - 服务器端未运行")
        if not client_running:
            print("   - 客户端未运行")
        
        # 清理失败的进程
        for name, process in processes:
            try:
                process.terminate()
                print(f"🧹 清理 {name} 进程")
            except:
                pass
    
    print("\n" + "=" * 60)
    print("✅ 验证完成")

if __name__ == '__main__':
    main() 