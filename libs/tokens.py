import datetime
import uuid
import jwt
from flask import current_app
from calendar import timegm


def utc_timestamp(t=datetime.datetime.utcnow()):
    return timegm(datetime.datetime.utcnow().utctimetuple())


def get_unverified_data(token, data=None):
    if data:
        return jwt.decode(token, verify=False)[data]
    return jwt.decode(token, verify=False)


def create_access_token(algorithm, key, uid, fresh_token=False, expires_delta=900):
    additional_data = {"type": "access_token"}
    if fresh_token:
        additional_data.update({"fresh": True})
    return encode_token(algorithm, key, uid, expires_delta, additional_data=additional_data)


def create_refresh_token(algorithm, key, uid, expires_delta=31536000):
    return encode_token(algorithm, key, uid, expires_delta, {"type": "refresh_token"})


def create_verification_token(algorithm, key, uid, expires_delta=False):
    return encode_token(algorithm, key, uid, expires_delta, {"type": "verification_token"})


def create_recovery_token(algorithm, key, uid, expires_delta=3600):
    return encode_token(algorithm, key, uid, expires_delta, {"type": "recovery_token"})


def verify_access_token(algorithm, key, uid, token):
    try:
        data = decode_token(token, algorithm, key['pubKey'])
        if data['sub'] != uid:
            return False
        if data['data']['type'] != "access_token":
            return False
        return True
    except:
        return False


def verify_refresh_token(algorithm, key, uid, token):
    try:
        data = decode_token(token, algorithm, key['pubKey'])
        if data['sub'] != uid:
            return False
        if data['data']['type'] != "refresh_token":
            return False
        return True
    except:
        return False


def verify_verification_token(algorithm, key, uid, token):
    try:
        data = decode_token(token, algorithm, key['pubKey'])
        if data['sub'] != uid:
            return False
        if data['data']['type'] != "verification_token":
            return False
        return True
    except:
        return False


def verify_recovery_token(algorithm, key, uid, token):
    try:
        data = decode_token(token, algorithm, key['pubKey'])
        if data['sub'] != uid:
            return False
        if data['data']['type'] != "recovery_token":
            return False
        return True
    except:
        return False


def encode_token(algorithm, key, subject, expires_delta, additional_data=None):
    uid = str(uuid.uuid4())
    now = utc_timestamp()
    token_data = {
        'iat': now,
        'aud': current_app.config['JWT_AUDIENCE'],
        'iss': current_app.config['JWT_ISSUER'],
        'nbf': now,
        'jti': uid,
        'kid': key['id'],
        'sub': subject
    }
    # If expires_delta is False, the JWT should never expire
    # and the 'exp' claim is not set.
    if expires_delta:
        token_data['exp'] = now + expires_delta
    if additional_data:
        token_data.update({"data": additional_data})
    encoded_token = jwt.encode(token_data, key['privKey'], algorithm).decode('utf-8')
    return encoded_token


def decode_token(token, algorithm, key, audience=None, issuer=None):
    if audience is None:
        audience = current_app.config['JWT_AUDIENCE']
    if issuer is None:
        issuer = current_app.config['JWT_ISSUER']
    return jwt.decode(token, key, audience=audience, issuer=issuer, algorithms=algorithm)
