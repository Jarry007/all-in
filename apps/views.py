# -*- coding: utf-8 -*-
from datetime import datetime
from imp import reload

import requests
from flask_uploads import configure_uploads
from markdown import markdown

from apps import app,db,pagedown,loginmanager,creat_folder,STATIC_DIR
from flask import render_template, url_for, flash, request, redirect, session, jsonify, json, Response, make_response
from flask_script import Manager
from flask_mail import Mail,Message
import time,random,os
from threading import Thread

from apps.WXBizDataCrypt import WXBizDataCrypt
from .model import Role, UserProfile, Article, IpList, Comment, Reply, Follow, Likes, LikeComment
import hashlib
from .forms import NameForm, Login, Register, Profile, photosSet,PostForm,CommentForm,ReplyForm,Mark
from flask_login import login_user,login_required,logout_user,current_user
import uuid
from PIL import Image, ImageDraw, ImageFont
from qqwry import QQwry




mail = Mail(app)
manager = Manager(app)
verificationCode = random.randint(1000, 9999)

configure_uploads(app, photosSet)
# 修剪头像
def compression_img(data):
    size= (120,120)
    im = Image.open(data)
    im.thumbnail(size)
    return im
# 生成初始头像
def default_avatar(email):
    size = 180
    default = 'monsterid'
    r = 'g'
    m = hashlib.md5()
    m.update(email.encode('utf-8'))
    hash = m.hexdigest()
    a_url = 'https://www.gravatar.com/avatar/{hash}?s={size}&d={default}&r={r}'.format(hash=hash,size=size,default=default,r=r)
    return a_url

def friends_circle():
    follow = Role.query.filter_by(uuid=current_user.uuid).first()
    follower = follow.followers
    followed = follow.followed
    list1 = []
    list2 = []
    for i in follower:
        list1.append(i.follower.uuid)
    for j in followed:
        list2.append(j.followed.uuid)

    friend_list = set(list1).intersection(set(list2))

    return friend_list





@loginmanager.user_loader
def load_user(user_id):
    return Role.query.get(int(user_id))

def md5(data):
    md = hashlib.md5()
    md.update(data.encode('utf-8'))
    data = md.hexdigest()
    return data

def send_async_email(app,send):
    with app.app_context():
        mail.send(send)

@app.route('/',methods=['POST','GET'])
def index():

    page = request.args.get('page', 1, type=int)
    article = Article.query.order_by(Article.id.desc()).paginate(page, per_page=6, error_out=False)
    news = Article.query.order_by(Article.id.desc()).limit(5).all()
    hot = Article.query.order_by(Article.view.desc()).limit(5).all()
    posts = article.items
    ip = str(request.remote_addr)
    agen = str(request.user_agent)
    list = IpList()
    list.ip = ip
    list.agent = agen
    db.session.add(list)
    db.session.commit()
    #like_num = current_user.new_like()

    return render_template('index.html', posts=posts, news=news, article=article, hot=hot,)

@app.route('/youcanyoudo',methods=['POST','GET'])
@login_required
def dele():
    posts = Article.query.all()
    return render_template('delete.html',posts=posts)

@app.route('/youcanyoudo/<int:id>',methods=['POST','GET'])
@login_required
def delete(id):
    role = Article.query.filter_by(id=id).first()
    db.session.delete(role)
    db.session.commit()
    return dele()


@app.route('/send', methods=['POST', 'GET'])
def send_msg():
    msg = verificationCode
    ip = request.remote_addr
    send = Message(ip, sender='1623332700@qq.com', recipients=['940615834@qq.com'])
    send.body = "ip地址是{},验证码是{}".format(ip, msg)
    thread = Thread(target=send_async_email, args=[app, send])
    thread.start()
    return '发送成功!'
