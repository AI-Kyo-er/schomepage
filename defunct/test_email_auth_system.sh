#!/bin/bash
# ===== 邮件认证系统验证脚本 =====
# 用于验证客户端-服务器邮件通信认证系统是否正常工作

echo "🧪 开始验证邮件认证系统..."
echo "=================================================="

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试结果统计
PASS=0
FAIL=0

# 测试函数
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((FAIL++))
    fi
}

# ===== 1. 环境和依赖检查 =====
echo -e "\n${BLUE}📋 1. 环境和依赖检查${NC}"
echo "----------------------------------------"

# 检查Python版本
echo "🐍 检查Python版本..."
python3 --version
test_result $? "Python3可用性检查"

# 检查必要的Python模块
echo "📦 检查Python依赖模块..."
python3 -c "import smtplib, poplib, email, json, threading, queue, flask, flask_cors" 2>/dev/null
test_result $? "Python依赖模块检查"

# ===== 2. 文件结构验证 =====
echo -e "\n${BLUE}📁 2. 文件结构验证${NC}"
echo "----------------------------------------"

# 检查关键文件是否存在
files_to_check=(
    "client/login/email_client.py"
    "client/login/server.py"
    "client/login/auth_email.js"
    "client/login/register_email.js"
    "cloudserver/login/email_server.py"
    "cloudserver/login/server.py"
    "cloudserver/login/crypto_utils.py"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} 存在: $file"
        ((PASS++))
    else
        echo -e "${RED}❌${NC} 缺失: $file"
        ((FAIL++))
    fi
done

# ===== 3. 配置文件检查 =====
echo -e "\n${BLUE}⚙️ 3. 配置文件检查${NC}"
echo "----------------------------------------"

# 检查服务器端users.csv
echo "📄 检查服务器端用户文件..."
if [ -f "cloudserver/users.csv" ]; then
    echo -e "${GREEN}✅${NC} cloudserver/users.csv 存在"
    head -3 cloudserver/users.csv
    ((PASS++))
else
    echo -e "${YELLOW}⚠️${NC} cloudserver/users.csv 不存在，将自动创建"
fi

# 检查重定向配置
if [ -f "redirect.csv" ]; then
    echo -e "${GREEN}✅${NC} redirect.csv 存在"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️${NC} redirect.csv 不存在"
fi

# ===== 4. 邮件配置验证 =====
echo -e "\n${BLUE}📧 4. 邮件配置验证${NC}"
echo "----------------------------------------"

# 检查客户端邮件配置
echo "📨 验证客户端邮件配置..."
python3 -c "
import sys
sys.path.append('client/login')
from email_client import CLIENT_EMAIL, SERVER_EMAIL, SMTP_SERVER, POP3_SERVER
print(f'客户端邮箱: {CLIENT_EMAIL}')
print(f'服务器邮箱: {SERVER_EMAIL}')
print(f'SMTP服务器: {SMTP_SERVER}')
print(f'POP3服务器: {POP3_SERVER}')
" 2>/dev/null
test_result $? "客户端邮件配置读取"

# 检查服务器端邮件配置
echo "📩 验证服务器端邮件配置..."
python3 -c "
import sys
sys.path.append('cloudserver/login')
from email_server import SERVER_EMAIL, CLIENT_EMAIL, SMTP_SERVER, POP3_SERVER
print(f'服务器邮箱: {SERVER_EMAIL}')
print(f'客户端邮箱: {CLIENT_EMAIL}')
print(f'SMTP服务器: {SMTP_SERVER}')
print(f'POP3服务器: {POP3_SERVER}')
" 2>/dev/null
test_result $? "服务器端邮件配置读取"

# ===== 5. 密码加密功能测试 =====
echo -e "\n${BLUE}🔒 5. 密码加密功能测试${NC}"
echo "----------------------------------------"

echo "🔐 测试密码加密算法..."
python3 -c "
import sys
sys.path.append('cloudserver/login')
from crypto_utils import convert_plaintext_to_encrypted, verify_password

# 测试密码加密
test_password = 'test123'
encrypted = convert_plaintext_to_encrypted(test_password)
print(f'原始密码: {test_password}')
print(f'加密结果: {encrypted}')

# 验证加密
is_valid = verify_password(test_password, encrypted)
print(f'验证结果: {is_valid}')

# 测试错误密码
wrong_password = 'wrong123'
is_invalid = verify_password(wrong_password, encrypted)
print(f'错误密码验证: {is_invalid}')

exit(0 if is_valid and not is_invalid else 1)
" 2>/dev/null
test_result $? "密码加密算法测试"

# ===== 6. 单独组件测试 =====
echo -e "\n${BLUE}🔧 6. 单独组件测试${NC}"
echo "----------------------------------------"

