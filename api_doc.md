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

#### 4.2 上传商品图片
- **接口**: `/api/products/products/upload_image/`
- **方法**: `POST`
- **权限**: 无需认证
- **Content-Type**: `multipart/form-data`
- **请求参数**:
  ```json
  {
    "image": "file"  // 图片文件
  }
  ```
- **响应**:
  ```json
  {
    "message": "图片上传成功",
    "image_url": "string"  // 图片访问URL
  }
  ```
- **错误响应**:
  ```json
  {
    "error": "错误信息"  // 可能的错误：没有提供图片文件、不支持的文件类型、文件大小超限等
  }
  ```
- **说明**:
  - 支持的文件类型：JPG、PNG、GIF
  - 文件大小限制：最大5MB
  - 返回的image_url为图片的完整访问路径
  - 图片将保存在 products/images/ 目录下，保持原始文件名

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

#### 2.3 更新任务状态
- **接口**: `/api/production/orders/{id}/update_status/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "status": "string"  // pending/in_progress/completed/cancelled
  }
  ```
- **响应**:
  ```json
  {
    "status": "success"
  }
  ```
- **错误响应**:
  ```json
  {
    "error": "Invalid status"
  }
  ```
- **说明**:
  - 状态只能在预定义的选项中选择
  - 状态变更会记录在系统日志中
  - 当状态更新为completed时，会自动记录完成时间

#### 2.4 上传任务主图
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

#### 6.3 获取步骤统计数据
- **接口**: `/api/production/reports/step_statistics/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `status`: 可选，步骤状态过滤
  - `category`: 可选，生产类目ID过滤
  - `start_date`: 可选，开始日期 (YYYY-MM-DD)
  - `end_date`: 可选，结束日期 (YYYY-MM-DD)
- **响应**:
  ```json
  {
    "data": [
      {
        "step_name": "模型打印",    // 步骤名称
        "count": 12,               // 总任务数量
        "percentage": 25.5,        // 百分比
        "status_distribution": {    // 状态分布
          "pending": 3,            // 待处理数量
          "in_progress": 4,        // 进行中数量
          "completed": 4,          // 已完成数量
          "on_hold": 1            // 已暂停数量
        }
      },
      {
        "step_name": "3D建模",
        "count": 18,
        "percentage": 38.3,
        "status_distribution": {
          "pending": 5,
          "in_progress": 8,
          "completed": 3,
          "on_hold": 2
        }
      }
    ],
    "total": 47  // 总任务数
  }
  ```
- **说明**:
  - percentage 为该步骤总任务数量占所有步骤总任务数量的百分比
  - count 为该步骤的总任务数量（所有状态之和）
  - status_distribution 显示该步骤中各状态的任务数量分布
  - 支持按日期范围、状态和生产类目筛选
  - 返回的数据按步骤名称排序
  - step_name 返回的是步骤的显示名称而不是代码

#### 6.4 获取类目优先级统计数据
- **接口**: `/api/production/reports/category_priority_statistics/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `status`: 可选，任务状态过滤
  - `start_date`: 可选，开始日期 (YYYY-MM-DD)
  - `end_date`: 可选，结束日期 (YYYY-MM-DD)
- **响应**:
  ```json
  {
    "data": [
      {
        "category_name": "类目1",
        "priority_distribution": {
          "high": 10,    // 高优先级任务数
          "medium": 20,  // 中优先级任务数
          "normal": 30,  // 普通优先级任务数
          "low": 15      // 低优先级任务数
        }
      },
      {
        "category_name": "类目2",
        "priority_distribution": {
          "high": 5,
          "medium": 15,
          "normal": 25,
          "low": 10
        }
      }
    ]
  }
  ```
- **说明**:
  - 返回每个类目下不同优先级的任务数量分布
  - 支持按日期范围和任务状态筛选
  - priority_distribution 中的数值表示该优先级的任务数量
  - 数据按类目名称排序

## 四、采购管理模块 (Purchase)

