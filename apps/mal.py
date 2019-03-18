from faker import Faker
import os,uuid,hashlib
from apps import db
from apps.model import Role,Article,Follow
from alembic import op
from functools import wraps
faker = Faker(locale='zh_CN')
def md5(data):
    md = hashlib.md5()
    md.update(data.encode('utf-8'))
    data = md.hexdigest()
    return data
num = 1
while num <20:
    name = faker.name()
    username = faker.user_name()
    pwd = md5(str(num))
    num +=1
    print('姓名：'+name)
    print('用户名：'+username)
    print('pwd：'+pwd)
"""
num = 1
while num < 10:
    #role = Role.query.filter_by(id=2ecfa8fcf29344899654acaa9fa4c7f2).first()
    u = Article()
    u.uuid = '2ecfa8fcf29344899654acaa9fa4c7f2'
    u.body = faker.name()
    u.body_html = faker.name()
    u.tittle = faker.company()
    u.addtime = faker.date_time()
    db.session.add(u)

    u = Role()
    uu_id = str(uuid.uuid4()).replace('-', '')
    u.uuid = uu_id
    u.username = faker.user_name()
    u.pwd = md5(str(num))
    u.email = faker.email()
    db.session.add(u)
   
    try:
        db.session.commit()
        num += 1
    except:
        db.session.rollback()



def avatar(email):
    size = 180
    default = 'monsterid'
    r = 'g'
    m = hashlib.md5()
    m.update(email.encode('utf-8'))
    hash = m.hexdigest()
    a_url = 'https://www.gravatar.com/avatar/{hash}?s={size}&d={default}&r={r}'.format(hash=hash,size=size,default=default,r=r)
    return a_url
    
follow = Role.query.filter_by(username='111').first()
follower = follow.followers
followed = follow.followed
list1 = []
list2 = []
for i in follower:
    list1.append(i.follower.uuid)
for j in followed:
    list2.append(j.followed.uuid)


list = set(list1).intersection(set(list2))
if '222' in list:
    print('222in')
print(list)
def friends_circle(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        follow = Role.query.filter_by(uuid= current_user.uuid).first()
        follower = follow.followers
        followed = follow.followed
        list1 = []
        list2 = []
        for i in follower:
            list1.append(i.follower.uuid)
        for j in followed:
            list2.append(j.followed.uuid)

        list = set(list1).intersection(set(list2))
        print(list)
        return func(*args, **kwargs)
    return wrapper
@friends_circle
def u(username):
    print('woshi u')
    return u
   


def seem_likes():
    #f = Follow.query.filter(Follow.follower_id == '1f675baf550d4bf09bf4a2ea422c3572').all()

    #p = Role.query.join(Follow, Follow.follower_id == '1f675baf550d4bf09bf4a2ea422c3572').filter(Follow.followed_id == "1f675baf550d4bf09bf4a2ea422c3572").all()
    q = Article.query.join(Follow, Follow.followed_id == Article.uuid).filter(Follow.follower_id == '1f675baf550d4bf09bf4a2ea422c3572' ).order_by(Article.addtime.desc())
    p = Article.query.join(Follow, Follow.follower_id ==  Article.uuid).filter(
        Follow.followed_id == '1f675baf550d4bf09bf4a2ea422c3572').order_by(Article.addtime.desc())

    o = [x for x in q if x in p].paginate

    for i in o:
        print(i.addtime)

    return 'dd'
seem_likes()

def kk():
    a = Article.query.join(Follow, Follow.follower_id == Article.uuid).filter(
        Follow.followed_id == '1f675baf550d4bf09bf4a2ea422c3572').order_by(Article.addtime.desc())
    p = a.paginate(1,per_page=5,error_out=False)
    s = p.items
    print(s)
    return 'd'
kk()


def friends_circle():
    follow = Role.query.filter_by(uuid='1f675baf550d4bf09bf4a2ea422c3572').first()
    follower = follow.followers
    followed = follow.followed
    list1 = []
    list2 = []
    for i in follower:
        list1.append(i.follower.uuid)
    for j in followed:
        list2.append(j.followed.uuid)

    friend_list =[x for x in list1 if x in list2 ]
    u = Article.query.filter(Article.uuid.in_(friend_list))
    r = u.order_by(Article.addtime.desc()).paginate(1, per_page=10, error_out=False)
    print(r.items)
    return friend_list
friends_circle()
"""