@app.route('/issue',methods=['POST','GET'])
def issue():
    title = request.form.get('issuet')
    say = request.form.get('issue')
    send = Message('反馈', sender='1623332700@qq.com',recipients=['940615834@qq.com'])
    send.body = "标题是{},内容是{}".format(title,say)
    thread = Thread(target=send_async_email, args=[app, send])
    thread.start()
    return '发送成功!'


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    form = Login()
    if form.validate_on_submit():
        user = Role.query.filter_by(username=form.username.data).first()
        if not user:

            return regist()
        else:
            pwd =md5(form.password.data)
            if not user.check(str(pwd)):
                flash('密码错误')
                return render_template('login.html', form=form)
            else:
                login_user(user, True)
                flash('登陆成功')
            return redirect(url_for('index'))
    return render_template('login.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('注销成功')
    return redirect(url_for('index'))

@app.route('/users',methods=['GET','POST'])
def users():

    return render_template('.html')


@app.route('/register', methods=['GET', 'POST'])
def regist():
    form = Register()
    if form.validate_on_submit():
        user = Role.query.filter_by(username=form.username.data).first()
        if user:
            flash('用户名已经存在',category='err')
            return render_template('register.html', form=form)
        else:
            users = Role()
            uu_id =str(uuid.uuid4()).replace('-', '')
            users.uuid = uu_id
            users.username = form.username.data
            users.pwd = md5(form.password.data)
            users.email = form.email.data
            users.default_avatar=default_avatar(md5(form.email.data))

            db.session.add(users)
            db.session.commit()
            login_user(users, True)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/list',methods=['POST','GET'])
@login_required
def listSql():

    page = request.args.get('page', 1, type=int)
    listt = Role.query.all()
    pagination = IpList.query.order_by(IpList.time.desc()).paginate(page, per_page=15, error_out=False)
    ip = pagination.items
    for i in ip:
        ip_data = i.ip
        q = QQwry()
        filename = os.path.join(STATIC_DIR, 'qqwry.dat')
        q.load_file(filename, loadindex=False)
        adders = q.lookup(ip_data)
        query_ip = IpList.query.order_by(IpList.time.desc()).filter_by(ip=ip_data).first()
        query_ip.adders = str(adders)
        db.session.commit()

    return render_template('list.html',  ip=ip, pagination=pagination, listt=listt)


#查询role表，如果存在profile表就修改列，如果不存在就添加
@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    form = Profile()
    if form.validate_on_submit():
        user = UserProfile()
        fn = time.strftime('%Y%m%d%H%M%S') + '_%d' % random.randint(0, 100) + '.png'
        avata =form.avatar.data
        new = compression_img(avata)
        creat_folder(os.path.join(app.config['UPLOADS_FOLDER'], md5(current_user.uuid)))
        pic_dir = os.path.join(app.config['UPLOADS_FOLDER'], md5(current_user.uuid), fn)
        print(pic_dir)
        new.save(pic_dir)

        header = Role.query.filter_by(uuid=current_user.uuid).first()
        folder = 'uploads/'+md5(current_user.uuid)
        header.avatar = folder+'/'+fn

        if header.profile:
            proid = UserProfile.query.filter_by(user_id=current_user.uuid).first()
            proid.nickname = form.nickname.data
            proid.gender = form.gender.data
            proid.intro = form.intro.data
            proid.birthday = request.form.get('birthday')
            db.session.commit()
        else:
            user.user_id = current_user.uuid
            user.nickname = form.nickname.data
            user.birthday = request.form.get('birthday')
            user.gender = form.gender.data
            user.intro = form.intro.data
            db.session.add(user)
            db.session.commit()
        return redirect(url_for('profile'))
    return render_template('profile.html', form=form)


@app.route('/e', methods=['POST', 'GET'])
@login_required
def ckeditor():
    form = PostForm()
    if form.validate_on_submit():
        post = Article()
        pic_ = form.pic.data
        if pic_ is not None:
            fn = time.strftime('%Y%m%d%H%M%S') + '_%d' % random.randint(0, 100) + '.png'
            creat_folder(os.path.join(app.config['UPLOADS_FOLDER'], md5(current_user.uuid)))
            pic_dir = os.path.join(app.config['UPLOADS_FOLDER'], md5(current_user.uuid), fn)
            print (pic_dir)
            pic = Image.open(pic_)
            pic.save(pic_dir)
            folder = 'uploads/'+md5(current_user.uuid)
            post.img = folder + '/' + fn

        post.uuid = current_user.uuid
        post.tittle = form.title.data
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('ck.html', form=form)

@app.route('/posts/<int:id>',methods=['POST','GET'])
def posts(id):
    form = CommentForm()
    replies = ReplyForm()
    post = Article.query.filter_by(id=id).first()
    user = post.role
    comments = post.comments
    post.view += 1
    db.session.commit()
    return render_template('posts.html', posts=post, user=user, form=form, comments=comments, replies=replies)
@app.route('/t')
def show():
    return render_template('test.html')

#非本人查看个人信息，
@app.route('/profile/<username>',methods=['POST','GET'])
def profileid (username):
    user = Role.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    art = Article.query.filter_by(uuid=user.uuid).paginate(page,per_page=6,error_out=False)
    article = art.items
    profiles = UserProfile.query.filter_by(user_id=user.uuid).first()

    return render_template('profiles.html', user=user, profile=profiles, article=article, art=art)

@app.route('/ckdemo',methods=['POST','GET'])
def ckdemo():
    form=PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        return showbody(title, body)
    return render_template('ckdemo.html', form=form)

@app.route('/showbody',methods=['POST','GET'])
def showbody(title, body):
    return render_template('show.html', title=title, body=body)

@app.route('/follow/<username>', methods=['POST','GET'])
@login_required
def follow(username):
    user = Role.query.filter_by(username=username).first()
    if user is None:
        flash('不存在用户')
        return redirect(url_for('index'))
    if current_user.is_following(user):
        flash('你已经关注该用户了')
        return redirect(url_for('profileid', username=username))
    current_user.follow(user)

    return redirect(url_for('profileid', username=username))

@app.route('/unfollow/<username>', methods=['POST','GET'])
@login_required
def unfollow(username):
    user = Role.query.filter_by(username=username).first()
    if user is None:
        flash('不存在用户')
        return redirect(url_for('index'))
    current_user.unfollow(user)
    flash('取关成功')
    return redirect(url_for('profileid', username=username))


@app.route('/followers/<username>', methods=['POST', 'GET'])
def followers(username):
    user = Role.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=10, error_out=False
    )
    follows = pagination.items
    return render_template('followed.html', user=user, pagination=pagination,
                           follows=follows)