# 测试邮件客户端初始化
echo "📧 测试客户端邮件模块初始化..."
timeout 10s python3 -c "
import sys
sys.path.append('client/login')
from email_client import EmailClient
client = EmailClient()
print('客户端邮件模块初始化成功')
" 2>/dev/null
test_result $? "客户端邮件模块初始化"

# 测试邮件服务器初始化
echo "📨 测试服务器端邮件模块初始化..."
timeout 10s python3 -c "
import sys
sys.path.append('cloudserver/login')
from email_server import EmailServer
server = EmailServer()
print('服务器端邮件模块初始化成功')
" 2>/dev/null
test_result $? "服务器端邮件模块初始化"

# ===== 7. Web服务器启动测试 =====
echo -e "\n${BLUE}🌐 7. Web服务器启动测试${NC}"
echo "----------------------------------------"

# 测试客户端服务器启动（短时间）
echo "🖥️ 测试客户端Web服务器启动..."
cd client/login
timeout 15s python3 server.py &
CLIENT_PID=$!
sleep 5

# 检查客户端服务器是否响应
curl -s http://localhost:5000/ >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅${NC} 客户端服务器启动成功 (PID: $CLIENT_PID)"
    ((PASS++))
else
    echo -e "${RED}❌${NC} 客户端服务器启动失败"
    ((FAIL++))
fi

# 停止客户端服务器
kill $CLIENT_PID 2>/dev/null
cd ../..

# 测试服务器端服务器启动（短时间）
echo "🖥️ 测试服务器端Web服务器启动..."
cd cloudserver/login
timeout 15s python3 server.py &
SERVER_PID=$!
sleep 5

# 检查服务器端服务器是否响应
curl -s http://localhost:5000/ >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅${NC} 服务器端服务器启动成功 (PID: $SERVER_PID)"
    ((PASS++))
else
    echo -e "${RED}❌${NC} 服务器端服务器启动失败"
    ((FAIL++))
fi

# 停止服务器端服务器
kill $SERVER_PID 2>/dev/null
cd ../..

# ===== 8. API端点测试 =====
echo -e "\n${BLUE}🔌 8. API端点测试${NC}"
echo "----------------------------------------"

# 启动客户端服务器进行API测试
echo "🧪 启动客户端服务器进行API测试..."
cd client/login
python3 server.py &
CLIENT_PID=$!
sleep 8

# 测试邮件客户端检查API
echo "📧 测试邮件客户端检查API..."
curl -s -X POST -H "Content-Type: application/json" -d '{}' http://localhost:5000/api/check_email_client | grep -q "available"
test_result $? "邮件客户端检查API"

# 测试登录API（无需真实邮件发送）
echo "🔒 测试登录API结构..."
response=$(curl -s -X POST -H "Content-Type: application/json" -d '{"username":"test","password":"test"}' http://localhost:5000/api/login)
echo $response | grep -q "success"
test_result $? "登录API结构测试"

# 停止客户端服务器
kill $CLIENT_PID 2>/dev/null
cd ../..

# ===== 9. 前端文件验证 =====
echo -e "\n${BLUE}🎨 9. 前端文件验证${NC}"
echo "----------------------------------------"

# 检查前端JavaScript文件语法
echo "📝 检查auth_email.js语法..."
node -c client/login/auth_email.js 2>/dev/null
test_result $? "auth_email.js语法检查"

echo "📝 检查register_email.js语法..."
node -c client/login/register_email.js 2>/dev/null
test_result $? "register_email.js语法检查"

# 检查HTML文件
echo "📄 检查HTML文件..."
if [ -f "client/index.html" ]; then
    echo -e "${GREEN}✅${NC} index.html 存在"
    ((PASS++))
else
    echo -e "${RED}❌${NC} index.html 缺失"
    ((FAIL++))
fi

# ===== 10. 邮件连接测试（可选） =====
echo -e "\n${BLUE}📮 10. 邮件连接测试（可选）${NC}"
echo "----------------------------------------"

echo "⚠️  跳过真实邮件连接测试（避免频繁发送邮件）"
echo "   如需测试真实邮件功能，请："
echo "   1. 确保邮箱授权码正确"
echo "   2. 手动运行 python3 client/login/email_client.py"
echo "   3. 手动运行 python3 cloudserver/login/email_server.py"

# ===== 测试总结 =====
echo -e "\n${BLUE}📊 测试总结${NC}"
echo "=================================================="
echo -e "总测试项目: $((PASS + FAIL))"
echo -e "${GREEN}通过: $PASS${NC}"
echo -e "${RED}失败: $FAIL${NC}"

if [ $FAIL -eq 0 ]; then
    echo -e "\n${GREEN}🎉 所有测试通过！邮件认证系统验证成功！${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  有 $FAIL 项测试失败，请检查相关组件${NC}"
    exit 1
fi 