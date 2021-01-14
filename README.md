<div align="center">
  <img src="https://placehold.it/350x150" width="350" height="150"/>
  <br/>
  <br/>
  <br/>
</div>

<br/>
<br/>

# Python JWT Auth

> A full JWT token authentication library in Python Flask. 

<br/>

This library intends to make API development easier by providing a base with JWT Authentication for mobile apps and websites.

#### Why a entirely new API and not a third-party tool?

Here is why:
 - Splitting code into more reusable parts
 - Easier to deploy
 - One point to take care of in the case of an incident
 - Code and database portability. No need to rely on expensive services like Google's Firebase.
 - And, it's fun.
 
<br/>

## Features
- JWT Based authentication
- Security best practices with rate limiting for logins (TODO)
- Protected endpoints
- Easy to deploy new keys and invalidate all user logins
- DigitalOcean Spaces / Amazon S3 (user files/pictures) Support
- Built in password reset and email verification pages
- Social Logins (TODO)

<br/>

## Getting started
#### 1 . Setup software
Generally you will need to install a couple of things if on a development environment, but both development and production environments require the following:
- Python 3
- Pip

Use the following command to install the required python modules:

```sh
$ pip install flask flask-Cors flask-sqlalchemy requests boto3
```

for _production_ environments you also need:
- A database (like MySQL) installed on the machine or a remote database setup (managed DigitalOcean MySQL)
```sh
$ pip install pymysql
```

#### 2. Generating JWT Keys
Repeat this step as many times as you want to create a larger set of keys. These keys will be used to sign your JWT tokens.

<small>Make sure you are saving everything inside of the `keys` folder! The name of the file does not matter, but we specifically prefer using random MD5 hashes as the name:</small>

1. Generate private keys:
```sh
$ openssl genrsa 2048
```

2. We will save our output as `keys/e517ff21f2eb3767c35685ad380e39cd.key`. This is what our key looks like (YOUR KEY MUST BE DIFFERENT):
```
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAv8EnGM6MkYN45sreu3vsAVkzWGDbhOoBBHUC9TEdGv5Kh3BY
twH8QFwmFENmjV3eHRAFoXG2NXN6aZBfOtxQg08mbPtnJdTxJplu7+HIQBmt7I7f
..........
L3y2k/4SP0JtabjOU1Nq
e3Rd3wKBgD2pDAokneERFx4AAX151ofg3GNnZF9VHfqlQatp9H8phFd+IkkmgF6a
LjpYUQHslCne2nTSQTDJ7UdHt3JVfa8hN0x6jVsyGYw8zm6dlt/TL/MSqFNsxM83
bWQkSxJhescog1IpvUtDVzHqZnUx0QejVYlsPMCh3onuzxXnJ4gT
-----END RSA PRIVATE KEY-----
```

2. Now run this command:

Remember to replace "PRIVATE_KEY_HERE" with the private key that you copied from the last command

```
private_key="PRIVATE_KEY_HERE"
```

It should look a little like this:
```
$ private_key="-----BEGIN RSA PRIVATE KEY-----                                                                          > MIIEowIBAAKCAQEAv8EnGM6MkYN45sreu3vsAVkzWGDbhOoBBHUC9TEdGv5Kh3BY
> twH8QFwmFENmjV3eHRAFoXG2NXN6aZBfOtxQg08mbPtnJdTxJplu7+HIQBmt7I7f
> 3xR3thdC0gsT1VmjYeOlCGIoyei5pViIYhwrJJxycM7Nj4g+cCG8duCJSBwKBivF
> ..........
> iKmIRLJo6gh3rEQtmi3kTNE1jwdlGkIW8dsZUiliElWQL3y2k/4SP0JtabjOU1Nq
> e3Rd3wKBgD2pDAokneERFx4AAX151ofg3GNnZF9VHfqlQatp9H8phFd+IkkmgF6a
> LjpYUQHslCne2nTSQTDJ7UdHt3JVfa8hN0x6jVsyGYw8zm6dlt/TL/MSqFNsxM83
> bWQkSxJhescog1IpvUtDVzHqZnUx0QejVYlsPMCh3onuzxXnJ4gT
> -----END RSA PRIVATE KEY-----"
```

