// 全局变量
let currentRegistrationEmail = '';
let countdownInterval = null;
let isVerificationSent = false;

// 立即执行：确认register.js文件已加载
registerDebugLog('register.js 文件开始加载');

// 显示注册弹窗
function showRegisterModal() {
    registerDebugLog('显示注册弹窗函数被调用');
    
    const modal = document.getElementById('registerModal');
    if (modal) {
        registerDebugLog('找到注册弹窗元素，显示弹窗');
        modal.style.display = 'block';
        clearRegisterForm();
    } else {
        registerDebugError('未找到注册弹窗元素 #registerModal');
    }
}

// 立即将关键函数暴露到全局作用域
window.showRegisterModal = showRegisterModal;
registerDebugLog('showRegisterModal函数已立即添加到window对象');

// 预声明其他重要函数到全局作用域（函数声明会被提升）
window.requestVerificationCode = requestVerificationCode;
window.registerUser = registerUser;
window.proceedWithVerification = proceedWithVerification;
window.updatePassword = updatePassword;
window.directLogin = directLogin;

registerDebugLog('所有关键函数已预声明到window对象');

// 关闭注册弹窗
function closeRegisterModal() {
    registerDebugLog('关闭注册弹窗');
    const modal = document.getElementById('registerModal');
    if (modal) {
        modal.style.display = 'none';
        clearRegisterForm();
        if (countdownInterval) {
            clearInterval(countdownInterval);
            countdownInterval = null;
            registerDebugLog('清除倒计时定时器');
        }
    } else {
        registerDebugError('未找到注册弹窗元素 #registerModal');
    }
}

// 清空注册表单
function clearRegisterForm() {
    registerDebugLog('清空注册表单');
    
    const elements = {
        registerEmail: document.getElementById('registerEmail'),
        verificationCode: document.getElementById('verificationCode'),
        agreeTerms: document.getElementById('agreeTerms'),
        registerErrorMessage: document.getElementById('registerErrorMessage'),
        registerSuccessMessage: document.getElementById('registerSuccessMessage'),
        countdown: document.getElementById('countdown'),
        sendCodeBtn: document.getElementById('sendCodeBtn')
    };
    
    // 检查并操作每个元素
    Object.entries(elements).forEach(([name, element]) => {
        if (element) {
            registerDebugLog(`✅ 找到元素 ${name}`);
            switch (name) {
                case 'registerEmail':
                case 'verificationCode':
                    element.value = '';
                    break;
                case 'agreeTerms':
                    element.checked = false;
                    break;
                case 'registerErrorMessage':
                case 'registerSuccessMessage':
                    element.style.display = 'none';
                    break;
                case 'countdown':
                    element.textContent = '';
                    break;
                case 'sendCodeBtn':
                    element.disabled = false;
                    element.textContent = '发送验证码';
                    break;
            }
        } else {
            registerDebugError(`❌ 未找到元素 ${name}`);
        }
    });
    
    isVerificationSent = false;
}

// 显示服务条款弹窗
function showTermsModal() {
    registerDebugLog('显示服务条款弹窗');
    const modal = document.getElementById('termsModal');
    if (modal) {
        modal.style.display = 'block';
    } else {
        registerDebugError('未找到服务条款弹窗元素 #termsModal');
    }
}

// 关闭服务条款弹窗
function closeTermsModal() {
    registerDebugLog('关闭服务条款弹窗');
    const modal = document.getElementById('termsModal');
    if (modal) {
        modal.style.display = 'none';
    } else {
        registerDebugError('未找到服务条款弹窗元素 #termsModal');
    }
}

// 显示人机验证弹窗
function showCaptchaModal() {
    registerDebugLog('显示人机验证弹窗');
    const modal = document.getElementById('captchaModal');
    const checkbox = document.getElementById('robotCheck');
    
    if (modal) {
        modal.style.display = 'block';
        if (checkbox) {
            checkbox.checked = false;
        } else {
            registerDebugError('未找到人机验证复选框 #robotCheck');
        }
    } else {
        registerDebugError('未找到人机验证弹窗元素 #captchaModal');
    }
}