@app.route('/followed_by/<username>')
def followed_by(username):
    user = Role.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, per_page=10, error_out=False)
    follows = pagination.items
    return render_template('followers.html', user=user, pagination=pagination, follows=follows)


@app.route('/posts/<int:id>/comment', methods=['POST', 'GET'])
@login_required
def comment(id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment()
        comment.article_id = id
        comment.user_id = current_user.uuid
        comment.body = form.body.data
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('posts', id=id))


@app.route('/posts/<int:id>/<int:comment>')
def delete_comment(id, comment):
    comments = Comment.query.filter_by(id=comment).first()
    db.session.delete(comments)
    db.session.commit()
    return redirect(url_for('posts', id=id))


@app.route('/posts/<int:id>/reply/<int:comment>', methods=['POST', 'GET'])
def reply_comment(id, comment):
    form = ReplyForm()
    if form.validate_on_submit():
        replies = Reply()
        replies.comment_id = comment
        replies.replies_id = current_user.uuid
        replies.body = form.body.data
        db.session.add(replies)
        db.session.commit()
    return redirect(url_for('posts', id=id))


@app.route('/friends', methods=['POST', 'GET'])
@login_required
def friends():
    page = request.args.get('page', 1, type=int)
    quer_y = current_user.friends_post
    article = quer_y.order_by(Article.addtime.desc()).paginate(
        page, per_page=6, error_out=False
    )
    posts = article.items

    return render_template('friends.html', posts=posts, article=article)


@app.route('/like/<int:id>', methods=['POST', 'GET'])
@login_required
def like(id):
    if current_user.is_liked(id):
        flash('您已经赞了这篇文章')
        return redirect(url_for('posts', id=id))
    current_user.like(id)
    return redirect(url_for('posts', id=id))


@app.route('/unlike/<int:id>', methods=['POST', 'GET'])
@login_required
def unlike(id):
    current_user.unlike(id)
    return redirect(url_for('posts', id=id))


@app.route('/vue', methods=['GET', 'POST'])
def vue_say():
    listt = Role.query.all()
    ip = IpList.query.order_by(IpList.time.desc()).all()
    t = {}
    for i in ip:
        t['ip'] = i.ip
        t['adress'] = i.adders
        print(t)
    return jsonify(t)