3. Finally run the command to generate public keys:

We will save our output with the SAME NAME as the private key but with a different extension (this is super important):
We will save our public key as: `keys/e517ff21f2eb3767c35685ad380e39cd.pub`.

```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAv8EnGM6MkYN45sreu3vs
AVkzWGDbhOoBBHUC9TEdGv5Kh3BYtwH8QFwmFENmjV3eHRAFoXG2NXN6aZBfOtxQ
..........
PH7dJM4oqOrYQbuzeu2mTy58PLeWVJWxXROu/SY+R23eHRAFoXG2NXN6aZBfOtxQ
IBN2gwt7fUxwBjnplaPijCEyDyhQ7BV1pFSVkFZbk9/xXCPoebTia92dbs44GMqR
JwIDAQAB
-----END PUBLIC KEY-----
```

#### 3. Configure the API
##### Development:
1. If running on a development environment we need to first initialize the database, this will be a simple example.sqlite file:
```sh
$ python
>>> from index import db
>>> db.create_all()
>>> db.session.commit()
```
##### Production:
1. First create a file, python will look for this file when it first starts the server. If it exists, it assumes the set up is in production:

<small>I'll make this nicer in the future</small>
```sh
$ touch enable_prod
```
2. Make sure you set up the database url and configuration inside of the Python `index.py` file:
```python
DB_URL = 'mysql+pymysql://USER_NAME:USER_PASSWORD@SERVER_NAME/DATABASE_NAME'
```
example:
```python
DB_URL = 'mysql+pymysql://db_user:4dt@wD*F!gLc8^a=k8XGH@localhost/database_name'
```
3. Now create the database tables:
```sh
$ python
>>> from index import db
>>> db.create_all()
>>> db.session.commit()
```
4. Make sure you check out the configuration options in the `app.py` file and
make the changes you need for your API!
```python
app.config['APP_VERSION'] = '0.0.1'
app.config['APP_NAME'] = 'Python JWT Auth'
app.config['APP_LOGO_URL'] = 'https://placehold.it/350x150'
app.config['APP_URL'] = 'https://localhost/'
app.config['JWT_HEADER_NAME'] = 'python-auth'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ALGORITHM'] = 'RS256'
app.config['JWT_KEYS'] = keys
app.config['JWT_AUDIENCE'] = 'python-jwt-auth'
app.config['JWT_ISSUER'] = 'localhost'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
```

5. Email configuration needs to be send so that verification and reset emails can be received by users! Create a Mailgun account and verify your domain then change the settings inside of the `app.py`.


6. Now you can start the API up (for deploying to a server look at the [DigitalOcean Guide](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04)):
```sh
$ python app.py
```
<br/>

## API documentation

List of endpoints, and examples of request and response data (JSON):

### Endpoint: **/**
### Request (GET):
```json
```
### Response:
```json
{
  "message": "Python JWT Auth API", 
  "version": "0.0.1"
}
```

### Endpoint: **/settings**
### Request (GET):
```json
```
### Response:
```json
{
  "alg": "RS256", 
  "disable_signup": false, 
  "external_auth": {
    "facebook": false, 
    "google": false, 
    "instagram": false, 
    "twitter": false
  }, 
  "key_url": "/settings/keys", 
  "version": "0.0.1"
}
```

### Endpoint: **/settings/keys**
### Request (GET):
```json
```
### Response (truncated): 
```json
{
  "189609ee7fa5955bd8679e00539645c3": "-----BEGIN PUBLIC KEY-----\n.......-----END PUBLIC KEY-----", 
  "5d4df58e583d0400f7c89987702a6c9c": "-----BEGIN PUBLIC KEY-----\n.......-----END PUBLIC KEY-----", 
  "8bb8b642396aab349660bda98d129b1d": "-----BEGIN PUBLIC KEY-----\n.......-----END PUBLIC KEY-----", 
  "a0777a60e60e24007a603c0a3d0562d5": "-----BEGIN PUBLIC KEY-----\n.......-----END PUBLIC KEY-----"
}
```

