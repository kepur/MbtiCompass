"""
create by khan.hozin {2018/12/6}
"""
__author__ = 'hozin'

from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField,SubmitField,SelectField,RadioField
from wtforms.validators import DataRequired

class NewFrom(FlaskForm):
    '''新闻表单'''
    title=StringField(
        label='新闻标题',
        validators=[DataRequired('请输入标题')],
        description="请输入标题",
        render_kw={'required':"required","class":"form-control"}
    )
    content=TextAreaField(
        label="新闻内容",
        validators=[DataRequired("请输入新闻内容")],
        render_kw={'required':'required','class':'form-control'},
    )
    author=TextAreaField(
        label="作者名字",
        validators=[DataRequired("请输入作者名字")],
        render_kw={'required': 'required', 'class': 'form-control'},
    )
    type=SelectField(
        label="新闻类型",
        choices=[('SEO','seo'),('ThinkPHP5','thinkphp5'),('Flutter','Flutter'),('Python','python'),('Dart','dart')]
    )
    image=StringField(
        label='新闻图片',
        render_kw={'required':'required','class':'form-control'}
    )
    submit=SubmitField('提交')