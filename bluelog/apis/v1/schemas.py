from flask import url_for

def post_schem(post):
    return {
        'id': post.id,
        'title': post.title,
        'body': post.body,
        'timestamp': post.timestamp,
        'can_comment': post.can_comment,
        'category_id': post.category_id,
    }

def category_schem(category):
    return {
        'id': category.id,
        'name': category.name,
    }

def comment_schem(comment):
    return {
        'id': comment.id,
        'author': comment.author,
        'email': comment.email,
        'site': comment.site,
        'body': comment.body,
        'from_admin': comment.from_admin,
        'reviewed': comment.reviewed,
        'timestamp': comment.timestamp,
        'post_id': comment.post_id,
        'replied_id': comment.replied_id,
    }