// 关闭人机验证弹窗
function closeCaptchaModal() {
    registerDebugLog('关闭人机验证弹窗');
    const modal = document.getElementById('captchaModal');
    if (modal) {
        modal.style.display = 'none';
    } else {
        registerDebugError('未找到人机验证弹窗元素 #captchaModal');
    }
}

// 显示密码设置弹窗
function showPasswordModal() {
    registerDebugLog('显示密码设置弹窗');
    const modal = document.getElementById('passwordModal');
    const newPassword = document.getElementById('newPassword');
    const confirmPassword = document.getElementById('confirmPassword');
    const passwordStrength = document.getElementById('passwordStrength');
    const passwordErrorMessage = document.getElementById('passwordErrorMessage');
    
    if (modal) {
        modal.style.display = 'block';
        
        if (newPassword) newPassword.value = '';
        if (confirmPassword) confirmPassword.value = '';
        if (passwordStrength) passwordStrength.textContent = '';
        if (passwordErrorMessage) passwordErrorMessage.style.display = 'none';
    } else {
        registerDebugError('未找到密码设置弹窗元素 #passwordModal');
    }
}

// 关闭密码设置弹窗
function closePasswordModal() {
    registerDebugLog('关闭密码设置弹窗');
    const modal = document.getElementById('passwordModal');
    if (modal) {
        modal.style.display = 'none';
    } else {
        registerDebugError('未找到密码设置弹窗元素 #passwordModal');
    }
}

// 显示注册错误消息
function showRegisterError(message) {
    registerDebugError('显示注册错误消息', message);
    const errorElement = document.getElementById('registerErrorMessage');
    if (errorElement) {
        // 将换行符转换为HTML换行
        const htmlMessage = message.replace(/\n/g, '<br>');
        errorElement.innerHTML = htmlMessage;
        errorElement.style.display = 'block';
        document.getElementById('registerSuccessMessage').style.display = 'none';
    } else {
        registerDebugError('未找到注册错误消息元素');
    }
}

// 显示注册成功消息
function showRegisterSuccess(message) {
    registerDebugLog('显示注册成功消息', message);
    const successElement = document.getElementById('registerSuccessMessage');
    successElement.textContent = message;
    successElement.style.display = 'block';
    document.getElementById('registerErrorMessage').style.display = 'none';
}

