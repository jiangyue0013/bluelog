import jwt

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import current_app, redirect, request, url_for

def is_safe_url(target):
    """检查一个链接是否安全

    检查一个链接是否和当前页面属于同一主机

    Args:需要检查的链接

    Returns:
        同一主机返回True，不同主机返回False

    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='blog.index', **kwargs):
    """实现返回上一页

    如果上一页存在返回航一页，如果不存在则返回主页

    Args:
        default:上一页不存在时，返回的位置
        **kwargs:

    Returns:
        返回上一页或者设置的默认页

    """
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def generate_jwt(payload, expiry, secret=None):
    """
    :param payload: dict 载荷
    :param expiry: dateime 有效期
    :param secret: 秘钥
    :return: 生成 jwt
    """
    _payload = {'exp': expiry}
    _payload.update(payload)
    if not secret:
        secret = current_app.config['JWT_SECRET']  # 在配置文件中配置 JWT_SECRET
    
    token = jwt.encode(_payload, secret, algorithm='HS256')
    return token.decode()


def verify_jwt(token, secret=None):
    """
    校验jwt
    :param token: jwt
    :param secret: 秘钥
    :return dict: payload
    """
    if not secret:
        secret = current_app.config['JWT_SECRET']
    
    try:
        payload = jwt.decode(token, secret, algorithm='HS256')
    except jwt.PyJWTError:
        payload = None
    
    return payload
