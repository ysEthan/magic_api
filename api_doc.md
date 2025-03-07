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

## 生产管理模块 (Production)

### 1. 生产类目管理 (Categories)

#### 1.1 获取生产类目列表
- **接口**: `/api/production/categories/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `category_type`: 类目类型 (resin/metal/ceramic/plush)
  - `is_active`: 是否启用
  - `search`: 搜索关键词（搜索编码、名称和描述）
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
        "category_type": "string",
        "description": "string",
        "is_active": "boolean",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

#### 1.2 创建生产类目
- **接口**: `/api/production/categories/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "code": "string",
    "name": "string",
    "category_type": "string",
    "description": "string",
    "is_active": "boolean"
  }
  ```

### 2. 生产任务管理 (Orders)

#### 2.1 获取生产任务列表
- **接口**: `/api/production/orders/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `order_type`: 生产类型 (trial/mass)
  - `status`: 状态
  - `priority`: 优先级 (0-3)
  - `category`: 生产类目ID
  - `product`: 产品ID
  - `manager`: 生产主管ID
  - `created_by`: 创建人ID
  - `min_planned_start_date`: 最早计划开始日期
  - `max_planned_start_date`: 最晚计划开始日期
  - `min_created_at`: 最早创建时间
  - `max_created_at`: 最晚创建时间
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
        "product": "integer",  // 可选
        "product_info": {      // 如果有产品则返回产品信息
          "id": "integer",
          "code": "string",
          "name": "string"
        },
        "category": "integer", // 可选
        "category_info": {     // 如果有类目则返回类目信息
          "id": "integer",
          "code": "string",
          "name": "string",
          "category_type": "string",
          "category_type_display": "string"
        },
        "order_type": "string",
        "order_type_display": "string",
        "quantity": "integer",
        "priority": "integer",
        "priority_display": "string",
        "status": "string",
        "status_display": "string",
        "planned_start_date": "date",
        "planned_end_date": "date",
        "actual_start_date": "date",
        "actual_end_date": "date",
        "manager": "integer",
        "manager_info": {
          "id": "integer",
          "username": "string",
          "email": "string"
        },
        "description": "string",
        "technical_requirements": "string",
        "quality_requirements": "string",
        "created_by": "integer",
        "created_by_info": {
          "id": "integer",
          "username": "string",
          "email": "string"
        },
        "steps": ["生产步骤列表..."],
        "comments": ["评论列表..."],
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

#### 2.2 创建生产任务
- **接口**: `/api/production/orders/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "code": "string",
    "product": "integer",     // 可选
    "category": "integer",    // 可选
    "order_type": "string",   // trial/mass
    "quantity": "integer",
    "priority": "integer",    // 0-3
    "planned_start_date": "date",
    "planned_end_date": "date",
    "manager": "integer",
    "description": "string",
    "technical_requirements": "string",
    "quality_requirements": "string"
  }
  ```

### 3. 生产步骤管理 (Steps)

#### 3.1 获取生产步骤列表
- **接口**: `/api/production/steps/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `order`: 生产任务ID
  - `step_type`: 步骤类型
  - `status`: 状态
  - `operator`: 操作员ID
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
        "order": "integer",
        "step_type": "string",
        "step_type_display": "string",
        "name": "string",
        "sequence": "integer",
        "description": "string",
        "status": "string",
        "status_display": "string",
        "planned_duration": "string",
        "actual_duration": "string",
        "start_time": "datetime",
        "end_time": "datetime",
        "operator": "integer",
        "operator_info": {
          "id": "integer",
          "username": "string",
          "email": "string"
        },
        "quality_check_result": "string",
        "notes": "string",
        "attachments": ["string"],
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

#### 3.2 更新步骤状态
- **接口**: `/api/production/steps/{id}/update_status/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "status": "string"  // pending/in_progress/completed/on_hold
  }
  ```

### 4. 生产评论管理 (Comments)

#### 4.1 获取评论列表
- **接口**: `/api/production/comments/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `order`: 生产任务ID
  - `step`: 生产步骤ID
  - `comment_type`: 评论类型
  - `author`: 评论人ID
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
        "order": "integer",
        "step": "integer",
        "comment_type": "string",
        "comment_type_display": "string",
        "content": "string",
        "images": ["string"],
        "author": "integer",
        "author_info": {
          "id": "integer",
          "username": "string",
          "email": "string"
        },
        "parent": "integer",
        "replies": ["回复列表..."],
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

#### 4.2 创建评论
- **接口**: `/api/production/comments/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "order": "integer",
    "step": "integer",  // 可选
    "comment_type": "string",
    "content": "string",
    "images": ["string"],
    "parent": "integer"  // 可选，回复其他评论时使用
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
