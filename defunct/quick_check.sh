#!/bin/bash
# ===== 邮件认证系统快速检查 =====
# 快速验证系统基本功能是否正常

echo "⚡ 邮件认证系统快速检查"
echo "========================"

# 结果计数
SUCCESS=0
FAILED=0

# 检查函数
check_result() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
        ((SUCCESS++))
    else
        echo "❌ $2"
        ((FAILED++))
    fi
}

# 1. 环境检查
echo -e "\n🔍 环境检查..."
python3 --version >/dev/null 2>&1
check_result $? "Python3环境"

python3 -c "import flask, flask_cors" >/dev/null 2>&1
check_result $? "Flask依赖"

python3 -c "import smtplib, poplib, email" >/dev/null 2>&1
check_result $? "邮件库依赖"

# 2. 文件检查
echo -e "\n📁 文件结构检查..."
[ -f "client/login/email_client.py" ]
check_result $? "客户端邮件模块"

[ -f "client/login/server.py" ]
check_result $? "客户端Web服务器"

[ -f "cloudserver/login/email_server.py" ]
check_result $? "服务器端邮件模块"

[ -f "cloudserver/login/server.py" ]
check_result $? "服务器端Web服务器"

[ -f "cloudserver/login/crypto_utils.py" ]
check_result $? "密码加密模块"

# 3. 配置检查
echo -e "\n⚙️ 配置检查..."
python3 -c "
import sys
sys.path.append('client/login')
from email_client import CLIENT_EMAIL, SERVER_EMAIL
assert '@' in CLIENT_EMAIL and '@' in SERVER_EMAIL
" >/dev/null 2>&1
check_result $? "客户端邮件配置"

python3 -c "
import sys
sys.path.append('cloudserver/login')
from email_server import SERVER_EMAIL, CLIENT_EMAIL
assert '@' in SERVER_EMAIL and '@' in CLIENT_EMAIL
" >/dev/null 2>&1
check_result $? "服务器端邮件配置"

# 4. 功能检查
echo -e "\n🔧 功能检查..."
python3 -c "
import sys
sys.path.append('cloudserver/login')
from crypto_utils import convert_plaintext_to_encrypted
result = convert_plaintext_to_encrypted('test')
assert len(result) == 16
" >/dev/null 2>&1
check_result $? "密码加密功能"

timeout 5s python3 -c "
import sys
sys.path.append('client/login')
from email_client import EmailClient
client = EmailClient()
" >/dev/null 2>&1
check_result $? "客户端邮件模块初始化"

timeout 5s python3 -c "
import sys
sys.path.append('cloudserver/login')
from email_server import EmailServer
server = EmailServer()
" >/dev/null 2>&1
check_result $? "服务器端邮件模块初始化"

# 5. 网络检查（可选）
echo -e "\n🌐 网络检查..."
ping -c 1 smtp.163.com >/dev/null 2>&1
check_result $? "SMTP服务器连通性"

ping -c 1 pop.163.com >/dev/null 2>&1
check_result $? "POP3服务器连通性"

# 6. 总结
echo -e "\n📊 验证总结"
echo "========================"
echo "成功项目: $SUCCESS"
echo "失败项目: $FAILED"
echo "总计项目: $((SUCCESS + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo -e "\n🎉 系统验证通过！可以开始使用邮件认证功能。"
    echo ""
    echo "📝 下一步操作："
    echo "1. 启动服务器端: cd cloudserver/login && python3 server.py"
    echo "2. 启动客户端: cd client/login && python3 server.py"
    echo "3. 浏览器访问: http://localhost:5000/"
    exit 0
else
    echo -e "\n⚠️  发现 $FAILED 个问题，建议运行详细测试："
    echo "   ./test_email_auth_system.sh"
    echo ""
    echo "🔧 常见问题解决："
    echo "   - 缺少依赖: pip3 install flask flask-cors"
    echo "   - 网络问题: 检查防火墙和网络连接"
    echo "   - 邮箱配置: 确认163邮箱授权码正确"
    exit 1
fi 