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

## 商品管理模块 (Products)

### 1. 品牌管理 (Brands)

#### 1.1 获取品牌列表
- **接口**: `/api/products/brands/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `is_active`: 是否启用（布尔值）
  - `search`: 搜索关键词（搜索名称和描述）
  - `page`: 页码
  - `page_size`: 每页数量
- **响应**:
  ```json
  {
    "count": "integer",
    "next": "string",
    "previous": "string",
    "results": [
      {
        "id": "integer",
        "name": "string",
        "description": "string",
        "logo_url": "string",
        "is_active": "boolean",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

#### 1.2 创建品牌
- **接口**: `/api/products/brands/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "name": "string",
    "description": "string",
    "logo_url": "string",
    "is_active": "boolean"
  }
  ```
- **响应**: 返回创建的品牌信息

#### 1.3 获取品牌详情
- **接口**: `/api/products/brands/{id}/`
- **方法**: `GET`
- **权限**: 需要认证
- **响应**: 返回品牌详细信息

#### 1.4 更新品牌
- **接口**: `/api/products/brands/{id}/`
- **方法**: `PUT`
- **权限**: 需要认证
- **请求参数**: 同创建品牌
- **响应**: 返回更新后的品牌信息

#### 1.5 删除品牌
- **接口**: `/api/products/brands/{id}/`
- **方法**: `DELETE`
- **权限**: 需要认证
- **响应**: `204 No Content`

### 2. 商品分类管理 (Categories)

#### 2.1 获取分类列表（树形结构）
- **接口**: `/api/products/categories/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `level`: 分类层级
  - `is_active`: 是否启用
  - `search`: 搜索关键词（搜索中英文名称）
- **响应**:
  ```json
  {
    "count": "integer",
    "next": "string",
    "previous": "string",
    "results": [
      {
        "id": "integer",
        "name_en": "string",
        "name": "string",
        "description": "string",
        "parent": "integer",
        "rank": "integer",
        "level": "integer",
        "is_last_level": "boolean",
        "is_active": "boolean",
        "children": [
          "递归的子分类数据..."
        ]
      }
    ]
  }
  ```

#### 2.2 获取所有分类（平铺列表）
- **接口**: `/api/products/categories/all_categories/`
- **方法**: `GET`
- **权限**: 需要认证
- **响应**: 返回所有分类的平铺列表

#### 2.3 创建分类
- **接口**: `/api/products/categories/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "name_en": "string",
    "name": "string",
    "description": "string",
    "parent": "integer",
    "rank": "integer",
    "level": "integer",
    "is_last_level": "boolean",
    "is_active": "boolean"
  }
  ```
- **响应**: 返回创建的分类信息

### 3. SPU管理

#### 3.1 获取SPU列表
- **接口**: `/api/products/spus/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `product_type`: 产品类型
  - `production_process`: 生产工艺
  - `brand`: 品牌ID
  - `category`: 分类ID
  - `is_active`: 是否启用
  - `poc`: 产品专员ID
  - `min_created_at`: 最早创建时间
  - `max_created_at`: 最晚创建时间
  - `search`: 搜索关键词（搜索编码、名称、备注）
  - `ordering`: 排序字段（created_at或updated_at）
- **响应**:
  ```json
  {
    "count": "integer",
    "next": "string",
    "previous": "string",
    "results": [
      {
        "id": "integer",
        "code": "string",
        "name": "string",
        "product_type": "string",
        "remark": "string",
        "sales_channel": "string",
        "design_elements": "string",
        "production_process": "string",
        "brand": {
          "id": "integer",
          "name": "string"
        },
        "category": {
          "id": "integer",
          "name_en": "string",
          "name": "string",
          "level": "integer"
        },
        "poc_name": "string",
        "is_active": "boolean",
        "created_at": "datetime",
        "updated_at": "datetime",
        "products": ["关联的SKU列表..."]
      }
    ]
  }
  ```

#### 3.2 创建SPU
- **接口**: `/api/products/spus/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "code": "string",
    "name": "string",
    "product_type": "string",
    "remark": "string",
    "sales_channel": "string",
    "design_elements": "string",
    "production_process": "string",
    "brand_id": "integer",
    "category_id": "integer",
    "poc": "integer"
  }
  ```

#### 3.3 切换SPU启用状态
- **接口**: `/api/products/spus/{id}/toggle_active/`
- **方法**: `POST`
- **权限**: 需要认证
- **响应**:
  ```json
  {
    "status": "success",
    "is_active": "boolean"
  }
  ```

### 4. SKU管理

#### 4.1 获取SKU列表
- **接口**: `/api/products/products/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `spu`: SPU ID
  - `material`: 材质
  - `color`: 颜色
  - `plating_process`: 电镀工艺
  - `is_reviewed`: 是否已审核
  - `is_active`: 是否启用
  - `min_weight`: 最小重量
  - `max_weight`: 最大重量
  - `search`: 搜索关键词
  - `ordering`: 排序字段
- **响应**:
  ```json
  {
    "count": "integer",
    "next": "string",
    "previous": "string",
    "results": [
      {
        "id": "integer",
        "code": "string",
        "name": "string",
        "spu": "integer",
        "material": "string",
        "color": "string",
        "plating_process": "string",
        "surface_treatment": "string",
        "weight": "number",
        "length": "integer",
        "width": "integer",
        "height": "integer",
        "other_dimensions": "string",
        "suppliers_list": "string",
        "main_image": "string",
        "images": ["string"],
        "is_reviewed": "boolean",
        "is_active": "boolean",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

#### 4.2 创建SKU
- **接口**: `/api/products/products/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**: 包含SKU的所有字段

#### 4.3 切换SKU审核状态
- **接口**: `/api/products/products/{id}/toggle_review/`
- **方法**: `POST`
- **权限**: 需要认证
- **响应**:
  ```json
  {
    "status": "success",
    "is_reviewed": "boolean"
  }
  ```

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
