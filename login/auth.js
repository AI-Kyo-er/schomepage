// 安全的调试函数定义 - 防止debugLog未定义错误
function safeDebugLog(message, data = null) {
    try {
        if (typeof window.debugLog === 'function') {
            window.debugLog(message, data);
        } else if (typeof debugLog === 'function') {
            debugLog(message, data);
        } else {
            // 如果debugLog未定义，使用console.log作为备用
            console.log(`[DEBUG] ${message}`, data || '');
        }
    } catch (error) {
        console.log(`[DEBUG] ${message}`, data || '');
    }
}

function safeDebugError(message, error = null) {
    try {
        if (typeof window.debugError === 'function') {
            window.debugError(message, error);
        } else if (typeof debugError === 'function') {
            debugError(message, error);
        } else {
            // 如果debugError未定义，使用console.error作为备用
            console.error(`[ERROR] ${message}`, error || '');
        }
    } catch (err) {
        console.error(`[ERROR] ${message}`, error || '');
    }
}

// 重新定义debugLog和debugError为安全版本
const debugLog = safeDebugLog;
const debugError = safeDebugError;

// 登录功能
async function login(event) {
    event.preventDefault();
    
    debugLog('开始登录流程');
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    
    debugLog('获取登录表单数据', { 
        username: username, 
        passwordLength: password.length,
        usernameElement: !!document.getElementById('username'),
        passwordElement: !!document.getElementById('password')
    });
    
    // 清除之前的消息
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
    debugLog('清除之前的消息显示');
    
    // 验证输入
    if (!username || !password) {
        debugError('输入验证失败', { username: !!username, password: !!password });
        showError('请输入用户名和密码');
        return;
    }
    
    debugLog('输入验证通过，准备加密密码');
    
    // 🔒 安全关键：在前端加密密码，后端只接收密文
    let encryptedPassword;
    try {
        debugLog('开始密码加密');
        encryptedPassword = window.CryptoUtils.convertToEncryptedHex(password);
        debugLog('密码加密完成', { 
            originalLength: password.length,
            encryptedPassword: encryptedPassword
        });
    } catch (error) {
        debugError('密码加密失败', error);
        showError('密码处理失败，请重试');
        return;
    }
    
    const requestData = { 
        username, 
        password: encryptedPassword  // 🔒 发送密文，不是明文！
    };
    debugLog('请求数据', { 
        username: requestData.username, 
        encryptedPasswordLength: requestData.password.length 
    });
    
    try {
        debugLog('发送登录请求到:', `${API_BASE_URL}/login`);
        
        // 调用后端登录API
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        debugLog('收到响应', {
            status: response.status,
            statusText: response.statusText,
            ok: response.ok,
            url: response.url
        });
        
        if (!response.ok) {
            debugError('HTTP响应状态异常', {
                status: response.status,
                statusText: response.statusText
            });
        }
        
        const result = await response.json();
        debugLog('解析响应数据', result);
        
        if (result.success) {
            debugLog('登录成功，设置会话数据');
            
            // 登录成功
            sessionStorage.setItem('isLoggedIn', 'true');
            sessionStorage.setItem('currentUser', username);
            sessionStorage.setItem('loginTime', new Date().getTime());
            
            debugLog('会话数据已设置', {
                isLoggedIn: sessionStorage.getItem('isLoggedIn'),
                currentUser: sessionStorage.getItem('currentUser'),
                loginTime: sessionStorage.getItem('loginTime')
            });
            
            showSuccess('登录成功，正在跳转...');
            
            // 延迟跳转以显示成功消息
            debugLog('准备跳转到主页面');
            setTimeout(() => {
                debugLog('执行页面跳转');
                window.location.href = 'main.html';
            }, 1000);
        } else {
            debugError('登录失败', result);
            showError(result.message || '登录失败');
        }
    } catch (error) {
        debugError('登录请求异常', error);
        showError('网络错误，请稍后重试');
    }
}

// 显示错误消息
function showError(message) {
    debugLog('显示错误消息', message);
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        debugLog('错误消息已显示');
    } else {
        debugError('未找到错误消息元素');
    }
}

