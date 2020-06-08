import os
import click
import logging

from flask import Flask, render_template
from flask_login import current_user
from flask_wtf.csrf import CSRFError
from logging.handlers import RotatingFileHandler

from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.blueprints.blog import blog_bp
from bluelog.extensions import (bootstrap, ckeditor, csrf,
                                db, mail, moment,
                                login_manager, migrate)
from bluelog.settings import config
from bluelog.models import Admin, Category, Comment, Link


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

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
    bootstrap.init_app(app)
    ckeditor.init_app(app)
    csrf.init_app(app)
    db.init_app(app,)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_template_context(app):
    @app.context_processor
    def make_template_content():
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
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html',
                               description=e.description), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
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
        """Build Bluelog, just for you."""
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
        """Generates the fake categories, posts, and comments."""
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