### 1. 供应商管理 (Suppliers)
#### 1.1 获取供应商列表
- **接口**: `/api/purchase/suppliers/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `status`: 是否启用
  - `name`: 供应商名称（模糊匹配）
  - `contact_person`: 联系人（模糊匹配）
  - `contact_phone`: 联系电话（模糊匹配）
  - `search`: 搜索关键词（搜索名称、联系人、电话、地址）
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "name": "string",
        "contact_person": "string",
        "contact_phone": "string",
        "address": "string",
        "email": "string",
        "status": "boolean",
        "remark": "string",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

### 2. 采购订单管理 (Orders)
#### 2.1 获取订单列表
- **接口**: `/api/purchase/orders/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `status`: 订单状态
    - `draft`: 草稿
    - `pending_order`: 待下单
    - `submitted`: 已提交
    - `approved`: 已审核
    - `pending_payment`: 待支付
    - `processing`: 处理中
    - `pending_storage`: 待入库
    - `completed`: 已完成
    - `cancelled`: 已取消
  - `supplier`: 供应商ID
  - `purchaser`: 采购员ID
  - `warehouse_id`: 仓库ID
  - `min_order_time`: 最小下单时间
  - `max_order_time`: 最大下单时间
  - `min_total_amount`: 最小总金额
  - `max_total_amount`: 最大总金额
  - `search`: 搜索关键词（搜索订单编号、备注）
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "order_number": "string",
        "order_time": "datetime",
        "supplier": "integer",
        "supplier_info": {
          "id": "integer",
          "name": "string",
          "contact_person": "string",
          "contact_phone": "string"
        },
        "purchaser": "integer",
        "purchaser_info": {
          "id": "integer",
          "username": "string",
          "first_name": "string",
          "last_name": "string"
        },
        "warehouse_id": "integer",
        "status": "string",
        "status_display": "string",
        "total_amount": "decimal",
        "expected_delivery_date": "date",
        "actual_delivery_date": "date",
        "tracking_number": "string",
        "remark": "string",
        "items": [
          {
            "id": "integer",
            "product": "integer",
            "product_info": {
              "id": "integer",
              "name": "string",
              "code": "string"
            },
            "quantity": "integer",
            "unit_price": "decimal",
            "total_price": "decimal",
            "received_quantity": "integer",
            "remark": "string"
          }
        ],
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

#### 2.2 更新订单状态
- **接口**: `/api/purchase/orders/{id}/update_status/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "status": "string"  // 状态代码
  }
  ```
- **响应**:
  ```json
  {
    "id": "integer",
    "status": "string",
    "status_display": "string",
    "order_time": "datetime",      // 当状态为submitted时会更新
    "actual_delivery_date": "date" // 当状态为completed时会更新
  }
  ```
- **说明**:
  - 当状态更新为 submitted 时，会自动设置下单时间
  - 当状态更新为 completed 时，如果未设置实际交付日期，会自动设置为当前日期

### 3. 采购订单明细管理 (Order Items)
#### 3.1 获取订单明细列表
- **接口**: `/api/purchase/order-items/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `purchase_order`: 订单ID
  - `product`: 商品ID
  - `search`: 搜索关键词（搜索备注）
  - `order_id`: 通过订单ID过滤明细
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "purchase_order": "integer",
        "product": "integer",
        "product_info": {
          "id": "integer",
          "name": "string",
          "code": "string"
        },
        "quantity": "integer",
        "unit_price": "decimal",
        "total_price": "decimal",
        "received_quantity": "integer",
        "remark": "string",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```
- **说明**:
  - total_price 字段为只读，由系统根据 quantity 和 unit_price 自动计算
  - 创建或更新订单明细时会自动更新订单的总金额 

## 五、订单管理模块 (Trade)

