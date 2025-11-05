#!/bin/bash
# ===== 邮件通信专项测试脚本 =====
# 用于测试客户端-服务器邮件通信的完整功能

echo "📧 邮件通信专项测试"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ===== 1. 邮件配置验证 =====
echo -e "\n${BLUE}📋 1. 邮件配置验证${NC}"
echo "----------------------------------------"

echo "🔍 检查客户端邮件配置..."
python3 << 'EOF'
import sys
sys.path.append('client/login')
try:
    from email_client import CLIENT_EMAIL, CLIENT_PASSWORD, SERVER_EMAIL, SMTP_SERVER, POP3_SERVER
    print(f"✅ 客户端邮箱: {CLIENT_EMAIL}")
    print(f"✅ 服务器邮箱: {SERVER_EMAIL}")
    print(f"✅ SMTP服务器: {SMTP_SERVER}")
    print(f"✅ POP3服务器: {POP3_SERVER}")
    print(f"✅ 授权码长度: {len(CLIENT_PASSWORD)}")
except Exception as e:
    print(f"❌ 客户端配置错误: {e}")
    exit(1)
EOF

echo -e "\n🔍 检查服务器端邮件配置..."
python3 << 'EOF'
import sys
sys.path.append('cloudserver/login')
try:
    from email_server import SERVER_EMAIL, SERVER_PASSWORD, CLIENT_EMAIL, SMTP_SERVER, POP3_SERVER
    print(f"✅ 服务器邮箱: {SERVER_EMAIL}")
    print(f"✅ 客户端邮箱: {CLIENT_EMAIL}")
    print(f"✅ SMTP服务器: {SMTP_SERVER}")
    print(f"✅ POP3服务器: {POP3_SERVER}")
    print(f"✅ 授权码长度: {len(SERVER_PASSWORD)}")
except Exception as e:
    print(f"❌ 服务器端配置错误: {e}")
    exit(1)
EOF

# ===== 2. 基础连接测试 =====
echo -e "\n${BLUE}🔌 2. 基础连接测试${NC}"
echo "----------------------------------------"

echo "📨 测试SMTP连接（客户端发送）..."
python3 << 'EOF'
import sys
sys.path.append('client/login')
import smtplib
from email_client import CLIENT_EMAIL, CLIENT_PASSWORD, SMTP_SERVER, SMTP_PORT

try:
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        server.login(CLIENT_EMAIL, CLIENT_PASSWORD)
        print("✅ 客户端SMTP连接成功")
except Exception as e:
    print(f"❌ 客户端SMTP连接失败: {e}")
    exit(1)
EOF

echo -e "\n📨 测试SMTP连接（服务器发送）..."
python3 << 'EOF'
import sys
sys.path.append('cloudserver/login')
import smtplib
from email_server import SERVER_EMAIL, SERVER_PASSWORD, SMTP_SERVER, SMTP_PORT

try:
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        server.login(SERVER_EMAIL, SERVER_PASSWORD)
        print("✅ 服务器端SMTP连接成功")
except Exception as e:
    print(f"❌ 服务器端SMTP连接失败: {e}")
    exit(1)
EOF

echo -e "\n📬 测试POP3连接（客户端接收）..."
python3 << 'EOF'
import sys
sys.path.append('client/login')
import poplib
from email_client import CLIENT_EMAIL, CLIENT_PASSWORD, POP3_SERVER, POP3_PORT

try:
    with poplib.POP3_SSL(POP3_SERVER, POP3_PORT, timeout=10) as pop_conn:
        pop_conn.user(CLIENT_EMAIL)
        pop_conn.pass_(CLIENT_PASSWORD)
        print("✅ 客户端POP3连接成功")
except Exception as e:
    print(f"❌ 客户端POP3连接失败: {e}")
    exit(1)
EOF

echo -e "\n📬 测试POP3连接（服务器接收）..."
python3 << 'EOF'
import sys
sys.path.append('cloudserver/login')
import poplib
from email_server import SERVER_EMAIL, SERVER_PASSWORD, POP3_SERVER, POP3_PORT

try:
    with poplib.POP3_SSL(POP3_SERVER, POP3_PORT, timeout=10) as pop_conn:
        pop_conn.user(SERVER_EMAIL)
        pop_conn.pass_(SERVER_PASSWORD)
        print("✅ 服务器端POP3连接成功")
except Exception as e:
    print(f"❌ 服务器端POP3连接失败: {e}")
    exit(1)
EOF

# ===== 3. 邮件发送测试 =====
echo -e "\n${BLUE}📤 3. 邮件发送测试${NC}"
echo "----------------------------------------"

echo "📧 测试客户端发送测试邮件..."
python3 << 'EOF'
import sys
sys.path.append('client/login')
from email_client import EmailClient
import time

client = EmailClient()

# 发送测试登录请求
success = client.send_login_request("test_user", "test_encrypted_password")
if success:
    print("✅ 测试登录请求发送成功")
else:
    print("❌ 测试登录请求发送失败")
    exit(1)

