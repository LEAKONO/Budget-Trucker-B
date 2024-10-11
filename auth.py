from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required
from app import db
from models import User  
from schemas import validate_user

bp_auth = Blueprint('auth', __name__)

@bp_auth.route('/signup', methods=['POST'])
def signup():
    data = request.json
    validated_data, errors = validate_user(data)
    if errors:
        return jsonify(errors), 400

    username = validated_data['username']
    password = validated_data['password']
    email = validated_data.get('email')
    
    if not email:
        return jsonify({'message': 'Email is required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password=hashed_password, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@bp_auth.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        }), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@bp_auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logged out successfully'}), 200
