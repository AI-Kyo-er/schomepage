#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schomepage主页生成系统 - Windows安装程序
版本: v2.5
更新时间: 2025年6月
"""

import os
import sys
import subprocess
import shutil
import platform
import winreg
from pathlib import Path
import urllib.request
import zipfile

def print_banner():
    """显示安装程序横幅"""
    print("=" * 60)
    print("    Schomepage主页生成系统 Windows安装程序")
    print("    版本: v2.5 | 更新时间: 2025年6月")
    print("=" * 60)
    print()

def check_windows():
    """检查是否为Windows系统"""
    if platform.system() != 'Windows':
        print("❌ 错误：此安装程序仅支持Windows 10/11系统")
        return False
    
    # 检查Windows版本
    version = platform.version()
    print(f"✅ 检测到Windows系统: {platform.platform()}")
    return True

def check_python():
    """检查Python是否已安装"""
    print("🔍 检查Python环境...")
    
    try:
        # 检查python命令
        result = subprocess.run(['python', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ 找到Python: {version}")
            
            # 检查版本是否满足要求（Python 3.7+）
            version_num = version.split()[1]
            major, minor = map(int, version_num.split('.')[:2])
            if major >= 3 and minor >= 7:
                return True
            else:
                print(f"⚠️  Python版本过低: {version_num} (需要3.7+)")
                return False
    except:
        pass
    
    try:
        # 尝试python3命令
        result = subprocess.run(['python3', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ 找到Python3: {version}")
            return True
    except:
        pass
    
    print("❌ 未找到Python环境")
    return False

def check_pip():
    """检查pip是否可用"""
    print("🔍 检查pip包管理器...")
    
    try:
        result = subprocess.run(['pip', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ 找到pip: {result.stdout.strip()}")
            return True
    except:
        pass
    
    try:
        result = subprocess.run(['pip3', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ 找到pip3: {result.stdout.strip()}")
            return True
    except:
        pass
    
    print("❌ 未找到pip包管理器")
    return False

def install_python():
    """安装Python"""
    print("📦 开始安装Python...")
    
    python_installer = "python-3.13.4-amd64.exe"
    
    if not os.path.exists(python_installer):
        print(f"❌ 错误：未找到Python安装包 {python_installer}")
        print("请确保将Python安装包放在与setup.py相同的目录中")
        return False
    
    print(f"🔧 正在运行Python安装程序: {python_installer}")
    print("⏳ 请在弹出的安装窗口中完成Python安装...")
    print("   建议勾选'Add Python to PATH'选项")
    
    try:
        # 静默安装Python，添加到PATH
        result = subprocess.run([
            python_installer,
            '/quiet',
            'InstallAllUsers=1',
            'PrependPath=1',
            'Include_test=0'
        ], timeout=600)  # 10分钟超时
        
        if result.returncode == 0:
            print("✅ Python安装完成")
            
            # 刷新环境变量
            print("🔄 刷新环境变量...")
            os.system('refreshenv')
            
            return True
        else:
            print(f"❌ Python安装失败，退出代码: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Python安装超时")
        return False
    except Exception as e:
        print(f"❌ Python安装出错: {e}")
        return False

def install_dependencies():
    """安装Python依赖包"""
    print("📦 安装项目依赖包...")
    
    dependencies = [
        'flask',
        'flask-cors',
        'pyinstaller'
    ]
    
    for dep in dependencies:
        print(f"⏳ 安装 {dep}...")
        try:
            result = subprocess.run([
                'pip', 'install', dep
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"✅ {dep} 安装成功")
            else:
                print(f"❌ {dep} 安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 安装 {dep} 时出错: {e}")
            return False
    
    return True

def create_launcher_script():
    """创建启动器脚本"""
    print("📝 创建启动器脚本...")
    
    launcher_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schomepage主页生成系统 - Windows启动器
自动启动服务器并打开浏览器
"""

import os
import sys
import time
import threading
import webbrowser
import subprocess
from pathlib import Path

def start_server():
    """启动Flask服务器"""
    # 切换到login目录
    login_dir = Path(__file__).parent / "login"
    os.chdir(login_dir)
    
    # 启动服务器
    subprocess.run([sys.executable, "server.py"])

def open_browser():
    """延迟打开浏览器"""
    print("⏳ 等待服务器启动...")
    time.sleep(3)  # 等待3秒让服务器启动
    
    print("🌐 正在打开浏览器...")
    webbrowser.open("http://localhost:5000")

