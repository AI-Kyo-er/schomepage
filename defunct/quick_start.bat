@echo off
chcp 65001 >nul
title Schomepage主页生成系统

echo ============================================================
echo    Schomepage主页生成系统 - 快速启动
echo    版本: v2.5 ^| 更新时间: 2025年6月
echo ============================================================
echo.

:: 切换到login目录
if not exist "login" (
    echo ❌ 错误：未找到login目录
    echo 请确保在项目根目录下运行此脚本
    pause
    exit /b 1
)

cd login

:: 检查Python环境
echo 🔍 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python环境
    echo.
    echo 💡 解决方案：
    echo    1. 运行 setup.exe 自动安装Python和依赖
    echo    2. 或手动安装Python 3.7+并运行: pip install flask flask-cors
    echo.
    pause
    exit /b 1
)

echo ✅ 找到Python环境

:: 检查Flask是否安装
echo 🔍 检查Flask依赖...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Flask依赖
    echo 📦 正在安装Flask...
    pip install flask flask-cors
    if %errorlevel% neq 0 (
        echo ❌ Flask安装失败
        pause
        exit /b 1
    )
)

echo ✅ 依赖检查通过

:: 启动服务器
echo.
echo 🚀 正在启动Schomepage主页生成系统...
echo ⏳ 等待服务器启动后自动打开浏览器...
echo 💡 如果浏览器未自动打开，请手动访问: http://localhost:5000
echo.
echo 📝 默认登录信息：
echo    用户名: admin
echo    密码: 123456
echo.
echo ⚠️  关闭此窗口将停止服务器
echo ============================================================

:: 启动服务器并打开浏览器
start "" http://localhost:5000
python server.py

pause 