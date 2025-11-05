# Schomepage主页生成系统 - 用户文档

**软件版本**: v2.5  
**文档版本**: v1.0  
**更新时间**: 2025年1月  

---

## 📋 软件简介

Schomepage主页生成系统是一个功能强大的HTML图文文章编辑器工作站，基于Python Flask + JavaScript构建。该系统专为教育工作者、学生、个人博主和小型团队设计，提供可视化的内容创作和个性化主页构建能力。

### ✨ 主要功能特性

- **🔐 用户管理系统**: 完整的登录注册系统，支持邮箱验证和端到端密码加密
- **✍️ 可视化编辑器**: 类似Word的图形化操作界面，支持文本、图片、格式化等
- **🖼️ 素材管理中心**: 集成背景图片库、图标库和个人图片管理
- **🎭 动态内容推送**: 通过"动态隐藏模块"实现针对不同访客类型的个性化内容展示
- **🌐 访客通道管理**: 支持别名访问和访客身份识别
- **📊 访客统计分析**: 跟踪不同类型访客的访问情况，提供数据支持
- **🔗 文章链接功能**: 支持文章间的相互链接和导航结构

---

## 💻 系统要求

### 最低系统要求
- **操作系统**: Windows 10/11, macOS, Linux
- **Python版本**: Python 3.7 或更高版本（推荐 Python 3.13）
- **内存**: 至少 2GB RAM
- **存储空间**: 至少 2GB 可用磁盘空间
- **网络**: 稳定的网络连接（用于邮件验证功能）
- **浏览器**: Chrome, Firefox, Edge, Safari（支持现代Web标准）

### 推荐配置
- **操作系统**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python版本**: Python 3.11 或 3.13
- **内存**: 4GB RAM 或更多
- **存储空间**: 5GB 可用磁盘空间
- **浏览器**: 最新版本的Chrome或Firefox

---

## 🚀 安装说明

### 方法一：自动化安装（推荐）

#### 1. 下载并解压软件包
1. 下载 `Schomepage_final.zip` 软件包
2. 解压到您希望安装的目录（如 `D:\Schomepage_final`）
3. 确保解压后的文件夹包含 `login` 和 `workplace` 两个主要目录

#### 2. 检查Python环境
打开命令行终端（Windows: 按 `Win+R`，输入 `cmd`；macOS/Linux: 打开Terminal），运行以下命令：

```bash
# 检查Python版本
python --version
# 或者
python3 --version

# 检查pip包管理器
pip --version
# 或者
pip3 --version
```

