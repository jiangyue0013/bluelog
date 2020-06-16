try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for, current_app


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