### Endpoint: **/signup**
### Request (POST):
```json
{
	"name": "Omar Quazi",
	"email": "omar@quazi.co",
	"password": "Myverystrongpassword123@"
}
```
### Response:
```json
{
  "code": "auth/user-registered",
  "message": "Successfully created your account! Login now.",
  "status": "success"
}
```

### Endpoint: **/login**
Keep in mind the fresh_token parameter is OPTIONAL. Include it only when a user needs to make a
secure change like changing the password as fresh_token will be required by the server to make that
change. Any requests made with a non-fresh token will be rejected automatically, this ensures that an
attacker cannot just simply steal the refresh token and start making huge changes to the users account.
### Request (POST):
```json
{
    "email": "omar@quazi.co",
    "password": "Myverystrongpassword123@",
    "fresh_token": false
}
```
### Response (refresh_token and access_token are VERY important):
```json
{
  "created_at": 1568578185,
  "email": "omar@quazi.co",
  "email_verified": false,
  "name": "Omar Quazi",
  "status": "success",
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE1Njg1NzgyMDQsImF1ZCI6Inhtb2JpbGUiLCJpc3MiOiJodHRwczovL2Rldi1hcGkueG1vYmlsZS50ZWwvIiwibmJmIjoxNTY4NTc4MjA0LCJqdGkiOiI2MmRkYmRjMC1iYWRlLTQ0MjMtOTk2My1kZTY2Zjk3NTViOTkiLCJraWQiOiJhMDc3N2E2MGU2MGUyNDAwN2E2MDNjMGEzZDA1NjJkNSIsInN1YiI6IjIyMmM4ZDUxLTlhMjMtNDFjMC05MzMwLWRjNzczMDFjNzczYyIsImV4cCI6MTU2ODU3OTEwNCwiZGF0YSI6eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIn19.j6xrOgZsSP_fJtO6TAsDbMUOmXMxkOh8603li7D4zkXYfPl8XqB2xOC3k1XH3QzlADDhrby1kTat4eI0HBeainAMw4l59w16iN3rm6v9UnFxdt3D5j7awctCu8Gmfw-iBVOKXXRd2oqBu45llpB_KELhSTg-iHXU0UYdOFmQk-uYGLTQW9oE5hg_iShGipTSbsENxPMxHps8OccV5KmlUEE3Fj0rQ7ZLiKBl5fiSqIMmZJa8gGNrqBTNsZSbaFje0h6tZ8hMoomtY8pMzTUoK4GZwsZDTxU4E5CQsWG0QCU0KQU8-AFUGtXYTznVl8wDEMsNkM6iuvZP4wIMoWGW9w",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE1Njg1NzgyMDQsImF1ZCI6Inhtb2JpbGUiLCJpc3MiOiJodHRwczovL2Rldi1hcGkueG1vYmlsZS50ZWwvIiwibmJmIjoxNTY4NTc4MjA0LCJqdGkiOiIwM2I1MGU2Ny0yMzExLTQ5ZTctYjEwZC04OGU5ZjI4ZDdlYjQiLCJraWQiOiJhMDc3N2E2MGU2MGUyNDAwN2E2MDNjMGEzZDA1NjJkNSIsInN1YiI6IjIyMmM4ZDUxLTlhMjMtNDFjMC05MzMwLWRjNzczMDFjNzczYyIsImV4cCI6MTYwMDExNDIwNCwiZGF0YSI6eyJ0eXBlIjoicmVmcmVzaF90b2tlbiJ9fQ.D0ZfiFHT0NrzMs0VW2lCSxyogrJSNSr97aBzibi75dmLuLSPD1fvCU8uWM3739X9ni13g-loZjtK-UdMJ8W3BtGhtZa_fKjZmv6N284OCYBM-2Xeh2W0lhuRT4N1AQg296mKyW7WfqGKqninzPGv2ONSOXEYl9ZkDxfoTJAUBbtbeRccRMikEkn2anl6beSjYoEtaqdO16IOupdtRa1yqrlVOAzr5XxcOpj58J0KirvLwIx1zfhW_yr6jabxTJYVfk7ikUG8-GtuGBMlHRe1l6L3sgYkWtoCm7_7Ek6AkcOA0WwHye9yppLYnO3cB_-Ub5-pKYpRIApGI05-ohMP0g"
  },
  "uid": "222c8d51-9a23-41c0-9330-dc77301c773c",
  "updated_at": 1568578064
}
```

