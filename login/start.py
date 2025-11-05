#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 6):
        print("❌ 错误：需要Python 3.6或更高版本")
        print(f"当前版本：{sys.version}")
        return False
    print(f"✅ Python版本检查通过：{sys.version.split()[0]}")
    return True

def install_requirements():
    """安装依赖包"""
    if not os.path.exists('requirements.txt'):
        print("❌ 错误：未找到requirements.txt文件")
        return False
    
    try:
        print("📦 正在安装Python依赖包...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 错误：依赖包安装失败")
        print("请手动运行：pip install -r requirements.txt")
        return False

def check_files():
    """检查必需文件"""
    required_files = [
        'server.py',
        'index.html',
        'main.html',
        'auth.js',
        'register.js',
        'users.csv'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 错误：缺少必需文件：{', '.join(missing_files)}")
        return False
    
    print("✅ 文件检查通过")
    return True

def start_server():
    """启动服务器"""
    try:
        print("🚀 正在启动服务器...")
        print("📌 访问地址：http://localhost:5000")
        print("⚠️  按 Ctrl+C 停止服务器")
        print("-" * 50)
        
        # 启动Flask服务器
        subprocess.call([sys.executable, 'server.py'])
        
    except KeyboardInterrupt:
        print("\n⏹️  服务器已停止")
    except Exception as e:
        print(f"❌ 错误：启动服务器失败 - {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("🏠 schomepage 登录系统启动器")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 检查文件
    if not check_files():
        return
    
    # 询问是否安装依赖
    install_deps = input("📦 是否需要安装Python依赖包？(y/n，默认为y): ").lower()
    if install_deps in ('', 'y', 'yes'):
        if not install_requirements():
            return
    
    print("\n✅ 所有检查完成，准备启动服务器...")
    print("🌐 启动后请在浏览器中访问：http://localhost:5000")
    print("📧 默认账号：admin，密码：123456")
    
    # 等待用户确认
    input("\n按 Enter 键启动服务器...")
    
    # 启动服务器
    start_server()

if __name__ == '__main__':
    main() 