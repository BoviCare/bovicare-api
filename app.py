from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
db = SQLAlchemy(app)
CORS(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Adicionando a senha criptografada

    def json(self):
        return {'id': self.id, 'username': self.username, 'email': self.email}

with app.app_context():
    db.create_all()

# Rota de Teste
@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'test route'}), 200)

# Criar um novo usuário (registro)
@app.route('/users/register', methods=['POST'])
def create_user():
    try:
        data = request.get_json()

        # Verificando se os dados necessários foram enviados
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return make_response(jsonify({'message': 'Missing data'}), 400)

        # Criptografando a senha
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

        # Criando o usuário
        new_user = User(username=data['username'], email=data['email'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return make_response(jsonify({'message': 'User created successfully'}), 201)

    except e:
        return make_response(jsonify({'message': f'Error creating user: {str(e)}'}), 500)

# Login de Usuário
@app.route('/users/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()

        # Verificando se os dados de login foram enviados
        if not data.get('email') or not data.get('password'):
            return make_response(jsonify({'message': 'Missing email or password'}), 400)

        # Buscando o usuário pelo email
        user = User.query.filter_by(email=data['email']).first()
        
        if user and check_password_hash(user.password, data['password']):
            # Se o usuário existe e a senha bate, autenticamos
            return make_response(jsonify({'message': 'Login successful', 'user': user.json()}), 200)
        else:
            # Se o usuário não for encontrado ou a senha for incorreta
            return make_response(jsonify({'message': 'Invalid email or password'}), 401)

    except e:
        return make_response(jsonify({'message': f'Error logging in: {str(e)}'}), 500)

# Obter todos os usuários
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return make_response(jsonify([user.json() for user in users]), 200)
    except e:
        return make_response(jsonify({'message': f'Error fetching users: {str(e)}'}), 500)

# Obter um usuário pelo ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            return make_response(jsonify({'user': user.json()}), 200)
        return make_response(jsonify({'message': 'User not found'}), 404)
    except e:
        return make_response(jsonify({'message': f'Error fetching user: {str(e)}'}), 500)

# Atualizar um usuário
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
    except e:
        return make_response(jsonify({'message': f'Error updating user: {str(e)}'}), 500)

# Deletar um usuário
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'message': 'User deleted'}), 200)
        return make_response(jsonify({'message': 'User not found'}), 404)
    except e:
        return make_response(jsonify({'message': f'Error deleting user: {str(e)}'}), 500)

if __name__ == '__main__':
    app.run(debug=True)