// 显示成功消息
function showSuccess(message) {
    debugLog('显示成功消息', message);
    const successMessage = document.getElementById('successMessage');
    if (successMessage) {
        successMessage.textContent = message;
        successMessage.style.display = 'block';
        debugLog('成功消息已显示');
    } else {
        debugError('未找到成功消息元素');
    }
}

// 检查用户是否已登录
function checkAuth() {
    debugLog('检查用户认证状态');
    
    const isLoggedIn = sessionStorage.getItem('isLoggedIn');
    const loginTime = sessionStorage.getItem('loginTime');
    const currentTime = new Date().getTime();
    
    debugLog('认证状态数据', {
        isLoggedIn: isLoggedIn,
        loginTime: loginTime,
        currentTime: currentTime,
        timeDiff: loginTime ? (currentTime - loginTime) : 'N/A'
    });
    
    // 检查会话是否过期（24小时）
    const sessionTimeout = 24 * 60 * 60 * 1000; // 24小时
    
    if (!isLoggedIn || !loginTime || (currentTime - loginTime) > sessionTimeout) {
        debugLog('认证检查失败，需要重新登录', {
            hasLoggedIn: !!isLoggedIn,
            hasLoginTime: !!loginTime,
            isExpired: loginTime ? (currentTime - loginTime) > sessionTimeout : 'N/A'
        });
        
        // 未登录或会话过期，重定向到登录页面
        alert('您尚未登录或登录已过期，请重新登录');
        logout();
        return false;
    }
    
    debugLog('认证检查通过');
    return true;
}

// 退出登录
function logout() {
    debugLog('执行退出登录');
    
    // 彻底清除所有会话和本地存储数据
    sessionStorage.clear();
    localStorage.clear();
    
    debugLog('所有本地数据已清除');
    
    // 使用强制退出参数重定向到登录页面
    window.location.href = 'index.html?logout=true';
}

// 检查当前页面是否需要登录
function requireAuth() {
    debugLog('检查页面访问权限');
    
    if (!checkAuth()) {
        debugLog('页面访问权限检查失败');
        return false;
    }
    
    debugLog('页面访问权限检查通过');
    return true;
}

