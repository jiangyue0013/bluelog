import os

from DO_NOT_UPLOAD import (MYSQL_USER, MYSQL_USER_PASSWORD, MYSQL_USER_PORT,
                           PRO_MYSQL_USER, PRO_MYSQL_PASSWORD, PRO_MYSQL_PORT,
                           SECRET_KEY)

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')

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
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://' + MYSQL_USER + ':' + MYSQL_USER_PASSWORD +'@' +  MYSQL_USER_PORT +'/bluelog_db?charset=utf8'

class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLE = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # in-emory database

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{}:{}@{}/bluelog_db?charset=utf8mb8".format(PRO_MYSQL_USER, PRO_MYSQL_PASSWORD, PRO_MYSQL_PORT)
    # SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://' + PRO_MYSQL_USER + ':' + PRO_MYSQL_PASSWORD +'@' +  PRO_MYSQL_PORT +'/bluelog_db' + ", encoding='utf8'"

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}