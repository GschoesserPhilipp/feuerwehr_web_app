import os
from datetime import timedelta, datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, set_access_cookies, unset_jwt_cookies
)
from flask_jwt_extended.exceptions import NoAuthorizationError
from dotenv import load_dotenv
from .models import User, db, ErrorList, ErrorHistory

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("JWT_SECRET_KEY")

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=48)

db.init_app(app)
jwt = JWTManager(app)

@app.route('/')
@jwt_required()
def index():

    top_entries = ErrorHistory.query.order_by(ErrorHistory.time.asc()).limit(10).all()
    all_entries = ErrorHistory.query.order_by(ErrorHistory.timestamp.asc()).all()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    grouped_data = {}
    for entry in all_entries:
        group = entry.group_name
        if group not in grouped_data:
            grouped_data[group] = {"timestamps": [], "times": []}
        grouped_data[group]["timestamps"].append(entry.timestamp.strftime('%Y-%m-%d %H:%M'))
        grouped_data[group]["times"].append(entry.time)

    return render_template('index.html', top_entries=top_entries, grouped_data=grouped_data, current_user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return render_template("login.html", error="Login fehlgeschlagen")

    access_token = create_access_token(identity=str(user.id))
    response = redirect(url_for('index'))
    set_access_cookies(response, access_token)
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")

    username = request.form.get('username')
    password = request.form.get('password')

    if User.query.filter_by(username=username).first():
        return render_template("register.html", error="Benutzername existiert bereits")

    new_user = User(username=username, is_admin=False)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    response = redirect(url_for('login'))
    unset_jwt_cookies(response)
    return response

@app.route("/table")
@jwt_required()
def table_view():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    history_entries = ErrorHistory.query.filter_by(group_name=user.username).order_by(ErrorHistory.timestamp.desc()).all()
    error_texts = {e.id: e.error_text for e in ErrorList.query.all()}

    measurements = []
    for entry in history_entries:
        total_errors = sum(getattr(entry, f"error_{i}") for i in range(1, 17))
        error_details = [
            {
                "id": i,
                "count": getattr(entry, f"error_{i}"),
                "name": error_texts.get(i, f"Fehler {i}")
            }
            for i in range(1, 17)
        ]

        measurements.append({
            "id": entry.id,
            "datetime": entry.timestamp.strftime("%d.%m.%Y %H:%M"),
            "time": entry.time,
            "time_with_errors": entry.time_with_errors,
            "total_errors": total_errors,
            "error_details": error_details
        })

    return render_template("table.html", measurements=measurements, current_user=user)


############################################### API ###############################################################

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Login failed"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)


@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username und Passwort sind erforderlich"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Benutzername existiert bereits"}), 409

    new_user = User(username=username, is_admin=False)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Benutzer erfolgreich registriert"}), 201


@app.route('/api/new-error', methods=['POST'])
@jwt_required()
def add_error_history():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    error_definitions = {e.id: e.time for e in ErrorList.query.all()}
    error_sum = 0
    error_data = {}


    for i in range(1, 17):
        key = f"error_{i}"
        count = data.get(key, 0)
        weight = error_definitions.get(i, 0)
        error_sum += count * weight
        error_data[key] = count

    time_with_errors = data["time"] + error_sum

    try:
        entry = ErrorHistory(
            group_name=user.username,
            timestamp=datetime.now(),
            time=data["time"],
            time_with_errors=time_with_errors,
            **error_data
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({"msg": "Eintrag erfolgreich hinzugefügt"}), 201
    except KeyError as e:
        return jsonify({"error": f"Fehlendes Feld: {e.args[0]}"}), 400


@app.route('/api/error-history', methods=['GET'])
@jwt_required()
def get_error_history():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Benutzer nicht gefunden"}), 404

    entries = ErrorHistory.query.filter_by(group_name=user.username).order_by(ErrorHistory.timestamp.desc()).all()
    error_definitions = {e.id: e.error_text for e in ErrorList.query.all()}

    result = []
    for entry in entries:
        error_list = []
        for i in range(1, 17):
            count = getattr(entry, f'error_{i}', 0)
            if count > 0:
                error_list.append({
                    "id": i,
                    "count": count,
                    "text": error_definitions.get(i, f"Fehler {i}")
                })

        result.append({
            "timestamp": entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "time": entry.time,
            "time_with_errors": entry.time_with_errors,
            "errors": error_list
        })

    return jsonify(result), 200


@app.route('/api/error-list')
@jwt_required()
def error_list():
    errors = ErrorList.query.with_entities(
        ErrorList.id,
        ErrorList.error_text,
        ErrorList.time
    ).all()
    return jsonify([
        {"id": e.id, "error_text": e.error_text, "time": e.time}
        for e in errors
    ])

@app.route('/api/user-list')
@jwt_required()
def user_list():
    users = User.query.with_entities(User.username).filter_by(is_admin=False).all()
    return jsonify([user.username for user in users])

@app.route("/api/docs")
def docs():
    return app.send_static_file("swagger.html")

@app.errorhandler(NoAuthorizationError)
def handle_missing_token(e):
    return redirect(url_for('login'))

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    response = make_response(redirect(url_for("login")))
    unset_jwt_cookies(response)
    return response

@app.errorhandler(401)
def handle_unauthorized(e):
    return redirect(url_for('login'))
