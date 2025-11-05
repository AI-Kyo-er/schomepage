# Schomepage主页生成系统 - UML建模图

**项目名称**: Schomepage主页生成系统  
**开发团队**: 潘旭, 韦先轶, 刘远巍  
**文档版本**: v1.0 (2025年6月)

---

## 1. 实体关系图（ER图）

使用PlantUML语法绘制的实体关系图：

```plantuml
@startuml Schomepage_ER_Diagram
!define ENTITY(name,desc) entity name as "desc"
!define RELATIONSHIP(entity1,entity2,desc) entity1 ||--o{ entity2 : desc

skinparam entity {
    BackgroundColor lightblue
    BorderColor black
}

' 实体定义
ENTITY(User, "用户\n----\n+ username (PK)\n+ password\n+ maxarticle\n+ created_time")

ENTITY(Article, "文章\n----\n+ filename (PK)\n+ title\n+ content\n+ created_time\n+ modified_time")

ENTITY(Image, "图片\n----\n+ filename (PK)\n+ upload_time\n+ file_size\n+ file_path")

ENTITY(Alias, "访客通道\n----\n+ alias_name (PK)\n+ target_article\n+ owner_username\n+ created_time")

ENTITY(AccessRecord, "访客记录\n----\n+ visitor_type\n+ access_count\n+ last_access\n+ article_id")

ENTITY(DynamicHideRule, "动态隐藏规则\n----\n+ element_id\n+ hide_rule\n+ target_users\n+ article_id")

' 关系定义
RELATIONSHIP(User, Article, "创建")
RELATIONSHIP(User, Image, "上传")
RELATIONSHIP(User, Alias, "管理")
RELATIONSHIP(Article, AccessRecord, "统计")
RELATIONSHIP(Article, DynamicHideRule, "包含")

note top of User : 存储在 users.csv
note top of Article : 存储在 ../workplace/<username>/article/
note top of Image : 存储在 ../workplace/<username>/pics/
note top of Alias : 存储在 redirect.csv
note top of AccessRecord : 存储在 accrecord.csv
note top of DynamicHideRule : 嵌入在HTML的data-hide-rule属性

@enduml
```

## 2. 类图（Class Diagram）

### 2.1 后端类图

```plantuml
@startuml Schomepage_Backend_Classes
package "后端核心模块" {
    
    class FlaskApplication {
        +app: Flask
        +CORS: Flask_CORS
        --
        +index(): str
        +login(): Response
        +register(): Response
        +send_verification_code(): Response
        +verify_code(): Response
        +get_articles(): Response
        +save_article(): Response
        +delete_article(): Response
        +upload_image(): Response
        +get_images(): Response
        +alias_access(): Response
        +get_visitor_stats(): Response
        +manage_alias(): Response
        --
        +run(): void
    }
    
    class CryptoUtils {
        +P: int = 2305843009213693951
        +G: int = 37
        --
        +convertToEncryptedHex(password: str, username: str): str
        +generatePrivateKey(username: str): int
        +modularExponentiation(base: int, exp: int, mod: int): int
        --
        {static} +encryptPassword(password: str, username: str): str
    }
    
    class CSVManager {
        --
        +readUsers(): List[Dict]
        +writeUser(userData: Dict): bool
        +updateUser(username: str, userData: Dict): bool
        +readRedirects(): List[Dict]
        +writeRedirect(redirectData: Dict): bool
        +readAccessRecord(articlePath: str): List[Dict]
        +updateAccessRecord(articlePath: str, visitorType: str): bool
    }
    
    class EmailService {
        +smtpServer: str
        +smtpPort: int
        +senderEmail: str
        +senderPassword: str
        --
        +sendVerificationCode(email: str, code: str): bool
        +generateVerificationCode(): str
        +validateEmailFormat(email: str): bool
    }
    
    class FileManager {
        --
        +createUserWorkspace(username: str): bool
        +saveArticle(username: str, filename: str, content: str): bool
        +loadArticle(username: str, filename: str): str
        +deleteArticle(username: str, filename: str): bool
        +saveImage(username: str, imageFile: File): str
        +getImageList(username: str): List[str]
    }
}

' 关系定义
FlaskApplication --> CryptoUtils : uses
FlaskApplication --> CSVManager : uses
FlaskApplication --> EmailService : uses
FlaskApplication --> FileManager : uses

@enduml
```

