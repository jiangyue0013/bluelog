from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

bootstrap = Bootstrap()
ckeditor = CKEditor()
csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
moment = Moment()
migrate = Migrate()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'waring'

@login_manager.user_loader
def load_user(user_id):
    from bluelog.models import Admin
    user = Admin.query.get(int(user_id))
    return user
