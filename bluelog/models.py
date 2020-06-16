from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from bluelog.extensions import db


class Admin(db.Model, UserMixin):
    """生成管理员表的类

    规定了管理员和博客的各个属性

    Attributes:
        id: 管理员的 id 主键
        username: 管理员的用户名
        password_hash: 管理员经过 hash 处理后的密码
        blog_title: 博客的主标题
        blog_sub_title: 博客的副标题
        name: 管理员在前台显示的名称
        about: 管理员的介绍

    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    blog_title = db.Column(db.String(60))
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))
    about = db.Column(db.Text)

    def set_password(self, password):
        """设置管理员密码

        将明文密码进行 hash 处理后，存储密码。

        Args:
            password:明文密码

        """
        self.password_hash = generate_password_hash(password)
    
    def validate_password(self, password):
        """验证明文密码

        讲明文密码 hash 处理后和存储的 hash 密码进行比较

        Args:
            password:明文密码

        Returns:
            若 hash 处理后的明文密码与存储的明文密码相同，返回 True；不同返回 False

        """
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    """生成分类的类

    规定了分类的各个属性及与文章的关系

    Attributes:
        id:分类的id，主键
        name: 分类的名称，长度限制30，不能重复
        posts: 设置中间表名称

    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    posts = db.relationship('Post', back_populates='category')

    def delete(self):
        """删除分类

        删除分类并将此分类下的文章移至默认分类

        """
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    """生成文章表的类

    规定文章表的各个属性

    Attributes:
        id:文章的 id，主键
        title:文章的标题，限制长度60
        body:文章的内容
        timestamp:文章的创建时间，默认是当前时间
        can_coment:文章是否可以评论
        category_id:文章的分类id，外键
        category:设置和分类的中间表的名称
        coments:设置和评论的中间表的名称，规定删除文章时，删除文章下的所有评论

    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    can_comment = db.Column(db.Boolean, default=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    category = db.relationship('Category', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')


class Comment(db.Model):
    """生成评论表的类

    规定评论表的各个属性

    Attributes:
        id:评论的id
        author:评论的作者
        email:评论作者的E-mail
        site:评论作者的网址
        body:评论的内容
        form_admin:评论是否来自管理员
        reviewed:评论是否经过管理员审核
        timestamp:评论的时间，默认为当前时间，并设置索引
        post_id:评论文章的评论的外键为文章的id
        relied_id:回复评论的评论的外键为评论的id
        post:设置和post的中间表
        replies:
        relied:

    """
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    email = db.Column(db.String(354))
    site = db.Column(db.String(255))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)
    reviewed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

    post = db.relationship('Post', back_populates='comments')
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])


class Link(db.Model):
    """生成链接表的类

    生成链接的各个属性

    Attributes:
        id:链接的表，主键
        name:链接的名字
        url:链接的链接
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))