### 2.2 前端类图

```plantuml
@startuml Schomepage_Frontend_Classes
package "前端核心模块" {
    
    class AuthManager {
        +currentUser: string
        +sessionToken: string
        +loginTime: Date
        --
        +loginUser(email: str, password: str): Promise<boolean>
        +logoutUser(): void
        +checkLoginState(): boolean
        +requireAuth(): void
        +refreshSession(): void
        +isSessionValid(): boolean
    }
    
    class EditorManager {
        +canvas: HTMLElement
        +selectedElement: HTMLElement
        +undoStack: Array<State>
        +redoStack: Array<State>
        +maxUndoSteps: number
        --
        +initializeEditor(): void
        +addTextElement(x: number, y: number): void
        +addImageElement(imageSrc: str, x: number, y: number): void
        +addShapeElement(shapeType: str, x: number, y: number): void
        +selectElement(element: HTMLElement): void
        +deleteElement(element: HTMLElement): void
        +updateElementProperty(property: str, value: any): void
        +moveElement(element: HTMLElement, deltaX: number, deltaY: number): void
        +saveArticle(articleName: str): Promise<void>
        +loadArticle(articleName: str): Promise<void>
        +undo(): void
        +redo(): void
        +saveState(): void
    }
    
    class CryptoService {
        +P: number = 2305843009213693951
        +G: number = 37
        --
        +convertToEncryptedHex(password: str, username: str): string
        +generatePrivateKey(username: str): number
        +modularExponentiation(base: number, exp: number, mod: number): number
    }
    
    class DynamicHideManager {
        +currentUserType: string
        +hideRules: Map<string, HideRule>
        --
        +parseUserFromURL(): string
        +applyHideRules(): void
        +setElementHideRule(element: HTMLElement, rule: str, users: str): void
        +removeHideRule(element: HTMLElement): void
        +evaluateHideRule(rule: str, userType: str, targetUsers: str): boolean
        +updateVisibility(element: HTMLElement, visible: boolean): void
    }
    
    class MaterialManager {
        +backgroundImages: Array<string>
        +iconLibrary: Array<string>
        +userImages: Array<string>
        --
        +loadBackgroundImages(): Promise<Array<string>>
        +loadIconLibrary(): Promise<Array<string>>
        +loadUserImages(): Promise<Array<string>>
        +uploadUserImage(file: File): Promise<string>
        +deleteUserImage(filename: str): Promise<boolean>
        +insertMaterial(type: str, src: str): void
    }
    
    class ArticleManager {
        +articleList: Array<Article>
        +currentArticle: Article
        --
        +getArticleList(): Promise<Array<Article>>
        +createNewArticle(name: str): Promise<boolean>
        +openArticle(filename: str): Promise<void>
        +deleteArticle(filename: str): Promise<boolean>
        +renameArticle(oldName: str, newName: str): Promise<boolean>
        +getArticleInfo(filename: str): Article
    }
    
    class AliasManager {
        +aliasList: Array<Alias>
        --
        +createAlias(aliasName: str, targetArticle: str): Promise<boolean>
        +updateAlias(aliasName: str, newTarget: str): Promise<boolean>
        +deleteAlias(aliasName: str): Promise<boolean>
        +getAliasList(): Promise<Array<Alias>>
        +validateAliasName(name: str): boolean
    }
    
    class VisitorStatsManager {
        --
        +getVisitorStats(articleName: str): Promise<VisitorStats>
        +updateVisitorCount(articleName: str, visitorType: str): void
        +exportStatsData(articleName: str): Promise<string>
    }
}

' 关系定义
AuthManager --> CryptoService : uses
EditorManager --> DynamicHideManager : contains
EditorManager --> MaterialManager : uses
EditorManager --> ArticleManager : uses
ArticleManager --> AliasManager : uses
ArticleManager --> VisitorStatsManager : uses

' 数据传输对象
class Article {
    +filename: string
    +title: string
    +content: string
    +createdTime: Date
    +modifiedTime: Date
}

class Alias {
    +aliasName: string
    +targetArticle: string
    +ownerUsername: string
    +createdTime: Date
}

class VisitorStats {
    +visitorType: string
    +accessCount: number
    +lastAccess: Date
}

class HideRule {
    +ruleType: string
    +targetUsers: Array<string>
}

@enduml
```

