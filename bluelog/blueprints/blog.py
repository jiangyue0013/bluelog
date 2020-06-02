from flask import (Blueprint, current_app, render_template,
                   request, redirect, url_for,
                   abort, make_response, flash)
from flask_login import current_user

from bluelog.models import Category, Comment, Post
from bluelog.emails import send_new_comment_email, send_new_reply_email
from bluelog.extensions import db
from bluelog.forms import AdminCommentForm, CommentForm
from bluelog.utils import redirect_back

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.order_by(
        Post.timestamp.desc()
    ).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/index.html',
                           pagination=pagination,
                           posts=posts)


@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(
        Post.timestamp.desc()
    ).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/category.html',
                           category=category,
                           pagination=pagination,
                           posts=posts)


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    perpage = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(
        reviewed=True
    ).order_by(Comment.timestamp.asc()).paginate(page, perpage)
    comments = pagination.items

    if current_user.is_authenticated:  # 如果当前用户已登录，使用管理员表单
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLUELOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False
    
    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author,
            email=email,
            site=site,
            body=body,
            from_admin=from_admin,
            post=post,
            reviewed=reviewed
        )
        replied_id = request.args.get('reply')
        if replied_id:  # 如果 URL 中 reply 查询参数存在，那么说明是回复
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)  # 发邮件给被回复用户
        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:  # 根据登录状态现实不同的提示信息
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed.',
                  'info')
            send_new_comment_email(post)  # 发送提醒邮件给管理员
        return redirect(url_for('.show_post', post_id=post.id))
    return render_template('blog/post.html',
                           post=post,
                           pagination=pagination,
                           comments=comments,
                           form=form)


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(url_for('.show_post',
                            post_id=comment.post.id,
                            reply=comment_id,
                            author=comment.author)
                    + '#comment-form')


@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BLUELOG_THEMES'].keys():
        abort(404)
    
    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30*24*60*60)
    return response
