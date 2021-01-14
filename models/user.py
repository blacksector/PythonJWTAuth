from .shared import db, ma, datetime, BaseModel
from libs import avatar



class User(BaseModel):
    __tablename__ = "users"
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(80), unique=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(255), nullable=True)
    last_failed_attempt = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    total_login_attempts = db.Column(db.Integer, default=0)
    timezone = db.Column(db.String(50), nullable=True)
    profile_picture = db.Column(db.String(300), nullable=True)
    phone_number = db.Column(db.String(15), nullable=True)
    stripe_customer_id = db.Column(db.String(25), nullable=True)



class PublicUserSchema(ma.Schema):
    class Meta:
        fields = ("uid", "first_name", "last_name", "profile_picture")
    
    profile_picture = ma.Method("check_profile_picture", dump_only=True)
    
    def check_profile_picture(self, user):
        if user.profile_picture is None:
            return avatar(user.email, 100)
        else:
            return user.profile_picture


class UserSchema(ma.Schema):
    class Meta:
        fields = (
            "uid", "first_name", "last_name", "profile_picture",
            "email", "email_confirmed", "timezone", "stripe_customer_id", "updated_at",
            "created_at"
        )
    profile_picture = ma.Method("check_profile_picture", dump_only=True)
    
    def check_profile_picture(self, user):
        if user.profile_picture is None:
            return avatar(user.email, 100)
        else:
            return user.profile_picture