## 3. 顺序图（Sequence Diagram）

### 3.1 用户注册流程

```plantuml
@startuml User_Registration_Sequence
participant "用户" as User
participant "注册页面" as RegisterPage
participant "前端加密" as CryptoService
participant "后端API" as Backend
participant "邮件服务" as EmailService
participant "CSV存储" as CSVStorage
participant "文件系统" as FileSystem

User -> RegisterPage: 输入注册信息
RegisterPage -> CryptoService: 加密密码
CryptoService -> RegisterPage: 返回加密密码

RegisterPage -> Backend: POST /register\n(邮箱, 加密密码)
Backend -> Backend: 验证邮箱格式
Backend -> CSVStorage: 检查邮箱唯一性
CSVStorage -> Backend: 返回检查结果

alt 邮箱已存在
    Backend -> RegisterPage: 返回错误: 邮箱已注册
    RegisterPage -> User: 显示错误信息
else 邮箱可用
    Backend -> EmailService: 发送验证码
    EmailService -> User: 邮件发送验证码
    Backend -> RegisterPage: 返回: 验证码已发送
    
    User -> RegisterPage: 输入验证码
    RegisterPage -> Backend: POST /verify_code\n(邮箱, 验证码)
    Backend -> Backend: 验证码校验
    
    alt 验证码正确
        Backend -> CSVStorage: 写入用户数据
        CSVStorage -> Backend: 写入成功
        Backend -> FileSystem: 创建用户工作目录
        FileSystem -> Backend: 目录创建成功
        Backend -> RegisterPage: 返回: 注册成功
        RegisterPage -> User: 显示注册成功
    else 验证码错误
        Backend -> RegisterPage: 返回错误: 验证码不正确
        RegisterPage -> User: 显示错误信息
    end
end

@enduml
```

### 3.2 文章编辑与保存流程

```plantuml
@startuml Article_Edit_Save_Sequence
participant "用户" as User
participant "编辑器" as Editor
participant "属性面板" as PropertyPanel
participant "素材库" as MaterialLib
participant "后端API" as Backend
participant "文件系统" as FileSystem

User -> Editor: 拖拽元素到画布
Editor -> Editor: 创建DOM元素
Editor -> Editor: 添加事件监听
Editor -> User: 显示新元素

User -> Editor: 选中元素
Editor -> PropertyPanel: 显示元素属性
PropertyPanel -> User: 展示属性面板

User -> PropertyPanel: 修改属性值
PropertyPanel -> Editor: 更新DOM元素
Editor -> Editor: 应用新属性
Editor -> User: 显示更新后的元素

User -> Editor: 插入图片
Editor -> MaterialLib: 打开素材库
MaterialLib -> User: 显示图片选择界面

User -> MaterialLib: 选择图片
MaterialLib -> Backend: GET /api/images\n获取图片路径
Backend -> MaterialLib: 返回图片URL
MaterialLib -> Editor: 返回选中图片信息
Editor -> Editor: 创建图片元素
Editor -> User: 显示插入的图片

User -> Editor: 保存文章
Editor -> Editor: 获取画布HTML内容
Editor -> Editor: 处理动态隐藏规则
Editor -> Backend: POST /api/save_article\n(文章名, HTML内容)

Backend -> Backend: 验证用户权限
Backend -> FileSystem: 写入HTML文件
FileSystem -> Backend: 写入成功

Backend -> Editor: 返回: 保存成功
Editor -> User: 显示保存成功提示

@enduml
```

### 3.3 动态隐藏模块访问流程

