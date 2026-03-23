from flask import Flask, jsonify, request
from database import db
from models.user import User
from auth import login_manager
from flask_login import login_user, current_user

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

if __name__ == "__main__":
    app.run(debug=True)