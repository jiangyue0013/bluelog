import os


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
    """本项目的基础设置类

    在这个类中，规定了开发环境和生产环境中通用的设置。其中包括SECRET_KEY，数据库，邮件，博客展示数目，博客主题设置。
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
    JWT_SECRET = os.getenv('JWT_SECRET', 'secret string')  # JWT 加密用的 secret

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEfAULT_SENDER = ('Bluelog Admin', MAIL_USERNAME)

    BLUELOG_EMAIL = os.getenv('BLUELOG_EMAIL')
    BLUELOG_POST_PER_PAGE = 10
    BLUELOG_MANAGE_POST_PER_PAGE = 15
    BLUELOG_COMMENT_PER_PAGE = 15
    # ('theme name', 'display name')
    BLUELOG_THEMES = {'perfect_blue':'Perfect Blue', 'Black_swan': 'Black Swan'}


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