### Endpoint: **/refresh**
This endpoint is used to get a new access_token.
### Request (GET):
```json
{
	"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE1Njg1NzgyMDQsImF1ZCI6Inhtb2JpbGUiLCJpc3MiOiJodHRwczovL2Rldi1hcGkueG1vYmlsZS50ZWwvIiwibmJmIjoxNTY4NTc4MjA0LCJqdGkiOiIwM2I1MGU2Ny0yMzExLTQ5ZTctYjEwZC04OGU5ZjI4ZDdlYjQiLCJraWQiOiJhMDc3N2E2MGU2MGUyNDAwN2E2MDNjMGEzZDA1NjJkNSIsInN1YiI6IjIyMmM4ZDUxLTlhMjMtNDFjMC05MzMwLWRjNzczMDFjNzczYyIsImV4cCI6MTYwMDExNDIwNCwiZGF0YSI6eyJ0eXBlIjoicmVmcmVzaF90b2tlbiJ9fQ.D0ZfiFHT0NrzMs0VW2lCSxyogrJSNSr97aBzibi75dmLuLSPD1fvCU8uWM3739X9ni13g-loZjtK-UdMJ8W3BtGhtZa_fKjZmv6N284OCYBM-2Xeh2W0lhuRT4N1AQg296mKyW7WfqGKqninzPGv2ONSOXEYl9ZkDxfoTJAUBbtbeRccRMikEkn2anl6beSjYoEtaqdO16IOupdtRa1yqrlVOAzr5XxcOpj58J0KirvLwIx1zfhW_yr6jabxTJYVfk7ikUG8-GtuGBMlHRe1l6L3sgYkWtoCm7_7Ek6AkcOA0WwHye9yppLYnO3cB_-Ub5-pKYpRIApGI05-ohMP0g"
}
```
### Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE1Njg1NzgzNDAsImF1ZCI6Inhtb2JpbGUiLCJpc3MiOiJodHRwczovL2Rldi1hcGkueG1vYmlsZS50ZWwvIiwibmJmIjoxNTY4NTc4MzQwLCJqdGkiOiI5MDJkYzczZS05ODk2LTRkMDgtYTY4NC1iYjliOWE2NmEzOGEiLCJraWQiOiI4YmI4YjY0MjM5NmFhYjM0OTY2MGJkYTk4ZDEyOWIxZCIsInN1YiI6IjIyMmM4ZDUxLTlhMjMtNDFjMC05MzMwLWRjNzczMDFjNzczYyIsImV4cCI6MTU2ODU3OTI0MCwiZGF0YSI6eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIn19.lyUU4fy0HqYK86Xua12BU3Eka9c5wTztMxEcZRqFSaFPxx6cVI_3gybYyrUm2iUqpLqkXfN09d64c4K4OxCVC_klayqU7TndyNfs9pxmxB6mkwaX6MkOTV4q9woAIxupFPcv_FvXvEBLW1LYFbuwyvucghVaxZTapsWPMXoCHaKDrHJkd5a-QB6oGxJaMxU9eya8S_abHOAmFAu4uh6FKzO_rH4_J1ZvGRjlo88c3-vFReS2g40Bv7I2DTTkR1GgY88wYKTEkeVs4OHuzmB0N4XHVEWGfxxheJpKvMz1dpocbw05DatfXHBxm86YU2sWox0wp7Zt_TvAa_LNPxTmEw",
  "exp": 1568579240,
  "status": "success"
}
```

### Endpoint: **/user**
### Request (GET):
```
Header Name: python-auth
Header Value: Bearer  eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE1Njg1NzgzNDAsImF1ZCI6Inhtb2JpbGUiLCJpc3MiOiJodHRwczovL2Rldi1hcGkueG1vYmlsZS50ZWwvIiwibmJmIjoxNTY4NTc4MzQwLCJqdGkiOiI5MDJkYzczZS05ODk2LTRkMDgtYTY4NC1iYjliOWE2NmEzOGEiLCJraWQiOiI4YmI4YjY0MjM5NmFhYjM0OTY2MGJkYTk4ZDEyOWIxZCIsInN1YiI6IjIyMmM4ZDUxLTlhMjMtNDFjMC05MzMwLWRjNzczMDFjNzczYyIsImV4cCI6MTU2ODU3OTI0MCwiZGF0YSI6eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIn19.lyUU4fy0HqYK86Xua12BU3Eka9c5wTztMxEcZRqFSaFPxx6cVI_3gybYyrUm2iUqpLqkXfN09d64c4K4OxCVC_klayqU7TndyNfs9pxmxB6mkwaX6MkOTV4q9woAIxupFPcv_FvXvEBLW1LYFbuwyvucghVaxZTapsWPMXoCHaKDrHJkd5a-QB6oGxJaMxU9eya8S_abHOAmFAu4uh6FKzO_rH4_J1ZvGRjlo88c3-vFReS2g40Bv7I2DTTkR1GgY88wYKTEkeVs4OHuzmB0N4XHVEWGfxxheJpKvMz1dpocbw05DatfXHBxm86YU2sWox0wp7Zt_TvAa_LNPxTmEw
```

```json

