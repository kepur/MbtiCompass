"""
create by khan.hozin 2018.09
"""
__author__ = 'hozin'

from . import admin
from flask import  render_template,redirect,flash,url_for
from app.models.user_model import News
from .payment_res import NewFrom
from datetime import datetime
from app import db


#博客的后台
@admin.route('/')
def index():
    return render_template('admin/index.html')

@admin.route("/list/<int:page>", methods=["GET"])
def list(page=None):
    #如果没有传择表示第一页
    if page is None:
        page=1
    news_list=News.query.filter_by(is_valid=True).paginate(page=page,per_page=5)
    return render_template('admin/list.html',news_list=news_list)

@admin.route('/add/',methods=['GET','POST'])
def add():
    form=NewFrom()
    if form.validate_on_submit():
        form_Data=News(
            title=form.title.data,
            content=form.content.data,
            type=form.type.data,
            image=form.image.data,
            created_at=datetime.now(),
            author=form.author(),
            is_valid=True
        )
        db.session.add(form_Data)
        db.session.commit()
        #文字提示
        #flash
        flash("添加内容成功", 'ola')
        return redirect(url_for('admin.add'))
    return render_template('admin/add.html',form=form)

# @app.route('/admin/edit/<int:pk>',methods=['GET','POST'])
# def edit(pk):
#     form=NewFrom()
#     old_obj=News.query.get(pk)
#     if not old_obj:
#         flash("没有数据", 'err')
#         return redirect(url_for('list',page=1))
#     if form.validate_on_submit():
#         form_Data=News(
#             title=form.title.data,
#             content=form.content.data,
#             type=form.news_type.data,
#             image=form.img_url.data,
#             created_at=datetime.now()
#         )
#         db.session.add(form_Data)
#         db.session.commit()
#         flash("更新成功",'ola')
#         return redirect(url_for(list))
#     return render_template('admin/edit.html',old_obj=old_obj,form=form)
# <div class="form-group">
# <label for="inputPassword3" class="col-md-3 control-label" >
#     {{ form.title.label.text }}
# </label>
# <div class="col-md-9">{{ form.title (value=old_obj.title)}}</div>
# </div>

@admin.route('/edit/<int:pk>',methods=['GET','POST'])
def edit(pk):
    new_obj=News.query.get(pk)
    if not new_obj:
        #TODO 使用Flash 文字提示用户
        return redirect(url_for('admin.list'))
    form = NewFrom(obj=new_obj)
    if form.validate_on_submit():
        new_obj.title=form.title.data
        new_obj.content=form.content.data
        new_obj.type=form.type.data
        new_obj.image=form.image.data
        new_obj.created_at=datetime.now()
        db.session.add(new_obj)
        db.session.commit()
        flash('修改信息成功','ola')
        return redirect(url_for('admin.list',page=1))
    return render_template('admin/edit.html',form=form)

@admin.route('/del/<int:pk>',methods=['GET','POST'])
def delete(pk):
    '''
    删除新闻信息
    '''
    new_obj=News.query.get(pk)
    if not new_obj:
        return 'no'
    new_obj.is_valid=False
    db.session.add(new_obj)
    db.session.commit()
    return 'yes'
