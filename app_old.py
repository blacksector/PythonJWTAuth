import base64
import json
import os
import random
import uuid
import jwt
from datetime import datetime
from functools import wraps
from os import path
from flask import Flask, Response, current_app, jsonify, render_template, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from lib.mailer import *
from lib.tokens import *
# from lib.boto3_backend import *
from lib.utils import *

if path.exists("enable_prod"):
    PRODUCTION = True
else:
    PRODUCTION = False

# Current keys we are using in the system
key_names = []

for x in os.listdir('keys'):
    if "pub" not in x:
        key_names.append(x.strip(".key"))


# This will simply store the keys in a python dict
# for easier access
keys = []

# Get all keys:
for x in key_names:

    key_id = x

    pubKey = open('keys/' + x + '.key.pub', 'r').read()
    pubKey = "\n".join([l.lstrip() for l in pubKey.split("\n")])

    privKey = open('keys/' + x + '.key', 'r').read()
    privKey = "\n".join([l.lstrip() for l in privKey.split("\n")])

    keys.append({
        "id": key_id,
        "pubKey": pubKey,
        "privKey": privKey
    })


app = Flask(__name__)

CORS(app)


app.config['APP_VERSION'] = '0.0.1'
app.config['APP_NAME'] = 'Python JWT Auth'
app.config['APP_LOGO_URL'] = 'https://placehold.it/350x150'
# APP_URL is your company website
app.config['APP_URL'] = 'https://localhost/'
# API_ENDPOINT is the URL where this python api is accessible:
app.config['API_ENDPOINT'] = 'https://api.localhost/'
app.config['JWT_HEADER_NAME'] = 'python-auth'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ALGORITHM'] = 'RS256'
app.config['JWT_KEYS'] = keys
app.config['JWT_AUDIENCE'] = 'python-jwt-auth'
app.config['JWT_ISSUER'] = 'localhost'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

# Mailer Configuration:
app.config['MAILER_NAME'] = 'Python JWT Auth'
app.config['MAILER_ADDRESS'] = 'python@example.com'
app.config['MAILGUN_API_KEY'] = '75c43912434316ded1ac024e04c7bada-f82g78bb-28b0458f'
app.config['MAILGUN_MESSAGES_ENDPOINT'] = 'https://api.mailgun.net/v3/<YOUR_DOMAIN>/messages'

# More user based configs:
app.config['disable_signup'] = False
app.config['require_verified_email'] = False

# Social Logins
app.config['google_signin_enabled'] = False
app.config['facebook_signin_enabled'] = False
app.config['twitter_signin_enabled'] = False
app.config['instagram_signin_enabled'] = False


if PRODUCTION:
    DB_URL = 'mysql+pymysql://xmobile_user:4dv=y^83S6g7Hy?dt@wD*F!gLc8^a=k8XGH@localhost/xmobile'

    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    profile_pic = db.Column(db.String(255), nullable=True)
    email_verified = db.Column(db.Boolean, default=False)
    last_failed_attempt = db.Column(db.String(30), nullable=True)
    total_login_attempts = db.Column(db.Integer, default=0)
    stripe_customer_id = db.Column(db.String(25), nullable=True)
    created_at = db.Column(db.String(30), nullable=False, default=utc_timestamp())
    updated_at = db.Column(db.String(30), nullable=False, default=utc_timestamp())


# This decorator is used for protected endpoints
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = request.headers.get(current_app.config['JWT_HEADER_NAME']).split(current_app.config['JWT_HEADER_TYPE'] + ' ')[1]
            if not token:
                return jsonify({
                    "status": "failed",
                    "code": "auth/invalid-token",
                    "message": "Invalid or missing token in request header."
                }), 403
            try:
                key_id = get_unverified_data(token, 'kid')
                uid = get_unverified_data(token, 'sub')
                for x in keys:
                    if x['id'] == key_id:
                        key = x
                user = User.query.filter_by(uid=uid).first()
                if verify_access_token(current_app.config['JWT_ALGORITHM'], key, user.uid, token):
                    pass
                else:
                    return jsonify({
                        "status": "failed",
                        "code": "auth/invalid-token",
                        "message": "Invalid or missing token in request header."
                    }), 403
            except:
                return jsonify({
                    "status": "failed",
                    "code": "auth/invalid-token",
                    "message": "Invalid or missing token in request header."
                }), 403
        except:
            return jsonify({
                "status": "failed",
                "code": "auth/invalid-token",
                "message": "Invalid or missing token in request header."
            }), 403
        return f(*args, **kwargs)
    return decorated


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'DELETE', 'PUT', 'PATCH'])
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


