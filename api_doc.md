# Magic API 接口文档

## 通用说明

### 1. 认证要求
所有接口都需要在请求头中携带JWT令牌：
```
Authorization: Bearer <access_token>
```

### 2. 响应格式
- 列表接口都支持分页
- 支持过滤和搜索
- 大部分接口支持排序

### 3. 错误响应
```json
{
  "detail": "错误信息"
}
```

### 4. 状态码
- 200: 请求成功
- 201: 创建成功
- 204: 删除成功
- 400: 请求参数错误
- 401: 未认证或认证失败
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误

## 一、用户认证模块 (Authentication)

### 1. 用户登录
- **接口**: `/api/auth/token/`
- **方法**: `POST`
- **权限**: 无需认证
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
    "access": "string",
    "refresh": "string"
  }
  ```

### 2. 刷新令牌
- **接口**: `/api/auth/token/refresh/`
- **方法**: `POST`
- **请求参数**:
  ```json
  {
    "refresh": "string"
  }
  ```
- **响应**:
  ```json
  {
    "access": "string"
  }
  ```

### 3. 获取用户信息
- **接口**: `/api/auth/users/profile/`
- **方法**: `GET`
- **权限**: 需要认证
- **响应**:
  ```json
  {
    "id": "integer",
    "username": "string",
    "email": "string",
    "phone": "string",
    "department": "string",
    "position": "string",
    "is_active": "boolean",
    "first_name": "string",
    "last_name": "string"
  }
  ```

## 二、商品管理模块 (Products)

### 1. 品牌管理 (Brands)
#### 1.1 获取品牌列表
- **接口**: `/api/products/brands/`
- **方法**: `GET`
- **查询参数**:
  - `is_active`: 是否启用
  - `search`: 搜索关键词
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "name": "string",
        "description": "string",
        "logo_url": "string",
        "is_active": "boolean"
      }
    ]
  }
  ```

### 2. 商品分类 (Categories)
#### 2.1 获取分类列表
- **接口**: `/api/products/categories/`
- **方法**: `GET`
- **查询参数**:
  - `level`: 分类层级
  - `is_active`: 是否启用
  - `search`: 搜索关键词

### 3. SPU管理
#### 3.1 获取SPU列表
- **接口**: `/api/products/spus/`
- **方法**: `GET`
- **查询参数**:
  - `product_type`: 产品类型
  - `brand`: 品牌ID
  - `category`: 分类ID
  - `is_active`: 是否启用
  - `search`: 搜索关键词

### 4. SKU管理
#### 4.1 获取SKU列表
- **接口**: `/api/products/products/`
- **方法**: `GET`
- **查询参数**:
  - `spu`: SPU ID
  - `material`: 材质
  - `is_reviewed`: 是否已审核
  - `is_active`: 是否启用
  - `search`: 搜索关键词

## 三、生产管理模块 (Production)

### 1. 生产类目管理 (Categories)
#### 1.1 获取生产类目列表
- **接口**: `/api/production/categories/`
- **方法**: `GET`
- **查询参数**:
  - `category_type`: 类目类型
  - `is_active`: 是否启用
  - `search`: 搜索关键词

### 2. 生产任务管理 (Orders)
#### 2.1 获取任务列表
- **接口**: `/api/production/orders/`
- **方法**: `GET`
- **查询参数**:
  - `order_type`: 生产类型
  - `status`: 状态
  - `priority`: 优先级
  - `manager`: 主管ID
  - `search`: 搜索关键词

#### 2.2 获取下一个任务编号
- **接口**: `/api/production/orders/next_id/`
- **方法**: `GET`
- **响应**:
  ```json
  {
    "code": "string"  // 例如：D2403070001
  }
  ```

#### 2.3 上传任务主图
- **接口**: `/api/production/orders/{id}/upload_image/`
- **方法**: `POST`
- **Content-Type**: `multipart/form-data`
- **请求参数**:
  ```json
  {
    "main_image": "file"
  }
  ```

### 3. 生产步骤管理 (Steps)
#### 3.1 获取步骤列表
- **接口**: `/api/production/steps/`
- **方法**: `GET`
- **查询参数**:
  - `order`: 任务ID
  - `step_type`: 步骤类型
  - `status`: 状态
  - `operator`: 操作员ID

### 4. 生产评论管理 (Comments)
#### 4.1 获取评论列表
- **接口**: `/api/production/comments/`
- **方法**: `GET`
- **查询参数**:
  - `order`: 任务ID
  - `step`: 步骤ID
  - `comment_type`: 评论类型
  - `author`: 评论人ID

### 5. 生产渠道管理 (Channels)
#### 5.1 获取渠道列表
- **接口**: `/api/production/channels/`
- **方法**: `GET`
- **查询参数**:
  - `is_active`: 是否启用
  - `search`: 搜索关键词
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "code": "string",
        "name": "string",
        "description": "string",
        "is_active": "boolean"
      }
    ]
  }
  ``` 