time.sleep(2)

# 发送测试注册请求
success = client.send_register_request("test_new_user", "user@example.com")
if success:
    print("✅ 测试注册请求发送成功")
else:
    print("❌ 测试注册请求发送失败")
EOF

# ===== 4. 邮件接收测试 =====
echo -e "\n${BLUE}📥 4. 邮件接收测试${NC}"
echo "----------------------------------------"

echo "📨 启动服务器端邮件监听（30秒）..."
cd cloudserver/login

# 在后台运行邮件服务器30秒
timeout 30s python3 << 'EOF' &
from email_server import EmailServer
import time

server = EmailServer()
server.start_listening()

print("📧 邮件服务器开始监听...")
try:
    time.sleep(25)  # 运行25秒
    print("📧 邮件服务器监听结束")
except KeyboardInterrupt:
    print("📧 邮件服务器被手动停止")
finally:
    server.stop_listening()
EOF

SERVER_PID=$!
sleep 5

echo "📨 启动客户端邮件监听（30秒）..."
cd ../../client/login

timeout 30s python3 << 'EOF' &
from email_client import EmailClient
import time

client = EmailClient()
client.start_reply_listener()

print("📧 客户端邮件监听开始...")
try:
    time.sleep(25)  # 运行25秒
    print("📧 客户端邮件监听结束")
except KeyboardInterrupt:
    print("📧 客户端邮件监听被手动停止")
finally:
    client.stop_reply_listener()
EOF

CLIENT_PID=$!
sleep 5

echo "⏰ 等待邮件处理完成（20秒）..."
sleep 20

# 停止后台进程
kill $SERVER_PID 2>/dev/null
kill $CLIENT_PID 2>/dev/null

cd ../..

# ===== 5. 完整流程测试 =====
echo -e "\n${BLUE}🔄 5. 完整流程测试${NC}"
echo "----------------------------------------"

echo "🚀 启动完整邮件通信测试..."

# 同时启动服务器和客户端进行完整测试
echo "📧 启动服务器端邮件服务..."
cd cloudserver/login
python3 email_server.py &
SERVER_EMAIL_PID=$!
sleep 3

echo "📧 启动客户端邮件服务..."
cd ../../client/login
python3 email_client.py &
CLIENT_EMAIL_PID=$!
sleep 3

echo "⏰ 运行20秒完整通信测试..."
sleep 20

echo "🛑 停止邮件服务..."
kill $SERVER_EMAIL_PID 2>/dev/null
kill $CLIENT_EMAIL_PID 2>/dev/null

cd ../..

# ===== 6. API集成测试 =====
echo -e "\n${BLUE}🔌 6. API集成测试${NC}"
echo "----------------------------------------"

echo "🌐 启动客户端Web服务器进行API测试..."
cd client/login
python3 server.py &
WEB_PID=$!
sleep 8

echo "📧 测试邮件API端点..."

# 测试邮件客户端状态
echo "🔍 检查邮件客户端状态..."
response=$(curl -s -X POST -H "Content-Type: application/json" -d '{}' http://localhost:5000/api/check_email_client)
echo "响应: $response"

if echo "$response" | grep -q "available"; then
    echo -e "${GREEN}✅${NC} 邮件客户端状态API正常"
else
    echo -e "${RED}❌${NC} 邮件客户端状态API异常"
fi

# 测试邮件登录请求
echo -e "\n🔒 测试邮件登录请求API..."
response=$(curl -s -X POST -H "Content-Type: application/json" -d '{"username":"test","encrypted_password":"testpass"}' http://localhost:5000/api/send_email_login)
echo "响应: $response"

if echo "$response" | grep -q "success"; then
    echo -e "${GREEN}✅${NC} 邮件登录请求API正常"
else
    echo -e "${RED}❌${NC} 邮件登录请求API异常"
fi

# 停止Web服务器
kill $WEB_PID 2>/dev/null
cd ../..

# ===== 测试总结 =====
echo -e "\n${BLUE}📊 邮件通信测试总结${NC}"
echo "=============================================="
echo -e "${GREEN}✅ 完成项目:${NC}"
echo "  - 邮件配置验证"
echo "  - SMTP/POP3连接测试"
echo "  - 邮件发送功能测试"
echo "  - 邮件接收监听测试"
echo "  - 完整通信流程测试"
echo "  - API集成测试"
echo ""
echo -e "${YELLOW}💡 注意事项:${NC}"
echo "  1. 确保邮箱授权码正确且有效"
echo "  2. 网络连接稳定，防火墙允许SMTP/POP3"
echo "  3. 邮件服务商（163邮箱）服务正常"
echo "  4. 如果测试失败，检查邮箱设置和网络"
echo ""
echo -e "${BLUE}🔧 手动测试建议:${NC}"
echo "  1. 分别启动服务器端和客户端邮件服务"
echo "  2. 在Web界面中尝试真实的登录/注册操作"
echo "  3. 观察终端日志输出和邮件收发情况"
echo "  4. 检查邮箱中是否收到测试邮件" 