```
### Response:
```json
{
  "created_at": "1568578185",
  "email": "omar@quazi.co",
  "email_verified": false,
  "name": "Omar Quazi",
  "uid": "222c8d51-9a23-41c0-9330-dc77301c773c",
  "updated_at": "1568578064"
}
```

### Endpoint: **/user**
### Request (PATCH):
```
Header Name: python-auth
Header Value: Bearer  eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE1Njg1NzgzNDAsImF1ZCI6Inhtb2JpbGUiLCJpc3MiOiJodHRwczovL2Rldi1hcGkueG1vYmlsZS50ZWwvIiwibmJmIjoxNTY4NTc4MzQwLCJqdGkiOiI5MDJkYzczZS05ODk2LTRkMDgtYTY4NC1iYjliOWE2NmEzOGEiLCJraWQiOiI4YmI4YjY0MjM5NmFhYjM0OTY2MGJkYTk4ZDEyOWIxZCIsInN1YiI6IjIyMmM4ZDUxLTlhMjMtNDFjMC05MzMwLWRjNzczMDFjNzczYyIsImV4cCI6MTU2ODU3OTI0MCwiZGF0YSI6eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIn19.lyUU4fy0HqYK86Xua12BU3Eka9c5wTztMxEcZRqFSaFPxx6cVI_3gybYyrUm2iUqpLqkXfN09d64c4K4OxCVC_klayqU7TndyNfs9pxmxB6mkwaX6MkOTV4q9woAIxupFPcv_FvXvEBLW1LYFbuwyvucghVaxZTapsWPMXoCHaKDrHJkd5a-QB6oGxJaMxU9eya8S_abHOAmFAu4uh6FKzO_rH4_J1ZvGRjlo88c3-vFReS2g40Bv7I2DTTkR1GgY88wYKTEkeVs4OHuzmB0N4XHVEWGfxxheJpKvMz1dpocbw05DatfXHBxm86YU2sWox0wp7Zt_TvAa_LNPxTmEw
```

```json
{
  "name": "Omar"
}
```
### Response:
```json
{
  "code": "auth/changed-name",
  "message": "Successfully changed your name!",
  "status": "success"
}
```

### Endpoint: **/user**
### Request (PATCH):
```
Header Name: python-auth
Header Value: Bearer  eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE1Njg1NzgzNDAsImF1ZCI6Inhtb2JpbGUiLCJpc3MiOiJodHRwczovL2Rldi1hcGkueG1vYmlsZS50ZWwvIiwibmJmIjoxNTY4NTc4MzQwLCJqdGkiOiI5MDJkYzczZS05ODk2LTRkMDgtYTY4NC1iYjliOWE2NmEzOGEiLCJraWQiOiI4YmI4YjY0MjM5NmFhYjM0OTY2MGJkYTk4ZDEyOWIxZCIsInN1YiI6IjIyMmM4ZDUxLTlhMjMtNDFjMC05MzMwLWRjNzczMDFjNzczYyIsImV4cCI6MTU2ODU3OTI0MCwiZGF0YSI6eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIn19.lyUU4fy0HqYK86Xua12BU3Eka9c5wTztMxEcZRqFSaFPxx6cVI_3gybYyrUm2iUqpLqkXfN09d64c4K4OxCVC_klayqU7TndyNfs9pxmxB6mkwaX6MkOTV4q9woAIxupFPcv_FvXvEBLW1LYFbuwyvucghVaxZTapsWPMXoCHaKDrHJkd5a-QB6oGxJaMxU9eya8S_abHOAmFAu4uh6FKzO_rH4_J1ZvGRjlo88c3-vFReS2g40Bv7I2DTTkR1GgY88wYKTEkeVs4OHuzmB0N4XHVEWGfxxheJpKvMz1dpocbw05DatfXHBxm86YU2sWox0wp7Zt_TvAa_LNPxTmEw
```

```json
{
  "email": "example2@quazi.co"
}
```
### Response:
```json
{
  "code": "auth/changed-email",
  "message": "Successfully changed your email address, please check your inbox for a verification email! You may now login again.",
  "status": "success"
}
```

_Note: User will be required to login again as the user uid has changed and all previous access and refresh tokens have been invalidated_

### Endpoint: **/user**
### Request (PATCH):
```
Header Name: python-auth
Header Value: Bearer  eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE1Njg1NzkyMDgsImF1ZCI6Inhtb2JpbGUiLCJpc3MiOiJodHRwczovL2Rldi1hcGkueG1vYmlsZS50ZWwvIiwibmJmIjoxNTY4NTc5MjA4LCJqdGkiOiI3MGZmMGM5ZC01NjBkLTQ5MGMtYTlmMy0yYTcxZmI2NmE1MzMiLCJraWQiOiI1ZDRkZjU4ZTU4M2QwNDAwZjdjODk5ODc3MDJhNmM5YyIsInN1YiI6ImE2YzY1NmY3LTgzZTUtNDk4NS04ZTExLTIyNDUzMDYxODI3NSIsImV4cCI6MTU2ODU4MDEwOCwiZGF0YSI6eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZnJlc2giOnRydWV9fQ.idJAFdPNVnBf0J7Ytlyzi24-RmtGuxb9WuE4e-fGJwWRK5tAZT2FL0Krne8eDX-mz3M1SQckm635lxE8Cnu7g_y0VSpzA9pv39Gz1JXw3HZlNImMKjnJ4kcTKa-RU6xo1YVKwJ67TnPUS1Erl2PW7kF3gyty7uZ1NXVWINYI95Y70dLHpQ0ANLxalnI8pwjHftDIWKEj_ot3VpI38H6YUzIgi0IxJDgn71ggmVRaLCR0_jFv-DOvZyTbFbjBEsYlsLTkBPsVLN7gYJZOdei7kvh-ofjC7P6vayb6SokfvOwK4NnQ5wRG_FmxdYpmdhzITANfuCC2Z7EhQkebrwblcw
```

```json
{
  "password": "ExtremelyStrongPassword123@@"
}
```
### Response:
```json
{
  "code": "auth/changed-password",
  "message": "Successfully changed your password!",
  "status": "success"
}
```

<br/>

## Editor configuration
I use Microsoft VS Code.

It does Python syntax highlighting well and I don't have any extra requirements from the IDE. If anything, there are a whole host of extensions and plugins available for use.