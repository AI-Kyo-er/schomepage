@echo off
chcp 65001 >nul
title Schomepage安装程序构建工具

echo ============================================================
echo    Schomepage主页生成系统 - 安装程序构建工具
echo    版本: v2.5 ^| 更新时间: 2025年6月  
echo ============================================================
echo.

:: 检查Python环境
echo 🔍 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python环境
    echo 请先安装Python后再运行此脚本
    pause
    exit /b 1
)

echo ✅ Python环境检查通过

:: 检查pip
echo 🔍 检查pip包管理器...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到pip包管理器
    pause
    exit /b 1
)

echo ✅ pip检查通过

:: 安装PyInstaller
echo 📦 安装PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo ❌ PyInstaller安装失败
    pause
    exit /b 1
)

echo ✅ PyInstaller安装完成

:: 构建setup.exe
echo 🔨 构建setup.exe...
pyinstaller --onefile --console --name=setup setup.py
if %errorlevel% neq 0 (
    echo ❌ setup.exe构建失败
    pause
    exit /b 1
)

:: 移动文件
if exist "dist\setup.exe" (
    move "dist\setup.exe" "setup.exe"
    echo ✅ setup.exe构建完成
) else (
    echo ❌ 未找到构建的setup.exe文件
    pause
    exit /b 1
)

:: 清理构建文件
echo 🧹 清理构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "setup.spec" del "setup.spec"

echo.
echo ============================================================
echo 🎉 构建完成！
echo ============================================================
echo.
echo 📁 生成的文件：
echo    • setup.exe - Windows安装程序
echo.
echo 🚀 使用方法：
echo    双击 setup.exe 开始安装Schomepage系统
echo.
echo 📋 安装包内容：
echo    • setup.exe - 安装程序
echo    • python-3.13.4-amd64.exe - Python运行环境
echo    • login文件夹 - 完整的项目源码
echo.

pause 