@app.route('/vue/list', methods=['GET', 'POST'])
def vue_list():
    # listt = Role.query.all()
    ip = IpList.query.order_by(IpList.time.desc()).all()
    t = []
    for i in ip:
        t.append(i.to_json())
    return jsonify(t)


@app.route('/mp/posts', methods=['POST', 'GET'])
def get_posts():
    info = request.values.get('info')
    user_info = json.loads(info)
    page = user_info['page']
    posts_ = Article.query.paginate(page, per_page=6, error_out=False)
    return jsonify({
        'posts': [post.to_json() for post in posts_.items]
    })
@app.route('/mp/new', methods=['POST', 'GET'])
def get_news():

    new_ = Article.query.order_by(Article.view.desc()).limit(4).all()
    return jsonify({
        'news': [new.to_dict() for new in new_]
    })

@app.route('/mp/login', methods=['GET','POST'])
def mp_login():
    info = request.values.get('info')
    appid = os.environ.get('APP_ID')
    secret = os.environ.get('MP_KEY')
    user_info = json.loads(info)
    code = user_info['code']
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code' % (
        appid, secret, code)
    data = requests.get(url).text
    session_ = json.loads(data)
    session_key = session_['session_key']
    encryptedData = user_info['encryptedData']
    iv = user_info['iv']
    pc = WXBizDataCrypt(appid, session_key)
    da = json.loads(pc.decrypt(encryptedData, iv).data)
    mp_id = md5(da['openId'])
    print(mp_id)
    user = Role.query.filter_by(uuid=mp_id).first()
    if not user:
        mp = Role()
        mp.uuid = mp_id
        mp.pwd = md5(str(datetime.now()))
        mp.username = da['nickName']
        mp.default_avatar = da['avatarUrl']
        mp.email = da['openId']
        db.session.add(mp)
        db.session.commit()

    return pc.decrypt(encryptedData, iv)

@app.route('/mp/like', methods=['GET', 'POST'])
def mp_like():
    info = request.values.get('info')
    user_info = json.loads(info)
    wx_name = md5(user_info['openId'])
    num = user_info['num']
    user = Role.query.filter_by(uuid=wx_name).first()
    article = Article.query.filter_by(id=num).first()
    article.view += 1
    db.session.commit()
    if user.is_liked(num):
        user.unlike(num)
    else:
        user.like(num)

    return jsonify(article.to_dict())

@app.route('/mp/like_comment', methods=['GET', 'POST'])
def mp_like_comment():
    info = request.values.get('info')
    user_info = json.loads(info)
    wx_name = md5(user_info['openId'])
    num = user_info['num']
    user = Role.query.filter_by(uuid=wx_name).first()
    comment = Comment.query.filter_by(id=num).first()
    if user.is_liked_comment(num):
        user.unlike_comment(num)
    else:
        user.like_comment(num)

    return jsonify(comment.to_json())

@app.route('/mp/notice', methods=['POST','GET'])
def mp_notice():
    info = request.values.get('info')
    user_info = json.loads(info)
    page = user_info['page'] or 1
    wx_name = md5(user_info['openId'])
    user = Role.query.filter_by(uuid=wx_name).first()
   # count = user.new_comment_like()
    #用户所有评论
    all_comment_id = [coment.id for coment in user.comments.all()]
    #每条评论收到的赞
    comment_like = LikeComment.query.filter(LikeComment.comment_id.in_(all_comment_id)).order_by(
        LikeComment.time.desc()).paginate(page, per_page=10, error_out=False)
    data = [like.to_like_comment() for like in comment_like.items]

    user.last_comment_like_time = datetime.now()
    db.session.commit()

    return jsonify({
        'all':data
    })
@app.route('/mp/notice_reply', methods=['POST','GET'])
def mp_notice_reply():
    info = request.values.get('info')
    user_info = json.loads(info)
    page = user_info['page']
    wx_name = md5(user_info['openId'])
    user = Role.query.filter_by(uuid=wx_name).first()
    all_comment_id = [coment.id for coment in user.comments.all()]
    comment_reply = Reply.query.filter(Reply.comment_id.in_(all_comment_id)).order_by(
        Reply.time.desc()).paginate(page,per_page=10, error_out=False
    )
    data = [reply.to_json() for reply in comment_reply.items]

    user.last_reply_read_time = datetime.now()
    db.session.commit()

    return jsonify({
        'all':data
    })

