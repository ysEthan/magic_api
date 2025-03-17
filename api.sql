cd /code/magic/
git clone https://github.com/ysEthan/magic_api.git
cd /code/magic/magic_api
git fetch origin && git checkout -b b07_procurement origin/b07_procurement

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
git add . && git commit -m "procurement & storage" && git push

我们已经完成了商品管理和生产管理的部分，接下来让我们继续完善采购管理。
首先，请创建应用，然后参考以下模型文件，创建模型



接下来让我们继续完善库存管理的部分
首先，请创建应用，然后参考以下模型文件，创建模型



接下来让我们继续完善订单管理的部分
首先，请创建应用，然后参考以下模型文件，创建模型
