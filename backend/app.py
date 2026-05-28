import os
import logging

from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_bcrypt import Bcrypt

try:
    from .models import db, User
except ImportError:
    from models import db, User


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True   # required when SameSite=None
app.config["SESSION_COOKIE_HTTPONLY"] = True

database_location = os.getenv("DATABASE_LOCATION")

if database_location:
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{Path(database_location).resolve().as_posix()}"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///financeable.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"], supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(id):
    try:
        return db.session.get(User, int(id)) if id else None
    except (TypeError, ValueError):
        return None

def _user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }

def get_user_key():
    if current_user.is_authenticated:
        return f"user:{current_user.id}"
    
    return f"ip:{get_remote_address()}"

# Configure storage backend for Flask-Limiter via env var `RATELIMIT_STORAGE_URI`.
# Examples: redis://localhost:6379 or memory://
storage_uri = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

if storage_uri.startswith("memory"):
    logging.getLogger(__name__).warning(
        "RATELIMIT_STORAGE_URI not set; using in-memory storage. Not recommended for production."
    )

limiter = Limiter(
    key_func=get_user_key,
    app=app,
    default_limits=["30 per minute"],
    storage_uri=storage_uri,
)

import src.getTransactions as getTransactions
import src.uploadTransaction as uploadTransaction
import src.pullReport as pullReport

@app.route("/register", methods=["POST"])
@limiter.limit("1 per day")
def register():
    data = request.json
    
    username = data.get("username", "").strip()
    password = data.get("password", "")
    email = data.get("email")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409

    user = User(
        username=username,
        password=bcrypt.generate_password_hash(password).decode("utf-8"),
        email=email,
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)

    return jsonify({"status": "success", "user": _user_payload(user)}), 201

@app.route("/login", methods=["POST"])
@limiter.limit("60 per minute; 20000 per day")
def login():
    data = request.json

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    try:
        password_matches = user and bcrypt.check_password_hash(user.password, password)
    except ValueError:
        password_matches = False

    if not password_matches:
        return jsonify({"error": "Invalid credentials"}), 401

    login_user(user)
    return jsonify({"status": "success", "user": _user_payload(user)}), 200


@app.route("/logout", methods=["POST"])
@limiter.limit("60 per minute; 20000 per day")
def logout():
    if current_user.is_authenticated:
        logout_user()

    return jsonify({"status": "success"}), 200

@app.route("/create-report", methods=['POST'])
@login_required
@limiter.limit("1 per minute; 10 per day")
def get_transations():
    if 'report' not in request.files: return 'No file', 400
    
    report = request.files['report']

    if not request.form['internal_transfers']:
        internal_transfers = set()

    else:
        internal_transfers = set(request.form['internal_transfers'].split(','))

    match request.form['returnType'].upper():
        case 'JSON': returnType = getTransactions.ReturnType.JSON
        case '': return jsonify({'Status': 'Fail', 'Message': "Null Return Type"}), 404
        case _: return jsonify({'Status': 'Fail', 'Message': "Invalid Return Type"}), 403
        
    transactions = getTransactions.run(report, returnType, internal_transfers)

    return jsonify({"Status": "Success", "transactions": transactions}), 200

@app.route("/upload-report", methods=['POST'])
@login_required
@limiter.limit("10 per minute; 200 per day")
def upload_report():
    data = request.json

    if 'user_id' not in data: return 'null id', 400

    if 'transactions' not in data: return 'null transactions', 400

    try:
        uploadTransaction.run(data['user_id'], data['transactions'])

        return jsonify({"Status": "Success"}), 200

    except Exception as e:
        print(e)
        return str(e), 500
    
@app.route("/get-report", methods=["POST"])
@login_required
@limiter.limit("60 per minute; 2000 per day")
def get_report():
    data = request.json

    input_type = data['input_type']
    date = data['date']
    return_type = data['return_type']

    user = _user_payload(current_user)

    print(user)

    try:
        report = pullReport.run(userID=user['id'], inputType=input_type, date=date, returnType=return_type)

        return jsonify({'status': 'success', 'report': report}), 200
    except Exception as e:
        print(e)
        return str(e), 500

if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5001"))
    app.run(debug=True, host=host, port=port)