// 页面加载时的初始化
document.addEventListener('DOMContentLoaded', function() {
    debugLog('页面DOM加载完成，开始初始化');
    
    // 检查当前页面
    const currentPage = window.location.pathname;
    debugLog('当前页面', currentPage);
    
    // 如果在登录页面
    if (document.getElementById('loginForm')) {
        debugLog('检测到登录页面，初始化登录功能');
        
        // 🔒 修复：不再自动检查登录状态和跳转，让用户主动选择登录
        // 检查是否有URL参数指示要强制退出
        const urlParams = new URLSearchParams(window.location.search);
        const forceLogout = urlParams.get('logout');
        
        if (forceLogout === 'true') {
            debugLog('检测到强制退出参数，清除所有会话数据');
            sessionStorage.clear();
            localStorage.clear();
            // 清除URL参数
            window.history.replaceState({}, document.title, window.location.pathname);
        }
        
        // 检查现有登录状态（仅用于显示信息，不自动跳转）
        const isLoggedIn = sessionStorage.getItem('isLoggedIn');
        const currentUser = sessionStorage.getItem('currentUser');
        
        if (isLoggedIn === 'true' && currentUser) {
            debugLog('检测到现有登录状态', { currentUser });
            
            // 显示登录状态提示，移动到页面顶部
            const statusDiv = document.createElement('div');
            statusDiv.id = 'loginStatusBar';
            statusDiv.innerHTML = `
                <div style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
                    color: white;
                    padding: 4px 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    z-index: 9999;
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                ">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="font-weight: bold;">🔒 检测到登录状态：${currentUser}</span>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <button onclick="continueToMain()" style="
                            background: rgba(255,255,255,0.2);
                            color: white;
                            border: 1px solid rgba(255,255,255,0.3);
                            padding: 6px 12px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 13px;
                            transition: all 0.3s;
                        " onmouseover="this.style.background='rgba(255,255,255,0.3)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">进入页面</button>
                        <button onclick="clearLoginAndStay()" style="
                            background: #f44336;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 13px;
                            transition: background 0.3s;
                        " onmouseover="this.style.background='#d32f2f'" onmouseout="this.style.background='#f44336'">退出登录</button>
                    </div>
                </div>
            `;
            
            // 添加到页面最顶部
            document.body.insertBefore(statusDiv, document.body.firstChild);
            
            // 为页面主体添加顶部边距，避免被状态栏遮挡 - 相应减小页面顶部边距
            document.body.style.paddingTop = '44px';
        } else {
            debugLog('未检测到登录状态，显示正常登录表单');
        }
        
        // 绑定登录表单提交事件
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', login);
            debugLog('登录表单事件已绑定');
        } else {
            debugError('未找到登录表单元素');
        }
        
        // 添加回车键登录支持
        const passwordInput = document.getElementById('password');
        if (passwordInput) {
            passwordInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    debugLog('检测到回车键，触发登录');
                    login(e);
                }
            });
            debugLog('密码输入框回车事件已绑定');
        } else {
            debugError('未找到密码输入框元素');
        }
        
        // 检查注册按钮
        const registerBtn = document.querySelector('.register-btn');
        if (registerBtn) {
            debugLog('✅ 找到注册按钮', {
                onclick: registerBtn.getAttribute('onclick'),
                hasOnclick: !!registerBtn.onclick,
                text: registerBtn.textContent
            });
            
            // 添加额外的点击事件监听器用于调试
            registerBtn.addEventListener('click', function(e) {
                debugLog('注册按钮被点击', {
                    event: e,
                    target: e.target,
                    currentTarget: e.currentTarget
                });
                
                // 检查showRegisterModal函数是否可用
                if (typeof showRegisterModal === 'function') {
                    debugLog('showRegisterModal函数可用，准备调用');
                } else if (typeof window.showRegisterModal === 'function') {
                    debugLog('window.showRegisterModal函数可用，准备调用');
                } else {
                    debugError('showRegisterModal函数不可用', {
                        typeofShowRegisterModal: typeof showRegisterModal,
                        windowShowRegisterModal: typeof window.showRegisterModal
                    });
                }
            });
            
            debugLog('注册按钮额外点击监听器已添加');
        } else {
            debugError('❌ 未找到注册按钮元素');
        }
        
        // 检查必要的DOM元素
        const requiredElements = ['username', 'password', 'errorMessage', 'successMessage'];
        requiredElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                debugLog(`✅ 元素 ${id} 存在`);
            } else {
                debugError(`❌ 元素 ${id} 不存在`);
            }
        });
    }
    
    // 如果在主页面，检查登录状态
    if (window.location.pathname.includes('main.html')) {
        debugLog('检测到主页面，检查登录状态');
        if (!requireAuth()) {
            debugLog('主页面访问被拒绝');
            return;
        }
    }
    
    debugLog('页面初始化完成');
});

// 🔒 新增：继续到主页功能
window.continueToMain = function() {
    debugLog('用户选择继续到主页');
    window.location.href = 'main.html';
};

// 🔒 新增：清除登录状态但留在登录页面
window.clearLoginAndStay = function() {
    debugLog('用户选择清除登录状态');
    sessionStorage.clear();
    localStorage.clear();
    window.location.reload();
};

// 添加会话活动检测
let lastActivity = new Date().getTime();

// 更新最后活动时间
function updateActivity() {
    lastActivity = new Date().getTime();
    if (sessionStorage.getItem('isLoggedIn') === 'true') {
        sessionStorage.setItem('loginTime', lastActivity);
        debugLog('更新用户活动时间', lastActivity);
    }
}

// 监听用户活动（简化版）
document.addEventListener('click', updateActivity);
document.addEventListener('keypress', updateActivity);

debugLog('用户活动监听器已设置');

// 简化的会话检查（不使用定时器避免死循环）
function checkSessionOnActivity() {
    if (sessionStorage.getItem('isLoggedIn') === 'true') {
        const currentTime = new Date().getTime();
        const loginTime = sessionStorage.getItem('loginTime');
        const sessionTimeout = 24 * 60 * 60 * 1000; // 24小时
        
        if (loginTime && (currentTime - parseInt(loginTime)) > sessionTimeout) {
            debugLog('会话超时，执行自动退出');
            alert('会话已过期，请重新登录');
            logout();
        }
    }
}

debugLog('会话检查功能已设置'); 