@app.route('/settings', methods=['GET'])
@app.route('/settings/<path:url>', methods=["GET"])
def settings(url=None):
    if url == "keys":
        # Output the public keys
        pub_keys = {}
        for x in current_app.config["JWT_KEYS"]:
            pub_keys[x['id']] = x['pubKey']
        return jsonify(pub_keys), 200
    else:
        ret = {
            "external_auth": {
                "google": current_app.config["google_signin_enabled"],
                "facebook": current_app.config["facebook_signin_enabled"],
                "twitter": current_app.config["twitter_signin_enabled"],
                "instagram": current_app.config["instagram_signin_enabled"]
            },
            "disable_signup": current_app.config["DISABLE_SIGNUP"],
            "alg": current_app.config["JWT_ALGORITHM"],
            "version": current_app.config["APP_VERSION"],
            "key_url": '/settings/keys'
        }
        return jsonify(ret), 200

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    # Used specifically for a fresh token.
    fresh_token = request.json.get('fresh_token', None)

    # Check if email is valid
    if not validateEmail(email):
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
        # Allow user to change name:
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
    key = random.choice(keys)

    # User data to return:
    user_data = {
        "uid": user.uid,
        "name": user.name,
        "email": user.email,
        "email_verified": user.email_verified,
        "profile_picture": user.profile_pic,
        "created_at": int(user.created_at),
        "updated_at": int(user.updated_at),
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


@app.route('/signup', methods=['POST'])
def signup():
    if current_app.config['DISABLE_SIGNUP']:
        return jsonify({
            "status": "failed",
            "code": "auth/signup-disabled",
            "message": "Creating an account has been disabled by the administrator."
        }), 200

    name = request.json.get('name', None)
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    # TODO
    # Check if email is valid
    if not validateEmail(email):
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
    if name is None or len(name) <= 0:
        return jsonify({
            "status": "failed",
            "code": "auth/invalid-name-format",
            "message": "Invalid name format. Please enter a name!"
        }), 400

    # Now that all the data is validated. Lets FINALLY save this user:
    hashed_password = generate_password_hash(password, method='sha256')
    uid = str(uuid.uuid4())
    new_user = User(uid=uid, email=email, name=name, password=hashed_password, created_at=utc_timestamp())
    db.session.add(new_user)
    db.session.commit()

    key = random.choice(keys)

    verification_token = create_verification_token(current_app.config['JWT_ALGORITHM'], key, uid)

    opts = {
        "name": name,
        "token": verification_token
    }

    # TODO
    send_email(email, opts, 'verification')

    return jsonify({
        "status": "success",
        "code": "auth/user-registered",
        "message": "Successfully created your account! Login now."
    }), 200


@app.route('/refresh', methods=['POST'])
def refresh():
    token = request.json.get('token', None)
    if not token:
        return jsonify({
            "status": "failed",
            "code": "auth/invalid-token",
            "message": "Invalid or missing token in request header."
        }), 403

    try:
        key_id = get_unverified_data(token, 'kid')
        uid = get_unverified_data(token, 'sub')
        for x in keys:
            if x['id'] == key_id:
                key = x
        user = User.query.filter_by(uid=uid).first()
        if verify_refresh_token(current_app.config['JWT_ALGORITHM'], key, user.uid, token):
            # Get a new key:
            key = random.choice(keys)
            # Create access token:
            access_token = create_access_token(current_app.config['JWT_ALGORITHM'], key, user.uid)
            exp = get_unverified_data(access_token, 'exp')
            ret = {
                "status": "success",
                "access_token": access_token,
                "exp": exp
            }
            return jsonify(ret), 200
        else:
            return jsonify({
                "status": "failed",
                "code": "auth/invalid-refresh-token",
                "message": "Invalid refresh token, login again."
            }), 403
    except:
        return jsonify({
            "status": "failed",
            "code": "auth/invalid-refresh-token",
            "message": "Invalid refresh token, login again."
        }), 403


@app.route('/user', methods=['GET'])
@token_required
def get_user():
    # we'll grab the data based on the sub id,
    # we don't need to verify again as it has already
    # been verified by the token_required decorator.
    token = request.headers.get(current_app.config['JWT_HEADER_NAME']).split(current_app.config['JWT_HEADER_TYPE'] + ' ')[1]
    uid = get_unverified_data(token, 'sub')

    user = User.query.filter_by(uid=uid).first()
    if not user:
        # This shouldn't happen. But just a weird
        # possible case?
        return jsonify({
            "status": "failed",
            "code": "auth/user-does-not-exist",
            "message": "This user does not exist in the database."
        }), 400

    user_data = {
        "uid": user.uid,
        "name": user.name,
        "email": user.email,
        "email_verified": user.email_verified,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }
    return jsonify(user_data), 200


@app.route('/user', methods=['PATCH'])
@token_required
def patch_user():
    token = request.headers.get(current_app.config['JWT_HEADER_NAME']).split(current_app.config['JWT_HEADER_TYPE'] + ' ')[1]
    uid = get_unverified_data(token, 'sub')

    user = User.query.filter_by(uid=uid).first()

    # Allow user to change name:
    name = request.json.get('name', None)
    if name:
        user.name = name
        user.updated_at = utc_timestamp()
        db.session.commit()
        return jsonify({
            "status": "success",
            "code": "auth/changed-name",
            "message": "Successfully changed your name!"
        }), 200

    # Allow user to change email:
    # Check if another user is already
    # using this email address?
    email = request.json.get('email', None)
    if email:
        if email == user.email:
            return jsonify({
                "status": "failed",
                "code": "auth/email-already-exists",
                "message": "This is already your current email address."
            }), 400
        old_user = User.query.filter_by(email=email).first()
        if old_user:
            # User already exists:
            return jsonify({
                "status": "failed",
                "code": "auth/email-already-exists",
                "message": "This email already exists in our database for another user. Login to that account or use a different email address?"
            }), 400

        if validateEmail(email):
            # Set email and set email_verified to False.
            user.email = email
            user.email_verified = False
            user.updated_at = utc_timestamp()

            # This is to invalidate previous email verification tokens:
            # and logout users.
            new_uid = str(uuid.uuid4())
            user.uid = new_uid

            db.session.commit()

            # Send new verification email:
            key = random.choice(keys)
            verification_token = create_verification_token(current_app.config['JWT_ALGORITHM'], key, new_uid)
            opts = {
                "name": name,
                "token": verification_token
            }
            send_email(email, opts, 'verification')
            return jsonify({
                "status": "success",
                "code": "auth/changed-email",
                "message": "Successfully changed your email address, please check your inbox for a verification email! You may now login again."
            }), 200
        else:
            return jsonify({
                "status": "failed",
                "code": "auth/invalid-email-format",
                "message": "Invalid email format."
            }), 400

    # Allow user to change password, only if it is a FRESH token.
    fresh = get_unverified_data(token, 'data').get('fresh', None)
    if fresh:
        password = request.json.get('password', None)
        # Now, lets make sure the password is up to our security standards:
        if not validate_password(password):
            return jsonify({
                "status": "failed",
                "code": "auth/invalid-password-format",
                "message": "Invalid password format. Must contain at least one number, an uppercase & lowercase letter, a special character and must be greater than 8 characters."
            }), 400
        # This is to invalidate previous refresh tokens:
        new_uid = str(uuid.uuid4())
        user.uid = new_uid
        hashed_password = generate_password_hash(password, method='sha256')
        user.password = hashed_password
        user.updated_at = utc_timestamp()
        db.session.commit()
        return jsonify({
            "status": "success",
            "code": "auth/changed-password",
            "message": "Successfully changed your password!"
        }), 200
    else:
        return jsonify({
            "status": "failed",
            "code": "auth/not-fresh-token",
            "message": "You must login again before we can change your password."
        }), 400

    return jsonify({}), 200


@app.route('/recover', methods=['POST'])
def recover():
    # This endpoint resets the user's password
    # sensitive endpoint. No need to tell the user if
    # the reset was successful or not.
    email = request.json.get('email', None)

    # Check if email is valid
    if not validateEmail(email):
        return jsonify({
            "status": "failed",
            "code": "auth/invalid-email-format",
            "message": "Invalid email format."
        }), 400

    # Check if email exists. If so, send
    # reset password email.
    user = User.query.filter_by(email=email).first()
    if user:
        key = random.choice(keys)
        recovery_token = create_recovery_token(current_app.config['JWT_ALGORITHM'], key, user.uid)
        opts = {
            "name": user.name,
            "recovery_token": recovery_token
        }
        send_email(email, opts, 'recovery')

    # Return empty json array
    return jsonify({}), 200


@app.route('/verify/', methods=['GET'])
@app.route('/verify/<verification_token>', methods=['GET'])
def email_verification(verification_token=None):

    company_name = current_app.config['APP_NAME']
    company_logo = current_app.config['APP_LOGO_URL']
    body_header = "Email Verified"
    body_text = 'Thank you for verifying your email! You may return to the app and login to your accout now.'

    if not verification_token:
        body_header = "Missing Token"
        body_text = 'Your verification token is missing.'
        return render_template('verify_email.html', company_name=company_name, company_logo=company_logo, body_header=body_header, body_text=body_text)
    try:
        key_id = get_unverified_data(verification_token, 'kid')
        uid = get_unverified_data(verification_token, 'sub')
        for x in keys:
            if x['id'] == key_id:
                key = x
        user = User.query.filter_by(uid=uid).first()
        if not user:
            body_header = "Couldn't Verify Token"
            body_text = "Couldn't verify your token. Check your verification token and try again."
            return render_template('verify_email.html', company_name=company_name, company_logo=company_logo, body_header=body_header, body_text=body_text)

        # This means all we need to do is switch email_verified = True
        if verify_verification_token(current_app.config['JWT_ALGORITHM'], key, user.uid, verification_token):
            user.email_verified = True
            db.session.commit()
            return render_template('verify_email.html', company_name=company_name, company_logo=company_logo, body_header=body_header, body_text=body_text)
        else:
            body_header = "Couldn't Verify Token"
            body_text = "Couldn't verify your token. Check your verification token and try again."
            return render_template('verify_email.html', company_name=company_name, company_logo=company_logo, body_header=body_header, body_text=body_text)
    except:
        body_header = "Couldn't Verify Token"
        body_text = "Couldn't verify your token. Check your verification token and try again."
        return render_template('verify_email.html', company_name=company_name, company_logo=company_logo, body_header=body_header, body_text=body_text)


@app.route('/reset', methods=['GET'])
@app.route('/reset/<reset_token>', methods=['GET'])
def email_reset(reset_token=None):

    company_name = current_app.config['APP_NAME']
    company_logo = current_app.config['APP_LOGO_URL']

    body_header = "Password Reset"
    body_text = 'Thank you for verifying your email! You may return to the app and login to your account now.'

    if not reset_token:
        body_header = "Missing Token"
        body_text = 'Your verification token is missing.'
        return render_template('verify_email.html', company_name=company_name, company_logo=company_logo, body_header=body_header, body_text=body_text)

    if reset_token == "success":
        body_header = 'Password Reset Successful'
        body_text = 'Successfully reset your password! You may login now with your new password.'
        return render_template('reset_password.html', company_name=company_name, company_logo=company_logo, body_header=body_header, body_text=body_text)

    return render_template('reset_password.html', company_name=company_name, company_logo=company_logo, body_header=body_header, body_text=body_text, valid_token=True, reset_token=reset_token)


@app.route('/reset', methods=['POST'])
def reset():
    # This function verify's an email address
    # or simply do a forgot password / password reset:
    reset_token = request.json.get('reset_token', None)

    if not reset_token:
        return jsonify({
            "status": "failed",
            "code": "auth/missing-verification-token",
            "message": "Missing verification token"
        }), 400

    key_id = get_unverified_data(reset_token, 'kid')
    uid = get_unverified_data(reset_token, 'sub')

    for x in keys:
        if x['id'] == key_id:
            key = x

    user = User.query.filter_by(uid=uid).first()
    if not user:
        return jsonify({
            "status": "failed",
            "code": "auth/user-does-not-exist",
            "message": "This user does not exist in the database."
        }), 400

    # TODO: If the reset_token is invalid, the program just crashes and throws an
    # "Internal Server Error", just need to build in a try except statement later

    # This means we MUST have a password sent over our json data
    # This means all we need to do is switch email_verified = True
    if verify_recovery_token(current_app.config['JWT_ALGORITHM'], key, user.uid, reset_token):
        password = request.json.get('password', None)
        if not validate_password(password):
            return jsonify({
                "status": "failed",
                "code": "auth/invalid-password-format",
                "message": "Invalid password format. Must contain at least one number, an uppercase & lowercase letter, a special character and must be greater than 8 characters."
            }), 400
        # Force the user's id to change. This will invalidate
        # all previous tokens as the 'sub' will no longer match
        new_uid = str(uuid.uuid4())
        hashed_password = generate_password_hash(password, method='sha256')
        user.uid = new_uid
        user.password = hashed_password
        user.updated_at = utc_timestamp()
        user.email_verified = True
        db.session.commit()

        return jsonify({
            "status": "success",
            "code": "auth/password-changed",
            "message": "Successfully changed your password."
        }), 200
    else:
        return jsonify({
            "status": "failed",
            "code": "auth/invalid-token",
            "message": "Invalid token, maybe it expired?"
        }), 400

    return jsonify({}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=(not PRODUCTION))