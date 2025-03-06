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