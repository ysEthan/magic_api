# API 接口文档

## 用户认证模块 (Authentication)

### 1. 用户注册
- **接口**: `/api/auth/users/`
- **方法**: `POST`
- **权限**: 允许所有用户
- **请求参数**:
  ```json
  {
    "username": "string",     // 用户名
    "password": "string",     // 密码
    "email": "string",        // 邮箱
    "phone": "string",        // 手机号（可选）
    "department": "string",   // 部门（可选）
    "position": "string"      // 职位（可选）
  }
  ```
- **响应**:
  ```json
  {
    "id": "integer",
    "username": "string",
    "email": "string",
    "phone": "string",
    "department": "string",
    "position": "string",
    "is_active": "boolean"
  }
  ```

### 2. 用户登录
- **接口**: `/api/auth/token/`
- **方法**: `POST`
- **权限**: 允许所有用户
- **请求参数**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **响应**:
  ```json
  {
    "access": "string",    // JWT访问令牌
    "refresh": "string"    // JWT刷新令牌
  }
  ```

### 3. 刷新Token
- **接口**: `/api/auth/token/refresh/`
- **方法**: `POST`
- **权限**: 允许所有用户
- **请求参数**:
  ```json
  {
    "refresh": "string"    // JWT刷新令牌
  }
  ```
- **响应**:
  ```json
  {
    "access": "string"     // 新的JWT访问令牌
  }
  ```

### 4. 获取用户个人信息
- **接口**: `/api/auth/users/profile/`
- **方法**: `GET`
- **权限**: 需要认证
- **请求头**:
  ```
  Authorization: Bearer <access_token>
  ```
- **响应**:
  ```json
  {
    "id": "integer",
    "username": "string",
    "email": "string",
    "phone": "string",
    "department": "string",
    "position": "string",
    "is_active": "boolean"
  }
  ```

### 5. 获取用户列表
- **接口**: `/api/auth/users/`
- **方法**: `GET`
- **权限**: 需要认证
- **请求头**:
  ```
  Authorization: Bearer <access_token>
  ```
- **查询参数**:
  - `page`: 页码（默认1）
  - `page_size`: 每页数量（默认10）
- **响应**:
  ```json
  {
    "count": "integer",
    "next": "string",
    "previous": "string",
    "results": [
      {
        "id": "integer",
        "username": "string",
        "email": "string",
        "phone": "string",
        "department": "string",
        "position": "string",
        "is_active": "boolean"
      }
    ]
  }
  ```

### 6. 获取特定用户信息
- **接口**: `/api/auth/users/{id}/`
- **方法**: `GET`
- **权限**: 需要认证
- **请求头**:
  ```
  Authorization: Bearer <access_token>
  ```
- **响应**:
  ```json
  {
    "id": "integer",
    "username": "string",
    "email": "string",
    "phone": "string",
    "department": "string",
    "position": "string",
    "is_active": "boolean"
  }
  ```

### 7. 更新用户信息
- **接口**: `/api/auth/users/{id}/`
- **方法**: `PUT`
- **权限**: 需要认证
- **请求头**:
  ```
  Authorization: Bearer <access_token>
  ```
- **请求参数**:
  ```json
  {
    "username": "string",
    "email": "string",
    "phone": "string",
    "department": "string",
    "position": "string"
  }
  ```
- **响应**:
  ```json
  {
    "id": "integer",
    "username": "string",
    "email": "string",
    "phone": "string",
    "department": "string",
    "position": "string",
    "is_active": "boolean"
  }
  ```

### 8. 删除用户
- **接口**: `/api/auth/users/{id}/`
- **方法**: `DELETE`
- **权限**: 需要认证
- **请求头**:
  ```
  Authorization: Bearer <access_token>
  ```
- **响应**: `204 No Content`

## 认证说明

1. 所有需要认证的接口都需要在请求头中携带JWT令牌：
   ```
   Authorization: Bearer <access_token>
   ```

2. access_token的有效期为60分钟，refresh_token的有效期为1天。

3. 当access_token过期时，可以使用refresh_token获取新的access_token。

4. 错误响应格式：
   ```json
   {
     "detail": "错误信息"
   }
   ```

## 状态码说明

- 200: 请求成功
- 201: 创建成功
- 204: 删除成功
- 400: 请求参数错误
- 401: 未认证或认证失败
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误
