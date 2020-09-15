from datetime import datetime, timedelta
from functools import wraps

from flask import current_app, g, request
from flask_restful import Resource
from flask_sqlalchemy import FSADeprecationWarning
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from bluelog.apis.v1.errors import api_abort, invalid_token, token_missing
from bluelog.models import Admin
from bluelog.utils import generate_jwt


def generate_token(admin):
    expiration = 3600
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    token = s.dump({'id': admin.id})
    return token, expiration


def validate_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (BadSignature, SignatureExpired):
        return False
    admin = Admin.query.get(data['id'])
    if admin is None:
        return False
    g.current_user = admin
    return True


def get_token():
    if 'Authorization' in request.headers:
        try:
            token_type, token = request.headers['Authorization'].split(None, 1)
        except ValueError:
            token_type = token = None
    else:
        token_type = token = None

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token_type, token = get_token()

        if request.method == 'OPTIONS':
            if token_type is None or token.lower() != 'bearer':
                return api_abort(400, 'THe token type must be bearer.')
            if token is None:
                return token_missing
            if not validate_token(token):
                return invalid_token()
        return f(*args, **kwargs)
    
    return decorated


class AuthorizationResource(Resource):
    """
    登录认证
    """
    def _generate_tokens(self, user_id, with_refresh_token=True):
        """
        生成 token 和 refresh_token
        :param user_id: 用户id
        :return: token, refresh_token
        """
        # 颁发 JWT
        now = datetime.utcnow()
        expiry = now + timedelta(hours=current_app.config['JWT_EXPIRE_HOURS'])  # 短期 token 过期小时数
        token = generate_jwt({'user_id': user_id, 'refresh': False}, expiry)
        refresh_token = None
        if with_refresh_token:
            refresh_exipry = now + timedelta(days=current_app.config['JWT_EXPIRE_DAYS'])  # 长期 token 过期天数
            refresh_token = generate_jwt({'user_id': user_id, 'refresh': True}, refresh_exipry)
        return token, refresh_token
    

    def post(self):
        """
        用户登录创建token
        """
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                token, refresh_token = self._generate_tokens(admin.id)
                return {"token":token, "refresh_token":refresh_token}, 201
            else:
                return {"message": "Username or password is incorrect"}, 401
        else:
            return {"message": "Admin is not valid."}, 403
    
    # 补充 put 方式，更新 token 接口
    def put(self):
        """
        刷新token
        """
        user_id = g.user_id
        if user_id and g.is_refresh_token:
            token, refresh_token = self._generate_tokens(user_id, with_refresh_token=False)
            return {'token': token}, 201
        else:
            return {'message': 'Wrong refresh token'}, 403
        



def jwt_login_required(func):
    """
    用户必须登录装饰器
    使用方法：放在 method_decorators 中
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user_id:
            return {'message': 'User must be authorzied.'}, 401
        elif g.is_refresh_token:
            return {'message': 'Do not use refresh tokens.'}, 403
        else:
            return func(*args, **kwargs)
    
    return wrapper
