from flask import Flask, jsonify, request
from database import db
from models.user import User
from auth import login_manager
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hello'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

login_manager.init_app(app)
db.init_app(app)

login_manager.login_view = 'login'

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/")
@login_required
def home():
    return '<h1>Welcome to the Flask App!</h1><p>Use the /health endpoint to check the health status.</p>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            
            print(current_user.is_authenticated)
            return jsonify({"message": "Login successful"}), 200

    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    if not username or not password or not confirm_password:
        return jsonify({"message": "All fields are required"}), 400

    if password != confirm_password: 
            return jsonify({"message": "Passwords do not match"}), 400

    if username and password and confirm_password:
    
        existing_user = User.query.filter_by(username=username).first()
    
        if existing_user:
            return jsonify({"message": "Username already exists"}), 400
    
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201

    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/user", methods=["GET"])
@login_required
def get_user():
    user_id = current_user.id
    user = User.query.get(user_id)
    if user:
        return jsonify({"id": user.id, "username": user.username}), 200
    return jsonify({"message": "User not found"}), 404

@app.route("/user", methods=["PUT"])
@login_required
def update_user():
    user_id = current_user.id
    data = request.get_json()
    new_username = data.get("new_username")

    user = User.query.get(user_id)
    if user:
        if new_username:
            user.username = new_username
            db.session.commit()
            return jsonify({"message": "User updated successfully"}), 200
        
        return jsonify({"message": "No new username provided"}), 400

    return jsonify({"message": "User not found"}), 404

@app.route("/user", methods=["DELETE"])
@login_required
def deleteu_user():
    user_id = current_user.id
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        logout_user()
        return jsonify({"message": "User deleted successfully"}), 200
    
    return jsonify({"message": "User not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)