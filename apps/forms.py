from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import Required,Email,EqualTo,Length
from flask_wtf.file import FileField,FileAllowed,FileRequired
import hashlib
from flask_uploads import UploadSet,IMAGES,UploadNotAllowed
from flask_pagedown.fields import PageDownField
photosSet = UploadSet(name='photos', extensions=IMAGES)




def md5(data):
    md = hashlib.md5()
    md.update(data.encode('utf-8'))
    data = md.hexdigest()
    return data

class NameForm(FlaskForm):
    name = StringField('what is your name?',validators=[Required()] )
    submit =SubmitField('Submit')

class Register(FlaskForm):
    username = StringField(validators=[Required()])
    password = PasswordField(validators=[Required(),EqualTo('password2')])
    password2 = PasswordField(validators=[Required()])
    email = StringField(validators=[Required(),Email()])
    submit = SubmitField('注册')

class Login(FlaskForm):
    username = StringField('username',validators=[Required()])
    password = PasswordField('password',validators=[Required()])
    submit = SubmitField('登陆')

class Profile(FlaskForm):
    avatar = FileField(
        label='上传头像',
        validators=[FileRequired(message='不能为空'), FileAllowed(photosSet)])
    nickname = StringField(validators=[Length(min=4, max=18)])
    gender = RadioField('gender',choices=[('男', 'Male'), ('女', 'Female')])
    birthday = DateField()
    intro = StringField()
    submit = SubmitField('修改')

class PostForm(FlaskForm):
    pic = FileField(
        label='上传封面图',
        validators=[ FileAllowed(photosSet)]
    )
    title = StringField('标题', validators=[Required()])
    body = PageDownField('文章')
    submit = SubmitField('发布')

class CommentForm(FlaskForm):
    body = StringField('', validators=[Length(max=200)])
    submit = SubmitField('评论')

class ReplyForm(FlaskForm):
    body = StringField('', validators=[Length(max=100)])
    submit = SubmitField('回复')



class Mark(FlaskForm):
    pic = FileField(
        label='上传封面图',
        validators=[FileAllowed(photosSet)]
    )
    title = StringField('标题', validators=[Required()])
    body = TextAreaField('文章',id='markdown')
    submit = SubmitField('发布')