@app.route('/mp/all_notice', methods=['POST','GET'])
def mp_all_notice():
    info = request.values.get('info')
    user_info = json.loads(info)
    wx_name = md5(user_info['openId'])
    user = Role.query.filter_by(uuid=wx_name).first()
    all_comment_id = [coment.id for coment in user.comments.all()]
    comment_like = LikeComment.query.filter(LikeComment.comment_id.in_(all_comment_id)).order_by(
        LikeComment.time.desc()).paginate(1, per_page=10, error_out=False)
    comment_reply = Reply.query.filter(Reply.comment_id.in_(all_comment_id)).order_by(
        Reply.time.desc()).paginate(1, per_page=10, error_out=False
                                    )
    data = [reply.to_json() for reply in comment_reply.items]
    data1 = [like.to_like_comment() for like in comment_like.items]

    return jsonify({
        'reply':data,
        'like':data1
    })


@app.route('/mp/comment',methods=['POST','GET'])
def mp_comment():
    info = request.values.get('info')
    user_info = json.loads(info)
    wx_name = md5(user_info['openId'])
    num = user_info['num']
    user = Role.query.filter_by(uuid=wx_name).first()
    article = Article.query.filter_by(id=num).first()
    if user :
        article.view += 1
        comment = Comment()
        comment.body = user_info['wx_comment']
        comment.user_id = wx_name
        comment.article_id = user_info['num']
        db.session.add(comment)
        db.session.commit()
    return jsonify(article.to_dict())

@app.route('/mp/my_say', methods=['POST','GET'])
def mp_my_say():
    info = request.values.get('info')
    user_info = json.loads(info)
    wx_name = md5(user_info['openId'])
    user = Role.query.filter_by(uuid=wx_name).first()
    comments = user.comments.order_by(Comment.time.desc())
    return jsonify({
        'all':[comment.to_say() for comment in comments]
    })
@app.route('/mp/my_like', methods=['POST','GET'])
def mp_my_like():
    info = request.values.get('info')
    user_info = json.loads(info)
    wx_name = md5(user_info['openId'])
    user = Role.query.filter_by(uuid=wx_name).first()
    likes = user.likes.order_by(Likes.time.desc())
    return jsonify({
        'all':[like.to_like() for like in likes]
    })

@app.route('/mp/refresh', methods=['POST','GET'])
def mp_refresh():
    info = request.values.get('info')
    user_info = json.loads(info)
    num = user_info['num']
    article = Article.query.filter_by(id=num).first()
    article.view += 1
    db.session.commit()
    return jsonify(article.to_dict())

@app.route('/guaguaka', methods=['POST', 'GET'])
def guaguaka():
    return render_template('guaguaka.html')


@app.route('/danmu', methods=['POST', 'GET'])
def danmu():
    return render_template('danmu.html')


@app.route('/verification', methods=['POST', 'GET'])
def verification():
    return render_template('verification.html')


@app.route('/shake', methods=['POST', 'GET'])
def shake():
    return render_template('shake.html')


@app.route('/loading', methods=['POST', 'GET'])
def loading():
    return render_template('pin.html')


@app.route('/write_mail', methods=['POST', 'GET'])
def write_mail():
    return render_template('oneforone.html')


@app.route('/send_code', methods=['POST', 'GET'])
@login_required
def send_code():
    user = Role.query.filter_by(id=current_user.id).first()
    code = verificationCode
    user.code = str(code)
    db.session.commit()
    send = Message('ALL-in 验证信息', sender=os.environ.get('MAIL_USER'), recipients=[current_user.email])
    send.body = "{}-{}".format('您正在修改ALL-in密码，验证码是', code)
    thread = Thread(target=send_async_email, args=[app, send])
    thread.start()
    return render_template('update_pwd.html')


@app.route('/update_pwd', methods=['POST', 'GET'])
@login_required
def update_pwd():
    code = request.form.get('code')
    new_pwd = request.form.get('new_pwd')
    user = Role.query.filter_by(id=current_user.id).first()
    if code == user.code:
        user.code = ''
        user.pwd = md5(new_pwd)

        db.session.commit()
        return redirect(url_for('logout'))
    else:
        flash('验证码错误')

    return render_template('update_pwd.html')


