import os


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
    """本项目的基础设置类

    在这个类中，规定了开发环境和生产环境中通用的设置。其中包括SECRET_KEY，数据库，邮件，博客展示数目，博客主题设置。
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
    # jwt 相关设置项
    JWT_SECRET = os.getenv('JWT_SECRET', 'secret string')  # JWT 加密用的 secret
    JWT_EXPIRE_HOURS = os.getenv('JWT_EXPIRE_HOURS', 1)  # JWT 短期 token 的过期时间， 默认 1 小时
    JWT_EXPIRE_DAYS = os.getenv('JWT_EXPIRE_DAYS', 1)  # JWT 长期 token 的过期时间，默认一天
    # SQLalchemy 相关设置项
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 邮件相关设置项
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEfAULT_SENDER = ('Bluelog Admin', MAIL_USERNAME)

    BLUELOG_EMAIL = os.getenv('BLUELOG_EMAIL')
    BLUELOG_POST_PER_PAGE = 10
    BLUELOG_MANAGE_POST_PER_PAGE = 15
    BLUELOG_COMMENT_PER_PAGE = 15
    # ('theme name', 'display name')
    BLUELOG_THEMES = {'perfect_blue':'Perfect Blue', 'Black_swan': 'Black Swan'}
    # 为了使 API post 方法不发生 csrf 错误，关闭 csrf 验证，如果不使用 API 要打开。
    WTF_CSRF_ENABLED = False


class DevelopmentConfig(BaseConfig):
    """开发环境设置

    包括基础设置之外的数据库设置

    """
    DE_MYSQL_USER = os.getenv('DE_MYSQL_USER')
    DE_MYSQL_USER_PASSWORD = os.getenv('DE_MYSQL_PASSWORD')
    DE_MYSQL_USER_PORT = os.getenv('DE_MYSQL_PORT')
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://' + DE_MYSQL_USER + ':' + DE_MYSQL_USER_PASSWORD +'@' +  DE_MYSQL_USER_PORT +'/bluelog_db'


class TestingConfig(BaseConfig):
    """测试环境设置

    基础设置外的数据库设置

    """
    TESTING = True
    WTF_CSRF_ENABLE = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # in-emory database


class ProductionConfig(BaseConfig):
    """生产环境设置

    设置生产环境的数据库设置

    """
    PR_MYSQL_USER = os.getenv('PR_MYSQL_USER')
    PR_MYSQL_PASSWORD = os.getenv('PR_MYSQL_PASSWORD')
    PR_MYSQL_PORT = os.getenv('PR_MYSQL_PORT')
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://' + PR_MYSQL_USER + ':' + PR_MYSQL_PASSWORD + '@' + PR_MYSQL_PORT + '/bluelog_db'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}