// 显示密码设置错误消息
function showPasswordError(message) {
    registerDebugError('显示密码设置错误消息', message);
    const errorElement = document.getElementById('passwordErrorMessage');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

// 请求验证码
async function requestVerificationCode() {
    registerDebugLog('开始请求验证码流程');
    
    const email = document.getElementById('registerEmail').value.trim();
    registerDebugLog('获取邮箱输入', { email, emailLength: email.length });
    
    if (!email) {
        registerDebugError('邮箱为空');
        showRegisterError('请输入邮箱地址');
        return;
    }
    
    // 验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        registerDebugError('邮箱格式无效', email);
        showRegisterError('请输入有效的邮箱地址');
        return;
    }
    
    registerDebugLog('邮箱格式验证通过');
    
    // 禁用发送按钮防止重复点击
    const sendBtn = document.getElementById('sendCodeBtn');
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.textContent = '正在发送...';
        registerDebugLog('发送按钮已禁用');
    }
    
    try {
        registerDebugLog('发送邮箱检查请求到:', `${API_BASE_URL}/check_email`);
        
        // 首先检查邮箱是否已注册
        const checkResponse = await fetch(`${API_BASE_URL}/check_email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });
        
        registerDebugLog('邮箱检查响应', {
            status: checkResponse.status,
            ok: checkResponse.ok,
            statusText: checkResponse.statusText
        });
        
        if (!checkResponse.ok) {
            throw new Error(`HTTP错误: ${checkResponse.status} ${checkResponse.statusText}`);
        }
        
        const checkResult = await checkResponse.json();
        registerDebugLog('邮箱检查结果', checkResult);
        
        if (!checkResult.success) {
            registerDebugError('邮箱已被注册', checkResult);
            showRegisterError(checkResult.message);
            // 恢复发送按钮
            if (sendBtn) {
                sendBtn.disabled = false;
                sendBtn.textContent = '发送验证码';
            }
            return;
        }
        
        // 如果邮箱可用，显示人机验证
        currentRegistrationEmail = email;
        registerDebugLog('邮箱可用，显示人机验证', currentRegistrationEmail);
        showCaptchaModal();
        
        // 恢复发送按钮
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.textContent = '发送验证码';
        }
        
    } catch (error) {
        registerDebugError('检查邮箱请求失败', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        
        // 显示详细错误信息
        let errorMessage = '网络错误，请检查以下问题：\n';
        if (error.message.includes('Failed to fetch')) {
            errorMessage += '• 服务器未启动或连接失败\n• 请确保服务器运行在 localhost:5000';
        } else if (error.message.includes('HTTP错误')) {
            errorMessage += `• 服务器响应错误: ${error.message}`;
        } else {
            errorMessage += `• ${error.message}`;
        }
        
        showRegisterError(errorMessage);
        
        // 恢复发送按钮
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.textContent = '发送验证码';
        }
    }
}

// 完成人机验证，继续发送验证码
async function proceedWithVerification() {
    registerDebugLog('开始人机验证流程');
    
    const robotCheck = document.getElementById('robotCheck').checked;
    registerDebugLog('人机验证状态', robotCheck);
    
    if (!robotCheck) {
        registerDebugError('人机验证未完成');
        alert('请先完成人机验证');
        return;
    }
    
    closeCaptchaModal();
    
    // 显示发送状态
    showRegisterSuccess('正在发送验证码，请稍候...');
    
    try {
        registerDebugLog('发送验证码请求到:', `${API_BASE_URL}/send_code`);
        registerDebugLog('请求数据:', { email: currentRegistrationEmail });
        
        // 发送验证码请求
        const response = await fetch(`${API_BASE_URL}/send_code`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: currentRegistrationEmail })
        });
        
        registerDebugLog('验证码发送响应', {
            status: response.status,
            ok: response.ok,
            statusText: response.statusText,
            url: response.url
        });
        
        if (!response.ok) {
            throw new Error(`HTTP错误: ${response.status} ${response.statusText}`);
        }
        
        const result = await response.json();
        registerDebugLog('验证码发送结果', result);
        
        if (result.success) {
            showRegisterSuccess(result.message);
            isVerificationSent = true;
            registerDebugLog('验证码发送成功，开始倒计时');
            startCountdown();
        } else {
            registerDebugError('验证码发送失败', result);
            showRegisterError(result.message || '验证码发送失败，请重试');
        }
        
    } catch (error) {
        registerDebugError('发送验证码请求异常', {
            name: error.name,
            message: error.message,
            stack: error.stack
        });
        
        // 显示详细错误信息
        let errorMessage = '发送验证码失败：\n';
        if (error.message.includes('Failed to fetch')) {
            errorMessage += '• 无法连接到服务器\n• 请检查网络连接\n• 确保服务器运行在 localhost:5000';
        } else if (error.message.includes('HTTP错误')) {
            errorMessage += `• 服务器错误: ${error.message}`;
        } else {
            errorMessage += `• ${error.message}`;
        }
        
        showRegisterError(errorMessage);
    }
}

// 开始倒计时
function startCountdown() {
    registerDebugLog('开始60秒倒计时');
    
    let remainingTime = 60;
    const sendBtn = document.getElementById('sendCodeBtn');
    const countdownElement = document.getElementById('countdown');
    
    sendBtn.disabled = true;
    sendBtn.textContent = `重新发送(${remainingTime}s)`;
    
    countdownInterval = setInterval(() => {
        remainingTime--;
        registerDebugLog('倒计时更新', remainingTime);
        
        if (remainingTime > 0) {
            sendBtn.textContent = `重新发送(${remainingTime}s)`;
            countdownElement.textContent = `${remainingTime}秒后可重新发送`;
        } else {
            registerDebugLog('倒计时结束');
            clearInterval(countdownInterval);
            countdownInterval = null;
            sendBtn.disabled = false;
            sendBtn.textContent = '发送验证码';
            countdownElement.textContent = '';
        }
    }, 1000);
}

// 注册用户
async function registerUser() {
    registerDebugLog('开始用户注册流程');
    
    const email = document.getElementById('registerEmail').value.trim();
    const code = document.getElementById('verificationCode').value.trim();
    const agreeTerms = document.getElementById('agreeTerms').checked;
    
    registerDebugLog('获取注册表单数据', {
        email,
        code,
        agreeTerms,
        isVerificationSent
    });
    
    // 验证输入
    if (!email) {
        registerDebugError('邮箱为空');
        showRegisterError('请输入邮箱地址');
        return;
    }
    
    if (!code) {
        registerDebugError('验证码为空');
        showRegisterError('请输入验证码');
        return;
    }
    
    if (!agreeTerms) {
        registerDebugError('未同意服务条款');
        showRegisterError('请阅读并同意用户服务条款');
        return;
    }
    
    if (!isVerificationSent) {
        registerDebugError('验证码未发送');
        showRegisterError('请先获取验证码');
        return;
    }
    
    registerDebugLog('注册表单验证通过');
    
    try {
        registerDebugLog('发送注册验证请求');
        
        // 验证验证码并注册
        const response = await fetch(`${API_BASE_URL}/verify_code`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, code })
        });
        
        registerDebugLog('注册验证响应', {
            status: response.status,
            ok: response.ok
        });
        
        const result = await response.json();
        registerDebugLog('注册验证结果', result);
        
        if (result.success) {
            showRegisterSuccess('注册成功！');
            currentRegistrationEmail = email;
            
            // 🔒 保存验证码供直接登录使用
            window.lastVerificationCode = code;
            registerDebugLog('保存验证码供直接登录使用', { code });
            
            registerDebugLog('注册成功，准备显示密码设置弹窗');
            
            // 延迟显示密码设置弹窗
            setTimeout(() => {
                registerDebugLog('显示密码设置弹窗');
                closeRegisterModal();
                showPasswordModal();
            }, 1500);
        } else {
            registerDebugError('注册验证失败', result);
            showRegisterError(result.message);
        }
        
    } catch (error) {
        registerDebugError('注册请求异常', error);
        showRegisterError('网络错误，请稍后重试');
    }
}

// 检查密码强度
function checkPasswordStrength(password) {
    registerDebugLog('检查密码强度', { passwordLength: password.length });
    
    const strengthElement = document.getElementById('passwordStrength');
    
    if (!password) {
        strengthElement.textContent = '';
        return;
    }
    
    let score = 0;
    const checks = {
        hasNumber: /\d/.test(password),
        hasLower: /[a-z]/.test(password),
        hasUpper: /[A-Z]/.test(password),
        hasUnderscore: /_/.test(password)
    };
    
    score = Object.values(checks).filter(Boolean).length;
    
    registerDebugLog('密码强度检查结果', { checks, score });
    
    let strengthText = '';
    let strengthClass = '';
    
    switch (score) {
        case 1:
            strengthText = '密码强度：弱';
            strengthClass = 'strength-weak';
            break;
        case 2:
            strengthText = '密码强度：中';
            strengthClass = 'strength-medium';
            break;
        case 3:
            strengthText = '密码强度：强';
            strengthClass = 'strength-strong';
            break;
        case 4:
            strengthText = '密码强度：极强';
            strengthClass = 'strength-very-strong';
            break;
        default:
            strengthText = '密码强度：弱';
            strengthClass = 'strength-weak';
    }
    
    strengthElement.textContent = strengthText;
    strengthElement.className = `password-strength ${strengthClass}`;
    
    registerDebugLog('密码强度显示更新', { strengthText, strengthClass });
}

// 验证密码格式
function validatePassword(password) {
    registerDebugLog('验证密码格式', { passwordLength: password.length });
    
    if (password.length < 6 || password.length > 16) {
        registerDebugError('密码长度不符合要求', password.length);
        return '密码长度必须在6-16位之间';
    }
    
    const validChars = /^[a-zA-Z0-9_]+$/;
    if (!validChars.test(password)) {
        registerDebugError('密码包含非法字符');
        return '密码只能包含数字、大小写字母和下划线';
    }
    
    registerDebugLog('密码格式验证通过');
    return null;
}

// 更新密码
async function updatePassword() {
    registerDebugLog('开始更新密码流程');
    
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    registerDebugLog('获取密码设置数据', {
        newPasswordLength: newPassword.length,
        confirmPasswordLength: confirmPassword.length,
        passwordsMatch: newPassword === confirmPassword
    });
    
    // 验证密码
    const passwordError = validatePassword(newPassword);
    if (passwordError) {
        showPasswordError(passwordError);
        return;
    }
    
    if (newPassword !== confirmPassword) {
        registerDebugError('两次输入的密码不一致');
        showPasswordError('两次输入的密码不一致');
        return;
    }
    
    registerDebugLog('密码验证通过');
    
    // 🔒 安全关键：在前端加密密码，后端只接收密文
    let encryptedPassword;
    try {
        registerDebugLog('开始密码加密');
        encryptedPassword = window.CryptoUtils.convertToEncryptedHex(newPassword);
        registerDebugLog('密码加密完成', { 
            originalLength: newPassword.length,
            encryptedPassword: encryptedPassword
        });
    } catch (error) {
        registerDebugError('密码加密失败', error);
        showPasswordError('密码处理失败，请重试');
        return;
    }
    
    try {
        registerDebugLog('发送密码更新请求');
        
        // 更新密码 - 🔒 发送密文，不是明文！
        const response = await fetch(`${API_BASE_URL}/update_password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                email: currentRegistrationEmail, 
                password: encryptedPassword  // 🔒 发送密文，不是明文！
            })
        });
        
        registerDebugLog('密码更新响应', {
            status: response.status,
            ok: response.ok
        });
        
        const result = await response.json();
        registerDebugLog('密码更新结果', result);
        
        if (result.success) {
            registerDebugLog('密码更新成功，刷新页面');
            alert('密码设置成功！请使用新密码登录。');
            closePasswordModal();
            window.location.reload(); // 刷新页面返回登录界面
        } else {
            registerDebugError('密码更新失败', result);
            showPasswordError(result.message);
        }
        
    } catch (error) {
        registerDebugError('密码更新请求异常', error);
        showPasswordError('网络错误，请稍后重试');
    }
}