@app.route('/markdown', methods=['POST', 'GET'])
@login_required
def markdown_edit():
    form = Mark()
    if form.validate_on_submit():
        post = Article()
        post.uuid = current_user.uuid
        post.tittle = form.title.data
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('markdown.html', form=form)

@app.route('/e_upload', methods=['POST','GET'])
@login_required
def e_upload():

    text = 'https://blogai.cn | @{}'.format(current_user.username)
    pic = request.files.get('editormd-image-file')
    fn = time.strftime('%Y%m%d%H%M%S') + '_%d' % random.randint(0, 100) + '.png'
    creat_folder(os.path.join(app.config['UPLOADS_FOLDER'], md5(current_user.uuid)))
    pic_dir = os.path.join(app.config['UPLOADS_FOLDER'], md5(current_user.uuid), fn)
    pic.save(pic_dir)
    image = Image.open(pic_dir)
    draw = ImageDraw.Draw(image)
    width, height = image.size
    margin = 20
    font = ImageFont.truetype("C://Windows/Fonts/simsun.ttc", 20)
    font_w,font_h = draw.textsize(text, font)

    x = (width  - font_w - margin) / 2
    y = height  - font_h - margin
    draw.text((x, y), text, fill=(144, 109, 189),font=font)
    image.save(pic_dir)

    folder = 'uploads/' + md5(current_user.uuid)
    url = folder + '/' + fn
    res = {
        'success': 1,
        'message': '上传成功',
        'url': 'http://127.0.0.1:5000/static/'+url
    }
    return jsonify(res)

@app.route('/c_upload', methods=['POST','GET'])
@login_required
def c_upload():
    error = ''
    #如果无法获取CKEditorFuncNum,去编辑器config下添加config.filebrowserUploadMethod = 'form';
    text = 'https://blogai.cn | @%s' % current_user.username
    callback = request.args.get("CKEditorFuncNum")
    pic = request.files.get('upload')
    fn = time.strftime('%Y%m%d%H%M%S') + '_%d' % random.randint(0, 100) + '.png'
    creat_folder(os.path.join(app.config['UPLOADS_FOLDER'], md5(current_user.uuid)))
    pic_dir = os.path.join(app.config['UPLOADS_FOLDER'], md5(current_user.uuid), fn)
    pic.save(pic_dir)
    image = Image.open(pic_dir)
    draw = ImageDraw.Draw(image)
    width, height = image.size
    margin = 20
    font = ImageFont.truetype("C://Windows/Fonts/simsun.ttc", 20)
    textWidth, textHeight = draw.textsize(text, font)
    x = (width - textWidth - margin) / 2
    y = height - textHeight - margin
    draw.text((x, y), text, fill=(144, 109, 189),font=font)
    image.save(pic_dir)
    folder = 'uploads/' + md5(current_user.uuid)
    url = folder + '/' + fn
    u = 'http://127.0.0.1:5000/static/'+url
    cb_str = """
    <script type="text/javascript">
    window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s')
    </script>
    """% (callback, u, error)
    response = make_response(cb_str)
    response.headers["Content-Type"] = "text/html"

    return response

@app.route('/like_notice', methods=['POST','GET'])
@login_required
def like_notice():
    list = []
    for i in current_user.article:
        for j in i.likes:
            list.append(j.id)

    likes = Likes.query.filter(Likes.id.in_(list)).order_by(Likes.time.desc()).all()
    current_user.last_like_read_time = datetime.now()
    db.session.commit()
    return render_template('like_notice.html', likes=likes)

@app.route('/follow_notice', methods=['POST','GET'])
@login_required
def follow_notice():
    followers=current_user.followers.order_by(Follow.times.desc()).all()
    current_user.last_follow_read_time = datetime.now()
    db.session.commit()
    return render_template('follow_notice.html', followers=followers)

@app.route('/comment_notice', methods=['POST','GET'])
@login_required
def comment_notice():
   # 找出所有评论，加入一个数组
    list = []
    for i in current_user.article:
        for j in i.comments:
            list.append(j.id)

    comments = Comment.query.filter(Comment.id.in_(list)).order_by(Comment.time.desc()).all()
    current_user.last_comment_read_time = datetime.now()
    db.session.commit()
    return render_template('comment_notice.html', comments= comments)