### 1. 店铺管理 (Shops)
#### 1.1 获取店铺列表
- **接口**: `/api/trade/shops/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `name`: 店铺名称（模糊匹配）
  - `platform`: 平台类型
    - `shopify`: Shopify
    - `shopline`: Shopline
    - `tiktok`: Tik Tok
    - `etsy`: Etsy
    - `offline`: 线下订单
  - `status`: 状态（1: 正常, 0: 停用）
  - `search`: 搜索关键词（搜索名称、编号、描述）
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "name": "string",
        "platform": "string",
        "platform_display": "string",
        "shop_code": "string",
        "manager": "integer",
        "manager_info": {
          "id": "integer",
          "username": "string",
          "email": "string"
        },
        "status": "integer",
        "status_display": "string",
        "description": "string",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

#### 1.2 切换店铺状态
- **接口**: `/api/trade/shops/{id}/toggle_status/`
- **方法**: `POST`
- **权限**: 需要认证
- **响应**:
  ```json
  {
    "status": "integer",
    "message": "店铺状态已更新"
  }
  ```

### 2. 订单管理 (Orders)
#### 2.1 获取订单列表
- **接口**: `/api/trade/orders/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `order_number`: 订单编号（模糊匹配）
  - `platform_order_number`: 平台订单号（模糊匹配）
  - `status`: 订单状态
    - `unpaid`: 未支付
    - `pending`: 待处理
    - `picking`: 配货中
    - `shipped`: 已发货
    - `cancelled`: 已取消
  - `order_type`: 订单类型
    - `platform`: 平台订单
    - `influencer`: 达人订单
    - `offline`: 线下订单
    - `requisition`: 员工领用
    - `employee`: 员工自购
  - `shop`: 店铺ID
  - `payment_status`: 支付状态（true/false）
  - `created_at`: 创建时间范围
  - `order_place_time`: 下单时间范围
  - `payment_time`: 支付时间范围
  - `total_amount`: 订单金额范围
  - `shipping_contact`: 收货人（模糊匹配）
  - `shipping_phone`: 联系电话（模糊匹配）
  - `search`: 搜索关键词（搜索订单号、收货人、电话、地址）
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "order_number": "string",
        "platform_order_number": "string",
        "order_type": "string",
        "order_type_display": "string",
        "exchange_rate_to_usd": "decimal",
        "package_id": "string",
        "shop": "integer",
        "shop_info": {
          "id": "integer",
          "name": "string",
          "platform": "string",
          "platform_display": "string"
        },
        "status": "string",
        "status_display": "string",
        "total_amount": "decimal",
        "currency": "string",
        "shipping_fee": "decimal",
        "payment_method": "string",
        "payment_method_display": "string",
        "payment_status": "boolean",
        "payment_time": "datetime",
        "order_place_time": "datetime",
        "shipping_address": "string",
        "shipping_contact": "string",
        "shipping_phone": "string",
        "postal_code": "string",
        "country": "string",
        "state": "string",
        "city": "string",
        "district": "string",
        "system_remark": "string",
        "cs_remark": "string",
        "buyer_remark": "string",
        "items": [
          {
            "id": "integer",
            "product": "integer",
            "product_info": {
              "id": "integer",
              "name": "string",
              "code": "string"
            },
            "quantity": "integer",
            "unit_price": "decimal",
            "discount": "decimal",
            "total_price": "decimal",
            "remark": "string"
          }
        ],
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

#### 2.2 创建订单
- **接口**: `/api/trade/orders/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "order_number": "string",
    "platform_order_number": "string",
    "order_type": "string",
    "exchange_rate_to_usd": "decimal",
    "package_id": "string",
    "shop": "integer",
    "status": "string",
    "total_amount": "decimal",
    "currency": "string",
    "shipping_fee": "decimal",
    "payment_method": "string",
    "payment_status": "boolean",
    "payment_time": "datetime",
    "order_place_time": "datetime",
    "shipping_address": "string",
    "shipping_contact": "string",
    "shipping_phone": "string",
    "postal_code": "string",
    "country": "string",
    "state": "string",
    "city": "string",
    "district": "string",
    "system_remark": "string",
    "cs_remark": "string",
    "buyer_remark": "string",
    "items": [
      {
        "product": "integer",
        "quantity": "integer",
        "unit_price": "decimal",
        "discount": "decimal",
        "remark": "string"
      }
    ]
  }
  ```

#### 2.3 更新订单状态
- **接口**: `/api/trade/orders/{id}/update_status/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "status": "string"  // unpaid/pending/picking/shipped/cancelled
  }
  ```
- **响应**:
  ```json
  {
    "status": "string",
    "message": "订单状态已更新"
  }
  ```

#### 2.4 更新支付状态
- **接口**: `/api/trade/orders/{id}/update_payment/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "payment_status": "boolean"
  }
  ```
- **响应**:
  ```json
  {
    "payment_status": "boolean",
    "payment_time": "datetime",
    "message": "支付状态已更新"
  }
  ```

### 3. 订单商品管理 (Order Items)
#### 3.1 获取订单商品列表
- **接口**: `/api/trade/order-items/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `order`: 订单ID
  - `product`: 商品ID
  - `search`: 搜索关键词（搜索备注）
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "order": "integer",
        "product": "integer",
        "product_info": {
          "id": "integer",
          "name": "string",
          "code": "string"
        },
        "quantity": "integer",
        "unit_price": "decimal",
        "discount": "decimal",
        "total_price": "decimal",
        "remark": "string",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```
- **说明**:
  - total_price 字段为只读，由系统根据 quantity、unit_price 和 discount 自动计算
  - 创建或更新订单商品时会自动更新订单的总金额
  
## 六、物流管理模块 (Logistics)