// 直接登录
async function directLogin() {
    registerDebugLog('执行直接登录');
    
    closePasswordModal();
    
    // 🔒 获取当前注册时使用的验证码
    const verificationCodeInput = document.getElementById('verificationCode');
    if (!verificationCodeInput || !verificationCodeInput.value) {
        registerDebugError('直接登录：验证码输入框为空');
        
        // 尝试从当前注册流程中获取验证码
        if (currentRegistrationEmail && typeof window.lastVerificationCode !== 'undefined') {
            registerDebugLog('使用缓存的验证码进行直接登录', { lastCode: window.lastVerificationCode });
            const verificationCode = window.lastVerificationCode;
        } else {
            // 如果确实无法获取验证码，提供更友好的提示
            alert('请先完成验证码验证，然后再选择直接登录');
            return;
        }
    }
    
    let verificationCode;
    if (verificationCodeInput && verificationCodeInput.value) {
        verificationCode = verificationCodeInput.value.trim();
    } else if (window.lastVerificationCode) {
        verificationCode = window.lastVerificationCode;
    } else {
        alert('无法获取验证码，请重新注册');
        return;
    }
    
    registerDebugLog('使用验证码进行登录', { verificationCode, source: verificationCodeInput ? 'input' : 'cache' });
    
    try {
        // 🔒 前端加密验证码
        const encryptedPassword = window.CryptoUtils.convertToEncryptedHex(verificationCode);
        registerDebugLog('验证码加密完成', { encryptedPassword });
        
        // 🔒 使用加密的验证码进行正常登录
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: currentRegistrationEmail,
                password: encryptedPassword  // 🔒 发送加密的验证码作为密码
            })
        });
        
        const result = await response.json();
        registerDebugLog('直接登录响应', result);
        
        if (result.success) {
            // 正常设置登录状态
            sessionStorage.setItem('isLoggedIn', 'true');
            sessionStorage.setItem('currentUser', currentRegistrationEmail);
            sessionStorage.setItem('loginTime', new Date().getTime());
            
            registerDebugLog('直接登录成功，跳转到主页');
            alert('注册完成，正在为您自动登录...');
            
            setTimeout(() => {
                window.location.href = 'main.html';
            }, 1000);
        } else {
            registerDebugError('直接登录失败', result);
            alert('登录失败：' + result.message);
        }
        
    } catch (error) {
        registerDebugError('直接登录异常', error);
        alert('登录过程中发生错误，请重试');
    }
}

