import random
from flask import Flask, request, jsonify, Blueprint, jsonify, current_app
from uuid import uuid4
from datetime import datetime

from .auth_decorator import token_required

# from libs.stripe_backend import create_stripe_customer
from libs import validate_password, utc_timestamp, validate_email, create_access_token, create_refresh_token
from sqlalchemy import or_

from werkzeug.security import check_password_hash, generate_password_hash

from models import db
from models import User, PublicUserSchema, UserSchema



user_handler = Blueprint('user_handler', __name__)

@user_handler.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
@user_handler.route('/<path:path>', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
def index(path=None):
    if path:
        return jsonify({
            "status": "failed",
            "code": "general/invalid-endpoint",
            "message": "Invalid API endpoint."
        }), 400
    return jsonify({
        'version': current_app.config["APP_VERSION"],
        'message': current_app.config["APP_NAME"]
    }), 200

@user_handler.route('/settings', methods=['GET'])
@user_handler.route('/settings/<path:url>', methods=["GET"])
def settings(url=None):
    if url == "keys":
        # Output the public keys
        pub_keys = {}
        for x in current_app.config["JWT_KEYS"]:
            pub_keys[x['id']] = x['pubKey']
        return jsonify(pub_keys), 200
    else:
        ret = {
            "disable_signup": current_app.config["DISABLE_SIGNUP"],
            "alg": current_app.config["JWT_ALGORITHM"],
            "version": current_app.config["APP_VERSION"],
            "key_url": '/settings/keys'
        }
        return jsonify(ret), 200

@user_handler.route('/login', methods=["GET", "POST"])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    # Used specifically for a fresh token.
    fresh_token = request.json.get('fresh_token', None)

    # Check if email is valid
    if not validate_email(email):
        return jsonify({
            "status": "failed",
            "code": "auth/invalid-email-format",
            "message": "Invalid email format."
        }), 400

    # Check if email already exists. Don't allow duplicate
    # registration:
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({
            "status": "failed",
            "code": "auth/user-does-not-exist",
            "message": "This user does not exist in the database."
        }), 400

    if user.total_login_attempts >= 3 and (int(user.last_failed_attempt) > int(utc_timestamp() - 30)):
        return jsonify({
            "status": "failed",
            "code": "auth/user-too-many-attempts",
            "message": "Too many attempts. Try again later in 5 minutes."
        }), 400

    if not check_password_hash(user.password, password):
        # Password was wrong! Update database with attempt:
        user.last_failed_attempt = utc_timestamp()
        user.total_login_attempts += 1
        db.session.commit()

        return jsonify({
            "status": "failed",
            "code": "auth/user-invalid-login",
            "message": "Invalid login data. Check your email and password and try again."
        }), 400

    if current_app.config['REQUIRE_VERIFIED_EMAIL'] is True and user.email_verified is False:
        return jsonify({
            "status": "failed",
            "code": "auth/require-verified-email",
            "message": "You must verify your email address before you can login."
        }), 403

    # User is verified. Write the access token and return data:
    # Get a random key for signing:
    key = random.choice(current_app.config["JWT_KEYS"])

    # User data to return:
    user_data = {
        "uid": user.uid,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "email_confirmed": user.email_confirmed,
        "profile_picture": user.profile_picture,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "status": "success"
    }

    # Everything looks okay, since this was a successful login,
    # reset the user password attempts:
    user.last_failed_attempt = None
    user.total_login_attempts = 0
    db.session.commit()

    # generate access token and refresh token:
    if fresh_token:
        access_token = create_access_token(current_app.config['JWT_ALGORITHM'], key, user.uid, fresh_token=True)
    else:
        access_token = create_access_token(current_app.config['JWT_ALGORITHM'], key, user.uid)

    refresh_token = create_refresh_token(current_app.config['JWT_ALGORITHM'], key, user.uid)

    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

    user_data.update({'tokens': tokens})

    return jsonify(user_data), 200

@user_handler.route('/signup', methods=['POST'])
def signup():
    if current_app.config['DISABLE_SIGNUP']:
        return jsonify({
            "status": "failed",
            "code": "auth/signup-disabled",
            "message": "Creating an account has been disabled by the administrator."
        }), 200

    first_name = request.json.get('first_name', None)
    last_name = request.json.get('last_name', None)
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    # TODO
    # Check if email is valid
    if not validate_email(email):
        return jsonify({
            "status": "failed",
            "code": "auth/invalid-email-format",
            "message": "Invalid email format."
        }), 400

    # Check if email already exists. Don't allow duplicate
    # registration:
    user = User.query.filter_by(email=email).first()
    if user:
        # User already exists:
        return jsonify({
            "status": "failed",
            "code": "auth/email-already-exists",
            "message": "This email already exists in our database. Login instead?"
        }), 400

    # TODO
    # Now, lets make sure the password is up to our security standards:
    if not validate_password(password):
        return jsonify({
            "status": "failed",
            "code": "auth/invalid-password-format",
            "message": "Invalid password format. Must contain at least one number, an uppercase & lowercase letter, a special character and must be greater than 8 characters."
        }), 400

    # Email and password is now validated. Let's force the user to at least submit a name:
    if (first_name is None or len(first_name) <= 0) or (last_name is None or len(last_name) <= 0):
        return jsonify({
            "status": "failed",
            "code": "auth/invalid-name-format",
            "message": "Invalid name format. Please enter a name!"
        }), 400

    # Now that all the data is validated. Lets FINALLY save this user:
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256:200000", salt_length=15)
    uid = str(uuid4())
    new_user = User(uid=uid, email=email, first_name=first_name, last_name=last_name, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    key = random.choice(current_app.config["JWT_KEYS"])

    verification_token = create_verification_token(current_app.config['JWT_ALGORITHM'], key, uid)

    opts = {
        "name": name,
        "token": verification_token
    }

    # TODO
    # send_email(email, opts, 'verification')

    return jsonify({
        "status": "success",
        "code": "auth/user-registered",
        "message": "Successfully created your account, login now."
    }), 200
