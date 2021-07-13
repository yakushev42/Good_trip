from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
import connectDB as cn

class User(UserMixin):
    # ...
    def __init__(self,userid=None,nickname=None,pass_hash=None,role=None):
        self.userid = userid
        self.pass_hash = pass_hash
        self.role = role
        self.nickname = nickname
    def set_password(self, password):
        self.pass_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pass_hash, password)
    def get_id(self):
        return self.userid
    def check_role(self):
        print('why')
        print(self.role)
        if self.role=='user':
            return 0
        else: 
            return 1
        
@login.user_loader
def load_user(userid):
    conn = cn.get_connection()
    cursor = conn.cursor()
    sql = "SELECT * FROM users WHERE userid = %s;"
    cursor.execute(sql, (int(userid),))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result is None:
        user = None
    else:
        user = User(result['userid'], result['nickname'], result['pass_hash'], result['role'])
    return user