// 页面加载时绑定事件
document.addEventListener('DOMContentLoaded', function() {
    registerDebugLog('注册模块DOM加载完成，开始初始化');
    
    // 检查关键DOM元素是否存在
    const criticalElements = [
        'registerModal', 'termsModal', 'captchaModal', 'passwordModal',
        'registerEmail', 'verificationCode', 'agreeTerms', 'sendCodeBtn',
        'registerErrorMessage', 'registerSuccessMessage', 'countdown',
        'newPassword', 'confirmPassword', 'passwordStrength', 'passwordErrorMessage',
        'robotCheck'
    ];
    
    let missingElements = [];
    criticalElements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            registerDebugLog(`✅ 关键元素 ${elementId} 存在`);
        } else {
            registerDebugError(`❌ 关键元素 ${elementId} 缺失`);
            missingElements.push(elementId);
        }
    });
    
    if (missingElements.length > 0) {
        registerDebugError('发现缺失的关键元素', missingElements);
    } else {
        registerDebugLog('所有关键DOM元素检查通过');
    }
    
    // 检查全局函数是否可用
    const globalFunctions = [
        'showRegisterModal', 'closeRegisterModal', 'showTermsModal', 'closeTermsModal',
        'showCaptchaModal', 'closeCaptchaModal', 'showPasswordModal', 'closePasswordModal',
        'requestVerificationCode', 'proceedWithVerification', 'registerUser', 'updatePassword',
        'directLogin'
    ];
    
    globalFunctions.forEach(funcName => {
        if (typeof window[funcName] === 'function') {
            registerDebugLog(`✅ 全局函数 ${funcName} 可用`);
        } else {
            registerDebugError(`❌ 全局函数 ${funcName} 不可用`);
            // 将函数添加到window对象
            if (typeof eval(funcName) === 'function') {
                window[funcName] = eval(funcName);
                registerDebugLog(`🔧 已将函数 ${funcName} 添加到window对象`);
            }
        }
    });
    
    // 特别检查showRegisterModal函数
    registerDebugLog('特别检查showRegisterModal函数可用性', {
        typeofShowRegisterModal: typeof showRegisterModal,
        windowShowRegisterModal: typeof window.showRegisterModal,
        functionExists: typeof showRegisterModal === 'function'
    });
    
    // 确保所有重要函数都在window对象上可用
    window.showRegisterModal = showRegisterModal;
    window.closeRegisterModal = closeRegisterModal;
    window.showTermsModal = showTermsModal;
    window.closeTermsModal = closeTermsModal;
    window.showCaptchaModal = showCaptchaModal;
    window.closeCaptchaModal = closeCaptchaModal;
    window.showPasswordModal = showPasswordModal;
    window.closePasswordModal = closePasswordModal;
    window.requestVerificationCode = requestVerificationCode;
    window.proceedWithVerification = proceedWithVerification;
    window.registerUser = registerUser;
    window.updatePassword = updatePassword;
    window.directLogin = directLogin;
    
    registerDebugLog('所有函数已确保在window对象上可用');
    
    // 绑定密码强度检测
    const newPasswordInput = document.getElementById('newPassword');
    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', function() {
            checkPasswordStrength(this.value);
        });
        registerDebugLog('密码强度检测事件已绑定');
    } else {
        registerDebugError('未找到新密码输入框 #newPassword');
    }
    
    // 点击弹窗外部关闭弹窗
    window.addEventListener('click', function(event) {
        const modals = ['registerModal', 'termsModal', 'captchaModal', 'passwordModal'];
        modals.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (event.target === modal) {
                registerDebugLog('点击弹窗外部，关闭弹窗', modalId);
                modal.style.display = 'none';
            }
        });
    });
    
    // 监听邮箱输入框，清除验证码相关状态
    const emailInput = document.getElementById('registerEmail');
    if (emailInput) {
        emailInput.addEventListener('input', function() {
            if (this.value.trim() !== currentRegistrationEmail) {
                registerDebugLog('邮箱地址改变，重置验证码状态');
                // 邮箱地址改变了，重置验证码状态
                isVerificationSent = false;
                const verificationCodeInput = document.getElementById('verificationCode');
                if (verificationCodeInput) verificationCodeInput.value = '';
                
                if (countdownInterval) {
                    clearInterval(countdownInterval);
                    countdownInterval = null;
                }
                const sendBtn = document.getElementById('sendCodeBtn');
                const countdown = document.getElementById('countdown');
                if (sendBtn) {
                    sendBtn.disabled = false;
                    sendBtn.textContent = '发送验证码';
                }
                if (countdown) countdown.textContent = '';
            }
        });
        registerDebugLog('邮箱输入监听事件已绑定');
    } else {
        registerDebugError('未找到邮箱输入框 #registerEmail');
    }
    
    // 测试注册按钮点击
    registerDebugLog('尝试手动测试showRegisterModal函数');
    try {
        // 不实际调用，只是测试函数是否存在
        if (typeof showRegisterModal === 'function') {
            registerDebugLog('✅ showRegisterModal函数测试通过');
        } else {
            registerDebugError('❌ showRegisterModal函数测试失败');
        }
    } catch (error) {
        registerDebugError('showRegisterModal函数测试异常', error);
    }
    
    registerDebugLog('注册模块初始化完成');
});

// 在文件最后再次确认函数已加载
registerDebugLog('register.js 文件加载完成，所有函数已定义');

// 立即将所有HTML onclick用到的函数暴露到全局作用域
window.showRegisterModal = showRegisterModal;
window.closeRegisterModal = closeRegisterModal;
window.showTermsModal = showTermsModal;
window.closeTermsModal = closeTermsModal;
window.showCaptchaModal = showCaptchaModal;
window.closeCaptchaModal = closeCaptchaModal;
window.showPasswordModal = showPasswordModal;
window.closePasswordModal = closePasswordModal;

registerDebugLog('所有HTML onclick函数已立即添加到window对象'); 