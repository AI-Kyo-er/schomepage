// 离散对数加密算法 - 前端JavaScript实现
// 对应Python后端的crypto_utils.py

// 离散对数加密参数 - 更新为更安全的参数
const P = 2305843009213693951n;  // 使用BigInt: p = 2^61 - 1
const G = 37n;                   // 使用BigInt: g = 37

// 调试标志
const CRYPTO_DEBUG = true;

function cryptoLog(...args) {
    if (CRYPTO_DEBUG) {
        console.log('[CRYPTO]', ...args);
    }
}

function cryptoError(...args) {
    if (CRYPTO_DEBUG) {
        console.error('[CRYPTO ERROR]', ...args);
    }
}

/**
 * 快速模幂运算: base^exp mod mod (使用BigInt)
 * @param {bigint} base 底数
 * @param {bigint} exp 指数
 * @param {bigint} mod 模数
 * @returns {bigint} 结果
 */
function powerMod(base, exp, mod) {
    cryptoLog(`计算 ${base}^${exp} mod ${mod}`);
    
    let result = 1n;
    base = base % mod;
    
    while (exp > 0n) {
        if (exp % 2n === 1n) {
            result = (result * base) % mod;
        }
        exp = exp / 2n;
        base = (base * base) % mod;
    }
    
    cryptoLog(`模幂运算结果: ${result}`);
    return result;
}

/**
 * 生成私钥
 * 私钥 a = (第0个字符ascii << 0) ⊕ (第1个字符ascii << 1) ⊕ ... ⊕ (第i个字符ascii << i)
 * @param {string} password 明文密码
 * @returns {bigint} 私钥
 */
function generatePrivateKey(password) {
    cryptoLog(`生成私钥，密码: ${password}`);
    
    if (!password) {
        return 0n;
    }
    
    let privateKey = 0n;
    for (let i = 0; i < password.length; i++) {
        const char = password[i];
        const asciiVal = BigInt(char.charCodeAt(0));
        const shiftedVal = asciiVal << BigInt(i);
        privateKey ^= shiftedVal;
        
        cryptoLog(`字符 '${char}' (ASCII ${asciiVal}) << ${i} = ${shiftedVal}, 当前私钥: ${privateKey}`);
    }
    
    cryptoLog(`最终私钥 a = ${privateKey}`);
    return privateKey;
}

/**
 * 加密密码
 * 计算 A = g^a (mod p)，返回A的后64位
 * @param {string} password 明文密码
 * @returns {bigint} 加密后的密码（64位整数）
 */
function encryptPassword(password) {
    cryptoLog(`开始加密密码: ${password}`);
    
    const startTime = performance.now();
    
    // 生成私钥
    const privateKey = generatePrivateKey(password);
    
    // 计算 A = g^a (mod p)
    cryptoLog(`计算 A = ${G}^${privateKey} (mod ${P})`);
    
    const publicKey = powerMod(G, privateKey, P);
    
    const endTime = performance.now();
    cryptoLog(`模幂运算耗时: ${(endTime - startTime).toFixed(4)}毫秒`);
    
    // 取后64位
    const mask64 = (1n << 64n) - 1n;
    const encryptedPassword = publicKey & mask64;
    
    cryptoLog(`完整公钥 A = ${publicKey}`);
    cryptoLog(`A 的后64位 = ${encryptedPassword}`);
    cryptoLog(`16进制表示 = ${encryptedPassword.toString(16).padStart(16, '0')}`);
    
    return encryptedPassword;
}

/**
 * 将加密密码转换为16进制字符串
 * @param {string} password 明文密码
 * @returns {string} 16进制加密密码
 */
function convertToEncryptedHex(password) {
    const encrypted = encryptPassword(password);
    return encrypted.toString(16).padStart(16, '0');
}

/**
 * 测试加密算法
 */
function testCrypto() {
    console.log('=== 前端离散对数加密算法测试 ===');
    console.log(`参数: p = 2^61 - 1 = ${P}, g = ${G}`);
    
    // 测试密码 "123456"
    const testPassword = "123456";
    console.log(`\n=== 测试密码: ${testPassword} ===`);
    
    // 加密密码
    const encryptedHex = convertToEncryptedHex(testPassword);
    console.log(`加密结果(16进制): ${encryptedHex}`);
    
    return encryptedHex;
}

// 导出函数供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    // Node.js 环境
    module.exports = {
        encryptPassword,
        convertToEncryptedHex,
        testCrypto
    };
} else {
    // 浏览器环境，添加到全局对象
    window.CryptoUtils = {
        encryptPassword,
        convertToEncryptedHex,
        testCrypto
    };
}

// 如果直接运行此脚本，执行测试
if (typeof document === 'undefined') {
    // Node.js 环境下的测试
    testCrypto();
} 