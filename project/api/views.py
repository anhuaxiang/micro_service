# project/api/views.py
from flask import Blueprint, jsonify, request, render_template
from project import db
from sqlalchemy import exc
from project.api.models import User


users_blueprint = Blueprint('users', __name__, template_folder='./templates')


@users_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        db.session.add(User(username=username, email=email))
        db.session.commit()
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('index.html', users=users)


@users_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@users_blueprint.route('/users', methods=['POST'])
def add_user():
    # 获取POST的数据
    post_data = request.get_json()

    if not post_data:
        response_data = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_data), 400

    email = post_data.get('email')
    username = post_data.get('username')

    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            # 证明数据库中不存在该email的用户，可以添加
            db.session.add(User(username=username, email=email))
            db.session.commit()
            response_data = {
                'status': 'success',
                'message': '%s was added!' % email
            }
            return jsonify(response_data), 201
        # 证明该email已经存在
        response_data = {
            'status': 'fail',
            'message': 'Sorry. That email already exists.'
        }
        return jsonify(response_data), 400
    except exc.IntegrityError as e:
        db.session.rollback()  # 出现异常了，回滚
        response_data = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_data), 400


@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """获取某用户的详细信息"""

    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    code = 404

    try:
        user = User.query.filter_by(id=int(user_id)).first()
        response_object = {
            'status': 'success',
            'data': {
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at
            }
        }
        code = 200
    except ValueError:
        response_object = {
            'status': 'fail',
            'message': 'Param id error'
        }
        code = 400
    finally:
        return jsonify(response_object), code


@users_blueprint.route('/users', methods=['GET'])
def get_all_users():
    """获取所有的用户列表"""
    users = User.query.all()
    users_message = []
    for u in users:
        users_message.append({
            'username': u.username,
            'email': u.email,
            'created_at': u.created_at,
            'id': u.id,
        })

    response_object = {
        'status': 'success',
        'data': {
            'users': users_message
        }
    }
    code = 200

    return jsonify(response_object), code
