from flask import session, jsonify, redirect, request, flash, current_app
from functools import wraps
from models import db
from models import User

from datetime import datetime

from libs import get_unverified_data, verify_access_token

# This decorator is used for protected endpoints
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            keys = current_app.config["JWT_KEYS"]
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
                    return f(*args, **kwargs)
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
        return jsonify({
            "status": "failed",
            "code": "auth/invalid-token",
            "message": "Invalid or missing token in request header."
        }), 403
    return decorated