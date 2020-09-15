import re
from flask import current_app, g, jsonify, request, url_for
from flask import json
from flask.views import MethodView

from bluelog.apis.v1 import api_v1
from bluelog.apis.v1.auth import auth_required, generate_token, AuthorizationResource, jwt_login_required
from bluelog.apis.v1.errors import api_abort, ValidationError
from bluelog.apis.v1.schemas import post_schem, posts_schem, category_schem
from bluelog.models import Admin, Post, Category
from bluelog.extensions import db


def get_post_body():
    data = request.get_json()
    body = data.get('body')
    if body is None or str(body).strip() == '':
        raise ValidationError('The post body was empty or invalid.')
    return body


class IndexAPI(MethodView):

    def get(self):
        return jsonify({
            "api_version": "1.0",
            "api_base_url": "http://excample.com/api/v1",
        })


class PostAPI(MethodView):
    # 装饰器
    # decorator = [auth_required]
    # @auth_required
    def get(self, post_id):
        post = Post.query.get_or_404(post_id)
        return jsonify(post_schem(post))
    
    @jwt_login_required
    def put(self, post_id):
        post = Post.query.get_or_404(post_id)
        post.body = get_post_body(post)
        db.session.commit()
        return '', 204
    
    @jwt_login_required
    def patch(self, post_id):
        post = Post.query.get(post_id)
        if post:
            data = request.get_json()
            post.title = data.get('title')
            post.body = data.get('body')

        else:
            return jsonify(message="文章不存在")

    @jwt_login_required
    def delete(self, post_id):
        post = Post.query.get(post_id)
        if post:
            post_title = post.title
            db.session.delete(post)
            db.session.commit()
            return jsonify(message="删除 %s 成功" % post_title), 204
        else:
            return jsonify(message="文章不存在")


class AuthTokenAPI(MethodView):
    
    def post(self):
        grant_type = request.form.get('grant_type')
        username = request.form.get('username')
        password = request.form.get('password')

        if grant_type is None or grant_type.lower() != 'password':
            return api_abort(code=400, message='The grant type must be password.')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin is None or admin.validate_password(password):
            return api_abort(code=400, message='Either the username or password was invalid.')
        
        token, expiration = generate_token(admin)

        response = jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': expiration
        })
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        return response


class PostsAPI(MethodView):
    def get(self):
        page = request.args.get('page', 1, type=int)
        pagination = Post.query.paginate(page, per_page=current_app.config['BLUELOG_POST_PER_PAGE'])
        posts = pagination.items
        current = url_for('.posts', page=page, _external=True)
        prev = None
        if pagination.has_prev:
            prev = url_for('.posts', page=page - 1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for('.posts', page=page + 1, _external=True)
        return jsonify(posts_schem(posts, current, prev, next, pagination))


class CategoryAPI(MethodView):

    # decorator = [auth_required]
    # @auth_required
    def get(self, category_id):
        category = Category.query.get_or_404(category_id)
        return jsonify(category_schem(category))


api_v1.add_url_rule('/', view_func=IndexAPI.as_view('index'), methods=['GET'])
api_v1.add_url_rule('/oauth/token', view_func=AuthTokenAPI.as_view('token'), methods=['POST'])
api_v1.add_url_rule('/postauth', view_func=AuthorizationResource.as_view('postauth'), methods=['GET', 'POST'])
api_v1.add_url_rule('/posts', view_func=PostsAPI.as_view('posts'), methods=['GET', 'POST'])
api_v1.add_url_rule('/post/<int:post_id>', view_func=PostAPI.as_view('post'), methods=['GET', 'PUT', 'PATCH', 'Delete'])
api_v1.add_url_rule('/category/<int:category_id>', view_func=CategoryAPI.as_view('category'), methods=['GET', 'POST'])
