from flask import Blueprint, redirect, render_template, flash, url_for
from flask_login import current_user, login_user, login_required, logout_user

from bluelog.forms import LoginForm
from bluelog.models import Admin
from bluelog.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """管理员登录函数"""
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = Admin.query.first()
        if admin:
            # 验证用户名和密码
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)  # 登录用户
                flash('Welcome back.', 'info')
                return redirect_back()  # 返回上一个页面
            flash('Invalid username or password', 'warning')
        else:
            flash('No account.', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required  # 用于视图保护
def logout():
    """管理员注销"""
    logout_user()
    flash('Logout success.', 'info')
    return redirect_back()
