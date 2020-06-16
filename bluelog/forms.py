from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import (BooleanField, HiddenField, PasswordField, SelectField,
                     StringField, SubmitField, TextAreaField, ValidationError)
from wtforms.validators import URL, DataRequired, Email, Length, Optional

from bluelog.models import Category


class LoginForm(FlaskForm):
    """"登录表单类

    设置登录表单的项目包括用户名，密码，是否记住和提交按钮。

    """
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    remember = BooleanField('Remember me')
    submit = SubmitField('登录')


class PostForm(FlaskForm):
    """文章表单类

    设置文章表单的项目包括，标题，分类，内容和提交按钮

    """
    title = StringField('Title', validators=[DataRequired(), Length(1, 60)])
    category = SelectField('Category', coerce=int, default=1)
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        """初始化表单内容

        为分类设置查询对象

        """
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


class CategoryForm(FlaskForm):
    """分类表单类

    设置分类的表单项目包括名称和提交按钮

    """
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField('提交')

    def validate_name(self, field):
        """验证分类名称是否合法

        验证分类名称是否重复，如果重复生成验证错误

        Args:
            field:表单项目名称

        """
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('Name already in use.')


class CommentForm(FlaskForm):
    """评论表单

    设置评论表单项目包括作者，邮箱地址，网站，内容和提交按钮

    """
    author = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    site = StringField('Site', validators=[Optional(), URL(), Length(0, 255)])
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('提交')


class AdminCommentForm(CommentForm):
    """管理员评论表单

    设置管理员评论隐藏表单包括作者，邮件，网址
    """
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()


class LinkForm(FlaskForm):
    """"链接表单

    设置链接表单包括名称，链接和提交按钮

    """
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    url = StringField('URL', validators=[DataRequired(), URL(), Length(1, 255)])
    submit = SubmitField('提交')


class SettingForm(FlaskForm):
    """设置表单

    设置表单项目包括名称，博客标题，博客副标题，介绍和提交按钮
    """
    name = StringField('Name', validators=[DataRequired(), Length(1,30)])
    blog_title = StringField('Blog Title', validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('Blog Sub Title', validators=[DataRequired(), Length(1, 100)])
    about = CKEditorField('About Page', validators=[DataRequired()])
    submit = SubmitField('提交')
