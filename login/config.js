// ===== 共享配置文件 =====
// 这个文件包含所有JavaScript文件需要的共享常量和配置

// API基础URL
const API_BASE_URL = 'http://localhost:5000/api';

// 调试模式开关
const DEBUG_MODE = true;

// 会话超时时间（24小时）
const SESSION_TIMEOUT = 24 * 60 * 60 * 1000;

// 验证码倒计时时间（60秒）
const VERIFICATION_COUNTDOWN = 60;

// 将常量暴露到全局作用域，供其他文件使用
window.API_BASE_URL = API_BASE_URL;
window.DEBUG_MODE = DEBUG_MODE;
window.SESSION_TIMEOUT = SESSION_TIMEOUT;
window.VERIFICATION_COUNTDOWN = VERIFICATION_COUNTDOWN;

// 全局调试日志函数
window.debugLog = function(message, data = null) {
    if (DEBUG_MODE) {
        console.log(`[DEBUG] ${message}`, data || '');
    }
};

// 全局调试错误函数
window.debugError = function(message, error = null) {
    if (DEBUG_MODE) {
        console.error(`[ERROR] ${message}`, error || '');
    }
};

// 注册模块专用调试函数
window.registerDebugLog = function(message, data = null) {
    if (DEBUG_MODE) {
        console.log(`[REGISTER DEBUG] ${message}`, data || '');
    }
};

window.registerDebugError = function(message, error = null) {
    if (DEBUG_MODE) {
        console.error(`[REGISTER ERROR] ${message}`, error || '');
    }
};

// 配置文件加载完成标记
console.log('[CONFIG] 配置文件加载完成，共享常量已设置'); 