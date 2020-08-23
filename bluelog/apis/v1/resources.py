from flask import jsonify

from bluelog.apis.v1 import api_v1
from bluelog.models import Post
from bluelog.apis.v1.schemas import post_schem


@api_v1.route('/')
def index():
    return jsonify(message='hello, world!')


@api_v1.route('/post/<int:post_id>')
def post_id(post_id):
    post = Post.query.get_or_404(post_id)
    return post_schem(post)

