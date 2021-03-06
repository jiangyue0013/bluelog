from flask import (Blueprint, render_template, request,
                   current_app, redirect, flash,
                   url_for)


from flask_login import login_required, current_user


from bluelog.extensions import db
from bluelog.models import Category, Post, Comment, Link, Admin
from bluelog.forms import PostForm, CategoryForm, LinkForm, SettingForm
from bluelog.utils import redirect_back

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/settings', methods=['get', 'post'])
@login_required
def settings():
    """设置界面路由函数

    Returns:
        设置界面
    """
    form = SettingForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.blog_title = form.blog_title.data
        current_user.blog_sub_title = form.blog_sub_title.data
        current_user.about = form.about.data
        db.session.commit()
        flash('Setting updated.', 'success')
        return redirect(url_for('blog.index'))
    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    form.about.data = current_user.about
    return render_template('admin/settings.html', form=form)


@admin_bp.route('/post/manage')
@login_required
def manage_post():
    """文章管理界面路由函数

    Returns:
        文章管理界面
    """
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(
        Post.timestamp.desc()
    ).paginate(page,
               per_page=current_app.config['BLUELOG_MANAGE_POST_PER_PAGE'])
    posts = pagination.items
    return render_template('admin/manage_post.html',
                           pagination=pagination,
                           posts=posts)


@admin_bp.route('/category/manage')
@login_required
def manage_category():
    """分类管理界面路由函数

    Returns:
        分类管理界面
    """
    categories = Category.query.all()
    return render_template('admin/manage_category.html', categories=categories)


@admin_bp.route('/comment/manage')
@login_required
def manage_comment():
    """评论管理界面路由函数

    Returns:
        评论管理界面
    """
    filter_rule = request.args.get('filter', 'all')  # 从查询字符串获取过滤规则
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        filtered_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == 'admin':
        filtered_comments = Comment.query.filter_by(from_admin=True)
    else:
        filtered_comments = Comment.query

    pagination = filtered_comments.order_by(
        Comment.timestamp.desc()
    ).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html',
                           comments=comments,
                           pagination=pagination)


@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """创建新文章界面路由函数

    Returns:
        创建新文章界面
    """
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        post = Post(title=title, body=body, category=category)
        db.session.add(post)
        db.session.commit()
        flash('Post Created', 'Success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """文章编辑界面路由函数

    Args:
        post_id:文章id

    Returns:
        文章编辑界面
    """
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """删除文章界面

    Args:
        post_id:删除的文章id
    Returns:
        删除界面
    """
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back()


@admin_bp.route('/link/manage')
@login_required
def manage_link():
    """链接管理界面

    Returns:
        返回路由管理界面
    """
    links = Link.query.all()
    return render_template('admin/manage_link.html', links=links)


@admin_bp.route('/set-comment/<int:post_id>', methods=['POST'])
@login_required
def set_comment(post_id):
    """设置评论开关"""
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled', 'info')
    else:
        post.can_comment = True
        flash('Comment enable.', 'inofo')
    db.session.commit()
    return redirect(url_for('blog.show_post', post_id=post_id))


@admin_bp.route('/comment/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """删除评论"""
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论删除成功.', 'success')
    return redirect_back()


@admin_bp.route('/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve_comment(comment_id):
    """已读评论"""
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash('Comment published.', 'success')
    return redirect_back()


@admin_bp.route('/category/<int:category_id>/delete', methods=['post'])
@login_required
def delete_category(category_id):
    """删除分类"""
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not delete the default category.', 'warning')
        return redirect(url_for('blog.index'))
    category.delete()
    flash('Category deleted.', 'success')
    return redirect(url_for('admin.manage_category'))


@admin_bp.route('/link/<int:link_id>/delete', methods=['post'])
@login_required
def delete_link(link_id):
    """删除链接"""
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('Link deleted.', 'success')
    return redirect(url_for('admin.manage_link'))


@admin_bp.route('/category/<int:category_id>/edit', methods=['get', 'post'])
@login_required
def edit_category(category_id):
    """编辑分类"""
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not edit the default category.', 'warning')
        return redirect(url_for('blog.index'))
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category update.', 'success')
        return redirect(url_for('admin.manage_category'))

    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)


@admin_bp.route('/link/<int:link_id>/edit', methods=['get', 'post'])
@login_required
def edit_link(link_id):
    """编辑链接"""
    form = LinkForm()
    link = Link.query.get_or_404(link_id)
    if form.validate_on_submit():
        link.name = form.name.data
        link.url = form.url.data
        db.session.commit()
        flash('Link update.', 'success')
        return redirect(url_for('admin.manage_link'))

    form.name.data = link.name
    form.url.data = link.url
    return render_template('admin/edit_link.html', form=form)


@admin_bp.route('/link/new', methods=['get', 'post'])
@login_required
def new_link():
    """新建链接"""
    form = LinkForm()
    if form.validate_on_submit():
        name = form.name.data
        url = form.url.data
        link = Link(name=name, url=url)
        db.session.add(link)
        db.session.commit()
        flash('New link created.', 'success')
        return redirect(url_for('admin.manage_link'))
    return render_template('admin/new_link.html', form=form)


@admin_bp.route('/category/new', methods=['get', 'post'])
@login_required
def new_category():
    """新建分类"""
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('New category created.', 'successs')
        return redirect(url_for('admin.manage_category'))
    return render_template('admin/new_category.html', form=form)