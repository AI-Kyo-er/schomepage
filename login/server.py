from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import smtplib
import csv
import random
import time
import os
import sys
import json
import os.path
from datetime import datetime, timedelta
import string
import re
from crypto_utils import verify_password, convert_plaintext_to_encrypted

# 修复Python 3.13的邮件导入问题
try:
    # 首先尝试模块级别的导入
    import email.mime.text
    import email.mime.multipart
    MimeText = email.mime.text.MIMEText
    MimeMultipart = email.mime.multipart.MIMEMultipart
    print("✅ 使用模块级导入成功")
except (ImportError, AttributeError):
    try:
        # 然后尝试传统导入
        from email.mime.text import MIMEText as MimeText
        from email.mime.multipart import MIMEMultipart as MimeMultipart
        print("✅ 使用传统导入成功")
    except ImportError:
        try:
            # 最后尝试新版本的EmailMessage
            from email.message import EmailMessage
            MimeText = EmailMessage
            MimeMultipart = EmailMessage
            print("✅ 使用EmailMessage成功")
        except ImportError:
            print("❌ 警告：无法导入邮件库，邮件功能不可用")
            MimeText = None
            MimeMultipart = None

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# SMTP配置 - 更新为更稳定的配置
SMTP_SERVER = "smtp.163.com"
SMTP_PORT_SSL = 465  # SSL端口
SMTP_PORT_TLS = 587  # STARTTLS端口（备用）
SMTP_USER = "test6535@163.com"
SMTP_PASSWORD = "ZBPyg39XDHzJFDCZ"  # 163邮箱正确授权码

# 存储验证码和限制信息
verification_codes = {}
rate_limits = {}
failed_attempts = {}

# 开发模式配置
DEVELOPMENT_MODE = False  # 启用真实邮件发送测试正确的授权码

# 🔧 SMTP修复说明：
# 163邮箱认证失败，需要以下步骤修复：
# 1. 登录 mail.163.com
# 2. 进入 设置 → POP3/SMTP/IMAP
# 3. 开启"SMTP服务"
# 4. 重新生成授权码
# 5. 将新授权码替换 SMTP_PASSWORD
# 
# 或者使用QQ邮箱替代方案：
# SMTP_SERVER = "smtp.qq.com"
# SMTP_USER = "your_qq@qq.com"  
# SMTP_PASSWORD = "16位QQ邮箱授权码"