def main():
    print("🚀 Schomepage主页生成系统 正在启动...")
    print("=" * 50)
    
    # 检查login目录是否存在
    login_dir = Path(__file__).parent / "login"
    if not login_dir.exists():
        print("❌ 错误：未找到login目录")
        input("按任意键退出...")
        return
    
    # 在后台打开浏览器
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动服务器（主线程）
    try:
        start_server()
    except KeyboardInterrupt:
        print("\\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        input("按任意键退出...")

if __name__ == "__main__":
    main()
'''
    
    with open('schomepage_launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_code)
    
    print("✅ 启动器脚本创建完成")
    return True

def build_executable():
    """使用PyInstaller构建可执行文件"""
    print("🔨 构建可执行文件...")
    
    try:
        # 构建命令
        cmd = [
            'pyinstaller',
            '--onefile',
            '--noconsole',
            '--name=schomepage',
            '--icon=icon.ico',  # 如果有图标文件
            'schomepage_launcher.py'
        ]
        
        # 如果没有图标文件，移除图标参数
        if not os.path.exists('icon.ico'):
            cmd.remove('--icon=icon.ico')
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ 可执行文件构建完成")
            
            # 移动exe文件到当前目录
            exe_path = Path('dist/schomepage.exe')
            if exe_path.exists():
                shutil.move(str(exe_path), 'schomepage.exe')
                print("✅ schomepage.exe 已生成")
                
                # 清理构建文件
                shutil.rmtree('build', ignore_errors=True)
                shutil.rmtree('dist', ignore_errors=True)
                os.remove('schomepage.spec')
                
                return True
            else:
                print("❌ 未找到生成的exe文件")
                return False
        else:
            print(f"❌ 构建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False

def create_readme():
    """创建README文件"""
    print("📄 创建用户指南...")
    
    readme_content = '''# Schomepage主页生成系统 - 用户指南

## 📋 软件简介

Schomepage主页生成系统是一个功能强大的HTML图文文章编辑器工作站，基于Python Flask + JavaScript构建。

### ✨ 主要功能
- 🔐 用户登录注册系统（支持邮箱验证）
- ✍️ 可视化HTML文章编辑器
- 🖼️ 图片素材管理（背景图片、图标库、我的图片）
- 🔗 文章链接功能
- 🎭 动态隐藏模块（针对不同访客显示不同内容）
- 🌐 访客通道管理
- 📊 访客统计功能
- 🔑 修改密码功能

## 💻 系统要求

- Windows 10 或 Windows 11
- 至少 2GB 可用磁盘空间
- 网络连接（用于邮件验证功能）

## 🚀 安装步骤

### 方法一：自动安装（推荐）

1. **下载安装包**
   - 确保已获得完整的软件包，包含 setup.py 和 python-3.13.4-amd64.exe

2. **运行安装程序**
   ```
   双击运行 setup.py
   ```
   或在命令行中执行：
   ```cmd
   python setup.py
   ```

3. **等待安装完成**
   - 安装程序会自动检查Python环境
   - 如果没有Python，会自动安装
   - 自动安装所需依赖包
   - 生成 schomepage.exe 可执行文件

### 方法二：手动安装

1. **安装Python**
   - 运行 python-3.13.4-amd64.exe
   - **重要：勾选"Add Python to PATH"选项**

2. **安装依赖包**
   ```cmd
   pip install flask flask-cors
   ```

3. **直接运行**
   ```cmd
   cd login
   python server.py
   ```

## 🎯 使用方法

### 启动软件

#### 自动启动（推荐）
```
双击 schomepage.exe
```
- 程序会自动启动服务器
- 自动在浏览器中打开 http://localhost:5000
- 无需任何命令行操作

#### 手动启动
```cmd
cd login
python server.py
```
然后在浏览器中访问：http://localhost:5000

### 首次使用

1. **登录系统**
   - 用户名：`admin`
   - 密码：`123456`

2. **注册新账户**
   - 点击"账号注册"
   - 输入邮箱地址
   - 完成邮箱验证
   - 设置密码

### 主要功能使用

#### ✍️ 创建文章
1. 登录后点击"新建文章"
2. 使用工具栏添加文本、图片等元素
3. 点击"保存"保存文章

#### 🖼️ 管理图片
1. 点击左侧"素材库" -> "我的图片"
2. 点击"导入图片"上传自己的图片
3. 在编辑文章时可以插入这些图片

#### 🎭 动态隐藏功能
1. 选择文章中的元素（文字或图片）
2. 在右侧属性面板中设置"动态隐藏模块"
3. 可以设置"只给谁看"或"不给谁看"
4. 支持多种访客类型：student、teacher、tourist等

#### 🌐 设置访客通道
1. 点击左侧"访客通道"
2. 选择文章并设置别名
3. 访客可通过 http://localhost:5000/别名 访问
4. 支持指定访客类型：http://localhost:5000/别名&user=student

#### 📊 查看访客统计
1. 点击左侧"访客统计"
2. 查看不同类型访客的访问次数
3. 了解文章的受欢迎程度

## ⚙️ 高级设置

### 邮件服务配置
如需修改邮件服务器设置，请编辑 `login/server.py`：
```python
SMTP_SERVER = "smtp.163.com"
SMTP_PORT_SSL = 465
SMTP_USER = "你的邮箱@163.com"
SMTP_PASSWORD = "你的邮箱授权码"
```

### 调试模式
开发者可以在 `login/config.js` 中启用调试模式：
```javascript
const DEBUG_MODE = true;  // 启用调试模式
```

## 🔧 故障排除

### 常见问题

#### 1. 程序无法启动
- **检查Python环境**：确保Python已正确安装且添加到PATH
- **检查端口占用**：确保5000端口未被其他程序占用
- **重新运行安装程序**：运行 setup.py 重新安装

#### 2. 邮件发送失败
- **检查网络连接**：确保网络畅通
- **检查邮箱设置**：确认SMTP配置正确
- **启用开发模式**：临时跳过邮件验证

#### 3. 文章保存失败
- **检查磁盘空间**：确保有足够的磁盘空间
- **检查文件权限**：确保程序有写入权限

#### 4. 浏览器无法访问
- **检查防火墙**：确保防火墙允许5000端口
- **尝试其他浏览器**：Chrome、Firefox、Edge都支持
- **清除浏览器缓存**：清除缓存后重试

### 获取支持

如果遇到其他问题：
1. 查看服务器控制台的错误信息
2. 按F12打开浏览器开发者工具查看错误
3. 检查系统是否满足最低要求

## 📝 版本信息

- **当前版本**：v2.5
- **更新时间**：2025年6月
- **兼容系统**：Windows 10/11
- **Python版本**：3.7+（推荐3.13）

## 🔒 安全说明

### 密码安全
- 系统采用离散对数端到端加密
- 服务器从不接触明文密码
- 网络传输仅传递16字节加密数据

### 数据安全
- 所有用户数据存储在本地
- 支持定期备份用户文件
- 文件夹权限隔离保护

## 💡 使用技巧

### 1. 高效创建内容
- 使用模板功能快速创建文章结构
- 利用素材库重复使用图片资源
- 设置常用的文本样式作为模板

### 2. 访客管理
- 为不同类型访客创建专门的内容
- 使用动态隐藏功能实现个性化展示
- 通过访客统计了解内容受欢迎程度

### 3. 内容组织
- 使用文章链接功能创建导航结构
- 合理命名文章以便管理
- 定期整理和更新内容

## 📞 技术支持

### 开发者信息
- 软件名称：Schomepage主页生成系统
- 开发团队：Schomepage开发组
- 更新时间：2025年6月

### 反馈建议
如有使用问题或改进建议，欢迎反馈。

---

🎉 **感谢使用Schomepage主页生成系统！祝您使用愉快！**

*最后更新：2025年6月*
'''
    
    with open('README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README.txt 用户指南已创建")
    return True

def main():
    """主安装流程"""
    print_banner()
    
    # 检查Windows系统
    if not check_windows():
        input("按任意键退出...")
        return
    
    # 检查Python环境
    python_ok = check_python()
    pip_ok = check_pip() if python_ok else False
    
    # 如果Python环境不完整，尝试安装
    if not python_ok or not pip_ok:
        print("\n🔧 需要安装或更新Python环境")
        
        if not python_ok:
            if not install_python():
                print("❌ Python安装失败，无法继续")
                input("按任意键退出...")
                return
            
            # 重新检查Python和pip
            python_ok = check_python()
            pip_ok = check_pip()
    
    if not python_ok or not pip_ok:
        print("❌ Python环境仍不完整，无法继续安装")
        input("按任意键退出...")
        return
    
    # 安装依赖包
    print("\n📦 安装项目依赖...")
    if not install_dependencies():
        print("❌ 依赖包安装失败")
        input("按任意键退出...")
        return
    
    # 创建启动器脚本
    print("\n🔨 创建应用程序...")
    if not create_launcher_script():
        print("❌ 启动器创建失败")
        input("按任意键退出...")
        return
    
    # 构建可执行文件
    if not build_executable():
        print("❌ 可执行文件构建失败")
        print("💡 您仍可以通过运行 'python schomepage_launcher.py' 来启动程序")
    
    # 创建用户指南
    create_readme()
    
    print("\n" + "=" * 60)
    print("🎉 Schomepage主页生成系统安装完成！")
    print("=" * 60)
    print()
    print("📁 生成的文件：")
    if os.path.exists('schomepage.exe'):
        print("   • schomepage.exe      - 主程序（双击启动）")
    print("   • schomepage_launcher.py - 启动器脚本")
    print("   • README.txt          - 用户指南")
    print()
    print("🚀 使用方法：")
    if os.path.exists('schomepage.exe'):
        print("   双击 schomepage.exe 即可启动程序")
    else:
        print("   运行: python schomepage_launcher.py")
    print("   程序会自动打开浏览器访问 http://localhost:5000")
    print()
    print("📖 详细使用说明请查看 README.txt")
    print()
    
    input("按任意键退出安装程序...")

if __name__ == "__main__":
    main() 