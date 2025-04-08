cd /code/magic/
git clone https://github.com/ysEthan/magic_api.git
cd /code/magic/magic_api
git fetch origin && git checkout -b b08_procurement origin/b08_procurement

mv -i .env.example .env

docker ps -q | xargs docker stop && docker ps -a -q | xargs docker rm && docker images -q | xargs docker rmi -f



"00 创建项目============================="
django-admin startproject mysite && rename mysite magic_api
--关联远程仓库
git init && git add . && git commit -m "first commit" && git branch -M main && git remote add origin https://github.com/ysEthan/magic_api.git && git push -u origin main

"01 提交默认分支============================="
git checkout -b b01_init
git add . && git commit -m "init" && git push



"02 基础配置============================="
git checkout -b b02_config
git add . && git commit -m "config" && git push





"03 用户认证============================="
git checkout -b b03_user_auth
git add . && git commit -m "user_auth" && git push

我要搭建一个一个ERP系统，主要满足供应链管理、和生产管理的需求，采用前后端分离的架构来设计。
本项目是基于Django 框架的后端项目，前端采用Vue3框架

系统主要包含：用户认证、商品管理、生产管理，采购管理、库存管理、销售管理、物流管理。以及一些报表页面

注意，我们已经在Django的项目根目录下，项目的配置文件在/mysite 中，所有新建的应用，都统一放在 /apps下

首先，让我们实现用户认证相关的功能




"04 商品管理============================="
git checkout -b b04_product
git add . && git commit -m "b04_product" && git push
我们已经完成了用户认证的部分，现在，让我们继续实现商品管理的部分
请参考一下模型文件，创建模型

完成视图和序列化器
数据迁移
更新API文档




"05 生产管理============================="
git checkout -b b05_production
git add . && git commit -m "production" && git push

git add . && git commit -m "test" && git checkout b04_product && git branch -D b05_production
我们已经完成了商品管理模块，现在，让我们继续实现生产管理。
生产分为试产和量产，每个生产任务有不同的环节，并且需要支持对生产任务进行评论
请先建立生产任务/生产步骤/评论 三个模型，

增加生产类目字段，包含树脂类/金属类/陶瓷类/毛绒类

ProductionStep
生产步骤字段，name可选 3D建模，模型打印，铸造，电镀，后处理


接下来，我们需要创建序列化器和视图来处理这些模型的API接口。





"06 生产管理 添加步骤============================="
git checkout -b b06_production_step
git add . && git commit -m "production_step" && git push

接下来让我们完善生产步骤管理
首先需要实现添加步骤的功能



"07 采购管理 ============================="
git checkout -b b07_procurement
git add . && git commit -m "order & logistics" && git push

我们已经完成了商品管理和生产管理的部分，接下来让我们继续完善采购管理。
首先，请创建应用，然后参考以下模型文件，创建模型



接下来让我们继续完善库存管理的部分
首先，请创建应用，然后参考以下模型文件，创建模型



接下来让我们继续完善订单管理的部分
首先，请创建应用，然后参考以下模型文件，创建模型

创建数据库迁移文件
实现序列化器（Serializers）
创建视图（Views）
配置URL路由



接下来让我们继续完善物流管理的部分
首先，请创建应用，然后参考以下模型文件，创建模型




"08 采购管理 优化 ============================="
git checkout -b b08_procurement
git add . && git commit -m "order & logistics" && git push


"09 增加库存动态功能 ============================="
git checkout -b b09_inventory_change
git add . && git commit -m "inventory_change" && git push


我们需要在前端展示库存变化明细，请帮我开发对应的API接口，
匹配一下请求参数和相应数据示例

接口路径：/api/storage/inventory-history/
1，请求参数：
{
  "page": 1,                    // 页码，默认 1
  "page_size": 10,             // 每页数量，默认 10
  "warehouse": 1,              // 仓库 ID，可选
  "product": "测试商品",        // 商品名称或 SKU，可选
  "operation_type": "in",      // 操作类型，可选：in/out/check/transfer
  "start_date": "2024-01-01",  // 开始日期，可选
  "end_date": "2024-01-31"     // 结束日期，可选
}

2，响应数据示例：
{
  "count": 100,  // 总记录数
  "results": [
    {
      "id": 1,
      "warehouse_id": 1,
      "warehouse_name": "主仓库",
      "product_id": 101,
      "product_name": "测试商品A",
      "sku": "SKU001",
      "operation_type": "in",
      "quantity": 100,
      "before_quantity": 0,
      "after_quantity": 100,
      "unit": "个",
      "operator": "张三",
      "operation_time": "2024-01-15 14:30:00",
      "remark": "采购入库",
      "source_type": "purchase",      // 来源类型：purchase/sale/inventory/transfer
      "source_id": 1001,             // 来源单据ID
      "source_number": "PO20240115001" // 来源单据编号
    },
    {
      "id": 2,
      "warehouse_id": 1,
      "warehouse_name": "主仓库",
      "product_id": 102,
      "product_name": "测试商品B",
      "sku": "SKU002",
      "operation_type": "out",
      "quantity": 50,
      "before_quantity": 200,
      "after_quantity": 150,
      "unit": "个",
      "operator": "李四",
      "operation_time": "2024-01-15 15:45:00",
      "remark": "销售出库",
      "source_type": "sale",
      "source_id": 2001,
      "source_number": "SO20240115001"
    },
    {
      "id": 3,
      "warehouse_id": 2,
      "warehouse_name": "分仓库",
      "product_id": 101,
      "product_name": "测试商品A",
      "sku": "SKU001",
      "operation_type": "transfer",
      "quantity": 30,
      "before_quantity": 100,
      "after_quantity": 70,
      "unit": "个",
      "operator": "王五",
      "operation_time": "2024-01-16 09:15:00",
      "remark": "调拨至分仓库",
      "source_type": "transfer",
      "source_id": 3001,
      "source_number": "TR20240116001"
    },
    {
      "id": 4,
      "warehouse_id": 1,
      "warehouse_name": "主仓库",
      "product_id": 103,
      "product_name": "测试商品C",
      "sku": "SKU003",
      "operation_type": "check",
      "quantity": 5,
      "before_quantity": 95,
      "after_quantity": 100,
      "unit": "个",
      "operator": "赵六",
      "operation_time": "2024-01-16 16:20:00",
      "remark": "盘盈调整",
      "source_type": "inventory",
      "source_id": 4001,
      "source_number": "IC20240116001"
    }
  ]
}


首先添加理由
然后添加视图函数，
再实现序列化器