### 1. 物流商管理 (Carriers)
#### 1.1 获取物流商列表
- **接口**: `/api/logistics/carriers/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `name`: 中文名称（模糊匹配）
  - `code`: 物流商代码（模糊匹配）
  - `contact`: 联系电话（模糊匹配）
  - `created_at`: 创建时间范围
  - `search`: 搜索关键词（搜索中文名、英文名、代码、联系电话）
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "name_zh": "string",
        "name_en": "string",
        "code": "string",
        "url": "string",
        "contact": "string",
        "query_key": "integer",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

### 2. 物流服务管理 (Services)
#### 2.1 获取服务列表
- **接口**: `/api/logistics/services/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `carrier`: 物流商ID
  - `carrier_name`: 物流商名称（模糊匹配）
  - `service_name`: 服务名称（模糊匹配）
  - `service_code`: 服务代码（模糊匹配）
  - `service_type`: 服务类型
  - `created_at`: 创建时间范围
  - `search`: 搜索关键词（搜索服务名称、代码、物流商名称）
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "carrier": "integer",
        "carrier_name": "string",
        "service_name": "string",
        "service_code": "string",
        "service_type": "integer",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

### 3. 包裹管理 (Packages)
#### 3.1 获取包裹列表
- **接口**: `/api/logistics/packages/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `order`: 订单ID
  - `order_number`: 订单编号（模糊匹配）
  - `warehouse`: 仓库ID
  - `warehouse_name`: 仓库名称（模糊匹配）
  - `tracking_no`: 跟踪号（模糊匹配）
  - `pkg_status_code`: 包裹状态码
    - `0`: 待发货
    - `1`: 待揽收
    - `2`: 转运中
    - `3`: 已签收
    - `4`: 已取消
  - `service`: 物流服务ID
  - `carrier`: 物流商ID
  - `carrier_name`: 物流商名称（模糊匹配）
  - `created_at`: 创建时间范围
  - `estimated_cost_min`: 最小预估费用
  - `estimated_cost_max`: 最大预估费用
  - `search`: 搜索关键词（搜索跟踪号、订单编号）
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "order": "integer",
        "order_info": {
          "order_number": "string",
          "shop_name": "string",
          "total_amount": "string",
          "status": "string"
        },
        "warehouse": "integer",
        "warehouse_name": "string",
        "tracking_no": "string",
        "pkg_status_code": "string",
        "service": "integer",
        "carrier_name": "string",
        "service_name": "string",
        "items": "json",
        "length": "decimal",
        "width": "decimal",
        "height": "decimal",
        "weight": "decimal",
        "volume": "decimal",
        "volume_weight": "decimal",
        "estimated_logistics_cost": "decimal",
        "carrier_cost": "decimal",
        "tracking_records": [
          {
            "id": "integer",
            "status": "integer",
            "status_display": "string",
            "location": "string",
            "description": "string",
            "operator": "integer",
            "operator_name": "string",
            "tracking_time": "datetime",
            "created_at": "datetime",
            "updated_at": "datetime"
          }
        ],
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

#### 3.2 更新包裹状态
- **接口**: `/api/logistics/packages/{id}/update_status/`
- **方法**: `POST`
- **权限**: 需要认证
- **请求参数**:
  ```json
  {
    "status": "string",     // 新状态码
    "location": "string",   // 当前位置
    "description": "string" // 状态描述
  }
  ```
- **响应**: 返回更新后的包裹完整信息
- **说明**:
  - 状态变更规则：
    - 待发货(0) -> 待揽收(1)/已取消(4)
    - 待揽收(1) -> 转运中(2)/已取消(4)
    - 转运中(2) -> 已签收(3)/已取消(4)
    - 已签收(3) -> 不可变更
    - 已取消(4) -> 不可变更
  - 状态变更时会自动创建物流轨迹记录
  - 操作人会自动设置为当前登录用户

### 4. 物流轨迹管理 (Tracking)
#### 4.1 获取轨迹列表
- **接口**: `/api/logistics/tracking/`
- **方法**: `GET`
- **权限**: 需要认证
- **查询参数**:
  - `package`: 包裹ID
  - `tracking_no`: 跟踪号（模糊匹配）
  - `status`: 物流状态
  - `location`: 当前位置（模糊匹配）
  - `operator`: 操作人ID
  - `operator_name`: 操作人用户名（模糊匹配）
  - `tracking_time`: 轨迹时间范围
  - `created_at`: 创建时间范围
  - `package_id`: 通过包裹ID过滤轨迹记录
  - `search`: 搜索关键词（搜索位置、描述、跟踪号）
- **响应**:
  ```json
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "package": "integer",
        "status": "integer",
        "status_display": "string",
        "location": "string",
        "description": "string",
        "operator": "integer",
        "operator_name": "string",
        "tracking_time": "datetime",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```
- **说明**:
  - status 对应的状态码：
    - 0: 待发货
    - 1: 待揽收
    - 2: 转运中
    - 3: 已签收
    - 4: 已取消
  - tracking_time 表示物流状态发生的实际时间
  - operator 为记录创建人，自动设置为当前登录用户
  - 支持按包裹ID过滤轨迹记录
  - 默认按轨迹时间倒序排序
  