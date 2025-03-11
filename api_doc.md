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

#### 2.7 获取当前进行中的步骤
- **接口**: `/api/production/orders/{id}/current_step/`
- **方法**: `GET`
- **权限**: 需要认证
- **响应**:
  ```json
  {
    "id": "integer",
    "order": "integer",
    "step_name": "string",        // 步骤名称代码
    "step_name_display": "string", // 步骤名称显示文本
    "sequence": "integer",
    "description": "string",
    "contractor": "string",
    "status": "string",           // 状态代码
    "status_display": "string",    // 状态显示文本
    "planned_duration": "string",
    "actual_duration": "string",
    "start_time": "datetime",
    "end_time": "datetime",
    "operator": "integer",
    "operator_info": {
      "id": "integer",
      "username": "string",
      "first_name": "string",
      "last_name": "string"
    },
    "quality_check_result": "string",
    "notes": "string",
    "attachments": ["string"]
  }
  ```
  或
  ```json
  {
    "message": "没有正在进行或待处理的步骤"
  }
  ```
- **说明**:
  - 返回状态为"进行中"且序号最小的步骤
  - 如果没有进行中的步骤，则返回第一个待处理的步骤
  - 如果既没有进行中也没有待处理的步骤，则返回提示信息

### 3. 生产步骤管理 (Steps)
#### 3.1 获取步骤列表
- **接口**: `/api/production/steps/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `order`: 任务ID
  - `step_name`: 步骤名称
    - `3d_modeling`: 3D建模
    - `model_printing`: 模型打印
    - `casting`: 铸造
    - `plating`: 电镀
    - `post_processing`: 后处理
  - `status`: 状态
    - `pending`: 待处理
    - `in_progress`: 进行中
    - `completed`: 已完成
    - `on_hold`: 已暂停
  - `operator`: 操作员ID
  - `contractor`: 承接方
  - `search`: 搜索关键词（搜索描述、承接方）
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "order": "integer",
        "step_name": "string",        // 步骤名称代码
        "step_name_display": "string", // 步骤名称显示文本
        "sequence": "integer",
        "description": "string",
        "contractor": "string",
        "status": "string",           // 状态代码
        "status_display": "string",    // 状态显示文本
        "planned_duration": "string",
        "actual_duration": "string",
        "start_time": "datetime",
        "end_time": "datetime",
        "operator": "integer",
        "operator_info": {
          "id": "integer",
          "username": "string",
          "first_name": "string",
          "last_name": "string"
        },
        "quality_check_result": "string",
        "notes": "string",
        "attachments": ["string"]
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
- **响应**:
  ```json
  {
    "status": "success",
    "old_status": "string",
    "new_status": "string",
    "end_time": "datetime"
  }
  ```
- **说明**:
  - 当状态更新为 completed 时，会自动设置结束时间
  - 状态只能在预定义的选项中选择

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

### 6. 生产报表 (Reports)

#### 6.1 获取报表汇总数据
- **接口**: `/api/production/reports/summary/`
- **方法**: `GET`
- **权限**: 需要认证
- **响应**:
  ```json
  {
    "total_orders": "integer",      // 任务总数
    "completion_rate": "number",    // 完成率（百分比）
    "total_planned": "integer",     // 计划生产总量
    "total_completed": "integer",   // 实际完成总量
    "status_distribution": {        // 状态分布
      "pending": "integer",         // 待处理数量
      "in_progress": "integer",     // 进行中数量
      "completed": "integer",       // 已完成数量
      "cancelled": "integer"        // 已取消数量
    }
  }
  ```
- **说明**:
  - completion_rate: 完成率 = 已完成任务数 / 总任务数 * 100
  - total_planned: 所有任务的计划生产数量之和
  - total_completed: 已完成任务的实际生产数量之和

#### 6.2 获取趋势数据
- **接口**: `/api/production/reports/trend/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `type`: 趋势类型
    - `daily`: 按日统计（默认）
    - `weekly`: 按周统计
    - `monthly`: 按月统计
  - `start_date`: 开始日期 (YYYY-MM-DD)
  - `end_date`: 结束日期 (YYYY-MM-DD)
  - `category`: 可选的类目ID，用于筛选特定类目的数据
- **响应**:
  ```json
  {
    "dates": [                      // 日期列表
      "2024-03-01",
      "2024-03-02",
      "2024-03-03"
    ],
    "new_orders": [                 // 新建任务数量列表
      5,                           // 2024-03-01新建了5个任务
      8,                           // 2024-03-02新建了8个任务
      3                            // 2024-03-03新建了3个任务
    ],
    "completed_orders": [           // 完成任务数量列表
      4,                           // 2024-03-01完成了4个任务
      6,                           // 2024-03-02完成了6个任务
      7                            // 2024-03-03完成了7个任务
    ]
  }
  ```
- **错误响应**:
  ```json
  {
    "error": "无效的日期格式"      // 当日期格式不正确时
  }
  ```
- **说明**:
  - 日期范围内的每一天都会返回数据，如果某天没有数据则返回0
  - 按周统计时，日期为每周的第一天
  - 按月统计时，日期为每月的第一天
  - 新建任务数：根据任务的创建时间统计
  - 完成任务数：根据任务的完成时间（更新时间）统计 