from flask import Flask,session,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost:3306/ajax"
app.config["DEBUG"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = 'hahanijinglaile'
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True


db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True)
    uname = db.Column(db.String(20),unique=True)
    upwd = db.Column(db.String(300))
    nickname = db.Column(db.String(50))

    comments = db.relationship(
        "Comment",
        backref='user',
        lazy='dynamic'
    )

    def __init__(self,uname,upwd,nickname):
        self.uname = uname
        self.upwd = upwd
        self.nickname = nickname

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.Text)
    up_time = db.Column(db.TIMESTAMP,nullable=False)
    uid = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self,text,uid):
        self.text = text
        # self.up_time = up_time
        self.uid = uid

    def to_dict(self):
        dic = {
            'uname':self.user,
            'text':self.text,
            'up_time':str(self.up_time),
        }
        return dic

def comm_all():
    comm = Comment.query.all()
    lst = []
    for c in comm:
        lst.append(c.to_dict())
    return lst

@app.route('/')
def index():
    if "uname" in session:
        uname = session.get('uname')
        user = User.query.filter_by(uname=uname).first()
    return render_template('index.html',params=locals())

@app.route('/register',methods=["GET","POST"])
def register_view():
    if request.method == "GET":
        return render_template('register.html')
    else:
        uname = request.form['uname']
        upwd = request.form['upwd']
        upwd = generate_password_hash(upwd)
        nickname = request.form['nickname']
        user = User(uname,upwd,nickname)
        # print(user.uname)
        db.session.add(user)
        session['uname'] = uname
        return redirect('/')


@app.route('/check')
def check_view():
    uname = request.args['uname']
    user = User.query.filter_by(uname=uname).first()
    if not user:
        return '0'
    else:
        return '1'

@app.route('/login',methods=["GET","POST"])
def login_view():
    if request.method == "GET":
        url = request.headers.get('Referer','/')
        session['url'] = url

        if 'uname' in session:
            # return redirect(url)
            user = User.query.filter_by(uname=session['uname']).first()
            return render_template('My_page.html',nickname=user.nickname)
        else:
            if 'uname' in request.cookies:
                uname = request.cookies['uname']
                user = User.query.filter_by(uname=uname).first()
                if user:
                    session['uname'] = uname
                    return redirect(url)
            return render_template('login.html')
    else:
        uname = request.form['uname']
        upwd = request.form['upwd']
        user = User.query.filter_by(uname=uname).first()
        if user and check_password_hash(user.upwd,upwd):
            session['uname'] = uname
            # url = session.get('url','/')
            url = '/My_page'
            resp = redirect(url)

            if 'isSaved' in request.form:
                resp.set_cookie('uname',uname,60*60*24*365*10)

            return resp
        else:
            return render_template('login.html',errMsg='用户名或密码不正确')

@app.route('/My_page',methods=["GET","POST"])
def My_page_view():
    if request.method == "GET":
        if 'uname' in session:
            user = User.query.filter_by(uname=session['uname']).first()
            comm = Comment.query.all()
            return render_template('My_page.html',nickname=user.nickname)
        else:
            return redirect('/')
    else:
        uname = session['uname']
        print(uname)
        text = request.form['uinfo']
        print(text)
        user = User.query.filter_by(uname=uname).first()
        uid = user.id
        comment = Comment(text,uid)
        db.session.add(comment)
        # print('提交数据库')
        # test = db.session.query(Comment).filter(Comment.up_time<datetime.datetime.now(),Comment.uid==uid).first()
        # print(type(test.text))
        # content = test.text + uname + '发表于:'+ str(up_time)
        return render_template('My_page.html',nickname=user.nickname)

@app.route('/logout')
def logout_view():
    resp = redirect('/')
    if 'uname' in session:
        del session['uname']
    if 'uname' in request.cookies:
        resp.delete_cookie('uname')
    return resp

@app.route('/get_comm')
def get_comm_view():
    lst = comm_all()
    return lst


if __name__ == "__main__":
    manager.run()














