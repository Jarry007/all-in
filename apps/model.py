from datetime import datetime
from apps import db
import bleach
from flask_login import UserMixin
from markdown import markdown


class Follow(db.Model):
    __tablename__ = 'follows1'
    follower_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'), primary_key=True)
    followed_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'), primary_key=True)
    times = db.Column(db.DATETIME, default=datetime.now)


class Role(UserMixin, db.Model):
    __tablename__ = 'role1'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pwd = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    default_avatar = db.Column(db.String(240))
    avatar = db.Column(db.String(240))
    code = db.Column(db.String(10))
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)
    article = db.relationship('Article', backref='role')
    profile = db.relationship('UserProfile', backref='role')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    replies = db.relationship('Reply', backref='author', lazy='dynamic')
    likes = db.relationship('Likes', backref='author', lazy='dynamic')
    likes_comment = db.relationship('LikeComment', backref='author', lazy='dynamic')
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'), lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'), lazy='dynamic',
                                cascade='all, delete-orphan')
    message_sent = db.relationship('Message', foreign_keys='Message.sender_id',
                                   backref='author', lazy='dynamic')
    message_received = db.relationship('Message', foreign_keys='Message.recipient_id',
                                       backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DATETIME)
    last_comment_read_time = db.Column(db.DATETIME)
    last_like_read_time = db.Column(db.DATETIME)
    last_follow_read_time = db.Column(db.DATETIME)
    last_reply_read_time = db.Column(db.DATETIME)
    last_comment_like_time = db.Column(db.DATETIME)


    def new_comment_like(self):
        last_read_time = self.last_reply_read_time or datetime(1900, 1, 1)
        like_num = 0
        for i in self.comments:
            for j in i.likes:
                if j.time > last_read_time:
                    like_num += 1
        return like_num
# 统计新的赞
    def new_like(self):
        last_read_time = self.last_like_read_time or datetime(1900, 1, 1) #上次查看的时间
        like_num = 0
        for i in self.article:   #遍历所有文章
            for j in i.likes:    #遍历文章下的赞
                if j.time > last_read_time:
                    like_num += 1     #大于上次查看时间的话+1
        return like_num

    # 统计新的评论
    def new_comment(self):
        last_read_time = self.last_comment_read_time or datetime(1900, 1 ,1)
        comment_num = 0
        for i in self.article:
            for j in i.comments:
                if j.time > last_read_time:
                    comment_num += 1
        return comment_num

    # 统计新的关注
    def new_follow(self):
        last_read_time = self.last_follow_read_time or datetime(1900, 1, 1)
        follow_num = 0
        for i in self.followers:
            if i.times > last_read_time:
                follow_num += 1
        return follow_num

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)

        return Message.query.filter_by(recipient=self).filter(Message.time > last_read_time).count()

    def check(self, pwd):  # 对比输入的密码与原密码
        return self.pwd == pwd

    def is_liked(self, post_id):
        return self.likes.filter_by(article_id=post_id).first() is not None

    def like(self, post_id):
        if not self.is_liked(post_id):
            l = Likes()
            l.article_id = post_id
            l.user_id = self.uuid
            db.session.add(l)
            db.session.commit()

    def unlike(self, post_id):
        l = self.likes.filter_by(article_id=post_id).first()
        if l:
            db.session.delete(l)
            db.session.commit()

    def is_liked_comment(self, post_id):
        return self.likes_comment.filter_by(comment_id=post_id).first() is not None

    def like_comment(self, post_id):
        if not self.is_liked_comment(post_id):
            l = LikeComment()
            l.comment_id = post_id
            l.user_id = self.uuid
            db.session.add(l)
            db.session.commit()

    def unlike_comment(self, post_id):
        l = self.likes_comment.filter_by(comment_id=post_id).first()
        if l:
            db.session.delete(l)
            db.session.commit()

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.uuid).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.uuid).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.uuid).first() is not None


    @property
    def friends_post(self):
        follow = Role.query.filter_by(uuid=self.uuid).first()
        follower = follow.followers
        followed = follow.followed
        list1 = []
        list2 = []
        for i in follower:
            list1.append(i.follower.uuid)
        for j in followed:
            list2.append(j.followed.uuid)
        friend_list = [x for x in list1 if x in list2]
        u = Article.query.filter(Article.uuid.in_(friend_list))
        return u


class Article(db.Model):
    __tablename__ = 'article1'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), db.ForeignKey('role1.uuid'), nullable=False)
    tittle = db.Column(db.String(128), nullable=False)
    collections = db.Column(db.Integer, default=0)
    view = db.Column(db.Integer, default=1)
    img = db.Column(db.String(240))
    show = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)
    likes = db.relationship('Likes', backref='article', lazy='dynamic')
    comments = db.relationship('Comment', backref='article', lazy='dynamic')

    def to_dict(self):
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'tittle': self.tittle,
            'view_count': self.view,
            'show': self.show,
            'img': self.img,
            'body': self.body,
            'body_html': self.body_html,
            'time': self.addtime,
            'like_count': self.likes.count(),
            'comment': self.comments.count(),
            'link_': {
                'avatar': self.send_avatar(),
                'username': self.role.username
            },
            'new_comment': {'comments': self.filter_c},
            'likes':self.filter_l()
            # 这里是一个路由，怎样让他返回一个查询结果，而不仅仅是一个路由.添加函数，使其返回。在
        }
        return data

    def send_avatar(self):
        if self.role.avatar:
            avatar = self.role.avatar
        else:
            avatar = self.role.default_avatar

        return avatar

    @property
    def filter_c(self):
        comments = Comment.query.filter_by(article_id=self.id).all()
        return [comment.to_json() for comment in comments]

    def filter_l(self):
        likes = Likes.query.filter_by(article_id=self.id).all()
        return [like.to_like() for like in likes]

    @staticmethod
    def on_change_body(target, value, oldvalue, initator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p',
                        'br', 'span', 'hr', 'src', 'class','table','thead','tr','th','td']
        allowed_attrs = {'*': ['class', 'pre'],
                         'a': ['href', 'rel'],
                         'img': ['src', 'alt']
                         }
        text =  markdown(value, output='html',extensions=['markdown.extensions.toc','markdown.extensions.fenced_code','markdown.extensions.tables'])

        target.body_html = bleach.linkify(bleach.clean(text,
            tags=allowed_tags, strip=True, attributes=allowed_attrs
        ))