def read_users_csv():
    """读取用户CSV文件"""
    users = {}
    try:
        with open('users.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # 确保用户名始终为小写，与登录API保持一致
                username = row['username'].strip().lower()
                users[username] = row['password']
                print(f"读取用户: {username}")  # 调试信息
    except FileNotFoundError:
        # 如果文件不存在，创建默认用户
        users = {'admin': '123456'}
        print("CSV文件不存在，创建默认用户")
        write_users_csv(users)
    return users

def write_users_csv(users):
    """写入用户CSV文件"""
    with open('users.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['username', 'password', 'maxarticle'])  # 添加maxarticle列
        for username, password in users.items():
            # 为现有用户添加默认maxarticle值
            writer.writerow([username, password, 30])
            print(f"写入用户: {username}")  # 调试信息

def load_registration_checklist():
    """加载注册操作清单"""
    try:
        with open('registration_checklist.json', 'r', encoding='utf-8') as file:
            checklist = json.load(file)
            print(f"✅ 加载注册清单成功")
            return checklist
    except FileNotFoundError:
        print("❌ 注册清单文件不存在")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ 注册清单JSON格式错误: {e}")
        return None

def create_user_folders(username, checklist):
    """根据清单文件为新用户创建文件夹结构"""
    if not checklist:
        print("❌ 清单文件无效，跳过文件夹创建")
        return False
    
    try:
        folder_ops = checklist['operations']['folder_operations']
        base_path = folder_ops['base_path']
        folders_to_create = folder_ops['folders_to_create']
        
        print(f"🗂️ 开始为用户 '{username}' 创建文件夹结构...")
        
        created_folders = []
        for folder_config in folders_to_create:
            # 替换路径中的占位符
            folder_path = folder_config['path'].replace('{username}', username)
            full_path = os.path.join(base_path, folder_path)
            
            # 检查文件夹是否已存在
            if os.path.exists(full_path):
                print(f"⚠️  文件夹已存在，保留现有: {full_path}")
                continue
            
            # 创建文件夹
            try:
                os.makedirs(full_path, exist_ok=True)
                created_folders.append(full_path)
                print(f"✅ 创建文件夹: {full_path}")
            except OSError as e:
                print(f"❌ 创建文件夹失败: {full_path}, 错误: {e}")
                return False
        
        print(f"🎉 用户 '{username}' 文件夹创建完成，共创建 {len(created_folders)} 个新文件夹")
        return True
        
    except Exception as e:
        print(f"❌ 创建用户文件夹时发生错误: {e}")
        return False

def write_users_csv_with_maxarticle(users):
    """写入用户CSV文件，包含maxarticle列"""
    try:
        with open('users.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'password', 'maxarticle'])
            for username, user_data in users.items():
                if isinstance(user_data, dict):
                    # 新的数据格式，包含密码和maxarticle
                    password = user_data.get('password', '')
                    maxarticle = user_data.get('maxarticle', 30)
                else:
                    # 旧的数据格式，只有密码
                    password = user_data
                    maxarticle = 30
                
                writer.writerow([username, password, maxarticle])
                print(f"写入用户: {username}, maxarticle: {maxarticle}")
        print("✅ CSV文件写入成功")
        return True
    except Exception as e:
        print(f"❌ 写入CSV文件失败: {e}")
        return False

def read_users_csv_with_maxarticle():
    """读取用户CSV文件，包含maxarticle列"""
    users = {}
    try:
        with open('users.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                username = row['username'].strip().lower()
                password = row['password']
                maxarticle = int(row.get('maxarticle', 30))  # 默认值30
                
                users[username] = {
                    'password': password,
                    'maxarticle': maxarticle
                }
                print(f"读取用户: {username}, maxarticle: {maxarticle}")
    except FileNotFoundError:
        # 如果文件不存在，创建默认用户
        users = {
            'admin': {
                'password': '18b16e270de878f3',  # 加密后的123456
                'maxarticle': 1
            }
        }
        print("CSV文件不存在，创建默认用户")
        write_users_csv_with_maxarticle(users)
    except Exception as e:
        print(f"❌ 读取CSV文件失败: {e}")
        users = {}
    
    return users

def generate_verification_code():
    """生成6位数字验证码"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_verification_email(email, code):
    """发送验证码邮件 - 修复163邮箱认证"""
    print(f"🔧 开始发送验证码邮件到: {email}")
    
    try:
        # 创建消息
        msg = MimeMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = email
        msg['Subject'] = '账号注册验证码'
        
        # 邮件正文
        body = f"""
        <html>
            <body>
                <h2>欢迎注册我们的系统</h2>
                <p>您的验证码是：<strong style="color: #007bff; font-size: 24px;">{code}</strong></p>
                <p>验证码有效期为10分钟，请尽快完成注册。</p>
                <p>如果您没有申请注册，请忽略此邮件。</p>
                <hr>
                <p><small>此邮件由系统自动发送，请勿回复。</small></p>
            </body>
        </html>
        """
        
        msg.attach(MimeText(body, 'html'))
        
        print(f"🔧 SMTP配置: {SMTP_SERVER}:{SMTP_PORT_SSL}, 用户: {SMTP_USER}")
        
        # 专门针对163邮箱优化的连接方式
        try:
            print("🔧 尝试163邮箱专用SMTP_SSL连接...")
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT_SSL, timeout=30) as server:
                # 不启用调试模式，减少干扰
                print("🔧 建立SSL连接成功")
                
                # 发送EHLO命令
                server.ehlo()
                print("🔧 EHLO握手成功")
                
                # 尝试LOGIN认证方式
                print("🔧 开始LOGIN认证...")
                server.login(SMTP_USER, SMTP_PASSWORD)
                print("🔧 LOGIN认证成功！")
                
                # 发送邮件
                text = msg.as_string()
                server.sendmail(SMTP_USER, email, text)
                print(f"✅ 验证码邮件已成功发送至: {email}")
                return True
                
        except smtplib.SMTPAuthenticationError as auth_error:
            print(f"❌ 163邮箱认证失败: {auth_error}")
            print("💡 可能的解决方案:")
            print("   1. 检查163邮箱是否开启了SMTP服务")
            print("   2. 确认授权码是否正确（不是邮箱密码）")
            print("   3. 在163邮箱设置中重新生成授权码")
            
            # 尝试替代配置
            try:
                print("🔧 尝试Gmail SMTP作为备用...")
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
                    # 这里需要用户配置Gmail的应用密码
                    print("⚠️  请在server.py中配置您的Gmail应用密码")
                    return False
            except:
                print("❌ Gmail备用方案也失败")
                return False
                
        except Exception as ssl_error:
            print(f"❌ SMTP_SSL连接失败: {ssl_error}")
            print("💡 连接问题可能的原因:")
            print("   1. 网络连接问题")
            print("   2. 防火墙阻止了465端口")
            print("   3. 163邮箱服务暂时不可用")
            return False
        
    except Exception as e:
        print(f"❌ 发送邮件异常: {e}")
        return False

def is_encrypted_password(password):
    """判断密码是否已经是加密形式（16进制，16位）"""
    if len(password) == 16:
        try:
            int(password, 16)
            return True
        except ValueError:
            return False
    return False

@app.route('/')
def index():
    """返回首页"""
    return send_from_directory('.', 'index.html')

@app.route('/<alias>')
def handle_alias_access(alias):
    """处理别名访问"""
    print(f"🔗 收到别名访问请求: {alias}")
    
    try:
        # 读取重定向规则
        redirects = read_redirect_csv()  # {address: alias}
        
        # 解析访客类型和干净别名
        visitor_type = parse_visitor_type(alias)
        clean_alias = get_clean_alias(alias)
        
        print(f"🔍 解析结果 - 干净别名: {clean_alias}, 访客类型: {visitor_type}")
        
        # 查找匹配的重定向规则 - 通过别名查找地址
        target_address = None
        
        # 遍历所有重定向规则，通过值(alias)查找键(address)
        for address, stored_alias in redirects.items():
            if stored_alias == alias or stored_alias == clean_alias:
                target_address = address
                break
        
        if not target_address:
            print(f"❌ 未找到别名 '{alias}' 的重定向规则")
            # 如果没有找到重定向规则，尝试作为静态文件处理
            return serve_static(alias)
        
        print(f"✅ 找到重定向目标: {alias} -> {target_address}")
        
        # 检查目标文件是否存在
        if not os.path.exists(target_address):
            print(f"❌ 目标文件不存在: {target_address}")
            return "文章不存在", 404
        
        # 记录访客访问（如果有访客类型）
        if visitor_type:
            article_dir = os.path.dirname(target_address)
            record_visitor_access(article_dir, visitor_type)
            print(f"📊 记录访客访问: {visitor_type} -> {article_dir}")
        
        # 获取文章内容
        content = get_article_content(target_address)
        
        # 添加访客统计脚本（如果有访客类型）
        visitor_script = ""
        if visitor_type:
            visitor_script = f"""
            <script>
                // 访客统计脚本
                console.log('访客类型: {visitor_type}');
                
                // 🎭 动态隐藏模块处理
                document.addEventListener('DOMContentLoaded', function() {{
                    applyDynamicHideRules('{visitor_type}');
                }});
                
                // 应用动态隐藏规则
                function applyDynamicHideRules(userType) {{
                    console.log('应用动态隐藏规则，用户类型:', userType);
                    
                    const elements = document.querySelectorAll('[data-hide-rule]');
                    elements.forEach(element => {{
                        const hideRule = element.getAttribute('data-hide-rule');
                        const hideUsers = element.getAttribute('data-hide-users');
                        
                        if (!hideRule || !hideUsers) return;
                        
                        const userList = hideUsers.split(',').map(u => u.trim());
                        let shouldHide = false;
                        
                        if (hideRule === 'show-only') {{
                            // 只给指定用户看：如果当前用户不在列表中，则隐藏
                            shouldHide = !userList.includes(userType);
                        }} else if (hideRule === 'hide-for') {{
                            // 不给指定用户看：如果当前用户在列表中，则隐藏
                            shouldHide = userList.includes(userType);
                        }}
                        
                        if (shouldHide) {{
                            element.style.display = 'none';
                            console.log('隐藏元素，规则:', hideRule, '用户:', userType);
                        }} else {{
                            element.style.display = '';
                            console.log('显示元素，规则:', hideRule, '用户:', userType);
                        }}
                    }});
                }}
            </script>
            """
        else:
            # 🔧 修复2: 匿名访问时，隐藏所有"只给谁看"的内容
            visitor_script = """
            <script>
                console.log('匿名访问，应用动态隐藏规则');
                
                // 🎭 动态隐藏模块处理
                document.addEventListener('DOMContentLoaded', function() {
                    applyDynamicHideRulesForAnonymous();
                });
                
                // 为匿名用户应用动态隐藏规则
                function applyDynamicHideRulesForAnonymous() {
                    console.log('为匿名用户应用动态隐藏规则');
                    
                    const elements = document.querySelectorAll('[data-hide-rule]');
                    elements.forEach(element => {
                        const hideRule = element.getAttribute('data-hide-rule');
                        const hideUsers = element.getAttribute('data-hide-users');
                        
                        if (!hideRule || !hideUsers) return;
                        
                        let shouldHide = false;
                        
                        if (hideRule === 'show-only') {
                            // 只给指定用户看：匿名用户不在任何列表中，所以隐藏
                            shouldHide = true;
                            console.log('隐藏"只给谁看"的元素，访客类型：匿名');
                        } else if (hideRule === 'hide-for') {
                            // 不给指定用户看：匿名用户不在禁止列表中，所以显示
                            shouldHide = false;
                            console.log('显示"不给谁看"的元素，访客类型：匿名');
                        }
                        
                        if (shouldHide) {
                            element.style.display = 'none';
                        } else {
                            element.style.display = '';
                        }
                    });
                }
            </script>
            """
        
        # 返回文章内容
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>文章访问</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #f8f9fa;
                    padding: 20px;
                    margin: 0;
                    line-height: 1.6;
                }}
                .article-container {{
                    background: white;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 40px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    border-radius: 5px;
                }}
                .image-element {{
                    max-width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            <div class="article-container">
                {content}
            </div>
            {visitor_script}
        </body>
        </html>
        """
        
    except Exception as e:
        print(f"❌ 处理别名访问失败: {e}")
        # 如果处理失败，尝试作为静态文件处理
        return serve_static(alias)

@app.route('/link/<username>/<filename>')
def handle_article_link(username, filename):
    """处理文章间链接访问"""
    try:
        print(f"🔗 收到文章链接访问: {username}/{filename}")
        
        # 获取来源文章参数
        from_article = request.args.get('from', '')
        print(f"📄 来源文章: {from_article}")
        
        # 构建目标文章路径
        article_path = f"../workplace/{username}/article/{filename}"
        
        # 获取文章内容
        article_content = get_article_content(article_path)
        if article_content is None:
            return f"文章文件不存在: {filename}", 404
        
        # 获取文章标题
        article_title = filename.replace('.html', '')
        
        # 构建返回链接
        back_url = f"/link/{username}/{from_article}" if from_article else "javascript:history.back();"
        
        # 返回带返回功能的文章页面
        link_html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_title} - 文章阅读</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8f9fa;
            line-height: 1.6;
            color: #333;
        }}
        
        .header {{
            background: #2c3e50;
            color: white;
            padding: 15px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header-content {{
            max-width: 800px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .logo {{
            font-size: 18px;
            font-weight: bold;
        }}
        
        .nav-info {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .back-button {{
            background: #e74c3c;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            text-decoration: none;
            display: inline-block;
            transition: background-color 0.3s;
        }}
        
        .back-button:hover {{
            background: #c0392b;
        }}
        
        .container {{
            max-width: 800px;
            margin: 20px auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .article-header {{
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .article-title {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .article-meta {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .article-content {{
            padding: 40px;
            min-height: 400px;
        }}
        
        .article-content h1, .article-content h2, .article-content h3 {{
            color: #2c3e50;
            margin: 20px 0 15px 0;
        }}
        
        .article-content p {{
            margin-bottom: 15px;
            text-indent: 2em;
        }}
        
        .article-content .image-element {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border-radius: 4px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .article-content blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            font-style: italic;
            color: #7f8c8d;
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 0 4px 4px 0;
        }}
        
        .navigation-notice {{
            background: #e8f4f8;
            border: 1px solid #3498db;
            color: #2c3e50;
            padding: 15px 20px;
            margin: 20px;
            border-radius: 4px;
            text-align: center;
            font-size: 14px;
        }}
        
        .footer {{
            background: #34495e;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }}
        
        /* 移除编辑控制元素 */
        .element-controls {{
            display: none !important;
        }}
        
        /* 禁用内容编辑 */
        [contenteditable] {{
            -webkit-user-modify: read-only;
            -moz-user-modify: read-only;
            user-modify: read-only;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 0;
            }}
            
            .article-content {{
                padding: 20px;
            }}
            
            .article-header {{
                padding: 20px;
            }}
            
            .article-title {{
                font-size: 24px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">🔗 文章链接导航</div>
            <div class="nav-info">
                {'<a href="' + back_url + '" class="back-button">⬅ 返回上级</a>' if from_article else '<button class="back-button" onclick="history.back()">⬅ 返回</button>'}
            </div>
        </div>
    </div>
    
    <div class="navigation-notice">
        🔗 您正在通过文章链接浏览此内容 {'· 来源: ' + from_article.replace('.html', '') if from_article else ''}
    </div>
    
    <div class="container">
        <div class="article-header">
            <h1 class="article-title">{article_title}</h1>
            <div class="article-meta">作者: {username} | 链接文章</div>
        </div>
        
        <div class="article-content">
            {article_content}
        </div>
    </div>
    
    <div class="footer">
        <p>© 2024 HTML图文文章编辑器 | 文章链接导航</p>
    </div>
    
    <script>
        // 禁用所有编辑功能
        document.addEventListener('DOMContentLoaded', function() {{
            // 移除所有控制按钮
            const controls = document.querySelectorAll('.element-controls');
            controls.forEach(control => control.remove());
            
            // 禁用内容编辑
            const editables = document.querySelectorAll('[contenteditable]');
            editables.forEach(element => {{
                element.removeAttribute('contenteditable');
                element.style.cursor = 'default';
            }});
            
            console.log('🔗 文章链接页面已设置为只读模式');
        }});
    </script>
</body>
</html>
        """
        
        return link_html
        
    except Exception as e:
        print(f"❌ 处理文章链接访问失败: {e}")
        return f"访问失败: {str(e)}", 500

@app.route('/api/get_visitor_stats', methods=['POST'])
def get_visitor_stats_api():
    """获取用户的访客统计信息API"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        
        if not username:
            return jsonify({
                'success': False,
                'message': '用户名不能为空'
            })
        
        stats = get_visitor_stats(username)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        print(f"❌ 获取访客统计失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取访客统计失败: {str(e)}'
        })

@app.route('/<path:filename>')
def serve_static(filename):
    """提供静态文件服务"""
    return send_from_directory('.', filename)

@app.route('/workplace/share/<path:filepath>')
def serve_shared_assets(filepath):
    """提供共享素材文件服务"""
    try:
        # 构建完整路径
        full_path = os.path.join('..', 'workplace', 'share')
        print(f"🖼️ 请求共享素材: {filepath}")
        print(f"📁 完整路径: {os.path.join(full_path, filepath)}")
        
        # 检查文件是否存在
        file_path = os.path.join(full_path, filepath)
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return "File not found", 404
        
        # 获取目录和文件名
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        source_dir = os.path.join(full_path, directory) if directory else full_path
        
        print(f"✅ 提供文件: {filename} 从 {source_dir}")
        return send_from_directory(source_dir, filename)
        
    except Exception as e:
        print(f"❌ 提供共享素材失败: {e}")
        return f"Error serving file: {str(e)}", 500

@app.route('/api/check_email', methods=['POST'])
def check_email():
    """检查邮箱是否已注册"""
    data = request.json
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'success': False, 'message': '请输入邮箱地址'})
    
    users = read_users_csv()
    if email in users:
        return jsonify({
            'success': False, 
            'message': '该邮箱已注册，如需重置密码请联系管理员：test6535@163.com'
        })
    
    return jsonify({'success': True, 'message': '邮箱可以注册'})

@app.route('/api/send_code', methods=['POST'])
def send_code():
    """发送验证码"""
    data = request.json
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'success': False, 'message': '请输入邮箱地址'})
    
    # 检查邮箱格式
    if '@' not in email or '.' not in email.split('@')[1]:
        return jsonify({'success': False, 'message': '邮箱格式不正确'})
    
    # 检查是否已注册
    users = read_users_csv()
    if email in users:
        return jsonify({
            'success': False, 
            'message': '该邮箱已注册，如需重置密码请联系管理员：test6535@163.com'
        })
    
    # 检查发送频率限制（60秒）
    current_time = time.time()
    if email in verification_codes:
        last_send_time = verification_codes[email]['timestamp']
        if current_time - last_send_time < 60:
            remaining_time = 60 - int(current_time - last_send_time)
            return jsonify({
                'success': False, 
                'message': f'请等待 {remaining_time} 秒后重新获取验证码'
            })
    
    # 生成6位验证码
    code = ''.join(random.choices(string.digits, k=6))
    
    # 发送邮件或开发模式跳过
    if DEVELOPMENT_MODE:
        print(f"🔧 开发模式：跳过邮件发送，验证码为 {code}")
        email_sent = True
    else:
        email_sent = send_verification_email(email, code)
    
    if email_sent:
        # 存储验证码
        verification_codes[email] = {
            'code': code,
            'timestamp': current_time,
            'attempts': 0
        }
        
        # 清除之前的失败记录
        if email in failed_attempts:
            del failed_attempts[email]
        
        if DEVELOPMENT_MODE:
            return jsonify({
                'success': True, 
                'message': f'验证码已生成：{code}（开发模式）'
            })
        else:
            return jsonify({'success': True, 'message': '验证码已发送，请查收邮件'})
    else:
        return jsonify({'success': False, 'message': '验证码发送失败，请稍后重试'})

@app.route('/api/verify_code', methods=['POST'])
def verify_code():
    """验证验证码"""
    data = request.json
    email = data.get('email', '').strip().lower()
    code = data.get('code', '').strip()
    
    if not email or not code:
        return jsonify({'success': False, 'message': '请输入邮箱和验证码'})
    
    # 检查是否被锁定
    if email in failed_attempts and failed_attempts[email] >= 5:
        return jsonify({
            'success': False, 
            'message': '验证码错误次数过多，请重新申请验证码'
        })
    
    # 检查验证码是否存在
    if email not in verification_codes:
        return jsonify({'success': False, 'message': '请先获取验证码'})
    
    stored_data = verification_codes[email]
    
    # 检查验证码是否过期（10分钟有效期）
    current_time = time.time()
    if current_time - stored_data['timestamp'] > 600:
        del verification_codes[email]
        return jsonify({'success': False, 'message': '验证码已过期，请重新获取'})
    
    # 验证验证码
    if stored_data['code'] != code:
        # 增加失败次数
        stored_data['attempts'] += 1
        if email not in failed_attempts:
            failed_attempts[email] = 0
        failed_attempts[email] += 1
        
        remaining_attempts = 5 - failed_attempts[email]
        if remaining_attempts <= 0:
            return jsonify({
                'success': False, 
                'message': '验证码错误次数过多，请重新申请验证码'
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'验证码错误，还有{remaining_attempts}次机会'
            })
    
    # 验证成功，注册用户
    print(f"🎉 验证码验证成功，开始注册用户 '{email}'")
    
    # 加载注册清单
    checklist = load_registration_checklist()
    if not checklist:
        return jsonify({'success': False, 'message': '系统配置错误，请联系管理员'})
    
    # 读取现有用户数据
    users = read_users_csv_with_maxarticle()
    
    # 🔒 关键修复：存储验证码的加密形式，而不是明文
    encrypted_code = convert_plaintext_to_encrypted(code)
    
    # 根据清单配置创建用户数据
    csv_config = checklist['operations']['csv_operations']
    maxarticle_default = None
    for column in csv_config['columns']:
        if column['name'] == 'maxarticle' and column['type'] == 'default_value':
            maxarticle_default = column['value']
            break
    
    if maxarticle_default is None:
        maxarticle_default = 30  # 备用默认值
    
    # 添加新用户
    users[email] = {
        'password': encrypted_code,  # 初始密码设为验证码的加密形式
        'maxarticle': maxarticle_default
    }
    
    # 写入CSV文件
    if not write_users_csv_with_maxarticle(users):
        return jsonify({'success': False, 'message': '注册失败：无法更新用户数据'})
    
    # 创建用户文件夹
    if not create_user_folders(email, checklist):
        print(f"⚠️  警告：用户 '{email}' 注册成功，但文件夹创建失败")
        # 注意：这里不返回错误，因为用户已经注册成功，只是文件夹创建失败
    
    print(f"✅ 用户 '{email}' 注册完成，初始密码为验证码 '{code}' 的加密形式: {encrypted_code}, maxarticle: {maxarticle_default}")
    
    # 清除验证码数据
    del verification_codes[email]
    if email in failed_attempts:
        del failed_attempts[email]
    
    return jsonify({'success': True, 'message': '注册成功'})

@app.route('/api/update_password', methods=['POST'])
def update_password():
    """更新用户密码 - 直接存储前端发送的密文"""
    data = request.json
    email = data.get('email', '').strip().lower()
    new_password = data.get('password', '')  # 这里是前端发送的密文
    
    print(f"收到密码更新请求: email={email}, 密文长度={len(new_password)}")
    
    if not email or not new_password:
        return jsonify({'success': False, 'message': '参数不完整'})
    
    users = read_users_csv_with_maxarticle()
    if email not in users:
        return jsonify({'success': False, 'message': '用户不存在'})
    
    # 更新密码，保持maxarticle不变
    users[email]['password'] = new_password
    
    if not write_users_csv_with_maxarticle(users):
        return jsonify({'success': False, 'message': '密码更新失败'})
    
    print(f"用户 {email} 密码已更新为密文: {new_password}")
    return jsonify({'success': True, 'message': '密码更新成功'})

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录 - 简单密文比对"""
    data = request.json
    print(f"收到登录请求: {data}")
    
    username = data.get('username', '').strip().lower()
    password = data.get('password', '')  # 这里是前端发送的密文
    
    print(f"处理后的用户名: '{username}', 密码长度: {len(password)}")
    
    if not username or not password:
        print("用户名或密码为空")
        return jsonify({'success': False, 'message': '请输入用户名和密码'})
    
    users = read_users_csv_with_maxarticle()
    print(f"从CSV读取的用户: {list(users.keys())}")
    print(f"查找用户 '{username}' 是否存在: {username in users}")
    
    if username in users:
        user_data = users[username]
        stored_password = user_data['password'] if isinstance(user_data, dict) else user_data
        maxarticle = user_data.get('maxarticle', 30) if isinstance(user_data, dict) else 30
        
        print(f"存储的密码: '{stored_password}'")
        print(f"接收的密码: '{password}'")
        print(f"用户maxarticle: {maxarticle}")
        print(f"密码匹配: {stored_password == password}")
        
        # 简单的字符串比对
        if stored_password == password:
            print("登录成功")
            return jsonify({
                'success': True, 
                'message': '登录成功',
                'user_info': {
                    'username': username,
                    'maxarticle': maxarticle
                }
            })
        else:
            print("密码不匹配")
            return jsonify({'success': False, 'message': '用户名或密码错误'})
    else:
        print("用户不存在")
        return jsonify({'success': False, 'message': '用户名或密码错误'})

@app.route('/api/convert_admin_password', methods=['POST'])
def convert_admin_password():
    """将admin密码从明文转换为加密形式"""
    try:
        users = read_users_csv()
        
        if 'admin' not in users:
            return jsonify({'success': False, 'message': 'admin用户不存在'})
        
        current_password = users['admin']
        
        # 如果已经是加密形式，不需要转换
        if is_encrypted_password(current_password):
            return jsonify({
                'success': True, 
                'message': f'admin密码已经是加密形式: {current_password}'
            })
        
        # 转换为加密形式
        encrypted_password = convert_plaintext_to_encrypted(current_password)
        users['admin'] = encrypted_password
        write_users_csv(users)
        
        print(f"admin密码已从明文 '{current_password}' 转换为加密形式 '{encrypted_password}'")
        
        return jsonify({
            'success': True, 
            'message': f'admin密码已转换为加密形式',
            'original': current_password,
            'encrypted': encrypted_password
        })
        
    except Exception as e:
        print(f"转换admin密码失败: {e}")
        return jsonify({'success': False, 'message': f'转换失败: {str(e)}'})

@app.route('/api/test_encrypt', methods=['POST'])
def test_encrypt():
    """测试加密功能"""
    try:
        data = request.json
        password = data.get('password', '')
        
        if not password:
            return jsonify({
                'success': False,
                'message': '密码不能为空'
            })
        
        # 加密密码
        encrypted = convert_plaintext_to_encrypted(password)
        
        # 验证加密后的密码
        is_valid = verify_password(password, encrypted)
        
        return jsonify({
            'success': True,
            'original': password,
            'encrypted': encrypted,
            'verification': is_valid
        })
        
    except Exception as e:
        print(f"❌ 测试加密失败: {e}")
        return jsonify({
            'success': False,
            'message': f'测试失败: {str(e)}'
        })

# 🆕 文章管理相关API接口

@app.route('/api/user_limits', methods=['POST'])
def get_user_limits():
    """获取用户的文章数量限制"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        
        if not username:
            return jsonify({
                'success': False,
                'message': '用户名不能为空'
            })
        
        users = read_users_csv_with_maxarticle()
        
        if username in users:
            maxarticle = users[username]['maxarticle']
            print(f"📊 用户 {username} 的文章限制: {maxarticle}")
            return jsonify({
                'success': True,
                'maxarticle': maxarticle
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            })
            
    except Exception as e:
        print(f"❌ 获取用户限制失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取用户限制失败: {str(e)}'
        })

@app.route('/api/user_articles', methods=['POST'])
def get_user_articles():
    """获取用户的文章列表"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        
        if not username:
            return jsonify({
                'success': False,
                'message': '用户名不能为空'
            })
        
        # 构建用户文章目录路径
        articles_path = os.path.join('..', 'workplace', username, 'article')
        
        articles = []
        
        if os.path.exists(articles_path):
            for filename in os.listdir(articles_path):
                if filename.endswith('.html'):
                    file_path = os.path.join(articles_path, filename)
                    # 获取文件的创建/修改时间
                    mtime = os.path.getmtime(file_path)
                    
                    # 从文件名生成显示名称
                    display_name = filename.replace('.html', '')
                    
                    articles.append({
                        'filename': filename,
                        'name': display_name,
                        'modified': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                    })
        
        # 按修改时间排序，最新的在前
        articles.sort(key=lambda x: x['modified'], reverse=True)
        
        print(f"📋 用户 {username} 的文章列表: {len(articles)} 篇文章")
        
        return jsonify({
            'success': True,
            'articles': articles
        })
        
    except Exception as e:
        print(f"❌ 获取文章列表失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取文章列表失败: {str(e)}'
        })

@app.route('/api/create_article', methods=['POST'])
def create_article():
    """创建新文章"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        article_name = data.get('name', '').strip()
        
        if not username or not article_name:
            return jsonify({
                'success': False,
                'message': '用户名和文章名不能为空'
            })
        
        # 检查用户文章数量限制
        users = read_users_csv_with_maxarticle()
        if username not in users:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            })
        
        max_articles = users[username]['maxarticle']
        
        # 构建用户文章目录路径
        articles_path = os.path.join('..', 'workplace', username, 'article')
        
        # 确保目录存在
        os.makedirs(articles_path, exist_ok=True)
        
        # 统计现有文章数量
        existing_articles = []
        if os.path.exists(articles_path):
            existing_articles = [f for f in os.listdir(articles_path) if f.endswith('.html')]
        
        if len(existing_articles) >= max_articles:
            return jsonify({
                'success': False,
                'message': f'已达到文章数量限制 ({max_articles}篇)'
            })
        
        # 生成文件名
        base_filename = article_name if article_name != 'article' else 'article'
        filename = f"{base_filename}.html"
        counter = 1
        
        # 检查文件名冲突
        while os.path.exists(os.path.join(articles_path, filename)):
            filename = f"{base_filename}{counter}.html"
            counter += 1
        
        # 创建默认文章内容
        default_content = '''<div class="editable-element" contenteditable="true">
    <h1>新文章标题</h1>
    <div class="element-controls">
        <button class="control-btn" onclick="deleteElement(this)" title="删除">×</button>
        <button class="control-btn" onclick="moveUp(this)" title="上移">↑</button>
        <button class="control-btn" onclick="moveDown(this)" title="下移">↓</button>
    </div>
</div>
<div class="editable-element" contenteditable="true">
    <p>在这里开始写您的文章内容...</p>
    <div class="element-controls">
        <button class="control-btn" onclick="deleteElement(this)" title="删除">×</button>
        <button class="control-btn" onclick="moveUp(this)" title="上移">↑</button>
        <button class="control-btn" onclick="moveDown(this)" title="下移">↓</button>
    </div>
</div>'''
        
        # 写入文件
        file_path = os.path.join(articles_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(default_content)
        
        print(f"📄 为用户 {username} 创建文章: {filename}")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': f'文章 "{article_name}" 创建成功'
        })
        
    except Exception as e:
        print(f"❌ 创建文章失败: {e}")
        return jsonify({
            'success': False,
            'message': f'创建文章失败: {str(e)}'
        })

@app.route('/api/load_article', methods=['POST'])
def load_article():
    """加载文章内容"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        filename = data.get('filename', '').strip()
        
        if not username or not filename:
            return jsonify({
                'success': False,
                'message': '用户名和文件名不能为空'
            })
        
        # 构建文件路径
        file_path = os.path.join('..', 'workplace', username, 'article', filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': '文章文件不存在'
            })
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📖 为用户 {username} 加载文章: {filename}")
        
        return jsonify({
            'success': True,
            'content': content
        })
        
    except Exception as e:
        print(f"❌ 加载文章失败: {e}")
        return jsonify({
            'success': False,
            'message': f'加载文章失败: {str(e)}'
        })

@app.route('/api/save_article', methods=['POST'])
def save_article():
    """保存文章内容"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        filename = data.get('filename', '').strip()
        content = data.get('content', '')
        
        if not username or not filename:
            return jsonify({
                'success': False,
                'message': '用户名和文件名不能为空'
            })
        
        # 构建文件路径
        file_path = os.path.join('..', 'workplace', username, 'article', filename)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 写入文件内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"💾 为用户 {username} 保存文章: {filename}")
        
        return jsonify({
            'success': True,
            'message': '文章保存成功'
        })
        
    except Exception as e:
        print(f"❌ 保存文章失败: {e}")
        return jsonify({
            'success': False,
            'message': f'保存文章失败: {str(e)}'
        })

@app.route('/api/delete_article', methods=['POST'])
def delete_article():
    """删除文章"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        filename = data.get('filename', '').strip()
        
        if not username or not filename:
            return jsonify({
                'success': False,
                'message': '用户名和文件名不能为空'
            })
        
        # 构建文件路径
        file_path = os.path.join('..', 'workplace', username, 'article', filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': '文章文件不存在'
            })
        
        # 删除文件
        os.remove(file_path)
        
        print(f"🗑️ 为用户 {username} 删除文章: {filename}")
        
        return jsonify({
            'success': True,
            'message': '文章删除成功'
        })
        
    except Exception as e:
        print(f"❌ 删除文章失败: {e}")
        return jsonify({
            'success': False,
            'message': f'删除文章失败: {str(e)}'
        })

@app.route('/api/rename_article', methods=['POST'])
def rename_article():
    """重命名文章"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        old_filename = data.get('old_filename', '').strip()
        new_name = data.get('new_name', '').strip()
        
        if not username or not old_filename or not new_name:
            return jsonify({
                'success': False,
                'message': '参数不能为空'
            })
        
        # 构建路径
        articles_path = os.path.join('..', 'workplace', username, 'article')
        old_file_path = os.path.join(articles_path, old_filename)
        
        if not os.path.exists(old_file_path):
            return jsonify({
                'success': False,
                'message': '原文章文件不存在'
            })
        
        # 生成新文件名
        new_filename = f"{new_name}.html"
        new_file_path = os.path.join(articles_path, new_filename)
        
        # 检查新文件名是否已存在
        counter = 1
        while os.path.exists(new_file_path):
            new_filename = f"{new_name}{counter}.html"
            new_file_path = os.path.join(articles_path, new_filename)
            counter += 1
        
        # 重命名文件
        os.rename(old_file_path, new_file_path)
        
        print(f"✏️ 为用户 {username} 重命名文章: {old_filename} -> {new_filename}")
        
        return jsonify({
            'success': True,
            'new_filename': new_filename,
            'message': '文章重命名成功'
        })
        
    except Exception as e:
        print(f"❌ 重命名文章失败: {e}")
        return jsonify({
            'success': False,
            'message': f'重命名文章失败: {str(e)}'
        })

@app.route('/api/get_shared_assets', methods=['POST'])
def get_shared_assets():
    """获取共享素材库内容"""
    try:
        data = request.json
        asset_type = data.get('type', '').strip()
        
        if not asset_type:
            return jsonify({
                'success': False,
                'message': '素材类型不能为空'
            })
        
        # 构建素材路径
        assets_path = os.path.join('..', 'workplace', 'share', asset_type)
        
        if not os.path.exists(assets_path):
            return jsonify({
                'success': False,
                'message': f'素材目录不存在: {asset_type}'
            })
        
        assets = []
        
        # 特殊处理图标类型
        if asset_type == 'icons':
            # 🔧 修复4: 首先添加根目录的SVG文件
            for item in os.listdir(assets_path):
                if item.endswith('.svg'):
                    file_path = os.path.join(assets_path, item)
                    if os.path.isfile(file_path):
                        assets.append({
                            'name': item,
                            'type': 'file',
                            'size': os.path.getsize(file_path),
                            'path': f'/workplace/share/icons/{item}'
                        })
            
            # 遍历图标主题目录
            for theme_dir in os.listdir(assets_path):
                theme_path = os.path.join(assets_path, theme_dir)
                if os.path.isdir(theme_path):
                    # 查看breeze主题的应用图标
                    if theme_dir == 'breeze':
                        apps_path = os.path.join(theme_path, 'apps', '48')  # 48px图标
                        if os.path.exists(apps_path):
                            for icon_file in os.listdir(apps_path):
                                if icon_file.endswith('.svg'):
                                    file_path = os.path.join(apps_path, icon_file)
                                    assets.append({
                                        'name': icon_file,
                                        'type': 'file',
                                        'size': os.path.getsize(file_path),
                                        'path': f'/workplace/share/icons/breeze/apps/48/{icon_file}'
                                    })
                    
                    # 🔧 其他主题目录的处理（可选）
                    elif theme_dir in ['breeze-dark', 'hicolor', 'Adwaita']:
                        # 可以添加其他主题的图标处理
                        apps_path = os.path.join(theme_path, 'apps', '48')
                        if os.path.exists(apps_path):
                            for icon_file in os.listdir(apps_path):
                                if icon_file.endswith('.svg') or icon_file.endswith('.png'):
                                    file_path = os.path.join(apps_path, icon_file)
                                    if os.path.isfile(file_path):
                                        assets.append({
                                            'name': f"{theme_dir}/{icon_file}",
                                            'type': 'file',
                                            'size': os.path.getsize(file_path),
                                            'path': f'/workplace/share/icons/{theme_dir}/apps/48/{icon_file}'
                                        })
        else:
            # 普通素材处理（背景图片等）
            for item in os.listdir(assets_path):
                item_path = os.path.join(assets_path, item)
                
                if os.path.isfile(item_path):
                    # 文件
                    file_size = os.path.getsize(item_path)
                    assets.append({
                        'name': item,
                        'type': 'file',
                        'size': file_size,
                        'path': f'/workplace/share/{asset_type}/{item}'
                    })
                elif os.path.isdir(item_path):
                    # 目录
                    assets.append({
                        'name': item,
                        'type': 'directory',
                        'path': f'/workplace/share/{asset_type}/{item}'
                    })
        
        print(f"🎨 获取 {asset_type} 素材: {len(assets)} 项")
        
        return jsonify({
            'success': True,
            'assets': assets
        })
        
    except Exception as e:
        print(f"❌ 获取共享素材失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取共享素材失败: {str(e)}'
        })

# 🖼️ 我的图片功能相关API

@app.route('/api/get_my_pictures', methods=['POST'])
def get_my_pictures():
    """获取用户的图片列表"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        
        if not username:
            return jsonify({
                'success': False,
                'message': '用户名不能为空'
            })
        
        # 构建用户图片目录路径
        pics_path = os.path.join('..', 'workplace', username, 'pics')
        
        pictures = []
        
        if os.path.exists(pics_path):
            for filename in os.listdir(pics_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(pics_path, filename)
                    if os.path.isfile(file_path):
                        # 获取文件信息
                        file_size = os.path.getsize(file_path)
                        mtime = os.path.getmtime(file_path)
                        
                        pictures.append({
                            'name': filename,
                            'size': file_size,
                            'modified': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                        })
        
        # 按修改时间排序，最新的在前
        pictures.sort(key=lambda x: x['modified'], reverse=True)
        
        print(f"📷 用户 {username} 的图片列表: {len(pictures)} 张图片")
        
        return jsonify({
            'success': True,
            'pictures': pictures
        })
        
    except Exception as e:
        print(f"❌ 获取用户图片失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取用户图片失败: {str(e)}'
        })

@app.route('/api/upload_my_pictures', methods=['POST'])
def upload_my_pictures():
    """上传用户图片"""
    try:
        username = request.form.get('username', '').strip().lower()
        
        if not username:
            return jsonify({
                'success': False,
                'message': '用户名不能为空'
            })
        
        # 检查是否有文件上传
        if 'pictures' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            })
        
        files = request.files.getlist('pictures')
        if not files or len(files) == 0:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            })
        
        # 构建用户图片目录路径
        pics_path = os.path.join('..', 'workplace', username, 'pics')
        
        # 确保目录存在
        os.makedirs(pics_path, exist_ok=True)
        
        uploaded_count = 0
        skipped_count = 0
        errors = []
        
        for file in files:
            if file.filename == '':
                continue
                
            # 验证文件类型
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                errors.append(f'{file.filename}: 不支持的文件格式')
                continue
            
            # 生成安全的文件名
            filename = file.filename
            file_path = os.path.join(pics_path, filename)
            
            # 检查文件是否已存在
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(file_path):
                if counter == 1:
                    # 第一次重复，检查是否是完全相同的文件
                    try:
                        # 读取现有文件的一部分进行比较
                        with open(file_path, 'rb') as existing_file:
                            existing_data = existing_file.read(1024)  # 读取前1KB
                        
                        file.seek(0)
                        new_data = file.read(1024)
                        file.seek(0)  # 重置文件指针
                        
                        if existing_data == new_data:
                            print(f"⚠️  跳过重复文件: {filename}")
                            skipped_count += 1
                            break
                    except:
                        pass  # 如果比较失败，继续处理
                
                # 生成新的文件名
                filename = f"{base_name}_{counter}{ext}"
                file_path = os.path.join(pics_path, filename)
                counter += 1
            else:
                # 保存文件
                try:
                    file.save(file_path)
                    uploaded_count += 1
                    print(f"📷 用户 {username} 上传图片: {filename}")
                except Exception as e:
                    errors.append(f'{file.filename}: 保存失败 - {str(e)}')
        
        # 返回结果
        result_message = f'处理完成'
        if uploaded_count > 0:
            result_message += f'，成功上传 {uploaded_count} 张图片'
        if skipped_count > 0:
            result_message += f'，跳过 {skipped_count} 张重复图片'
        if errors:
            result_message += f'，{len(errors)} 个错误'
        
        return jsonify({
            'success': True,
            'message': result_message,
            'uploaded_count': uploaded_count,
            'skipped_count': skipped_count,
            'errors': errors
        })
        
    except Exception as e:
        print(f"❌ 上传用户图片失败: {e}")
        return jsonify({
            'success': False,
            'message': f'上传失败: {str(e)}'
        })

@app.route('/api/get_user_picture/<username>/<filename>')
def get_user_picture(username, filename):
    """获取用户图片文件"""
    try:
        username = username.strip().lower()
        
        # 构建文件路径
        pics_path = os.path.join('..', 'workplace', username, 'pics')
        file_path = os.path.join(pics_path, filename)
        
        if not os.path.exists(file_path):
            print(f"❌ 用户图片不存在: {file_path}")
            return "Picture not found", 404
        
        print(f"📷 提供用户图片: {username}/{filename}")
        return send_from_directory(pics_path, filename)
        
    except Exception as e:
        print(f"❌ 获取用户图片失败: {e}")
        return f"Error serving picture: {str(e)}", 500

@app.route('/api/delete_my_picture', methods=['POST'])
def delete_my_picture():
    """删除用户图片"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        filename = data.get('filename', '').strip()
        
        if not username or not filename:
            return jsonify({
                'success': False,
                'message': '用户名和文件名不能为空'
            })
        
        # 构建文件路径
        file_path = os.path.join('..', 'workplace', username, 'pics', filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': '图片文件不存在'
            })
        
        # 删除文件
        os.remove(file_path)
        
        print(f"🗑️ 用户 {username} 删除图片: {filename}")
        
        return jsonify({
            'success': True,
            'message': '图片删除成功'
        })
        
    except Exception as e:
        print(f"❌ 删除用户图片失败: {e}")
        return jsonify({
            'success': False,
            'message': f'删除图片失败: {str(e)}'
        })

def read_redirect_csv():
    """读取redirect.csv文件，获取地址到别名的映射"""
    redirects = {}
    try:
        redirect_csv_path = os.path.join('..', 'redirect.csv')
        with open(redirect_csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                address = row['address'].strip()
                alias = row['alias'].strip()
                redirects[address] = alias
                print(f"读取重定向: {address} -> {alias}")
    except FileNotFoundError:
        print("❌ redirect.csv文件不存在")
        # 创建一个空的CSV文件
        try:
            redirect_csv_path = os.path.join('..', 'redirect.csv')
            with open(redirect_csv_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['address', 'alias'])
            print("✅ 已创建空的redirect.csv文件")
        except Exception as create_error:
            print(f"❌ 创建redirect.csv失败: {create_error}")
    except Exception as e:
        print(f"❌ 读取redirect.csv失败: {e}")
    return redirects

def parse_visitor_type(alias):
    """解析别名中的访客类型，例如从 'WHU_PAGE&user=student' 中提取 'student'"""
    if '&user=' in alias:
        match = re.search(r'&user=([^&]+)', alias)
        if match:
            return match.group(1)
    return None

def get_clean_alias(alias):
    """获取去掉参数的干净别名，例如从 'WHU_PAGE&user=student' 得到 'WHU_PAGE'"""
    if '&' in alias:
        return alias.split('&')[0]
    return alias

def record_visitor_access(article_dir, visitor_type):
    """记录访客访问统计到accrecord.csv"""
    if not visitor_type:
        return
    
    # 处理相对路径
    if article_dir.startswith('./'):
        full_dir = os.path.join('..', article_dir[2:])
    else:
        full_dir = article_dir
    
    accrecord_path = os.path.join(full_dir, 'accrecord.csv')
    print(f"📊 记录访客访问: {visitor_type} -> {accrecord_path}")
    
    # 读取现有记录
    records = {}
    if os.path.exists(accrecord_path):
        try:
            with open(accrecord_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    identity = row['identity'].strip()
                    viewtime = int(row['viewtime'])
                    records[identity] = viewtime
        except Exception as e:
            print(f"❌ 读取accrecord.csv失败: {e}")
    
    # 更新访问记录
    if visitor_type in records:
        records[visitor_type] += 1
    else:
        records[visitor_type] = 1
    
    # 写入更新后的记录
    try:
        # 确保目录存在
        os.makedirs(full_dir, exist_ok=True)
        
        with open(accrecord_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['identity', 'viewtime'])
            for identity, viewtime in records.items():
                writer.writerow([identity, viewtime])
        print(f"✅ 更新访客记录: {visitor_type} -> {records[visitor_type]}")
    except Exception as e:
        print(f"❌ 写入accrecord.csv失败: {e}")

def get_article_content(article_path):
    """读取文章内容并返回只读版本"""
    try:
        # 处理相对路径，确保从正确的位置读取文件
        if article_path.startswith('./'):
            # 从login目录的角度，需要去掉一个层级
            full_path = os.path.join('..', article_path[2:])
        else:
            full_path = article_path
            
        print(f"🔍 尝试读取文章: {article_path} -> {full_path}")
        print(f"📂 当前工作目录: {os.getcwd()}")
        print(f"✅ 文件是否存在: {os.path.exists(full_path)}")
        
        with open(full_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"❌ 文件未找到: {full_path}")
        return None
    except Exception as e:
        print(f"❌ 读取文章失败: {e}")
        return None

def get_visitor_stats(username):
    """获取指定用户的访客统计信息"""
    article_dir = f"../workplace/{username}/article"
    accrecord_path = os.path.join(article_dir, 'accrecord.csv')
    
    stats = []
    if os.path.exists(accrecord_path):
        try:
            with open(accrecord_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    stats.append({
                        'identity': row['identity'].strip(),
                        'viewtime': int(row['viewtime'])
                    })
        except Exception as e:
            print(f"❌ 读取访客统计失败: {e}")
    
    # 按访问次数降序排序
    stats.sort(key=lambda x: x['viewtime'], reverse=True)
    return stats

# 🔑 修改密码相关API

@app.route('/api/send_change_password_code', methods=['POST'])
def send_change_password_code():
    """发送修改密码验证码"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        
        if not username:
            return jsonify({'success': False, 'message': '用户名不能为空'})
        
        # 检查用户是否存在
        users = read_users_csv_with_maxarticle()
        if username not in users:
            return jsonify({'success': False, 'message': '用户不存在'})
        
        # 生成验证码
        code = generate_verification_code()
        timestamp = time.time()
        
        # 存储验证码（用于修改密码）
        change_password_codes[username] = {
            'code': code,
            'timestamp': timestamp,
            'attempts': 0
        }
        
        # 发送邮件
        if DEVELOPMENT_MODE:
            print(f"🔧 开发模式：修改密码验证码为 {code}")
            return jsonify({'success': True, 'message': f'验证码已生成：{code}'})
        else:
            send_verification_email(username, code)
            return jsonify({'success': True, 'message': '验证码已发送到您的邮箱'})
            
    except Exception as e:
        print(f"❌ 发送修改密码验证码失败: {e}")
        return jsonify({'success': False, 'message': f'发送失败: {str(e)}'})

@app.route('/api/verify_change_password_code', methods=['POST'])
def verify_change_password_code():
    """验证修改密码验证码"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        input_code = data.get('code', '').strip()
        
        if not username or not input_code:
            return jsonify({'success': False, 'message': '参数不完整'})
        
        if username not in change_password_codes:
            return jsonify({'success': False, 'message': '验证码已过期或不存在'})
        
        stored_data = change_password_codes[username]
        current_time = time.time()
        
        # 检查验证码是否过期（10分钟）
        if current_time - stored_data['timestamp'] > 600:
            del change_password_codes[username]
            return jsonify({'success': False, 'message': '验证码已过期'})
        
        # 检查错误次数
        if stored_data['attempts'] >= 5:
            del change_password_codes[username]
            return jsonify({'success': False, 'message': '验证码错误次数过多，请重新获取'})
        
        # 验证码匹配检查
        if stored_data['code'] != input_code:
            change_password_codes[username]['attempts'] += 1
            return jsonify({'success': False, 'message': f'验证码错误，还可尝试{5-stored_data["attempts"]}次'})
        
        # 验证成功，保留验证码用于后续密码更新验证
        print(f"✅ 用户 {username} 修改密码验证码验证成功")
        return jsonify({'success': True, 'message': '验证成功'})
        
    except Exception as e:
        print(f"❌ 验证修改密码验证码失败: {e}")
        return jsonify({'success': False, 'message': f'验证失败: {str(e)}'})

@app.route('/api/change_user_password', methods=['POST'])
def change_user_password():
    """修改用户密码"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        new_password = data.get('password', '')  # 前端加密后的密文
        
        if not username or not new_password:
            return jsonify({'success': False, 'message': '参数不完整'})
        
        # 检查验证码是否已验证（验证成功后验证码仍在字典中）
        if username not in change_password_codes:
            return jsonify({'success': False, 'message': '请先完成验证码验证'})
        
        # 更新密码
        users = read_users_csv_with_maxarticle()
        if username not in users:
            return jsonify({'success': False, 'message': '用户不存在'})
        
        users[username]['password'] = new_password
        
        if not write_users_csv_with_maxarticle(users):
            return jsonify({'success': False, 'message': '密码更新失败'})
        
        # 清除验证码
        del change_password_codes[username]
        
        print(f"✅ 用户 {username} 密码修改成功")
        return jsonify({'success': True, 'message': '密码修改成功'})
        
    except Exception as e:
        print(f"❌ 修改用户密码失败: {e}")
        return jsonify({'success': False, 'message': f'修改失败: {str(e)}'})

# 🌐 访客通道管理API

@app.route('/api/get_visitor_links', methods=['POST'])
def get_visitor_links():
    """获取用户的访客链接列表"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        
        if not username:
            return jsonify({'success': False, 'message': '用户名不能为空'})
        
        # 读取redirect.csv
        redirect_data = read_redirect_csv()
        
        # 筛选出属于当前用户的链接 - 修复路径前缀
        user_links = []
        user_path_prefix = f'../workplace/{username}/'
        
        for address, alias in redirect_data.items():
            if address.startswith(user_path_prefix):
                # 提取文章名
                article_file = os.path.basename(address)
                article_name = article_file.replace('.html', '')
                
                user_links.append({
                    'address': address,
                    'alias': alias,
                    'article_name': article_name
                })
        
        print(f"📊 用户 {username} 有 {len(user_links)} 个访客链接")
        return jsonify({
            'success': True,
            'links': user_links
        })
        
    except Exception as e:
        print(f"❌ 获取访客链接失败: {e}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/add_visitor_link', methods=['POST'])
def add_visitor_link():
    """添加访客链接"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        article_file = data.get('article_file', '').strip()
        alias = data.get('alias', '').strip()
        
        if not username or not article_file or not alias:
            return jsonify({'success': False, 'message': '参数不完整'})
        
        # 构建文章路径 - 修复路径问题，使用../workplace/而不是./workplace/
        article_path = f'../workplace/{username}/article/{article_file}'
        
        # 检查文章是否存在
        full_article_path = os.path.join('..', 'workplace', username, 'article', article_file)
        if not os.path.exists(full_article_path):
            return jsonify({'success': False, 'message': '文章不存在'})
        
        # 读取现有的redirect数据
        redirect_data = read_redirect_csv()
        
        # 检查别名是否已存在
        if alias in redirect_data.values():
            return jsonify({'success': False, 'message': '别名已存在'})
        
        # 添加新记录
        redirect_data[article_path] = alias
        
        # 写回CSV文件
        redirect_csv_path = os.path.join('..', 'redirect.csv')
        with open(redirect_csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['address', 'alias'])
            for address, alias_name in redirect_data.items():
                writer.writerow([address, alias_name])
        
        print(f"✅ 用户 {username} 添加访客链接成功: {alias} -> {article_path}")
        return jsonify({'success': True, 'message': '访客链接添加成功'})
        
    except Exception as e:
        print(f"❌ 添加访客链接失败: {e}")
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'})

@app.route('/api/remove_visitor_link', methods=['POST'])
def remove_visitor_link():
    """删除访客链接"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        alias = data.get('alias', '').strip()
        
        if not username or not alias:
            return jsonify({'success': False, 'message': '参数不完整'})
        
        # 读取现有的redirect数据
        redirect_data = read_redirect_csv()
        
        # 查找要删除的记录 - 修复路径前缀
        address_to_remove = None
        user_path_prefix = f'../workplace/{username}/'
        
        for address, alias_name in redirect_data.items():
            if alias_name == alias and address.startswith(user_path_prefix):
                address_to_remove = address
                break
        
        if not address_to_remove:
            return jsonify({'success': False, 'message': '访客链接不存在或无权限删除'})
        
        # 删除记录
        del redirect_data[address_to_remove]
        
        # 写回CSV文件
        redirect_csv_path = os.path.join('..', 'redirect.csv')
        with open(redirect_csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['address', 'alias'])
            for address, alias_name in redirect_data.items():
                writer.writerow([address, alias_name])
        
        print(f"✅ 用户 {username} 删除访客链接成功: {alias}")
        return jsonify({'success': True, 'message': '访客链接删除成功'})
        
    except Exception as e:
        print(f"❌ 删除访客链接失败: {e}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})

# 添加修改密码验证码存储
change_password_codes = {}

# 📤 发布内容管理API

def read_publications_csv():
    """读取publications.csv文件"""
    publications_csv_path = os.path.join('..', 'publications.csv')
    publications = []
    
    if os.path.exists(publications_csv_path):
        try:
            with open(publications_csv_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    publications.append(row)
        except Exception as e:
            print(f"❌ 读取publications.csv失败: {e}")
    
    return publications

def write_publications_csv(publications):
    """写入publications.csv文件"""
    publications_csv_path = os.path.join('..', 'publications.csv')
    try:
        with open(publications_csv_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['id', 'username', 'article_file', 'type', 'title', 'description', 'author', 'cover_image', 'publish_date']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(publications)
        return True
    except Exception as e:
        print(f"❌ 写入publications.csv失败: {e}")
        return False

@app.route('/api/get_published_content', methods=['POST'])
def get_published_content():
    """获取用户的已发布内容列表"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        
        if not username:
            return jsonify({'success': False, 'message': '用户名不能为空'})
        
        # 读取publications.csv
        publications = read_publications_csv()
        
        # 筛选出属于当前用户的发布内容
        user_publications = [pub for pub in publications if pub.get('username', '').lower() == username]
        
        print(f"📊 用户 {username} 有 {len(user_publications)} 个已发布内容")
        return jsonify({
            'success': True,
            'publications': user_publications
        })
        
    except Exception as e:
        print(f"❌ 获取已发布内容失败: {e}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

@app.route('/api/publish_content', methods=['POST'])
def publish_content():
    """发布内容到主页"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        article_file = data.get('article_file', '').strip()
        content_type = data.get('type', '').strip()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        author = data.get('author', '').strip()
        cover_image = data.get('cover_image', '').strip()
        
        # 验证参数
        if not all([username, article_file, content_type, title, description, author]):
            return jsonify({'success': False, 'message': '参数不完整'})
        
        # 检查文章是否存在
        article_path = os.path.join('..', 'workplace', username, 'article', article_file)
        if not os.path.exists(article_path):
            return jsonify({'success': False, 'message': '文章不存在'})
        
        # 读取现有发布内容
        publications = read_publications_csv()
        
        # 检查是否已经发布过该文章
        for pub in publications:
            if pub.get('username', '').lower() == username and pub.get('article_file') == article_file:
                return jsonify({'success': False, 'message': '该文章已经发布过了'})
        
        # 生成唯一ID
        import time
        publication_id = f"{username}_{int(time.time() * 1000)}"
        
        # 获取当前日期
        from datetime import datetime
        publish_date = datetime.now().strftime('%Y-%m-%d')
        
        # 添加新发布记录
        new_publication = {
            'id': publication_id,
            'username': username,
            'article_file': article_file,
            'type': content_type,
            'title': title,
            'description': description,
            'author': author,
            'cover_image': cover_image,
            'publish_date': publish_date
        }
        
        publications.append(new_publication)
        
        # 写回CSV文件
        if write_publications_csv(publications):
            print(f"✅ 用户 {username} 发布内容成功: {title}")
            return jsonify({'success': True, 'message': '内容发布成功'})
        else:
            return jsonify({'success': False, 'message': '写入文件失败'})
        
    except Exception as e:
        print(f"❌ 发布内容失败: {e}")
        return jsonify({'success': False, 'message': f'发布失败: {str(e)}'})

@app.route('/api/unpublish_content', methods=['POST'])
def unpublish_content():
    """取消发布内容"""
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        publication_id = data.get('publication_id', '').strip()
        
        if not username or not publication_id:
            return jsonify({'success': False, 'message': '参数不完整'})
        
        # 读取现有发布内容
        publications = read_publications_csv()
        
        # 找到要删除的记录
        publication_to_remove = None
        for pub in publications:
            if pub.get('id') == publication_id and pub.get('username', '').lower() == username:
                publication_to_remove = pub
                break
        
        if not publication_to_remove:
            return jsonify({'success': False, 'message': '发布内容不存在或无权限删除'})
        
        # 删除记录
        publications.remove(publication_to_remove)
        
        # 写回CSV文件
        if write_publications_csv(publications):
            print(f"✅ 用户 {username} 取消发布成功: {publication_id}")
            return jsonify({'success': True, 'message': '已取消发布'})
        else:
            return jsonify({'success': False, 'message': '写入文件失败'})
        
    except Exception as e:
        print(f"❌ 取消发布失败: {e}")
        return jsonify({'success': False, 'message': f'取消发布失败: {str(e)}'})

@app.route('/api/get_all_publications', methods=['GET'])
def get_all_publications():
    """获取所有已发布内容（用于主页显示）"""
    try:
        # 读取所有发布内容
        publications = read_publications_csv()
        
        # 转换文章路径为可访问的URL
        for pub in publications:
            username = pub.get('username', '')
            article_file = pub.get('article_file', '')
            pub['article_url'] = f"/link/{username}/{article_file}?from=home.html"
        
        return jsonify({
            'success': True,
            'publications': publications
        })
        
    except Exception as e:
        print(f"❌ 获取所有发布内容失败: {e}")
        return jsonify({'success': False, 'message': f'获取失败: {str(e)}'})

if __name__ == '__main__':
    print("🚀 HTML文章编辑器服务器启动...")
    print("📊 服务器配置:")
    print(f"   - 端口: 5000")
    print(f"   - 调试模式: False")
    print(f"   - SMTP服务器: {SMTP_SERVER}")
    print(f"   - 工作目录: {os.getcwd()}")
    
    # 检查关键目录是否存在
    workplace_path = os.path.join('..', 'workplace')
    if os.path.exists(workplace_path):
        print(f"✅ 工作目录存在: {workplace_path}")
    else:
        print(f"❌ 工作目录不存在: {workplace_path}")
    
    app.run(host='localhost', port=5000, debug=False) 