```plantuml
@startuml Dynamic_Hide_Access_Sequence
participant "访客" as Visitor
participant "浏览器" as Browser
participant "前端JS" as Frontend
participant "后端API" as Backend
participant "访客统计" as VisitorStats
participant "文件系统" as FileSystem

Visitor -> Browser: 访问别名URL\n(例: /course-intro&user=student)
Browser -> Backend: GET /<alias>?user=<type>

Backend -> Backend: 解析别名
Backend -> FileSystem: 读取目标文章
FileSystem -> Backend: 返回文章HTML内容

Backend -> VisitorStats: 记录访客统计
VisitorStats -> FileSystem: 更新accrecord.csv
FileSystem -> VisitorStats: 更新成功

Backend -> Browser: 返回HTML内容\n+ 用户类型参数
Browser -> Frontend: 加载页面JS

Frontend -> Frontend: 解析URL中的user参数
Frontend -> Frontend: 获取当前访客类型

Frontend -> Frontend: 遍历所有有hide-rule的元素
loop 对每个元素
    Frontend -> Frontend: 读取data-hide-rule属性
    Frontend -> Frontend: 读取data-hide-users属性
    Frontend -> Frontend: 评估隐藏规则
    
    alt 规则为show-only且用户类型匹配
        Frontend -> Frontend: 显示元素
    else 规则为hide-for且用户类型匹配
        Frontend -> Frontend: 隐藏元素
    else 无匹配规则
        Frontend -> Frontend: 保持默认状态
    end
end

Frontend -> Browser: 应用最终显示规则
Browser -> Visitor: 显示个性化内容

note right of Visitor
访客看到根据其身份
定制的页面内容
end note

@enduml
```

### 3.4 用户登录与会话管理流程

```plantuml
@startuml Login_Session_Management_Sequence
participant "用户" as User
participant "登录页面" as LoginPage
participant "前端加密" as CryptoService
participant "后端API" as Backend
participant "会话存储" as SessionStorage
participant "主编辑页" as MainPage

User -> LoginPage: 输入邮箱和密码
LoginPage -> CryptoService: 加密密码
CryptoService -> LoginPage: 返回加密密码

LoginPage -> Backend: POST /login\n(邮箱, 加密密码)
Backend -> Backend: 从CSV读取用户数据
Backend -> Backend: 比对加密密码

alt 密码正确
    Backend -> SessionStorage: 创建会话记录
    SessionStorage -> Backend: 返回会话ID
    Backend -> LoginPage: 返回: 登录成功 + 会话信息
    LoginPage -> MainPage: 跳转到主编辑页
    
    MainPage -> Backend: GET /api/user_info\n验证会话
    Backend -> SessionStorage: 检查会话有效性
    SessionStorage -> Backend: 会话有效
    Backend -> MainPage: 返回用户信息
    MainPage -> User: 显示主界面

    note over SessionStorage: 会话24小时有效期\n用户活动自动续期

else 密码错误
    Backend -> LoginPage: 返回错误: 用户名或密码错误
    LoginPage -> User: 显示错误信息
end

' 会话超时处理
...用户操作一段时间后...

MainPage -> Backend: API请求 (任意操作)
Backend -> SessionStorage: 检查会话
alt 会话过期
    SessionStorage -> Backend: 会话已过期
    Backend -> MainPage: 返回: 401 未授权
    MainPage -> LoginPage: 自动跳转到登录页
    LoginPage -> User: 提示重新登录
else 会话有效
    SessionStorage -> Backend: 会话有效
    Backend -> SessionStorage: 更新活动时间
    Backend -> MainPage: 正常响应
end

@enduml
```

---

## 使用说明

这些UML图表使用PlantUML语法编写，可以通过以下方式查看：

1. **在线查看**: 复制代码到 [PlantUML在线编辑器](http://www.plantuml.com/plantuml/uml/)
2. **VS Code插件**: 安装"PlantUML"插件，直接在编辑器中预览
3. **生成图片**: 使用PlantUML工具生成PNG/SVG格式图片

### 图表说明

- **ER图**: 展示了系统数据模型和实体间关系，基于CSV文件存储结构设计
- **类图**: 分别展示了后端Flask应用和前端JavaScript模块的类结构设计
- **顺序图**: 详细描述了用户注册、文章编辑、动态隐藏访问、登录会话等核心业务流程

这些图表为Schomepage系统的架构理解、代码维护和功能扩展提供了重要的参考文档。 