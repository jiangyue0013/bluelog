import logging
import os
from logging.handlers import RotatingFileHandler

import click
from flask import Flask, render_template
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from bluelog.apis.v1 import api_v1
from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.blueprints.blog import blog_bp
from bluelog.extensions import (bootstrap, ckeditor, csrf, db, login_manager,
                                mail, migrate, moment)
from bluelog.models import Admin, Category, Comment, Link
from bluelog.settings import config


def create_app(config_name=None):
    """创建和注册 app 的函数

    注册日志处理器、扩展、蓝本、自定义 shell 命令、错误处理函数、shell 上下文处理函数和模板上下文注册函数

    Args:
        config_name:配置的名称，默认为 None
    Returns:
        返回注册完成后的 app
    """
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG')

    app = Flask('bluelog')
    app.config.from_object(config[config_name])

    register_logger(app)  # 注册日志处理器
    register_extensions(app)  # 注册扩展（扩展初始化）
    register_blueprints(app)  # 注册蓝本
    register_commands(app)  # 注册自定义 shell 命令
    register_errors(app)  # 注册错误处理函数
    register_shell_context(app)  # 注册 shell 上下文处理函数
    register_template_context(app)  # 注册模板上下文处理函数
    return app


def register_logger(app):
    """注册日志处理器

    设置日志的格式、目录等内容

    Args:
        app:Flask 对象
    """
    app.logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - $(levelname)s - %(message)s')

    file_handler = RotatingFileHandler('./logs/bluelog.log',
                                       maxBytes=10 * 1024 * 1024,
                                       backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    if not app.debug:
        app.logger.addHandler(file_handler)


def register_extensions(app):
    """初始化扩展

    初始化 bootstrap, ckeditor, csrf, db, login_manager, mail, moment, migrate

    Args:
        app:Flask 对象
    """
    bootstrap.init_app(app)
    ckeditor.init_app(app)
    csrf.init_app(app)
    csrf.exempt(api_v1)
    db.init_app(app,)  # 取消 api_v1 蓝本的 csrf 保护
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    """注册蓝图

    注册 blog_bp, admin, auth_bp

    Args:
        app:Flask 对象
    """
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_v1, url_prefix='/api/v1')
    # 为 api_v1 指定子域
    # app.register_blueprint(api_v1, subdomain='api', url_prefix='/v1')



def register_shell_context(app):
    """注册 shell 上下文对象

    使用 make_shell_context 函数注册上下文对象

    Args:
        app: Flask 对象

    """
    @app.shell_context_processor
    def make_shell_context():
        """向 shell 中传入数据库对象

        使用 shell_context_processor 装饰器传入数据库对象

        Returns:
            以{ 'db': db }传回数据库对象db
        """
        return dict(db=db)


def register_template_context(app):
    """注册模板上下文对象

    使用 make_template_context 函数生成模板中所需上下文对象

    Args:
        app:Flask 对象

    """
    @app.context_processor
    def make_template_content():
        """"为模板传入所需的上下文对象

        传入 admin, categories, links, unread_comments 数据库查询对象

        Returns:
            以
            {
            'admin': admin,
            'categories': categories,
            'links': links,
            'unread_comments': unread_comments
            }
            形式传回
            admin数据库查询对象
            categories数据库查询对象
            links数据库查询对象
            unread_coments数据库查询对象。
        """
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(admin=admin,
                    categories=categories,
                    links=links,
                    unread_comments=unread_comments)


def register_errors(app):
    """注册错误处理函数

    注册400,404,500,CSRFError 错误处理函数

    Args:
        app:Flask 对象
    """
    @app.errorhandler(400)
    def bad_request(e):
        """400错误处理函数

        Args:
            e:运行中出现的异常

        Returns:
            返回 templates/errors/400.html 状态码为 400

        """
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        """404错误处理函数

        Args:
            e:运行中出现的异常错误对象

        Returns:
            返回 templates/errors/404.html 状态码为 404

        """
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """500错误处理函数

        Args:
            e:运行中出现的异常错误对象

        Returns:
            返回 templates/errors/500.html 状态码为 500
        """
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """CSRFError错误处理函数

        Args:
            e:运行中出现的异常错误处理对象
        Returns:
            返回 templates/errors/400.html 状态码为 400, 页面中有错误描述
        """
        return render_template('errors/400.html',
                               description=e.description), 400


def register_commands(app):
    """注册 flask 命令

    Args:
        app:Flask对象
    """
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database.

        Args:
            drop: 可选参数，如果为True,则删除数据库中的数据
        """
        if drop:
            click.confirm(
                'This operation will delete the database, '
                'do you want to continue?',
                abort=True
            )
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')
    
    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password',
                  prompt=True,
                  hide_input=True,
                  confirmation_prompt=True,
                  help='The password used to login.')
    def init(username, password):
        """Build Bluelog, just for you.

        初始化管理员账户和密码

        Args:
            username:管理员账户
            password:管理员密码

        """
        click.echo('Initializing the database...')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='Bluelog',
                blog_sub_title="No, I'm the real thing.",
                name='Admin',
                about='Anything about you.'
            )
            admin.set_password(password)
            db.session.add(admin)
        
        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            
        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category',
                  default=10,
                  help='Quantity of categories, default is 10.')
    @click.option('--post',
                  default=50,
                  help='Quantity of posts, default is 50.')
    @click.option('--comment',
                  default=500,
                  help='Quantity of comments, default is 500.')
    @click.option('--url',
                  default=5,
                  help='Quantity of comments, default is 5.')
    def forge(category, post, comment, url):
        """Generates the fake categories, posts, and comments.

        生成假数据用于展示效果。

        Args:
            category:生成分类数量，默认为10
            post:生成文章数量，默认为50
            comment:生成评论数量，默认为500
            url:生成链接数量，默认为5

        """
        from bluelog.fakes import (fake_admin, fake_categories, fake_posts,
                                   fake_comments, fake_url)

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating %d categories..' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Gemerating %d comments..' % comment)
        fake_comments(comment)

        click.echo('Generating %d urls..' % url)
        fake_url(url)

        click.echo('Done.')
