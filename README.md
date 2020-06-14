# Bluelog
## 简介
这是一个基于 flask 数据库使用 MySQL 存储的个人博客项目。

根据《Flask Web 开发实战：入门、进阶与原理解析》（李辉 著）写的。

购买链接：https://item.jd.com/12430774.html

Demo: http://119.23.223.51

主要功能：

前台可以浏览文章，评论文章，根据分类浏览文章。查看友情链接。

后台可以创建新文章，编辑和删除已创建文章。创建分类，编辑和删除已创建分类。创建友情链接，编辑和删除已创建的友情链接。审核评论，打开或关闭文章的评论等博客的基本功能。

## 

## 安装
复制代码:

    $ git clone https://github.com/jiangyue0013/bluelog.git
    $ cd bluelog 
创建虚拟环境：
本项目所安装的包全部保存在 requiremens.txt 中。创建虚拟环境后进入虚拟环境使用 pip 进行安装。

    $ pip install -r requirements.txt
设置运行所需变量运行：
在项目根目录创建 .env 文件保存运行时所需的变量来运行。

文件内容如下：

    # MySQL 数据库用户名
    PR_MYSQL_USER="username"
    # MySQL 数据库用户名的密码
    PR_MYSQL_PASSWORD="password"
    # MySQL 数据库所在的主机名或ip地址
    PR_MYSQL_PORT="localhost"
    # MySQL 数据库的库名
    PR_MYSQL_DATABASE="databasename"

    # flask app 名称
    FLASK_APP="bluelog"
    # flask 的运行环境  
    FLASK_ENV="development" # 
    FLASK_CONFIG="development"  
文件创建并设置正确后，在虚拟环境中输入：

    $ flask initdb
创建保存数据所用的表。

输入：

    $ flask init
根据提示创建管理员用户和密码。

输入：

    $ flask forge
创建虚拟数据。

上述三个命令可在 /__init__.py 中查看具体参数和实现。

输入：

    $ flask run
运行项目。

## 代码目录结构
    bluelog
    |--blueprints        // 蓝图包
    |  |--__init__.py
    |  |--admin.py       // 管理界面蓝图
    |  |--auth.py        // 认证界面蓝图
    |  |--blog.py        // 博客界面蓝图
    |--static
    |  |--ckeditor       // ckeditor 相关文件
    |  |--css            // 样式表文件
    |  |--js             // javascript 文件
    |--tmplates
    |  |--admin          // 管理界面模板
    |  |--auth           // 认证界面模板
    |  |--blog           // 博客界面模板
    |  |--errors         // 错误界面模板
    |  |--base.html      // 基模板
    |--__init__.py       // flask 的 current_app 函数
    |--commands.py       // flask 命令所在的文件
    |--emails.py         // 发送邮件相关的文件
    |--extensions.py     // 扩展包的实例化文件
    |--fakes.py          // 生成假数据的函数所在的文件
    |--forms.py          // 表单的所在的文件
    |--models.py         // 数据库模型所在的文件
    |--settings.py       // 项目设置文件
    |--utils.py          // 工具函数所在的文件
    |--logs              // 日志文件夹
    |--.flaskenv         // flask 环境设置
    |--.gitignore        // git 的忽略文件
    |--README.md         // 帮助文档
    |--requirements.txt  // 虚拟环境安装的包的列表
    |--wsgi.py           // 部署时所需的文件
## 开源协议
本项目是 MIT 开源协议