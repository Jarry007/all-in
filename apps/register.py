from flask import Flask
from flask import Flask,render_template,url_for,flash,request
from flask_script import Manager
from flask_mail import Mail,Message
import datetime,time,requests,random
from threading import Thread

app = Flask(__name__)

app.config['SECRET_KEY'] = 'jarry'
app.config.update(
    MAIL_DEBUG = True,
    MAIL_SERVER = 'smtp.qq.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL=True,
    MAIL_USE_TLS = False,
    MAIL_USERNAME ='1623332700@qq.com',
    MAIL_PASSWORD = 'uyqelwhivvfqejij',
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:940615834@193.112.54.232:3306/jarry',
    SQLALCHEMY_TRACK_MODIFICATIONS = True
)
mail = Mail(app)
manager = Manager(app)
verificationCode = random.randint(1000, 9999)

def send_async_email(app,send):
    with app.app_context():
        mail.send(send)

@app.route('/')
def index():
    nowTime = datetime.datetime.now()
    time.sleep(1)
    print(nowTime)
    return render_template('index.html',nowTime=nowTime)

@app.route('/send',methods=['POST','GET'])
def send_msg():
    msg = verificationCode
    ip = request.remote_addr

    send = Message(ip,sender='1623332700@qq.com',recipients=['940615834@qq.com'])
    send.body = "ip地址是{},验证码是{}".format(ip,msg)
    thread = Thread(target=send_async_email, args=[app, send])
    thread.start()
    return 'success!'


if __name__ == "__main__":
    app.run()