**如果Python未安装**：
- Windows: 前往 [python.org](https://www.python.org) 下载安装，安装时务必勾选"Add Python to PATH"
- macOS: 使用Homebrew: `brew install python3`
- Linux: 使用包管理器: `sudo apt-get install python3 python3-pip`

#### 3. 安装项目依赖
导航到项目的 `login` 文件夹并安装依赖：

```bash
# 进入项目的login目录
cd path/to/your/Schomepage_final/login

# 安装依赖包
pip install -r requirements.txt

# 或手动安装
pip install Flask==2.3.3 flask-cors==4.0.0 Werkzeug==2.3.7
```

### 方法二：手动安装

如果自动安装遇到问题，可以按以下步骤手动安装：

#### 1. 逐步安装依赖包
```bash
pip install Flask==2.3.3
pip install flask-cors==4.0.0
pip install Werkzeug==2.3.7
```

#### 2. 验证安装
```bash
python -c "import flask; print('Flask安装成功')"
python -c "import flask_cors; print('Flask-CORS安装成功')"
```

### 安装故障排除

#### 问题1: pip安装失败
**解决方案**:
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 或者升级pip
python -m pip install --upgrade pip
```

#### 问题2: 权限问题
**解决方案**:
```bash
# Windows: 以管理员身份运行命令行
# macOS/Linux: 使用sudo
sudo pip install -r requirements.txt
```

#### 问题3: Python版本兼容性
**解决方案**:
- 确保使用Python 3.7+版本
- 如有多个Python版本，使用 `python3` 和 `pip3` 命令

---

## ▶️ 启动与初次使用

### 启动服务器

#### 方法1：标准启动（推荐）
1. 打开命令行终端
2. 导航到项目的 `login` 目录
3. 运行启动命令：

```bash
cd path/to/your/Schomepage_final/login
python server.py
```

#### 方法2：使用启动脚本
```bash
cd path/to/your/Schomepage_final/login
python start.py
```

#### 启动成功标志
看到以下信息表示启动成功：
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
 * Restarting with stat
 * Debugger is active!
```

**重要提示**: 请保持命令行窗口开启状态，关闭它将导致服务器停止运行。

### 访问系统

#### 1. 打开浏览器
推荐使用以下浏览器之一：
- Google Chrome（推荐）
- Mozilla Firefox
- Microsoft Edge
- Safari

#### 2. 访问登录页面
在浏览器地址栏输入：
```
http://localhost:5000
```

### 首次登录

#### 使用默认管理员账户
- **用户名**: `admin`
- **密码**: `123456`

#### 登录步骤
1. 在登录页面输入用户名和密码
2. 点击"登录"按钮
3. 成功登录后将自动跳转到主工作页面

---

## 📖 操作手册

### 🔑 用户管理

#### 注册新账户
1. **开始注册**
   - 在登录页面点击"账号注册"按钮
   - 注册弹窗将自动打开

2. **邮箱验证**
   - 输入有效的邮箱地址
   - 系统会自动检查邮箱是否已被注册
   - 完成人机验证（滑动验证）

3. **获取验证码**
   - 点击"发送验证码"按钮
   - 检查邮箱收取6位数字验证码
   - 验证码有效期：10分钟
   - 最多可重发5次

4. **完成注册**
   - 在10分钟内输入正确的验证码
   - 勾选服务条款复选框
   - 选择注册完成方式：
     - **设置密码**: 自定义6-16位密码
     - **直接登录**: 使用验证码作为登录密码

#### 修改密码
1. 登录到主页面
2. 点击用户名旁的设置图标
3. 选择"修改密码"
4. 输入当前密码和新密码
5. 确认修改

#### 会话管理
- **会话时长**: 24小时自动过期
- **活动检测**: 用户操作会自动续期会话
- **安全退出**: 点击"退出登录"或使用快捷键 `Ctrl+L`

### ✍️ 内容创作

#### 创建新文章
1. **启动编辑器**
   - 登录后点击"新建文章"按钮
   - 编辑器界面将在新页面打开

2. **文章基本信息**
   - 输入文章标题
   - 选择文章模板（可选）

3. **内容编辑**
   - 使用工具栏添加文本框
   - 设置文本格式（字体、大小、颜色、对齐方式）
   - 插入图片和媒体元素
   - 调整元素位置和大小

4. **保存文章**
   - 点击工具栏中的"保存"按钮
   - 系统会自动保存到您的个人工作区

#### 编辑现有文章
1. 在主页面的"我的文章"列表中找到要编辑的文章
2. 点击文章标题或"编辑"按钮
3. 在编辑器中进行修改
4. 完成后点击"保存"

#### 文章管理
- **查看文章列表**: 在主页面查看所有已创建的文章
- **删除文章**: 选择文章后点击删除按钮
- **复制文章**: 基于现有文章创建副本
- **文章配额**: 每个用户默认可创建30篇文章

### 🖼️ 素材管理

#### 上传图片
1. **访问素材库**
   - 在主页面点击左侧"素材库"
   - 选择"我的图片"选项卡

2. **上传新图片**
   - 点击"导入图片"按钮
   - 选择本地图片文件（支持JPG, PNG, GIF格式）
   - 等待上传完成

3. **管理图片**
   - 查看已上传图片的缩略图
   - 重命名或删除图片
   - 查看图片使用情况

#### 使用预设素材
1. **背景图片库**
   - 浏览系统预设的背景图片
   - 直接应用到文章背景

2. **图标库**
   - 选择合适的图标元素
   - 调整图标大小和颜色

#### 在文章中插入图片
1. 在编辑器中点击"插入图片"按钮
2. 从以下来源选择图片：
   - 我的图片
   - 背景图片库
   - 图标库
   - 本地上传
3. 调整图片位置和大小
4. 设置图片属性（链接、替代文本等）

### 🎭 动态内容推送

动态隐藏模块是Schomepage的特色功能，允许您为不同类型的访客展示个性化内容。

#### 设置动态隐藏规则
1. **选择目标元素**
   - 在编辑器中选择任意元素（文本框、图片等）
   - 点击右侧属性面板

2. **配置显示规则**
   - 找到"动态隐藏模块"设置区域
   - 选择规则类型：
     - **只给谁看**: 仅对指定类型访客可见
     - **不给谁看**: 对指定类型访客隐藏

3. **指定访客类型**
   - 在输入框中填入访客标识（如：student, teacher, visitor）
   - 多个类型用英文逗号分隔
   - 点击"应用规则"

#### 应用场景示例

**校园主页管理**:
- 通知公告只对学生可见：`只给谁看: student`
- 科研动态主要推送给教师：`只给谁看: teacher, researcher`
- 访客隐藏内部信息：`不给谁看: visitor, guest`

**企业门户网站**:
- 员工专区：`只给谁看: employee, staff`
- 客户服务：`只给谁看: customer, client`
- 合作伙伴专区：`只给谁看: partner`

#### 测试动态内容
1. 保存包含动态隐藏规则的文章
2. 使用不同的访客身份访问：
   ```
   http://localhost:5000/别名?user=student
   http://localhost:5000/别名?user=teacher
   http://localhost:5000/别名?user=visitor
   ```
3. 观察内容显示差异

### 🌐 访客通道管理

#### 创建访客通道
1. **设置文章别名**
   - 在主页面点击左侧"访客通道"
   - 选择要分享的文章
   - 为文章设置一个易记的别名

2. **生成访客链接**
   - 系统会自动生成访客访问链接
   - 基本格式：`http://localhost:5000/别名`
   - 带身份标识：`http://localhost:5000/别名?user=类型`

3. **管理现有通道**
   - 查看所有已创建的访客通道
   - 修改别名或删除通道
   - 查看通道访问统计

#### 分享文章给访客
1. **复制访客链接**
   - 从访客通道管理页面复制链接
   - 可以选择是否包含访客类型参数

2. **通过社交媒体分享**
   - 将链接发送给目标访客
   - 访客无需登录即可查看内容

3. **二维码分享（可选功能）**
   - 生成文章的二维码
   - 方便移动设备访问

### 📊 访客统计分析

#### 查看统计数据
1. **访问统计页面**
   - 在主页面点击左侧"访客统计"
   - 选择要查看的文章或时间范围

2. **统计指标解读**
   - **访问次数**: 各类访客的总访问量
   - **访客类型分布**: 不同身份访客的比例
   - **热门内容**: 最受欢迎的文章或模块
   - **访问趋势**: 时间维度的访问变化

#### 数据驱动的内容优化
1. **分析访客偏好**
   - 识别不同类型访客关注的内容
   - 发现被忽视的重要信息

2. **优化动态隐藏规则**
   - 根据统计数据调整内容显示策略
   - 提高信息传递的精准度

3. **内容推荐**
   - 为高访问量内容增加更多相关信息
   - 调整低访问量内容的展示方式

### 🔗 文章链接功能

#### 创建文章间链接
1. **插入链接**
   - 在编辑器中选择文本或元素
   - 点击工具栏中的"插入链接"按钮

2. **链接类型选择**
   - **内部文章链接**: 链接到您的其他文章
   - **外部链接**: 链接到外部网站
   - **锚点链接**: 链接到当前文章的特定位置

3. **设置链接属性**
   - 输入链接地址
   - 设置打开方式（当前窗口/新窗口）
   - 添加链接描述

#### 构建导航结构
1. **创建主页导航**
   - 设计主页作为网站入口
   - 添加到各个子页面的链接

2. **分类页面组织**
   - 按主题或功能创建文章分类
   - 建立层次化的导航结构

3. **相关文章推荐**
   - 在文章末尾添加相关文章链接
   - 提高内容的连接性和用户体验

---

## 🔧 高级设置与配置

### 邮件服务器配置

如需修改邮件服务设置，请编辑 `login/server.py` 文件中的SMTP配置：

```python
# 邮件服务器配置
SMTP_SERVER = "smtp.163.com"          # SMTP服务器地址
SMTP_PORT_SSL = 465                   # SSL端口
SMTP_USER = "your_email@163.com"      # 发送邮箱
SMTP_PASSWORD = "your_authorization_code"  # 邮箱授权码
```

**配置步骤**:
1. 申请邮箱的SMTP服务（如163邮箱、QQ邮箱等）
2. 获取邮箱授权码（非登录密码）
3. 更新配置文件中的相关信息
4. 重启服务器使配置生效

### 系统调试模式

#### 开启前端调试
在 `login/config.js` 中设置：
```javascript
const DEBUG_MODE = true;  // 启用调试模式
const API_BASE_URL = 'http://localhost:5000';  // API地址
```

#### 开启后端调试
在 `login/server.py` 中设置：
```python
DEVELOPMENT_MODE = True   # 开发模式：跳过邮件发送，直接显示验证码
DEBUG_MODE = True         # 调试模式：显示详细日志
```

#### 调试信息查看
- **前端调试**: 按F12打开浏览器开发者工具，查看Console标签页
- **后端调试**: 在运行服务器的命令行窗口查看日志输出

### 安全设置优化

#### 密码策略调整
在 `login/server.py` 中可以修改密码安全策略：
```python
# 密码长度限制
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 16

# 验证码设置
VERIFICATION_CODE_LENGTH = 6
VERIFICATION_CODE_EXPIRE_MINUTES = 10
MAX_VERIFICATION_ATTEMPTS = 5
```

#### 会话安全配置
```python
# 会话超时时间（小时）
SESSION_TIMEOUT_HOURS = 24

# 自动续期阈值（小时）
SESSION_REFRESH_THRESHOLD = 2
```

### 文件存储配置

#### 修改存储路径
默认情况下，用户数据存储在 `../workplace/<username>/` 目录下。如需修改存储位置，请编辑：

```python
# 在server.py中修改基础路径
BASE_WORKPLACE_PATH = "../workplace"  # 修改为您的自定义路径
```

#### 文件配额管理
在 `login/registration_checklist.json` 中调整用户配额：
```json
{
  "csv_operations": {
    "columns": [
      {
        "name": "maxarticle",
        "type": "default_value",
        "value": 50,  # 修改默认文章数量限制
        "description": "用户可发布文章的最大数量限制"
      }
    ]
  }
}
```

---

## 🔄 升级方法

### 版本检查

#### 查看当前版本
1. **通过系统界面**:
   - 登录到主页面
   - 点击右上角的"系统信息"
   - 查看当前版本号

2. **通过文件检查**:
   - 查看 `README.txt` 文件中的版本信息
   - 检查 `login/版本更新与修复说明.md` 中的更新记录

#### 检查更新
定期访问项目官方网站或代码仓库，查看是否有新版本发布。

### 升级准备

#### 数据备份
在进行任何升级操作前，请务必备份您的数据：

1. **备份用户数据**:
   ```bash
   # 备份整个workplace目录
   cp -r workplace workplace_backup_YYYYMMDD
   
   # 备份用户信息
   cp login/users.csv login/users_backup_YYYYMMDD.csv
   ```

2. **备份配置文件**:
   ```bash
   cp login/server.py login/server_backup.py
   cp login/config.js login/config_backup.js
   ```

3. **导出文章内容**:
   - 通过系统界面导出重要文章
   - 保存为HTML或其他格式

#### 环境检查
```bash
# 检查Python环境
python --version

# 检查依赖包
pip list | grep -E "(flask|werkzeug|cors)"

# 检查磁盘空间
df -h  # Linux/macOS
dir   # Windows
```

### 升级操作

#### 方法1：覆盖升级（推荐）
1. **下载新版本**:
   - 下载最新版本的软件包
   - 解压到临时目录

2. **停止当前服务**:
   - 在运行服务器的命令行中按 `Ctrl+C`
   - 确认服务已完全停止

3. **替换程序文件**:
   ```bash
   # 备份当前版本
   mv Schomepage_final Schomepage_old
   
   # 部署新版本
   mv Schomepage_new Schomepage_final
   
   # 恢复数据文件
   cp Schomepage_old/login/users.csv Schomepage_final/login/
   cp -r Schomepage_old/workplace/* Schomepage_final/workplace/
   ```

4. **更新依赖**:
   ```bash
   cd Schomepage_final/login
   pip install -r requirements.txt --upgrade
   ```

5. **恢复自定义配置**:
   - 对比新旧配置文件
   - 手动合并自定义设置

#### 方法2：增量升级
适用于小版本更新：

1. **下载更新包**:
   - 获取增量更新文件
   - 查看更新说明文档

2. **应用更新**:
   ```bash
   # 停止服务
   # 应用更新文件
   # 重新启动服务
   ```

### 升级后验证

#### 功能测试
1. **基础功能验证**:
   - 测试登录功能
   - 验证文章编辑功能
   - 检查图片上传功能

2. **数据完整性检查**:
   - 确认所有用户账户正常
   - 验证现有文章内容完整
   - 检查图片文件是否正常显示

3. **新功能测试**:
   - 根据更新说明测试新增功能
   - 验证修复的问题是否解决

#### 回滚操作
如果升级后发现问题，可以回滚到之前版本：

```bash
# 停止当前服务
# 恢复备份
mv Schomepage_final Schomepage_failed
mv Schomepage_old Schomepage_final

# 重新启动服务
cd Schomepage_final/login
python server.py
```

### 升级故障排除

#### 常见升级问题

**问题1: 依赖包冲突**
```bash
# 解决方案：重新安装依赖
pip uninstall flask flask-cors werkzeug
pip install -r requirements.txt
```

**问题2: 数据文件格式不兼容**
- 查看版本更新说明中的数据迁移指南
- 使用提供的数据迁移脚本
- 必要时手动转换数据格式

**问题3: 配置文件冲突**
- 对比新旧配置文件的差异
- 手动合并重要的自定义配置
- 参考默认配置重新设置

**问题4: 文件权限问题**
```bash
# 修复文件权限
chmod -R 755 Schomepage_final/
chown -R user:group Schomepage_final/
```

---

## 🚨 故障排除

### 常见问题解决

#### 启动问题

**问题：Python命令无法识别**
```
解决方案：
1. 确认Python已正确安装
2. 检查PATH环境变量设置
3. 尝试使用 python3 命令
4. 重新安装Python并勾选"Add to PATH"
```

**问题：依赖包导入失败**
```
解决方案：
1. 重新安装依赖包：pip install -r requirements.txt
2. 检查Python虚拟环境
3. 使用 pip list 查看已安装包
4. 尝试手动安装：pip install flask flask-cors
```

**问题：端口5000被占用**
```
解决方案：
1. 查找占用进程：netstat -ano | findstr :5000
2. 结束占用进程或重启电脑
3. 修改server.py中的端口号
4. 使用其他端口启动：python server.py --port 5001
```

#### 访问问题

**问题：浏览器无法访问localhost:5000**
```
解决方案：
1. 确认服务器已成功启动
2. 检查防火墙设置
3. 尝试使用 127.0.0.1:5000
4. 清除浏览器缓存和Cookie
5. 尝试使用其他浏览器
```

**问题：页面显示异常或功能无法使用**
```
解决方案：
1. 按F12检查浏览器控制台错误
2. 刷新页面或硬刷新（Ctrl+F5）
3. 检查网络连接
4. 确认JavaScript已启用
```

#### 功能问题

**问题：登录失败**
```
解决方案：
1. 确认用户名密码正确
2. 检查users.csv文件是否存在
3. 查看服务器控制台错误信息
4. 尝试重新注册账户
```

**问题：邮件验证码收不到**
```
解决方案：
1. 检查邮箱地址是否正确
2. 查看垃圾邮件文件夹
3. 确认SMTP配置正确
4. 检查网络连接
5. 启用开发模式跳过邮件验证
```

**问题：文章保存失败**
```
解决方案：
1. 检查磁盘空间是否充足
2. 确认文件写入权限
3. 检查文章内容是否过大
4. 尝试重新登录
```

**问题：图片上传失败**
```
解决方案：
1. 检查图片格式是否支持（JPG/PNG/GIF）
2. 确认图片文件大小不超过限制
3. 检查pics目录权限
4. 尝试使用其他图片
```

### 日志分析

#### 前端日志
在浏览器中按F12，查看Console标签页：
```javascript
// 常见错误类型
[ERROR] Failed to fetch - 网络连接问题
[ERROR] 401 Unauthorized - 会话过期
[ERROR] 500 Internal Server Error - 服务器内部错误
```

#### 后端日志
在服务器控制台查看：
```python
# 常见日志信息
INFO: 用户登录成功
WARNING: 验证码发送失败
ERROR: 数据库操作异常
```

### 性能优化

#### 系统优化建议
1. **定期清理**:
   - 删除不需要的文章和图片
   - 清理临时文件和日志

2. **资源管理**:
   - 压缩大图片文件
   - 限制单篇文章的复杂度

3. **缓存优化**:
   - 清理浏览器缓存
   - 重启服务器释放内存

#### 监控系统状态
```bash
# 查看系统资源使用
# Windows
tasklist | findstr python

# Linux/macOS
top | grep python
ps aux | grep server.py
```

---

## 📞 技术支持

### 联系方式
- **项目开发团队**: 潘旭, 韦先轶, 刘远巍
- **技术支持**: 通过项目代码仓库提交问题报告
- **用户社区**: 参与用户讨论群组

### 获取帮助
1. **查看文档**: 优先阅读本用户文档和系统内置帮助
2. **问题报告**: 详细描述问题现象、操作步骤和错误信息
3. **日志收集**: 提供前端控制台日志和后端服务器日志
4. **环境信息**: 说明操作系统、Python版本、浏览器版本等

### 文档更新
- 本用户文档会随软件版本更新而更新
- 最新版本文档请访问项目官方页面
- 欢迎用户反馈文档改进建议

---

## 📝 附录

### 文件结构说明
```
Schomepage_final/
├── login/                          # 后端服务和认证模块
│   ├── server.py                   # Flask后端服务器
│   ├── auth.js                     # 前端认证逻辑
│   ├── register.js                 # 注册功能模块
│   ├── crypto.js                   # 前端加密模块
│   ├── crypto_utils.py             # 后端加密工具
│   ├── config.js                   # 系统配置文件
│   ├── index.html                  # 登录页面
│   ├── main.html                   # 主工作页面
│   ├── users.csv                   # 用户数据文件
│   ├── requirements.txt            # Python依赖包
│   └── registration_checklist.json # 注册操作清单
├── workplace/                      # 用户工作区
│   ├── admin/                      # 管理员用户目录
│   │   ├── article/                # 文章存储目录
│   │   └── pics/                   # 图片存储目录
│   └── share/                      # 共享资源目录
├── redirect.csv                    # 访客通道配置
└── README.txt                      # 项目说明文档
```

### 快捷键列表
- `Ctrl + L`: 快速退出登录
- `Ctrl + S`: 保存当前文章（在编辑器中）
- `Ctrl + Z`: 撤销操作（在编辑器中）
- `Ctrl + Y`: 重做操作（在编辑器中）
- `F12`: 打开浏览器开发者工具

### 版本历史摘要
- **v1.0**: 基础登录系统和编辑器
- **v1.1**: 注册功能和邮箱验证
- **v2.0**: 动态隐藏模块和访客管理
- **v2.1**: 配置管理优化和模块化重构
- **v2.5**: 访客统计分析和系统稳定性改进

### 开源协议
本软件遵循开源协议，详细信息请查看项目根目录下的LICENSE文件。

---

**文档结束**

*本文档最后更新时间：2025年1月* 