db.event.listen(Article.body,'set',Article.on_change_body)


class Likes(db.Model):
    __tablename__ = 'likes1'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article1.id'))
    user_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'))
    time = db.Column(db.DATETIME, default=datetime.now)

    def to_like(self):
        data = {
            'id': self.id,
            'article_id': self.article_id,
            'article_title':self.article.tittle,
            'user_id': self.user_id,
            'time': self.time,
            'img':self.send_img()

        }
        return data
    def send_img(self):
        if self.article.img:
            img = self.article.img
        else:
            img = 'img/blog/blog-2.jpg'

        return img


class UserProfile(db.Model):
    __tablename__= 'userprofile1'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'))
    nickname = db.Column(db.String(80))
    gender = db.Column(db.String(80))
    birthday = db.Column(db.Date)
    intro = db.Column(db.Text)


class IpList(db.Model):
    __tablename__ = 'ip1'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50))
    agent = db.Column(db.Text)
    adders = db.Column(db.String(300))
    time = db.Column(db.DATETIME, index=True, default=datetime.now)


class Comment(db.Model):
    __tablename__ = 'comments1'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article1.id'))
    user_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'))
    body = db.Column(db.String(200))
    time = db.Column(db.DATETIME, index=True, default=datetime.now)
    reply = db.relationship('Reply', backref='comments', lazy='dynamic')
    likes = db.relationship('LikeComment', backref='comments', lazy='dynamic')

    def to_json(self):
        data = {
            'id': self.id,
            'article_id': self.article_id,
            'user_id': self.user_id,
            'body': self.body,
            'time': self.time,
            '_link': {
                'avatar': self.send_avatar(),
                'username': self.author.username
            },
            'replies': {
                'r': self.filter_reply
            }
        }
        return data
    def to_say(self):
        data={
            'id' :self.id,
            'article_id': self.article_id,
            'article_title':self.article.tittle,
            'body':self.body,
            'user_id': self.user_id,
            'time': self.time,
            'img':self.send_img()
        }

        return data
    def send_img(self):
        if self.article.img:
            img = self.article.img
        else:
            img = 'img/blog/blog-2.jpg'

        return img

    def show_title(self):

        return self.article.tittle

    def send_avatar(self):
        if self.author.avatar:
            avatar = self.author.avatar
        else:
            avatar = self.author.default_avatar

        return avatar



    # 这里必须返回值是一个list,否则后续json话时无法成功
    @property
    def filter_reply(self):
        reply = Reply.query.filter_by(comment_id=self.id).all()
        return [r.to_json() for r in reply]


class Reply(db.Model):
    __tablename__ = 'replies1'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments1.id'))
    replies_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'))
    body = db.Column(db.String(100))
    time = db.Column(db.DATETIME, index=True, default=datetime.now)

    def to_json(self):
        data = {
            'id': self.id,
            'comment_id': self.comment_id,
            'comment_body': self.comments.body,
            'user_id': self.replies_id,
            'body': self.body,
            'time': self.time,
            'user_name': self.author.username,
            'article_id': self.comments.article_id,
            'user_avatar': self.send_avatar(),
            'new': self.is_new(self.author.last_reply_read_time or datetime(1900, 1, 1))
        }
        return data

    def send_avatar(self):
        if self.author.avatar:
            avatar = self.author.avatar
        else:
            avatar = self.author.default_avatar
        return avatar

    def is_new(self,time):
        if self and self.time > time:
            status = 'is_new'
        else:
            status = ''
        return status


class LikeComment(db.Model):
    __tablename__ = 'likecomment'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments1.id'))
    user_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'))
    time = db.Column(db.DATETIME, default=datetime.now)

    def to_like_comment(self):
        data = {
            'id': self.id,
            'comment_id': self.comment_id,
            'comment_body': self.comments.body,
            'user_id': self.user_id,
            'user_name':self.author.username,
            'time': self.time,
            'article_id': self.comments.article_id,
            'user_avatar':self.send_avatar(),
            'new':self.is_new(self.author.last_comment_like_time or datetime(1900, 1, 1))
        }
        return data

    def send_avatar(self):
        if self.author.avatar:
            avatar = self.author.avatar
        else:
            avatar = self.author.default_avatar

        return avatar

    def is_new(self,time):
        if self and self.time > time:
            status = 'is_new'
        else:
            status = ''
        return status


class Message(db.Model):
    __tablename__ = 'message1'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'), primary_key=True)
    recipient_id = db.Column(db.String(32), db.ForeignKey('role1.uuid'), primary_key=True)
    body = db.Column(db.String(140))
    time = db.Column(db.DATETIME, index=True, default=datetime.now)



if __name__ == '__main__':
    db.drop_all()
    db.create_all()
