# 表单报名页面

一个简洁美观的在线报名表单页面实现，参考 InfoQ 表单页面设计，使用原生技术栈开发，无需大型框架。

## 技术栈

- **前端**：纯原生 HTML + CSS + JavaScript
- **后端**：Python (Flask)
- **数据存储**：SQLite 数据库（生产环境建议使用 PostgreSQL 或 MySQL）

## 功能特性

✅ 响应式设计，支持 PC、平板、手机  
✅ 实时表单验证  
✅ 友好的错误提示  
✅ 提交加载状态  
✅ 成功反馈提示  
✅ 美观的 UI 设计  

## 快速开始

### 方式一：仅前端（无需后端）

直接用浏览器打开 `index.html` 文件即可查看页面。

> 注意：这种方式提交会失败，但可以在浏览器控制台查看提交的数据。

### 方式二：使用 Python 后端

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **启动服务器**
```bash
python server.py
```

3. **访问页面**
打开浏览器访问：http://localhost:5000

### 方式三：使用 Docker 部署（推荐）

#### 方法一：使用 Docker 构建和运行

1. **构建 Docker 镜像**
```bash
docker build -t team-registration .
```

2. **运行容器**
```bash
# Windows
docker run -d -p 5000:5000 -v %cd%:/app --name team-registration-app team-registration

# Linux/macOS
docker run -d -p 5000:5000 -v $(pwd):/app --name team-registration-app team-registration
```

3. **访问页面**
打开浏览器访问：http://localhost:5000

#### 方法二：使用 Docker Compose（推荐）

1. **启动服务**
```bash
docker-compose up -d
```

2. **访问页面**
打开浏览器访问：http://localhost:5000

3. **停止服务**
```bash
docker-compose down
```

**注意**：
- 使用 Docker 部署时，SQLite 数据库文件 (`users.db`) 将直接保存在项目根目录中，宿主机可以直接访问
- 确保项目目录有足够的磁盘空间来存储数据库文件
- 如果使用 docker-compose，整个项目目录将被挂载到容器中，所有文件的更改都会同步到宿主机

## 项目结构

```
.
├── web/                # 前端文件目录
│   ├── index.html     # 主页面
│   ├── styles.css     # 样式文件
│   ├── script.js      # 前端逻辑
│   └── qr_code.png    # 二维码图片
├── server.py          # Python 后端
├── requirements.txt   # Python 依赖配置
├── Dockerfile         # Docker 构建文件
├── docker-compose.yml # Docker Compose 配置
├── .dockerignore      # Docker 忽略文件
├── data/              # 数据目录（Docker 挂载，自动创建）
├── users.db          # SQLite 数据库文件（自动生成）
└── README.md         # 说明文档
```

## API 接口

### 提交团队信息

**POST** `/api/team/submit`

**请求体：**
```json
{
  "team_info": {
    "team_name": "团队名称",
    "competition_track": "技术挑战赛",
    "project_name": "作品名称",
    "repo_url": "https://github.com/user/repo",
    "costrict_uid": "用户ID",
    "project_intro": "项目简介...",
    "tech_solution": "技术方案...",
    "goals_and_outlook": "目标与展望..."
  },
  "members": [
    {
      "name": "张三",
      "is_captain": true,
      "school": "XX大学",
      "department": "计算机学院",
      "major_grade": "计算机科学 大三",
      "phone": "13800138000",
      "email": "zhangsan@example.com",
      "student_id": "学号",
      "role": "前端开发",
      "tech_stack": "HTML, CSS, JavaScript"
    }
  ]
}
```

**响应：**
```json
{
  "success": true,
  "message": "团队信息提交成功！",
  "team_id": 1
}
```

### 获取所有团队信息（管理接口）

**GET** `/api/teams`

**响应：**
```json
{
  "success": true,
  "count": 10,
  "data": [...]
}
```

### 获取特定团队信息

**GET** `/api/team/<team_id>`

**响应：**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "team_name": "团队名称",
    "competition_track": "技术挑战赛",
    "project_name": "作品名称",
    "members": [...]
  }
}
```

## 表单字段说明

### 团队信息必填字段
- **团队名称**：团队名称（20字内）
- **参赛赛道**：技术挑战赛 或 创新应用赛
- **作品名称**：作品名称（20字内）
- **CoStrict 用户ID**：用于接收Credits，插件端点击"查看账户详情"可复制

### 团队信息选填字段
- **代码仓库链接**：GitHub仓库链接，可在提交作品后公开该仓库
- **项目简介**：200-500字
- **技术方案**：200-500字
- **目标与展望**：200-500字

### 团队成员必填字段
- **姓名**：至少2个字符
- **学校/单位**：学校或单位名称
- **学院/系别**：学院或系别
- **专业与年级**：例如：计算机科学 大三
- **联系电话**：11位手机号（1开头）
- **电子邮箱**：标准邮箱格式
- **项目角色**：例如：前端开发、后端开发、算法、UI/UX设计、产品经理等

### 团队成员选填字段
- **学号**：用于身份验证，可选
- **技术栈/擅长领域**：例如：Python, React, Node.js, TensorFlow, Figma

## 自定义配置

### 修改 API 地址

在 `script.js` 文件中找到：
```javascript
const response = await fetch('/api/form/submit', {
```

修改为你的实际 API 地址。

### 修改样式

直接编辑 `styles.css` 文件，所有样式都有清晰的注释。

### 添加验证规则

在 `script.js` 的 `validationRules` 对象中添加新的验证规则：
```javascript
const validationRules = {
    // 添加新字段
    new_field: {
        validate: (value) => value.length > 0,
        message: '错误提示信息'
    }
};
```

## 部署建议

### 静态托管（仅前端）

- GitHub Pages
- Netlify
- Vercel
- 任何静态文件托管服务

### 完整部署（前端 + 后端）

**Python 版本：**
- Heroku
- Railway
- PythonAnywhere
- 自建服务器

### 生产环境建议

1. **使用数据库**：当前已使用 SQLite，生产环境建议使用 PostgreSQL 或 MySQL
2. **添加验证码**：防止机器人提交
3. **HTTPS**：确保数据传输安全
4. **CSRF 防护**：添加 CSRF Token
5. **邮件通知**：提交成功后发送确认邮件
6. **日志记录**：记录所有提交操作
7. **使用反向代理**：如 Nginx，处理静态文件和负载均衡
8. **容器化部署**：使用 Docker 或 Kubernetes 进行容器化部署
9. **环境变量管理**：使用环境变量管理敏感配置
10. **健康检查**：实现健康检查接口，便于监控系统状态

## 浏览器兼容性

- Chrome/Edge（最新版）
- Firefox（最新版）
- Safari（最新版）
- 移动端浏览器

## 许可证

MIT License

## 注意事项

- 当前实现使用 SQLite 数据库存储数据，适合中小规模使用
- 生产环境建议使用 PostgreSQL 或 MySQL 数据库
- 建议添加更多的安全措施（验证码、CSRF 防护等）
- 可以根据实际需求扩展功能（文件上传、多步骤表单等）
- 使用 Docker 部署时，请确保数据目录 (./data) 有足够的磁盘空间

