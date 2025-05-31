from flask import request, jsonify, make_response
from app import app, db
from app.models import User

@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'test route'}), 200)

@app.route('/users/register', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return make_response(jsonify({'message': 'Missing data'}), 400)

        # Senha será salva como texto puro (sem criptografia)
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )

        db.session.add(new_user)
        db.session.commit()

        return make_response(jsonify({'message': 'User created successfully'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error creating user: {str(e)}'}), 500)

@app.route('/users/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        if not data.get('email') or not data.get('password'):
            return make_response(jsonify({'message': 'Missing email or password'}), 400)

        user = User.query.filter_by(email=data['email']).first()

        if user and user.password == data['password']:
            return make_response(jsonify({'message': 'Login successful', 'user': user.json()}), 200)
        else:
            return make_response(jsonify({'message': 'Invalid email or password'}), 401)

    except Exception as e:
        return make_response(jsonify({'message': f'Error logging in: {str(e)}'}), 500)

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return make_response(jsonify([user.json() for user in users]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error fetching users: {str(e)}'}), 500)

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            return make_response(jsonify({'user': user.json()}), 200)
        return make_response(jsonify({'message': 'User not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error fetching user: {str(e)}'}), 500)

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            data = request.get_json()
            user.username = data['username']
            user.email = data['email']
            db.session.commit()
            return make_response(jsonify({'message': 'User updated'}), 200)
        return make_response(jsonify({'message': 'User not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating user: {str(e)}'}), 500)

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'message': 'User deleted'}), 200)
        return make_response(jsonify({'message': 'User not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting user: {str(e)}'}), 500)
